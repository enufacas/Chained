#!/usr/bin/env python3
"""
Universal API Client for Chained Agents
Created by @bridge-master for Mission idea:30

A unified client for agent communication across multiple protocols and formats.
Provides a bridge for seamless API integration.

Usage:
    async with UniversalAPIClient() as client:
        response = await client.call_api('https://api.example.com/data', method='GET')
        
    # Or with monitoring
    async with UniversalAPIClient(monitor=monitor) as client:
        response = await client.call_api('https://api.example.com/data')
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Protocol(Enum):
    """Supported API protocols"""
    REST = "rest"
    GRAPHQL = "graphql"
    WEBSOCKET = "websocket"
    WEBHOOK = "webhook"


@dataclass
class APIRequest:
    """Represents an API request"""
    url: str
    method: str = 'GET'
    headers: Optional[Dict[str, str]] = None
    data: Optional[Dict[str, Any]] = None
    params: Optional[Dict[str, str]] = None
    timeout: Optional[int] = None
    protocol: Protocol = Protocol.REST


@dataclass
class APIResponse:
    """Represents an API response"""
    success: bool
    status_code: Optional[int] = None
    data: Optional[Any] = None
    headers: Optional[Dict[str, str]] = None
    error: Optional[str] = None
    message: Optional[str] = None
    duration_ms: Optional[float] = None


class CircuitBreaker:
    """
    Circuit breaker pattern for API resilience
    
    Prevents cascading failures by stopping calls to failing services.
    States: CLOSED (normal), OPEN (failing), HALF_OPEN (testing recovery)
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        half_open_max_calls: int = 3
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'
        self.half_open_calls = 0
    
    def can_proceed(self) -> bool:
        """Check if call can proceed"""
        if self.state == 'CLOSED':
            return True
        
        if self.state == 'OPEN':
            # Check if recovery timeout elapsed
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = 'HALF_OPEN'
                self.half_open_calls = 0
                return True
            return False
        
        if self.state == 'HALF_OPEN':
            # Allow limited calls in half-open state
            if self.half_open_calls < self.half_open_max_calls:
                self.half_open_calls += 1
                return True
            return False
        
        return False
    
    def record_success(self):
        """Record successful call"""
        if self.state == 'HALF_OPEN':
            # Recovery confirmed, close circuit
            self.state = 'CLOSED'
            self.failure_count = 0
        elif self.state == 'CLOSED':
            # Gradual recovery
            self.failure_count = max(0, self.failure_count - 1)
    
    def record_failure(self):
        """Record failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == 'HALF_OPEN':
            # Failed during recovery, reopen circuit
            self.state = 'OPEN'
        elif self.failure_count >= self.failure_threshold:
            # Too many failures, open circuit
            self.state = 'OPEN'


class UniversalAPIClient:
    """
    Universal API client for Chained agents
    
    Built by @bridge-master to create bridges between systems.
    Supports multiple protocols with automatic retry, circuit breaking, and monitoring.
    """
    
    def __init__(
        self,
        timeout: int = 30,
        retry_count: int = 3,
        retry_delay: int = 1,
        monitor: Optional[Any] = None,
        enable_circuit_breaker: bool = True
    ):
        """
        Initialize Universal API Client
        
        Args:
            timeout: Default request timeout in seconds
            retry_count: Number of retries for failed requests
            retry_delay: Initial delay between retries (exponential backoff)
            monitor: Optional monitoring instance (APIMonitoringBridge)
            enable_circuit_breaker: Enable circuit breaker pattern
        """
        self.session: Optional[aiohttp.ClientSession] = None
        self.timeout = timeout
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.monitor = monitor
        self.enable_circuit_breaker = enable_circuit_breaker
        
        # Circuit breakers per host
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _get_circuit_breaker(self, url: str) -> CircuitBreaker:
        """Get or create circuit breaker for host"""
        from urllib.parse import urlparse
        host = urlparse(url).netloc
        
        if host not in self.circuit_breakers:
            self.circuit_breakers[host] = CircuitBreaker()
        
        return self.circuit_breakers[host]
    
    async def call_api(
        self,
        url: str,
        method: str = 'GET',
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None
    ) -> APIResponse:
        """
        Universal API call method
        
        Supports REST APIs with automatic retry, circuit breaking, and monitoring.
        
        Args:
            url: Full URL of the API endpoint
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            headers: Optional request headers
            data: Optional request body (will be JSON encoded)
            params: Optional query parameters
            timeout: Optional request timeout (overrides default)
        
        Returns:
            APIResponse with success status, data, and metadata
        
        Example:
            response = await client.call_api(
                'https://api.example.com/users',
                method='POST',
                data={'name': 'Agent Smith', 'role': 'bridge-master'}
            )
        """
        # Check circuit breaker
        if self.enable_circuit_breaker:
            circuit_breaker = self._get_circuit_breaker(url)
            if not circuit_breaker.can_proceed():
                return APIResponse(
                    success=False,
                    error='circuit_breaker_open',
                    message=f'Circuit breaker is OPEN for {url}'
                )
        
        # Prepare headers
        headers = headers or {}
        headers.setdefault('Content-Type', 'application/json')
        headers.setdefault('User-Agent', 'Chained-Agent/1.0 (bridge-master)')
        headers.setdefault('Accept', 'application/json')
        
        timeout_val = timeout or self.timeout
        start_time = time.time()
        
        # Retry logic with exponential backoff
        last_error = None
        for attempt in range(self.retry_count):
            try:
                async with self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=timeout_val)
                ) as response:
                    duration_ms = (time.time() - start_time) * 1000
                    
                    # Try to parse JSON response
                    try:
                        response_data = await response.json()
                    except:
                        response_data = await response.text()
                    
                    # Create response object
                    api_response = APIResponse(
                        success=response.status < 400,
                        status_code=response.status,
                        data=response_data,
                        headers=dict(response.headers),
                        duration_ms=duration_ms
                    )
                    
                    # Record in monitoring
                    if self.monitor:
                        self.monitor.record_request(
                            endpoint=url,
                            method=method,
                            duration_ms=duration_ms,
                            status_code=response.status,
                            error=None if api_response.success else 'http_error'
                        )
                    
                    # Update circuit breaker
                    if self.enable_circuit_breaker:
                        if api_response.success:
                            circuit_breaker.record_success()
                        else:
                            circuit_breaker.record_failure()
                    
                    return api_response
            
            except asyncio.TimeoutError as e:
                last_error = e
                duration_ms = (time.time() - start_time) * 1000
                
                if attempt == self.retry_count - 1:
                    # Final attempt failed
                    if self.monitor:
                        self.monitor.record_request(
                            endpoint=url,
                            method=method,
                            duration_ms=duration_ms,
                            status_code=0,
                            error='timeout'
                        )
                    
                    if self.enable_circuit_breaker:
                        circuit_breaker.record_failure()
                    
                    return APIResponse(
                        success=False,
                        error='timeout',
                        message=f'Request timed out after {timeout_val}s',
                        duration_ms=duration_ms
                    )
                
                # Wait before retry (exponential backoff)
                await asyncio.sleep(self.retry_delay * (2 ** attempt))
            
            except Exception as e:
                last_error = e
                duration_ms = (time.time() - start_time) * 1000
                
                if attempt == self.retry_count - 1:
                    # Final attempt failed
                    if self.monitor:
                        self.monitor.record_request(
                            endpoint=url,
                            method=method,
                            duration_ms=duration_ms,
                            status_code=0,
                            error=str(e)
                        )
                    
                    if self.enable_circuit_breaker:
                        circuit_breaker.record_failure()
                    
                    return APIResponse(
                        success=False,
                        error='exception',
                        message=str(e),
                        duration_ms=duration_ms
                    )
                
                # Wait before retry
                await asyncio.sleep(self.retry_delay * (2 ** attempt))
        
        # Should never reach here, but just in case
        return APIResponse(
            success=False,
            error='unknown',
            message='Unexpected failure after all retries'
        )
    
    async def call_graphql(
        self,
        url: str,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None
    ) -> APIResponse:
        """
        GraphQL query support
        
        Args:
            url: GraphQL endpoint URL
            query: GraphQL query or mutation
            variables: Optional query variables
            operation_name: Optional operation name
        
        Returns:
            APIResponse with query results
        
        Example:
            response = await client.call_graphql(
                'https://api.example.com/graphql',
                query='query GetUser($id: ID!) { user(id: $id) { name email } }',
                variables={'id': '123'}
            )
        """
        payload = {
            'query': query,
            'variables': variables or {}
        }
        
        if operation_name:
            payload['operationName'] = operation_name
        
        return await self.call_api(
            url=url,
            method='POST',
            data=payload
        )
    
    async def webhook_trigger(
        self,
        url: str,
        event: str,
        payload: Dict[str, Any],
        secret: Optional[str] = None
    ) -> APIResponse:
        """
        Trigger a webhook
        
        Args:
            url: Webhook URL
            event: Event type
            payload: Event payload
            secret: Optional webhook secret for signing
        
        Returns:
            APIResponse
        
        Example:
            response = await client.webhook_trigger(
                'https://hooks.example.com/webhook',
                event='agent.completed',
                payload={'agent': 'bridge-master', 'status': 'success'}
            )
        """
        headers = {
            'X-Event-Type': event,
            'X-Webhook-ID': f'{int(time.time())}'
        }
        
        if secret:
            # Add signature for webhook verification
            import hmac
            import hashlib
            
            signature = hmac.new(
                secret.encode(),
                json.dumps(payload).encode(),
                hashlib.sha256
            ).hexdigest()
            
            headers['X-Webhook-Signature'] = signature
        
        return await self.call_api(
            url=url,
            method='POST',
            headers=headers,
            data=payload
        )
    
    async def batch_requests(
        self,
        requests: List[APIRequest]
    ) -> List[APIResponse]:
        """
        Execute multiple API requests in parallel
        
        Args:
            requests: List of APIRequest objects
        
        Returns:
            List of APIResponse objects
        
        Example:
            requests = [
                APIRequest('https://api1.example.com/data', method='GET'),
                APIRequest('https://api2.example.com/data', method='GET'),
            ]
            responses = await client.batch_requests(requests)
        """
        tasks = []
        
        for req in requests:
            if req.protocol == Protocol.REST:
                task = self.call_api(
                    url=req.url,
                    method=req.method,
                    headers=req.headers,
                    data=req.data,
                    params=req.params,
                    timeout=req.timeout
                )
            elif req.protocol == Protocol.GRAPHQL:
                task = self.call_graphql(
                    url=req.url,
                    query=req.data.get('query', ''),
                    variables=req.data.get('variables')
                )
            else:
                # Unsupported protocol, return error
                task = asyncio.coroutine(lambda: APIResponse(
                    success=False,
                    error='unsupported_protocol',
                    message=f'Protocol {req.protocol} not supported'
                ))()
            
            tasks.append(task)
        
        return await asyncio.gather(*tasks)
    
    def circuit_breaker_status(self, url: str) -> Dict[str, Any]:
        """Get circuit breaker status for a URL"""
        circuit_breaker = self._get_circuit_breaker(url)
        
        return {
            'state': circuit_breaker.state,
            'failure_count': circuit_breaker.failure_count,
            'last_failure_time': circuit_breaker.last_failure_time,
            'can_proceed': circuit_breaker.can_proceed()
        }


# Decorator for monitoring function calls
def monitor_function(client: UniversalAPIClient, endpoint: str, method: str):
    """
    Decorator to monitor API function calls
    
    Usage:
        @monitor_function(client, '/api/users', 'GET')
        async def get_users():
            async with client:
                return await client.call_api('https://api.example.com/users')
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start = time.time()
            error = None
            status_code = 200
            
            try:
                result = await func(*args, **kwargs)
                if hasattr(result, 'status_code'):
                    status_code = result.status_code
                if hasattr(result, 'success') and not result.success:
                    error = result.error
                return result
            except Exception as e:
                error = str(e)
                status_code = 500
                raise
            finally:
                duration = (time.time() - start) * 1000
                if client.monitor:
                    client.monitor.record_request(
                        endpoint, method, duration, status_code, error
                    )
        
        return wrapper
    return decorator


