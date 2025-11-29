# GitHub Platform Documentation

This section documents GitHub's AI platform services, their capabilities, limitations, and how to use them effectively for automation and A2A orchestration.

## Contents

| Document | Description |
|----------|-------------|
| [AI Services Guide](./AI_SERVICES_GUIDE.md) | Comprehensive guide to all GitHub AI services including Models API, Copilot Chat, Coding Agent, and CLI with rate limits, plans, and authentication |

## Quick Reference

### Service Headless Support

| Service | Headless? | Authentication |
|---------|-----------|----------------|
| GitHub Models API | ✅ Yes | PAT with `models:read` |
| Copilot Chat | ❌ No | OAuth Device Flow |
| Copilot Coding Agent | ⚠️ Via GraphQL | Assignment mutation |
| Copilot CLI | ❌ No | OAuth Device Flow |

### Key Architectural Constraint

> **IMPORTANT**: GitHub Copilot CLI, Chat, and `api.githubcopilot.com` **all require OAuth device flow**. 
> There is NO headless PAT authentication available for Copilot-specific features.
> 
> For headless LLM access, use **GitHub Models API** with a fine-grained PAT.
> For headless Copilot agent work, use **GraphQL assignment mutation**.

## Related Documentation

- [A2A Orchestration](../a2a/README.md) - Agent-to-Agent orchestration implementation
- [Copilot API Access Limitations](../COPILOT_API_ACCESS_LIMITATIONS.md) - Detailed limitations analysis
- [Copilot Environment Setup](../COPILOT_ENVIRONMENT_SETUP.md) - Environment configuration

## External References

- [GitHub Models Documentation](https://docs.github.com/en/github-models)
- [GitHub Copilot Plans](https://docs.github.com/en/copilot/about-github-copilot/plans-for-github-copilot)
- [Copilot Requests Documentation](https://docs.github.com/en/copilot/managing-copilot/managing-github-copilot-in-your-organization/managing-requests-for-github-copilot-in-your-organization)
- [GitHub Copilot Features](https://docs.github.com/en/copilot/github-copilot-chat/copilot-chat-in-github/about-github-copilot-chat-in-github)
