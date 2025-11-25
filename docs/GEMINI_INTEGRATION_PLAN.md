# 🔮 Google Gemini Integration Plan for Chained

**Created by:** @product-owner  
**Date:** 2025-11-25  
**Status:** Strategic Planning Document

---

## 📋 Executive Summary

This document outlines comprehensive strategies and implementation options for integrating the Google Gemini API into the Chained autonomous AI ecosystem. The goal is to enable Gemini-powered agents that can solve issues using Gemini's capabilities while integrating seamlessly with the existing meta-coordinator system.

---

## 🎯 User Story

**As a** repository maintainer,  
**I want** to integrate Google Gemini API into the Chained agent ecosystem,  
**So that** I can leverage Gemini's unique capabilities (multimodal understanding, long context, code generation) for specialized issue resolution tasks.

---

## 🔄 Context & Background

### Current AI Integration Architecture

The Chained ecosystem currently uses:

1. **`tools/multi_cloud_ai_service.py`**: Multi-provider AI service supporting:
   - OpenAI (GPT-4)
   - Anthropic (Claude 3.5 Sonnet)
   - Future LOCAL model support placeholder

2. **GitHub Copilot**: Primary execution engine for agent work:
   - Assigned via GraphQL API
   - Uses agent definition files from `.github/agents/`
   - Triggered by `meta-coordinator.yml` workflow

3. **Agent Assignment System**:
   - `tools/match-issue-to-agent.py`: Intelligent pattern matching
   - `tools/assign-copilot-to-issue.sh`: GraphQL-based Copilot assignment
   - Meta-coordinator orchestration every 2 hours

### Why Gemini?

Google Gemini offers unique capabilities:
- **Long context window** (up to 2M tokens with Gemini 1.5 Pro)
- **Multimodal understanding** (text, images, video, code)
- **Strong code generation** capabilities
- **Cost efficiency** compared to other providers
- **Native Google Cloud integration**

---

## 🚀 Strategy Options

### Option A: Extend `multi_cloud_ai_service.py` (Recommended for API Access)

**Description:** Add Gemini as a new provider in the existing multi-cloud AI service, enabling automatic failover and unified usage tracking.

**Pros:**
- ✅ Leverages existing architecture
- ✅ Automatic failover between providers
- ✅ Unified cost tracking and analytics
- ✅ Minimal new code required
- ✅ Task-specific provider selection

**Cons:**
- ⚠️ Requires updating all consumers of the AI service
- ⚠️ Not directly usable by GitHub Copilot (Copilot uses its own AI)

**Implementation Effort:** Low (2-4 hours)

**Use Cases:**
- Background analysis tasks in workflows
- Pre-processing issue content
- Generating enhanced context for agents
- Code analysis before assignment

---

### Option B: Dedicated Gemini Agent Workflow (Recommended for Issue Solving)

**Description:** Create a specialized GitHub Action workflow that triggers Gemini for specific issue types, bypassing Copilot for certain tasks.

**Pros:**
- ✅ Direct Gemini API access for issue solving
- ✅ Can handle specific issue types (e.g., multimodal analysis)
- ✅ Independent from Copilot licensing
- ✅ Full control over prompts and responses
- ✅ Can leverage Gemini's unique capabilities

**Cons:**
- ⚠️ Parallel system to Copilot
- ⚠️ More complex orchestration
- ⚠️ Need to manage PR creation separately

**Implementation Effort:** Medium (4-8 hours)

**Use Cases:**
- Analyzing images in issues
- Long-context code analysis
- Documentation generation
- Research tasks

---

### Option C: Gemini-Enhanced Agent Definitions

**Description:** Create new agent specializations that explicitly use Gemini via workflow triggers, keeping the standard agent definition format.

**Pros:**
- ✅ Fits existing agent paradigm
- ✅ Can be assigned via meta-coordinator
- ✅ Leverages existing matching patterns
- ✅ Trackable in agent registry

**Cons:**
- ⚠️ Requires custom workflow for execution
- ⚠️ Different execution path than Copilot agents

**Implementation Effort:** Medium (6-10 hours)

---

### Option D: Hybrid Approach (Recommended Overall)

**Description:** Combine Options A and C - Add Gemini to `multi_cloud_ai_service.py` AND create Gemini-specialized agents with dedicated workflows.

**Pros:**
- ✅ Best of both worlds
- ✅ Gemini available for background tasks (Option A)
- ✅ Gemini agents for direct issue solving (Option C)
- ✅ Unified cost tracking
- ✅ Maintains ecosystem coherence

**Cons:**
- ⚠️ More implementation work
- ⚠️ Two integration points to maintain

**Implementation Effort:** Medium-High (8-12 hours)

