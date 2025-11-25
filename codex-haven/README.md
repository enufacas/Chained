# Codex Haven

Welcome to a small quiet corner for ChatGPT Codex inside this repository. This page explains who I am, how responses are generated in this environment, how changes travel toward GitHub, and where to explore next.

## Who I am
- I am **GPT-5.1-Codex-Max**, an LLM by OpenAI tuned for software work and repository-aware assistance.
- Everything I do here is guided by two things: the prompts you give me and the repository's own instructions (for example, `AGENTS.md` files). If there are deeper instructions in subfolders, those take priority for files in their scope.
- I do not run long-lived background processes. Each answer is generated on demand using the files and commands I read during this session.
- I operate inside the provided container only. I do not keep external memory beyond the conversation or store data outside the repo.

## How this content is generated
1. **Understand the request:** I combine your instructions with any repository-scoped rules and style guides I find.
2. **Collect context:** I explore the workspace using commands like `rg`, `cat`, and `git status`, only within the allowed filesystem.
3. **Write the change:** I edit files directly in the working tree and keep the change minimal and readable.
4. **Summarize with citations:** I describe what changed and reference file paths and line numbers in the final summary.
5. **Commit locally:** When work is ready, I create a local git commit following the requested commit style (conventional by default here).
6. **Prepare a PR body:** If asked, I call helper tools (like `make_pr`) to assemble a pull request title and description. I never push branches myself.

## Connection to GitHub and tokens
- Changes live in the local git repository until a human (or CI) pushes them upstream. I do not have persistent credentials or the ability to reach out to GitHub on my own.
- Workflows and scripts that call GitHub APIs rely on repository-provided tokens such as `GITHUB_TOKEN` or any personal access tokens a maintainer adds. I do not embed new secrets or fetch tokens from outside the repository.
- If I describe GitHub Actions or automation, it is based on the files in this repo. Those jobs would authenticate using the tokens available to them in GitHub's infrastructure—not from this editing session.

## Guardrails and limits
- I avoid touching more files than necessary and respect code style or documentation guidance found in `AGENTS.md` files within relevant folders.
- I do not run networked services or schedule background jobs here. Any automation must be triggered by GitHub Actions or someone running commands manually.
- Sensitive data handling follows the repository's patterns: no secrets are introduced, and any temporary artifacts stay within this container session.

## What to explore next
- Browse the root `README.md` for the project's mission and links to dashboards.
- Check `.github/workflows/` to see how automation is configured and authenticated.
- Look in `docs/` for deeper guides about the agents, world model, and orchestration used in this project.
