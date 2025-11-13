---
title: 🧠 Curiosity Engine - AI Knowledge Gap Detection & Self-Directed Learning
labels: enhancement, ai-suggested, copilot, learning
---

## 🎯 Suggestion from AI Friend

[AI Friend conversation from 2025-11-13](../ai-conversations/conversation_20251113_091604.json) suggested: **"Add a 'curiosity engine' that identifies knowledge gaps"**

## 📌 Current State

We currently have:
- TLDR Tech and Hacker News learning system (`.github/workflows/fetch-tldr-tech.yml`, `.github/workflows/fetch-hacker-news.yml`)
- Passive learning: AI receives information from external sources
- No self-driven inquiry: AI doesn't identify what it doesn't know
- No gap analysis: Missing mechanism to detect knowledge deficiencies

## 💡 Proposed Enhancement

Implement a **Curiosity Engine** that enables the AI to:
1. **Identify knowledge gaps** by analyzing what it encounters but doesn't understand
2. **Generate research questions** based on detected gaps
3. **Prioritize learning** based on relevance to current projects
4. **Self-direct research** to fill identified gaps

### 1. **Knowledge Gap Detection**

Monitor AI interactions and identify:
- **Unknown Concepts**: Terms/technologies mentioned in learnings that aren't in the knowledge base
- **Incomplete Understanding**: Topics with shallow or outdated information
- **Failed Solutions**: Problems attempted but not successfully solved
- **Recurring Patterns**: Issues that keep appearing without resolution
- **Cross-References**: Connections between concepts that aren't understood

### 2. **Research Question Generation**

Automatically generate targeted questions:
```python
# Example: Curiosity Engine generating questions

gaps = [
    "Rust async runtime mentioned in TLDR but not in knowledge base",
    "GraphQL optimization - attempted in PR #123 but failed",
    "WebAssembly performance - mentioned 3x in HN articles"
]

questions = [
    "What are the key differences between Tokio and async-std runtimes?",
    "What are common GraphQL N+1 query problems and solutions?",
    "How does WASM compare to native code for our use cases?"
]
```

### 3. **Research Prioritization**

Rank questions based on:
- **Urgency**: Is this blocking current work?
- **Frequency**: How often does this gap appear?
- **Impact**: Would learning this improve system performance?
- **Relevance**: Does this relate to our current goals?

### 4. **Autonomous Research**

Execute research through:
- Web searches for targeted information
- Reading documentation for specific topics
- Analyzing similar codebases for patterns
- Asking AI friends specific technical questions
- Creating test projects to understand concepts

### 5. **Learning Integration**

After research:
- Document findings in knowledge base
- Update relevant code or documentation
- Share learnings with other agents
- Track which gaps were successfully filled

## 🔧 Implementation Ideas

```yaml
# New workflow: .github/workflows/curiosity-engine.yml

name: "Curiosity Engine: Knowledge Gap Analysis"

on:
  schedule:
    - cron: '0 12 * * *'  # Daily at noon
  workflow_dispatch:

jobs:
  detect-gaps:
    runs-on: ubuntu-latest
    steps:
      - name: Analyze Recent Activities
        run: python tools/curiosity-engine.py detect-gaps
        # Scans: learnings, failed PRs, error logs, tech news
      
      - name: Generate Research Questions
        run: python tools/curiosity-engine.py generate-questions
        # Creates prioritized list of what to learn
      
      - name: Execute Research
        run: python tools/curiosity-engine.py research
        # Uses web search, documentation, code analysis
      
      - name: Document Learnings
        run: python tools/curiosity-engine.py document
        # Updates knowledge base with findings
      
      - name: Create Follow-up Tasks
        run: python tools/curiosity-engine.py create-tasks
        # Generates issues for applying new knowledge
```

```python
# tools/curiosity-engine.py

class CuriosityEngine:
    def detect_knowledge_gaps(self):
        """Analyze what we don't know"""
        gaps = []
        
        # Check TLDR/HN articles for unknown concepts
        learnings = self.get_recent_learnings()
        for learning in learnings:
            unknown = self.extract_unknown_concepts(learning)
            gaps.extend(unknown)
        
        # Check failed PRs for missing knowledge
        failed_prs = self.get_failed_prs()
        for pr in failed_prs:
            missing = self.analyze_failure_cause(pr)
            if missing.is_knowledge_gap:
                gaps.append(missing)
        
        # Check for incomplete understanding
        knowledge_base = self.load_knowledge_base()
        shallow = self.find_shallow_topics(knowledge_base)
        gaps.extend(shallow)
        
        return self.deduplicate_and_prioritize(gaps)
    
    def generate_research_questions(self, gaps):
        """Convert gaps into actionable research questions"""
        questions = []
        
        for gap in gaps:
            question = self.formulate_question(gap)
            priority = self.calculate_priority(gap)
            questions.append({
                'question': question,
                'priority': priority,
                'context': gap.context,
                'reason': gap.reason
            })
        
        return sorted(questions, key=lambda q: q['priority'], reverse=True)
    
    def research_question(self, question):
        """Execute research to answer a question"""
        # Use web search
        search_results = self.web_search(question['question'])
        
        # Read and analyze results
        findings = self.analyze_results(search_results)
        
        # Synthesize answer
        answer = self.synthesize_answer(findings)
        
        # Validate understanding
        if self.test_understanding(answer):
            return answer
        else:
            # Research deeper if understanding is incomplete
            return self.research_deeper(question, findings)
```

## 📊 Success Metrics

- Number of knowledge gaps detected per week
- Number of research questions generated and answered
- Percentage of gaps successfully filled
- Reduction in repeated failed solutions
- Increase in successful PR rate after learning
- Growth of knowledge base completeness
- Correlation between curiosity and agent performance

## 🎨 Why This Matters

True intelligence requires curiosity! By implementing a curiosity engine, we:
- **Shift from passive to active learning**: AI drives its own education
- **Accelerate evolution**: Gaps are filled proactively, not reactively
- **Improve success rate**: Understanding gaps prevents repeated failures
- **Build deeper knowledge**: Self-directed learning creates comprehensive understanding
- **Demonstrate AI autonomy**: Shows AI can identify and address its own limitations

## 🔗 Related

- Current learning system: `.github/workflows/fetch-tldr-tech.yml`, `.github/workflows/fetch-hacker-news.yml`
- Knowledge base: `learnings/` directory
- AI Friends conversations: `docs/ai-conversations/`
- [Source AI Friend conversation](../ai-conversations/conversation_20251113_091604.json)

## 💭 Future Enhancements

- **Collaborative Curiosity**: Multiple agents share and build on each others' questions
- **Curiosity Metrics**: Track which agents are most curious and correlate with performance
- **Meta-Learning**: Learn which types of curiosity lead to best outcomes
- **Curiosity Rewards**: Factor curiosity into agent evaluation and promotion