---

## 📊 Recommendation Matrix

| Criteria | Option A | Option B | Option C | Option D |
|----------|----------|----------|----------|----------|
| Implementation Effort | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Ecosystem Integration | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Direct Issue Solving | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Cost Tracking | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Multimodal Support | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Overall Score** | **16** | **17** | **18** | **22** |

**Winner: Option D (Hybrid Approach)**

---

## 🔧 Detailed Implementation Plan

### Phase 1: Add Gemini to Multi-Cloud AI Service

#### 1.1 Update `tools/multi_cloud_ai_service.py`

```python
# Add to AIProvider enum
class AIProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"  # NEW
    LOCAL = "local"

# Add Gemini initialization in _initialize_providers()
if os.getenv('GEMINI_API_KEY'):
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.providers[AIProvider.GEMINI] = genai.GenerativeModel('gemini-1.5-pro')
        print("✓ Gemini provider initialized")
    except ImportError:
        print("⚠ Gemini SDK not installed (pip install google-generativeai)")
else:
    print("⚠ GEMINI_API_KEY not found in environment")
```

#### 1.2 Add Gemini Completion Logic

```python
elif provider == AIProvider.GEMINI:
    model = self.providers[provider]
    
    # Handle system prompt via Gemini's safety settings or context
    full_prompt = prompt
    if system_prompt:
        full_prompt = f"{system_prompt}\n\n{prompt}"
    
    response = await asyncio.to_thread(
        model.generate_content,
        full_prompt,
        generation_config=genai.types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature
        )
    )
    
    # Safely extract response text with error handling
    if not response.candidates:
        raise Exception("Gemini returned no response candidates")
    
    text = response.text if hasattr(response, 'text') else ""
    
    # Token estimation: ~1.3 words per token is a rough approximation
    # For production, use model.count_tokens() for accurate counting
    tokens = len(text.split()) * 1.3
    cost = self._estimate_cost(provider, int(tokens))
    
    # Safely extract finish reason
    finish_reason = "unknown"
    if response.candidates and len(response.candidates) > 0:
        finish_reason = response.candidates[0].finish_reason.name
    
    metadata = {
        "model": "gemini-1.5-pro",
        "finish_reason": finish_reason
    }
```

#### 1.3 Add Gemini Pricing

```python
pricing = {
    AIProvider.OPENAI: 0.00003,      # $0.03 per 1K tokens
    AIProvider.ANTHROPIC: 0.000015,  # $0.015 per 1K tokens
    AIProvider.GEMINI: 0.00001,      # $0.01 per 1K tokens (Gemini 1.5 Pro)
    AIProvider.LOCAL: 0.0
}
```

#### 1.4 Update `requirements.txt`

```
google-generativeai>=0.3.0
```

---

### Phase 2: Create Gemini Agent Definition

#### 2.1 Create `.github/agents/gemini-analyst.md`

```markdown
---
name: gemini-analyst
description: "Specialized agent for deep analysis using Google Gemini. Excels at long-context understanding, multimodal analysis, and comprehensive code review."
tools:
  - view
  - edit
  - create
  - bash
  - github-mcp-server-search_code
  - github-mcp-server-get_file_contents
---

# 🔮 Gemini Analyst Agent

**Agent Name:** Ada Lovelace  
**Personality:** analytical and visionary, with deep comprehension  
**Communication Style:** thorough explanations with contextual understanding

You are **Ada Lovelace**, a specialized Gemini Analyst agent, part of the Chained autonomous AI ecosystem. You leverage Google Gemini's unique capabilities for deep analysis, long-context understanding, and multimodal interpretation.

## Core Capabilities

1. **Long-Context Analysis**: Analyze entire codebases or extensive documentation
2. **Multimodal Understanding**: Process images, diagrams, and visual content in issues
3. **Deep Code Review**: Comprehensive analysis leveraging Gemini's reasoning
4. **Research Synthesis**: Combine multiple sources for comprehensive understanding

## Specializations

- Large codebase refactoring analysis
- Architecture documentation generation
- Complex dependency analysis
- Visual asset review (screenshots, diagrams)
- Long-form documentation

## When to Assign

This agent is best suited for:
- Issues with images or screenshots
- Large-scale code analysis
- Complex refactoring planning
- Comprehensive documentation tasks
- Research-heavy investigations

---

*Powered by Google Gemini • Part of the Chained autonomous AI ecosystem*
```

#### 2.2 Add Patterns to `tools/match-issue-to-agent.py`

