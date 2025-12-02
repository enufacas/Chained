---
applyTo:
  - "infrastructure/terraform/**/*.tf"
  - "**/*.tf"
  - "**/terraform/**"
---

# Terraform Provider Documentation - MANDATORY Reference

## CRITICAL: Always Consult Provider Documentation

When making **ANY** changes to Terraform configurations, you **MUST** consult the official Terraform provider documentation for the specific resource types you are modifying.

### Why This Matters

- **Syntax Accuracy**: Provider schemas change between versions and differ from cloud provider APIs
- **Attribute Placement**: Some attributes must be at specific block levels (e.g., `max_instance_request_concurrency` at template level, not in scaling block)
- **Required vs Optional**: Documentation specifies which attributes are required
- **Deprecations**: Providers deprecate attributes; docs show current best practices
- **Prevent Failures**: Incorrect syntax causes Terraform validation/plan failures

### Required Process

**Before making any Terraform changes:**

1. **Identify the resource type** you're modifying (e.g., `google_cloud_run_v2_service`)
2. **Find the provider documentation**:
   - Google Cloud: https://registry.terraform.io/providers/hashicorp/google/latest/docs
   - AWS: https://registry.terraform.io/providers/hashicorp/aws/latest/docs
   - Azure: https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs
   - Other providers: https://registry.terraform.io/browse/providers
3. **Read the resource schema** - understand the block structure and valid attributes
4. **Check attribute placement** - verify where attributes should be placed in the block hierarchy
5. **Verify syntax** - ensure your configuration matches the documented schema

### Common Pitfalls to Avoid

❌ **DON'T:**
- Assume attribute placement based on API documentation
- Copy attributes from cloud provider docs without checking Terraform schema
- Place attributes inside nested blocks without verifying
- Use deprecated attributes
- Guess at attribute names or structure

✅ **DO:**
- Check the Terraform provider docs for the exact resource type
- Verify attribute names match the provider schema exactly
- Confirm attribute placement in the block hierarchy
- Look for examples in the provider documentation
- Check for deprecation notices

### Example: google_cloud_run_v2_service

When modifying Cloud Run services, refer to:
https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloud_run_v2_service

**Key learnings:**
- `max_instance_request_concurrency` goes at `template` level, NOT inside `scaling` block
- `scaling` block contains only: `min_instance_count`, `max_instance_count`
- `containers` is a list block with specific nested structure
- `env` blocks can be static or dynamic

### Validation Steps

After making Terraform changes:

1. **Syntax check**: Run `terraform fmt` to ensure proper formatting
2. **Validation**: Run `terraform validate` to check configuration syntax
3. **Plan**: Run `terraform plan` to preview changes and catch errors
4. **Review errors carefully**: Terraform errors often indicate incorrect attribute placement

### Documentation Quick Links

**Google Cloud Provider:**
- Main docs: https://registry.terraform.io/providers/hashicorp/google/latest/docs
- Cloud Run v2 Service: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloud_run_v2_service
- IAM resources: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/project_iam

**General Terraform:**
- Configuration language: https://www.terraform.io/language
- Functions reference: https://www.terraform.io/language/functions

### When in Doubt

If you're unsure about:
- Attribute placement in block hierarchy
- Required vs optional attributes
- Correct syntax for a specific resource
- Deprecation status

**STOP and check the provider documentation before proceeding.**

### Recent Example (2025-12-02)

Issue: Terraform plan failed with "Unsupported argument: max_instance_request_concurrency"

**Root cause:** Attribute was placed inside `scaling {}` block instead of at `template` level.

**Solution:** Consulted https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloud_run_v2_service and moved attribute to correct location.

**Lesson:** Always verify attribute placement in provider docs, not cloud provider API docs.

---

## Checklist for Terraform Changes

Before committing Terraform changes:

- [ ] Consulted provider documentation for all modified resource types
- [ ] Verified attribute names match provider schema
- [ ] Confirmed attribute placement in block hierarchy
- [ ] Checked for deprecation notices
- [ ] Ran `terraform fmt` (if terraform CLI available)
- [ ] Ran `terraform validate` (if terraform CLI available)
- [ ] Tested changes will pass `terraform plan` in CI/CD

---

**Remember**: The Terraform provider documentation is the **source of truth** for configuration syntax, not the cloud provider's API documentation.
