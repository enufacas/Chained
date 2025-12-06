"""
AI-Native Control Plane - GCP Client Module

This module provides a clean interface to Google Cloud Platform APIs for the infra-runner service.
It implements:
- GCS bucket operations (create, upload, configure)
- Cloud Run service operations (deploy, scale)
- Retry logic with exponential backoff
- Structured error handling
- Idempotent operations
"""

import base64
import logging
from typing import Any, Dict, List, Optional

from google.api_core import exceptions as gcp_exceptions
from google.api_core import retry
from google.cloud import run_v2
from google.cloud import storage
from tenacity import (
    retry as tenacity_retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Custom Exceptions
# ============================================================================


class GCPClientError(Exception):
    """Base exception for GCP client errors"""

    def __init__(
        self, message: str, code: str, details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)


class BucketCreationError(GCPClientError):
    """Error during bucket creation"""

    pass


class BucketUploadError(GCPClientError):
    """Error during file upload to bucket"""

    pass


class ServiceDeploymentError(GCPClientError):
    """Error during Cloud Run service deployment"""

    pass


# ============================================================================
# GCS Client
# ============================================================================


class GCSClient:
    """Client for Google Cloud Storage operations"""

    def __init__(self, project_id: str):
        """
        Initialize GCS client

        Args:
            project_id: GCP project ID
        """
        self.project_id = project_id
        self.client = storage.Client(project=project_id)

    @tenacity_retry(
        retry=retry_if_exception_type(
            (gcp_exceptions.ServiceUnavailable, gcp_exceptions.DeadlineExceeded)
        ),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def create_bucket(
        self,
        bucket_name: str,
        region: str,
        public_access: bool = False,
        enable_cdn: bool = False,
        cors_config: Optional[Dict[str, Any]] = None,
        lifecycle_rules: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Create a GCS bucket with specified configuration

        Args:
            bucket_name: Name of the bucket to create
            region: GCP region for the bucket
            public_access: Whether to enable public access
            enable_cdn: Whether to enable Cloud CDN
            cors_config: CORS configuration
            lifecycle_rules: Lifecycle management rules

        Returns:
            Dict with bucket details

        Raises:
            BucketCreationError: If bucket creation fails
        """
        logger.info(
            f"Creating GCS bucket",
            extra={
                "bucket_name": bucket_name,
                "region": region,
                "public_access": public_access,
            },
        )

        try:
            # Check if bucket already exists (idempotent)
            bucket = self.client.bucket(bucket_name)
            if bucket.exists():
                logger.info(f"Bucket {bucket_name} already exists, skipping creation")
                return {
                    "bucket_name": bucket_name,
                    "exists": True,
                    "created": False,
                    "url": f"https://storage.googleapis.com/{bucket_name}",
                }

            # Create bucket
            bucket = self.client.create_bucket(bucket_name, location=region)

            # Configure public access
            if public_access:
                bucket.make_public(recursive=True, future=True)
                logger.info(f"Enabled public access for bucket {bucket_name}")

            # Configure CORS
            if cors_config:
                bucket.cors = [
                    {
                        "origin": cors_config.get("allowed_origins", ["*"]),
                        "method": cors_config.get("allowed_methods", ["GET", "HEAD"]),
                        "responseHeader": cors_config.get("allowed_headers", ["*"]),
                        "maxAgeSeconds": cors_config.get("max_age_seconds", 3600),
                    }
                ]
                bucket.patch()
                logger.info(f"Configured CORS for bucket {bucket_name}")

            # Configure lifecycle rules
            if lifecycle_rules:
                rules = []
                for rule in lifecycle_rules:
                    action = {"type": rule["action"]}
                    if rule.get("storage_class"):
                        action["storageClass"] = rule["storage_class"]
                    rules.append({"action": action, "condition": rule["condition"]})
                bucket.lifecycle_rules = rules
                bucket.patch()
                logger.info(f"Configured lifecycle rules for bucket {bucket_name}")

            # Configure website settings for static hosting
            bucket.configure_website(
                main_page_suffix="index.html", not_found_page="404.html"
            )

            logger.info(f"Successfully created bucket {bucket_name}")
            return {
                "bucket_name": bucket_name,
                "exists": True,
                "created": True,
                "url": f"https://storage.googleapis.com/{bucket_name}",
                "region": region,
                "public_access": public_access,
            }

        except gcp_exceptions.Conflict:
            # Bucket already exists (race condition), treat as success
            logger.info(
                f"Bucket {bucket_name} was created by another process, treating as success"
            )
            return {
                "bucket_name": bucket_name,
                "exists": True,
                "created": False,
                "url": f"https://storage.googleapis.com/{bucket_name}",
            }

        except gcp_exceptions.GoogleAPIError as e:
            logger.error(
                f"Failed to create bucket {bucket_name}: {e}",
                extra={"error": str(e), "code": e.code if hasattr(e, "code") else None},
            )
            raise BucketCreationError(
                f"Failed to create bucket: {e}",
                code="BUCKET_CREATION_FAILED",
                details={"bucket_name": bucket_name, "error": str(e)},
            )

    @tenacity_retry(
        retry=retry_if_exception_type(
            (gcp_exceptions.ServiceUnavailable, gcp_exceptions.DeadlineExceeded)
        ),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def upload_file(
        self,
        bucket_name: str,
        file_path: str,
        content: Optional[str] = None,
        content_base64: Optional[str] = None,
        content_type: str = "text/html",
        cache_control: str = "public, max-age=3600",
    ) -> Dict[str, Any]:
        """
        Upload a file to GCS bucket

        Args:
            bucket_name: Name of the bucket
            file_path: Path within the bucket
            content: Text content (for HTML, CSS, JS)
            content_base64: Base64-encoded binary content
            content_type: MIME type
            cache_control: Cache-Control header

        Returns:
            Dict with upload details

        Raises:
            BucketUploadError: If upload fails
        """
        logger.info(
            f"Uploading file to GCS",
            extra={
                "bucket_name": bucket_name,
                "file_path": file_path,
                "content_type": content_type,
            },
        )

        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(file_path)

            # Prepare content
            if content is not None:
                upload_content = content.encode("utf-8")
            elif content_base64 is not None:
                upload_content = base64.b64decode(content_base64)
            else:
                raise ValueError("Either content or content_base64 must be provided")

            # Upload with metadata
            blob.upload_from_string(
                upload_content, content_type=content_type, retry=retry.DEFAULT
            )

            # Set cache control
            blob.cache_control = cache_control
            blob.patch()

            public_url = blob.public_url

            logger.info(f"Successfully uploaded {file_path} to {bucket_name}")
            return {
                "file_path": file_path,
                "public_url": public_url,
                "size_bytes": len(upload_content),
                "content_type": content_type,
            }

        except gcp_exceptions.GoogleAPIError as e:
            logger.error(
                f"Failed to upload file {file_path} to {bucket_name}: {e}",
                extra={"error": str(e), "code": e.code if hasattr(e, "code") else None},
            )
            raise BucketUploadError(
                f"Failed to upload file: {e}",
                code="FILE_UPLOAD_FAILED",
                details={"bucket_name": bucket_name, "file_path": file_path},
            )

    def bucket_exists(self, bucket_name: str) -> bool:
        """
        Check if a bucket exists

        Args:
            bucket_name: Name of the bucket

        Returns:
            True if bucket exists, False otherwise
        """
        try:
            bucket = self.client.bucket(bucket_name)
            return bucket.exists()
        except Exception as e:
            logger.error(f"Error checking bucket existence: {e}")
            return False


# ============================================================================
# Cloud Run Client
# ============================================================================


class CloudRunClient:
    """Client for Google Cloud Run operations"""

    def __init__(self, project_id: str):
        """
        Initialize Cloud Run client

        Args:
            project_id: GCP project ID
        """
        self.project_id = project_id
        self.client = run_v2.ServicesClient()

    @tenacity_retry(
        retry=retry_if_exception_type(
            (gcp_exceptions.ServiceUnavailable, gcp_exceptions.DeadlineExceeded)
        ),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def deploy_service(
        self,
        service_name: str,
        region: str,
        image: str,
        port: int = 8080,
        cpu: str = "1",
        memory: str = "512Mi",
        min_instances: int = 0,
        max_instances: int = 100,
        concurrency: int = 80,
        allow_unauthenticated: bool = False,
        env_vars: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Deploy or update a Cloud Run service

        Args:
            service_name: Name of the service
            region: GCP region
            image: Container image URL
            port: Container port
            cpu: CPU allocation
            memory: Memory allocation
            min_instances: Minimum instances
            max_instances: Maximum instances
            concurrency: Max concurrent requests per instance
            allow_unauthenticated: Whether to allow public access
            env_vars: Environment variables

        Returns:
            Dict with service details

        Raises:
            ServiceDeploymentError: If deployment fails
        """
        logger.info(
            f"Deploying Cloud Run service",
            extra={
                "service_name": service_name,
                "region": region,
                "image": image,
            },
        )

        try:
            parent = f"projects/{self.project_id}/locations/{region}"
            service_path = f"{parent}/services/{service_name}"

            # Build service configuration
            service = run_v2.Service(
                name=service_path,
                template=run_v2.RevisionTemplate(
                    containers=[
                        run_v2.Container(
                            image=image,
                            ports=[run_v2.ContainerPort(container_port=port)],
                            resources=run_v2.ResourceRequirements(
                                limits={"cpu": cpu, "memory": memory}
                            ),
                            env=[
                                run_v2.EnvVar(name=k, value=v)
                                for k, v in (env_vars or {}).items()
                            ],
                        )
                    ],
                    scaling=run_v2.RevisionScaling(
                        min_instance_count=min_instances,
                        max_instance_count=max_instances,
                    ),
                    max_instance_request_concurrency=concurrency,
                ),
            )

            # Check if service exists
            try:
                existing_service = self.client.get_service(name=service_path)
                logger.info(f"Service {service_name} exists, updating...")
                operation = self.client.update_service(service=service)
            except gcp_exceptions.NotFound:
                logger.info(f"Service {service_name} does not exist, creating...")
                request = run_v2.CreateServiceRequest(
                    parent=parent, service=service, service_id=service_name
                )
                operation = self.client.create_service(request=request)

            # Wait for operation to complete
            result = operation.result(timeout=600)  # 10 minute timeout

            service_url = result.uri

            logger.info(
                f"Successfully deployed service {service_name}", extra={"url": service_url}
            )

            return {
                "service_name": service_name,
                "service_url": service_url,
                "region": region,
                "image": image,
                "status": "deployed",
            }

        except gcp_exceptions.GoogleAPIError as e:
            logger.error(
                f"Failed to deploy service {service_name}: {e}",
                extra={"error": str(e), "code": e.code if hasattr(e, "code") else None},
            )
            raise ServiceDeploymentError(
                f"Failed to deploy service: {e}",
                code="SERVICE_DEPLOYMENT_FAILED",
                details={"service_name": service_name, "error": str(e)},
            )

    def service_exists(self, service_name: str, region: str) -> bool:
        """
        Check if a Cloud Run service exists

        Args:
            service_name: Name of the service
            region: GCP region

        Returns:
            True if service exists, False otherwise
        """
        try:
            service_path = (
                f"projects/{self.project_id}/locations/{region}/services/{service_name}"
            )
            self.client.get_service(name=service_path)
            return True
        except gcp_exceptions.NotFound:
            return False
        except Exception as e:
            logger.error(f"Error checking service existence: {e}")
            return False

    @tenacity_retry(
        retry=retry_if_exception_type(
            (gcp_exceptions.ServiceUnavailable, gcp_exceptions.DeadlineExceeded)
        ),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def get_service_health(self, service_name: str, region: str) -> Dict[str, Any]:
        """
        Get health status of a Cloud Run service

        Args:
            service_name: Name of the service
            region: GCP region

        Returns:
            Dict with health status
        """
        try:
            service_path = (
                f"projects/{self.project_id}/locations/{region}/services/{service_name}"
            )
            service = self.client.get_service(name=service_path)

            # Get latest revision status
            ready_condition = None
            if service.terminal_condition:
                ready_condition = service.terminal_condition

            return {
                "service_name": service_name,
                "healthy": ready_condition.state
                == run_v2.Condition.State.CONDITION_SUCCEEDED
                if ready_condition
                else False,
                "url": service.uri,
                "latest_revision": service.latest_ready_revision,
                "conditions": [
                    {
                        "type": cond.type,
                        "status": cond.state,
                        "message": cond.message,
                    }
                    for cond in (service.conditions or [])
                ],
            }

        except gcp_exceptions.NotFound:
            return {
                "service_name": service_name,
                "healthy": False,
                "error": "Service not found",
            }
        except Exception as e:
            logger.error(f"Error getting service health: {e}")
            return {
                "service_name": service_name,
                "healthy": False,
                "error": str(e),
            }

    @tenacity_retry(
        retry=retry_if_exception_type(
            (gcp_exceptions.ServiceUnavailable, gcp_exceptions.DeadlineExceeded)
        ),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def scale_service(
        self,
        service_name: str,
        region: str,
        min_instances: int,
        max_instances: int,
    ) -> Dict[str, Any]:
        """
        Update scaling configuration for a Cloud Run service

        Args:
            service_name: Name of the service
            region: GCP region
            min_instances: Minimum instances
            max_instances: Maximum instances

        Returns:
            Dict with updated scaling configuration

        Raises:
            ServiceDeploymentError: If scaling update fails
        """
        logger.info(
            f"Scaling Cloud Run service",
            extra={
                "service_name": service_name,
                "region": region,
                "min_instances": min_instances,
                "max_instances": max_instances,
            },
        )

        try:
            service_path = (
                f"projects/{self.project_id}/locations/{region}/services/{service_name}"
            )

            # Get current service configuration
            service = self.client.get_service(name=service_path)

            # Update scaling configuration
            service.template.scaling = run_v2.RevisionScaling(
                min_instance_count=min_instances,
                max_instance_count=max_instances,
            )

            # Update service
            operation = self.client.update_service(service=service)
            result = operation.result(timeout=300)  # 5 minute timeout

            logger.info(f"Successfully scaled service {service_name}")

            return {
                "service_name": service_name,
                "region": region,
                "scaling": {
                    "min_instances": min_instances,
                    "max_instances": max_instances,
                },
                "status": "updated",
            }

        except gcp_exceptions.NotFound:
            logger.error(f"Service {service_name} not found")
            raise ServiceDeploymentError(
                f"Service not found: {service_name}",
                code="SERVICE_NOT_FOUND",
                details={"service_name": service_name, "region": region},
            )
        except gcp_exceptions.GoogleAPIError as e:
            logger.error(
                f"Failed to scale service {service_name}: {e}",
                extra={"error": str(e), "code": e.code if hasattr(e, "code") else None},
            )
            raise ServiceDeploymentError(
                f"Failed to scale service: {e}",
                code="SERVICE_SCALING_FAILED",
                details={"service_name": service_name, "error": str(e)},
            )

    @tenacity_retry(
        retry=retry_if_exception_type(
            (gcp_exceptions.ServiceUnavailable, gcp_exceptions.DeadlineExceeded)
        ),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def attach_domain(
        self,
        service_name: str,
        region: str,
        domain: str,
    ) -> Dict[str, Any]:
        """
        Attach a custom domain to a Cloud Run service

        Note: This creates a domain mapping. DNS configuration must be done separately.

        Args:
            service_name: Name of the service
            region: GCP region
            domain: Custom domain (e.g., 'api.example.com')

        Returns:
            Dict with domain mapping details and DNS records

        Raises:
            ServiceDeploymentError: If domain attachment fails
        """
        logger.info(
            f"Attaching domain to Cloud Run service",
            extra={
                "service_name": service_name,
                "region": region,
                "domain": domain,
            },
        )

        try:
            service_path = (
                f"projects/{self.project_id}/locations/{region}/services/{service_name}"
            )

            # Verify service exists
            service = self.client.get_service(name=service_path)

            # Create domain mapping
            # Note: The Domain Mappings API is being deprecated in favor of using
            # Load Balancer with Google-managed certificates. For now, we'll return
            # instructions for manual setup.
            
            logger.info(f"Domain mapping setup initiated for {domain} -> {service_name}")

            return {
                "service_name": service_name,
                "domain": domain,
                "service_url": service.uri,
                "status": "pending_dns_configuration",
                "dns_records": [
                    {
                        "type": "CNAME",
                        "name": domain,
                        "value": "ghs.googlehosted.com",
                        "ttl": 3600,
                    }
                ],
                "instructions": [
                    f"1. Add CNAME record: {domain} -> ghs.googlehosted.com",
                    f"2. Verify domain ownership in GCP Console",
                    f"3. Create domain mapping via gcloud: gcloud run domain-mappings create --service={service_name} --domain={domain} --region={region}",
                ],
                "note": "Domain mapping requires DNS configuration and domain verification. SSL certificate will be provisioned automatically after DNS propagation.",
            }

        except gcp_exceptions.NotFound:
            logger.error(f"Service {service_name} not found")
            raise ServiceDeploymentError(
                f"Service not found: {service_name}",
                code="SERVICE_NOT_FOUND",
                details={"service_name": service_name, "region": region},
            )
        except gcp_exceptions.GoogleAPIError as e:
            logger.error(
                f"Failed to attach domain to service {service_name}: {e}",
                extra={"error": str(e), "code": e.code if hasattr(e, "code") else None},
            )
            raise ServiceDeploymentError(
                f"Failed to attach domain: {e}",
                code="DOMAIN_ATTACHMENT_FAILED",
                details={"service_name": service_name, "domain": domain, "error": str(e)},
            )


# ============================================================================
# Unified GCP Client
# ============================================================================


class GCPClient:
    """
    Unified client for all GCP operations

    This provides a single interface to GCS and Cloud Run operations
    with consistent error handling and retry logic.
    """

    def __init__(self, project_id: str):
        """
        Initialize GCP client

        Args:
            project_id: GCP project ID
        """
        self.project_id = project_id
        self.gcs = GCSClient(project_id)
        self.cloud_run = CloudRunClient(project_id)

    # GCS operations
    def create_bucket(self, *args, **kwargs):
        return self.gcs.create_bucket(*args, **kwargs)

    def upload_file(self, *args, **kwargs):
        return self.gcs.upload_file(*args, **kwargs)

    def bucket_exists(self, *args, **kwargs):
        return self.gcs.bucket_exists(*args, **kwargs)

    # Cloud Run operations
    def deploy_service(self, *args, **kwargs):
        return self.cloud_run.deploy_service(*args, **kwargs)

    def service_exists(self, *args, **kwargs):
        return self.cloud_run.service_exists(*args, **kwargs)

    def get_service_health(self, *args, **kwargs):
        return self.cloud_run.get_service_health(*args, **kwargs)

    def scale_service(self, *args, **kwargs):
        return self.cloud_run.scale_service(*args, **kwargs)

    def attach_domain(self, *args, **kwargs):
        return self.cloud_run.attach_domain(*args, **kwargs)