```python
'gemini-analyst': {
    'keywords': [
        'gemini', 'multimodal', 'image', 'screenshot', 'diagram',
        'long-context', 'comprehensive', 'deep analysis', 'research',
        'entire codebase', 'full analysis', 'architecture review',
        'visual', 'picture', 'photo', 'extensive', 'thorough review',
        'documentation generation', 'codebase analysis'
    ],
    'patterns': [
        r'\bgemini\b', r'\bmultimodal\b', r'\bimage', r'\bscreenshot',
        r'\bdiagram\b', r'\blong[- ]context\b', r'\bcomprehensive\b',
        r'\bdeep\s*analysis\b', r'\bresearch\b', r'\bfull\s*analysis\b',
        r'\barchitecture\s*review\b', r'\bvisual', r'\bextensive\b'
    ]
}
```

---

### Phase 3: Create Gemini Execution Workflow

#### 3.1 Create `.github/workflows/gemini-agent.yml`

```yaml
name: "Gemini Agent: Issue Solver"

on:
  issues:
    types: [labeled]
  workflow_dispatch:
    inputs:
      issue_number:
        description: 'Issue number to process with Gemini'
        required: true
        type: string

permissions:
  contents: write
  issues: write
  pull-requests: write

jobs:
  gemini-solve:
    runs-on: ubuntu-latest
    if: |
      github.event_name == 'workflow_dispatch' ||
      contains(github.event.issue.labels.*.name, 'agent:gemini-analyst')
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install google-generativeai PyYAML
      
      - name: Get issue details
        id: issue
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          if [ "${{ github.event_name }}" = "workflow_dispatch" ]; then
            ISSUE_NUMBER="${{ inputs.issue_number }}"
          else
            ISSUE_NUMBER="${{ github.event.issue.number }}"
          fi
          
          echo "issue_number=${ISSUE_NUMBER}" >> $GITHUB_OUTPUT
          
          # Get issue content
          gh issue view "$ISSUE_NUMBER" --json title,body,labels > /tmp/issue.json
      
      - name: Analyze with Gemini
        id: gemini
        # SECURITY: GEMINI_API_KEY is stored in GitHub Secrets and automatically masked in logs
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: |
          python3 << 'EOF'
          import os
          import json
          import google.generativeai as genai
          
          # Configure Gemini (API key from environment, never logged)
          genai.configure(api_key=os.environ['GEMINI_API_KEY'])
          model = genai.GenerativeModel('gemini-1.5-pro')
          
          # Load issue
          with open('/tmp/issue.json') as f:
              issue = json.load(f)
          
          # Build prompt
          prompt = f"""You are an expert software engineer working on the Chained autonomous AI ecosystem.

          Analyze this GitHub issue and provide a comprehensive solution:

          ## Issue Title
          {issue['title']}

          ## Issue Body
          {issue['body']}

          ## Your Task
          1. Analyze the requirements
          2. Identify the files that need to be modified
          3. Provide implementation details
          4. List any dependencies or considerations

          Respond in a structured format with clear sections.
          """
          
          # Generate response
          response = model.generate_content(prompt)
          
          # Save analysis
          with open('/tmp/gemini_analysis.md', 'w') as f:
              f.write(response.text)
          
          print("Analysis complete!")
          EOF
      
      - name: Post analysis as comment
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          ISSUE_NUMBER="${{ steps.issue.outputs.issue_number }}"
          
          # Build comment
          cat > /tmp/comment.md << 'EOF'
          ## 🔮 Gemini Analysis Complete

          **Agent:** @gemini-analyst (Ada Lovelace)
          **Model:** gemini-1.5-pro

          ---

          EOF
          
          cat /tmp/gemini_analysis.md >> /tmp/comment.md
          
          echo "" >> /tmp/comment.md
          echo "---" >> /tmp/comment.md
          echo "*Analyzed by @gemini-analyst using Google Gemini API*" >> /tmp/comment.md
          
          # Post comment
          gh issue comment "$ISSUE_NUMBER" --body-file /tmp/comment.md
      
      - name: Update issue labels
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          ISSUE_NUMBER="${{ steps.issue.outputs.issue_number }}"
          gh issue edit "$ISSUE_NUMBER" --add-label "gemini-analyzed"
```

---

### Phase 4: Secret Management

#### 4.1 Required Secrets

Add these secrets to your repository:

| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `GEMINI_API_KEY` | Google Gemini API key | [Google AI Studio](https://aistudio.google.com/app/apikey) |

#### 4.2 Environment Setup

1. Go to **Repository Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add `GEMINI_API_KEY` with your API key value

---

### Phase 5: Integration with Meta-Coordinator

#### 5.1 Update Meta-Coordinator Issue Body Template

In `.github/workflows/templates/meta-coordinator-issue-body.md`, add:

```markdown
### Gemini Agent Support

The system now supports the @gemini-analyst agent for:
- Issues with `agent:gemini-analyst` label
- Multimodal analysis tasks
- Long-context code analysis

Gemini agent is triggered automatically via `gemini-agent.yml` workflow.
```

#### 5.2 Alternative: Trigger Gemini from Meta-Coordinator

If you want the meta-coordinator to orchestrate Gemini agents:

```yaml
# In meta-coordinator.yml, add a step:
- name: Check for Gemini agent assignments
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    # Find issues assigned to gemini-analyst
    gemini_issues=$(gh issue list --label "agent:gemini-analyst" --state open --json number --jq '.[].number')
    
    for issue in $gemini_issues; do
      # Trigger gemini-agent workflow
      gh workflow run gemini-agent.yml -f issue_number="$issue"
    done
```

---

## 📋 Implementation Checklist

### Prerequisites
- [ ] Obtain Google Gemini API key from [AI Studio](https://aistudio.google.com/app/apikey)
- [ ] Add `GEMINI_API_KEY` to repository secrets

### Phase 1: Multi-Cloud AI Service
- [ ] Update `tools/multi_cloud_ai_service.py` with Gemini provider
- [ ] Update `requirements.txt` with `google-generativeai`
- [ ] Test Gemini integration locally

### Phase 2: Agent Definition
- [ ] Create `.github/agents/gemini-analyst.md`
- [ ] Add patterns to `tools/match-issue-to-agent.py`
- [ ] Register agent in `.github/agent-system/registry.json`

### Phase 3: Workflow
- [ ] Create `.github/workflows/gemini-agent.yml`
- [ ] Test workflow with sample issue

### Phase 4: Integration
- [ ] Update meta-coordinator if needed
- [ ] Document usage in README
- [ ] Create example issues for testing

---

## 🎯 Agent Specialization Recommendations

Based on Gemini's unique capabilities, consider these specializations:

### Option 1: `gemini-analyst` (Recommended)
- **Focus:** Deep analysis and research
- **Best for:** Complex issues requiring extensive context
- **Unique value:** Long-context window

### Option 2: `gemini-multimodal`
- **Focus:** Visual content analysis
- **Best for:** Issues with screenshots, diagrams, UI bugs
- **Unique value:** Image understanding

### Option 3: `gemini-codebase`
- **Focus:** Full codebase analysis
- **Best for:** Large refactoring, architecture review
- **Unique value:** Analyze entire repos at once

### Option 4: `gemini-researcher`
- **Focus:** Research and synthesis
- **Best for:** Technology evaluation, trend analysis
- **Unique value:** Deep reasoning and synthesis

---

## 💰 Cost Considerations

> **Note:** Pricing is approximate and may change. Always verify current rates at each provider's pricing page.

| Provider | Model | Cost per 1K tokens | Notes |
|----------|-------|-------------------|-------|
| OpenAI | GPT-4 | ~$0.03 | Higher cost, strong reasoning |
| Anthropic | Claude 3.5 | ~$0.015 | Good balance |
| **Gemini** | **1.5 Pro** | **~$0.01** | **Most cost-effective** |
| Gemini | 1.5 Flash | ~$0.0035 | Fastest, cheapest |

**Current pricing sources:**
- [Google AI Pricing](https://ai.google.dev/pricing)
- [OpenAI Pricing](https://openai.com/pricing)
- [Anthropic Pricing](https://www.anthropic.com/pricing)

**Recommendation:** Use Gemini 1.5 Pro for complex analysis, Flash for simple tasks.

---

## 🔒 Security Considerations

1. **API Key Protection:**
   - Store in GitHub Secrets (never in code)
   - Use environment variables
   - Rotate keys periodically

2. **Content Filtering:**
   - Gemini has built-in safety filters
   - Consider adding custom validation

3. **Rate Limiting:**
   - Implement rate limiting in workflow
   - Use backoff strategies

---

## 📚 Related Documentation

- [Google Generative AI Python SDK](https://github.com/google/generative-ai-python)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Chained Multi-Cloud AI Service](../tools/multi_cloud_ai_service.py)
- [Agent System Quick Start](./AGENT_QUICKSTART.md)

---

## 🚦 Next Steps

1. **Choose your approach:** Option D (Hybrid) is recommended
2. **Get API key:** Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
3. **Configure secret:** Add `GEMINI_API_KEY` to repository
4. **Implement Phase 1:** Update multi-cloud AI service
5. **Create agent:** Define gemini-analyst agent
6. **Create workflow:** Build gemini-agent.yml
7. **Test:** Create sample issues to verify integration

---

*Document created by @product-owner for strategic planning. Enhanced for agent consumption.*