# Example usage
async def example_agent_communication():
    """
    Example: Agent-to-Agent communication via Universal API Client
    
    Demonstrates @bridge-master's vision of seamless agent bridges
    """
    # Create monitor (optional)
    from api_monitoring_bridge import APIMonitoringBridge
    monitor = APIMonitoringBridge()
    
    async with UniversalAPIClient(monitor=monitor) as client:
        print("🌉 Bridge Master connecting agents...\n")
        
        # 1. Agent A queries Agent B's status
        print("1️⃣ Checking Agent B status...")
        response = await client.call_api(
            url='http://agent-b.chained.local/status',
            method='GET'
        )
        
        if response.success:
            print(f"   ✅ Agent B is active: {response.data}")
        else:
            print(f"   ❌ Failed to reach Agent B: {response.error}")
        
        # 2. Agent A sends work to Agent B
        print("\n2️⃣ Assigning task to Agent B...")
        response = await client.call_api(
            url='http://agent-b.chained.local/tasks',
            method='POST',
            data={
                'task_type': 'analyze_api_trends',
                'repository': 'chained/main',
                'requester': 'agent-a',
                'priority': 'high'
            }
        )
        
        if response.success:
            task_id = response.data.get('task_id')
            print(f"   ✅ Task assigned: {task_id}")
        else:
            print(f"   ❌ Task assignment failed: {response.error}")
        
        # 3. GraphQL query for complex data
        print("\n3️⃣ Querying agent network via GraphQL...")
        response = await client.call_graphql(
            url='http://coordinator.chained.local/graphql',
            query='''
                query GetAgentNetwork {
                    agents(status: "active") {
                        id
                        name
                        specialization
                        currentTasks {
                            id
                            type
                            progress
                        }
                    }
                }
            '''
        )
        
        if response.success:
            agents = response.data.get('data', {}).get('agents', [])
            print(f"   ✅ Found {len(agents)} active agents")
        else:
            print(f"   ❌ GraphQL query failed: {response.error}")
        
        # 4. Batch requests for efficiency
        print("\n4️⃣ Batch querying multiple agents...")
        batch_requests = [
            APIRequest('http://agent-c.chained.local/metrics', method='GET'),
            APIRequest('http://agent-d.chained.local/metrics', method='GET'),
            APIRequest('http://agent-e.chained.local/metrics', method='GET'),
        ]
        
        responses = await client.batch_requests(batch_requests)
        successful = sum(1 for r in responses if r.success)
        print(f"   ✅ {successful}/{len(responses)} agents responded")
        
        # 5. Trigger webhook notification
        print("\n5️⃣ Triggering completion webhook...")
        response = await client.webhook_trigger(
            url='https://hooks.chained.local/mission-complete',
            event='mission.completed',
            payload={
                'mission_id': 'idea:30',
                'agent': 'bridge-master',
                'status': 'success',
                'timestamp': time.time()
            }
        )
        
        if response.success:
            print(f"   ✅ Webhook triggered successfully")
        else:
            print(f"   ❌ Webhook failed: {response.error}")
        
        # Print monitoring report
        print("\n" + "="*60)
        print(monitor.generate_report())
        print("="*60)
        
        print("\n🌉 Bridge Master: All systems connected! ")


if __name__ == '__main__':
    # Run example
    asyncio.run(example_agent_communication())
