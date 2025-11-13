# GitHub Copilot Assignment Setup

This repository uses a workflow to automatically assign GitHub Copilot to issues. To enable this functionality, you need to set up a Personal Access Token (PAT).

## Why is a PAT Required?

The default `GITHUB_TOKEN` provided by GitHub Actions **cannot** assign issues to GitHub Copilot due to licensing and security restrictions. According to the [official GitHub documentation](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-a-pr), you must use a Personal Access Token with appropriate permissions.

## Setup Instructions

### 1. Create a Personal Access Token

1. Go to [GitHub Settings → Personal Access Tokens](https://github.com/settings/tokens)
2. Click "Generate new token" (use classic tokens for now, as fine-grained tokens may have limited Copilot support)
3. Give your token a descriptive name (e.g., "Copilot Assignment Token")
4. Set an appropriate expiration date
5. Select the following scopes:
   - ✅ `repo` (Full control of private repositories)
   
6. Click "Generate token" and **copy the token immediately** (you won't be able to see it again)

### 2. Add Token as Repository Secret

1. Go to your repository's **Settings → Secrets and variables → Actions**
2. Click "New repository secret"
3. Name: `COPILOT_PAT`
4. Value: Paste the token you copied in step 1
5. Click "Add secret"

### 3. Verify Copilot is Enabled

1. Go to your repository's **Settings → Copilot**
2. Ensure GitHub Copilot is enabled for this repository
3. Verify you have an active Copilot subscription (Individual, Business, or Enterprise)

## Testing the Workflow

After setting up the PAT:

1. Create a new issue, or
2. Manually trigger the "Copilot Assignment Workflow" from the Actions tab
3. The workflow should successfully assign Copilot to open issues

## Troubleshooting

### "Could not find Copilot actor ID"

This error occurs when:
- No PAT is configured (the workflow falls back to `GITHUB_TOKEN`)
- The PAT doesn't have sufficient permissions
- Copilot is not enabled for the repository
- Your account doesn't have a Copilot subscription

**Solution:** Follow the setup instructions above to create and add a PAT.

### "Failed to assign issue to Copilot"

This typically means:
- The PAT is configured but Copilot is not enabled in repository settings
- Your Copilot subscription is expired or not active
- The repository doesn't have Copilot access

**Solution:** Verify Copilot settings and subscription status.

## Security Notes

- **Keep your PAT secure** - Never commit it to the repository or share it publicly
- **Use repository secrets** - Always store the PAT as a secret, never hardcode it
- **Set appropriate expiration** - Regularly rotate your PATs for security
- **Minimal scope** - Only grant the `repo` scope needed for this functionality

## More Information

- [GitHub Copilot Coding Agent Documentation](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-a-pr)
- [Managing Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
- [GitHub Copilot Subscription Plans](https://github.com/features/copilot)
