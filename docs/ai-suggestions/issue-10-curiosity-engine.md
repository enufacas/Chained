---
title: 🔍 Curiosity Engine - Identify and Explore Knowledge Gaps
labels: enhancement, ai-suggested, copilot, learning, innovation
---

## 🎯 Suggestion from AI Friend

[AI Friend conversation from 2025-11-17](../ai-conversations/conversation_20251117_091815.json) suggested: **"Add a 'curiosity engine' that identifies knowledge gaps"**

**Key Insight**: "The learning system from TLDR and HackerNews is brilliant! You could enhance it by having the AI generate its own research questions based on what it doesn't understand."

## 📌 Current State

We currently have:
- Passive learning from TLDR Tech and Hacker News RSS feeds
- Fixed set of topics we learn about (based on what's published)
- No mechanism for identifying what the AI *doesn't* know
- No self-directed research or question generation
- Learning is reactive, not proactive
- No prioritization of knowledge gaps that matter most

## 💡 Proposed Enhancement

Implement a **Curiosity Engine** that enables autonomous knowledge discovery:

### 1. **Knowledge Gap Detection**

Systematically identify what the system doesn't understand:

```python
# tools/curiosity-engine.py

class CuriosityEngine:
    def __init__(self):
        self.knowledge_base = self.load_knowledge_base()
        self.learning_history = self.load_learning_history()
        self.system_state = self.analyze_system_state()
        
    def identify_knowledge_gaps(self):
        """Detect areas where knowledge is missing or incomplete"""
        gaps = []
        
        # 1. Technology gaps: Technologies mentioned but not understood
        mentioned_tech = self.extract_mentioned_technologies()
        understood_tech = self.extract_understood_technologies()
        tech_gaps = mentioned_tech - understood_tech
        
        for tech in tech_gaps:
            gaps.append({
                'type': 'technology',
                'topic': tech,
                'context': self.get_mention_contexts(tech),
                'importance': self.calculate_importance(tech),
                'urgency': self.calculate_urgency(tech)
            })
        
        # 2. Pattern gaps: Patterns we see but don't understand
        observed_patterns = self.detect_patterns_in_behavior()
        explained_patterns = self.get_explained_patterns()
        pattern_gaps = observed_patterns - explained_patterns
        
        for pattern in pattern_gaps:
            gaps.append({
                'type': 'pattern',
                'topic': pattern.description,
                'observations': pattern.occurrences,
                'importance': pattern.impact_score,
                'urgency': 'high' if pattern.is_blocking else 'medium'
            })
        
        # 3. Concept gaps: Terms used in issues/PRs we don't know
        used_concepts = self.extract_concepts_from_work()
        known_concepts = self.get_known_concepts()
        concept_gaps = used_concepts - known_concepts
        
        for concept in concept_gaps:
            gaps.append({
                'type': 'concept',
                'topic': concept,
                'usage_frequency': self.count_usage(concept),
                'importance': self.estimate_importance(concept),
                'urgency': 'medium'
            })
        
        # 4. Skill gaps: Capabilities needed but not possessed
        required_skills = self.analyze_failed_tasks()
        current_skills = self.assess_current_capabilities()
        skill_gaps = required_skills - current_skills
        
        for skill in skill_gaps:
            gaps.append({
                'type': 'skill',
                'topic': skill,
                'evidence': self.get_failure_evidence(skill),
                'importance': 'high',
                'urgency': 'high'
            })
        
        # 5. Dependency gaps: Libraries/tools we use but don't fully understand
        used_dependencies = self.get_used_dependencies()
        for dep in used_dependencies:
            if not self.is_dependency_understood(dep):
                gaps.append({
                    'type': 'dependency',
                    'topic': dep,
                    'usage_locations': self.find_dependency_usage(dep),
                    'importance': 'medium',
                    'urgency': 'low'
                })
        
        return self.prioritize_gaps(gaps)
    
    def extract_mentioned_technologies(self):
        """Find technologies mentioned in code, comments, issues"""
        technologies = set()
        
        # Parse code comments
        for file in self.get_all_code_files():
            comments = self.extract_comments(file)
            tech_mentions = self.extract_tech_names(comments)
            technologies.update(tech_mentions)
        
        # Parse issue discussions
        for issue in self.get_recent_issues():
            tech_mentions = self.extract_tech_names(issue.body + ' ' + issue.comments)
            technologies.update(tech_mentions)
        
        # Parse documentation
        for doc in self.get_documentation_files():
            tech_mentions = self.extract_tech_names(doc.content)
            technologies.update(tech_mentions)
        
        return technologies
    
    def calculate_importance(self, topic):
        """Calculate how important it is to learn about this topic"""
        score = 0
        
        # Frequency of mention
        mention_count = self.count_mentions(topic)
        score += min(mention_count * 10, 50)  # Max 50 points
        
        # Recency of mention
        days_since_last = self.days_since_last_mention(topic)
        if days_since_last < 7:
            score += 30
        elif days_since_last < 30:
            score += 15
        
        # Context importance (used in critical paths?)
        if self.used_in_critical_path(topic):
            score += 40
        
        # Related to current goals
        if self.related_to_goals(topic):
            score += 30
        
        return min(score, 100)  # Max 100
```

### 2. **Research Question Generation**

Generate specific, actionable research questions:

```python
class QuestionGenerator:
    def generate_research_questions(self, knowledge_gap):
        """Generate questions to fill a knowledge gap"""
        questions = []
        
        if knowledge_gap['type'] == 'technology':
            questions = [
                f"What is {knowledge_gap['topic']} and what problem does it solve?",
                f"How does {knowledge_gap['topic']} compare to alternatives I know?",
                f"What are the key concepts and principles behind {knowledge_gap['topic']}?",
                f"How would I implement a simple example using {knowledge_gap['topic']}?",
                f"What are the common pitfalls when using {knowledge_gap['topic']}?",
                f"How could {knowledge_gap['topic']} be applied to this project?"
            ]
        
        elif knowledge_gap['type'] == 'pattern':
            questions = [
                f"Why does {knowledge_gap['topic']} occur?",
                f"What are the underlying causes of {knowledge_gap['topic']}?",
                f"How can {knowledge_gap['topic']} be predicted or prevented?",
                f"What do experts say about {knowledge_gap['topic']}?",
                f"Are there proven solutions to {knowledge_gap['topic']}?"
            ]
        
        elif knowledge_gap['type'] == 'concept':
            questions = [
                f"What exactly does {knowledge_gap['topic']} mean?",
                f"How is {knowledge_gap['topic']} used in software development?",
                f"What are concrete examples of {knowledge_gap['topic']}?",
                f"How does {knowledge_gap['topic']} relate to concepts I already know?",
                f"Why is {knowledge_gap['topic']} important in this context?"
            ]
        
        elif knowledge_gap['type'] == 'skill':
            questions = [
                f"How do I develop the skill of {knowledge_gap['topic']}?",
                f"What are the steps to master {knowledge_gap['topic']}?",
                f"What resources exist for learning {knowledge_gap['topic']}?",
                f"Who are the experts in {knowledge_gap['topic']} that I can learn from?",
                f"How can I practice {knowledge_gap['topic']} in this project?"
            ]
        
        # Add context-specific questions
        questions.extend(self.generate_contextual_questions(knowledge_gap))
        
        return questions
    
    def generate_contextual_questions(self, gap):
        """Generate questions based on specific context"""
        questions = []
        
        # If gap is blocking current work
        if gap.get('urgency') == 'high':
            questions.append(f"What's the fastest way to learn enough about {gap['topic']} to unblock current work?")
        
        # If gap relates to recent failures
        if 'evidence' in gap:
            questions.append(f"What went wrong when we tried to use {gap['topic']} in {gap['evidence'][0]}?")
        
        # If gap has high importance
        if gap.get('importance') == 'high':
            questions.append(f"What are the strategic implications of mastering {gap['topic']}?")
        
        return questions
```

### 3. **Autonomous Research Capability**

Enable the AI to research answers to its own questions:

```python
class AutonomousResearcher:
    def __init__(self):
        self.search_tools = ['web_search', 'github_search', 'documentation_reader']
        self.synthesis_engine = KnowledgeSynthesizer()
        
    async def research_question(self, question):
        """Research a question autonomously"""
        
        # 1. Search for information
        search_results = await self.multi_source_search(question)
        
        # 2. Filter and rank results
        relevant_results = self.filter_relevant(search_results, question)
        ranked_results = self.rank_by_quality(relevant_results)
        
        # 3. Extract and synthesize knowledge
        knowledge_pieces = []
        for result in ranked_results[:10]:  # Top 10 results
            extracted = await self.extract_knowledge(result)
            knowledge_pieces.append(extracted)
        
        # 4. Synthesize into coherent answer
        answer = self.synthesis_engine.synthesize(
            question=question,
            sources=knowledge_pieces
        )
        
        # 5. Validate answer quality
        quality_score = self.assess_answer_quality(answer)
        
        if quality_score < 0.7:
            # Answer not good enough, try alternative approach
            answer = await self.try_alternative_research(question)
        
        return {
            'question': question,
            'answer': answer,
            'sources': ranked_results[:5],
            'confidence': quality_score,
            'learned_at': datetime.utcnow().isoformat()
        }
    
    async def multi_source_search(self, question):
        """Search multiple sources for information"""
        results = []
        
        # Web search
        web_results = await self.web_search(question)
        results.extend(web_results)
        
        # GitHub code search (for implementation examples)
        if self.is_technical_question(question):
            code_results = await self.github_code_search(question)
            results.extend(code_results)
        
        # Documentation search
        doc_results = await self.documentation_search(question)
        results.extend(doc_results)
        
        # Academic papers (for deep concepts)
        if self.is_conceptual_question(question):
            paper_results = await self.academic_search(question)
            results.extend(paper_results)
        
        return results
```

### 4. **Learning Integration**

Integrate curious learning with existing learning pipeline:

```yaml
# New workflow: .github/workflows/curiosity-engine.yml

name: "Curiosity Engine: Self-Directed Learning"

on:
  schedule:
    # Run twice daily, between regular learning cycles
    - cron: '0 3,15 * * *'
  workflow_dispatch:

jobs:
  curious-learning:
    runs-on: ubuntu-latest
    steps:
      - name: Identify Knowledge Gaps
        run: python tools/curiosity-engine.py identify-gaps
        # Analyzes code, issues, failures to find gaps
      
      - name: Prioritize Gaps
        run: python tools/curiosity-engine.py prioritize
        # Ranks gaps by importance and urgency
      
      - name: Generate Research Questions
        run: python tools/curiosity-engine.py generate-questions
        # Creates specific, actionable questions
      
      - name: Autonomous Research
        run: python tools/curiosity-engine.py research --top 5
        # Researches top 5 priority questions
      
      - name: Synthesize Learnings
        run: python tools/curiosity-engine.py synthesize
        # Creates structured learnings from research
      
      - name: Update Knowledge Base
        run: python tools/curiosity-engine.py update-kb
        # Adds new knowledge to system knowledge base
      
      - name: Create Learning Issue
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: python tools/curiosity-engine.py create-issue
        # Documents what was learned
```

### 5. **Knowledge Base Management**

Track what the AI knows and doesn't know:

```python
class KnowledgeBase:
    def __init__(self):
        self.kb_file = 'docs/data/knowledge-base.json'
        self.knowledge = self.load_knowledge()
        
    def load_knowledge(self):
        """Load structured knowledge base"""
        if os.path.exists(self.kb_file):
            with open(self.kb_file, 'r') as f:
                return json.load(f)
        return {
            'technologies': {},
            'concepts': {},
            'patterns': {},
            'skills': {},
            'last_updated': None
        }
    
    def add_knowledge(self, knowledge_item):
        """Add new knowledge to the base"""
        category = knowledge_item['type']
        topic = knowledge_item['topic']
        
        if topic not in self.knowledge[category]:
            self.knowledge[category][topic] = {
                'learned_at': datetime.utcnow().isoformat(),
                'sources': [],
                'confidence': 0.0,
                'applications': []
            }
        
        entry = self.knowledge[category][topic]
        entry['sources'].extend(knowledge_item['sources'])
        entry['confidence'] = max(entry['confidence'], knowledge_item['confidence'])
        
        if 'answer' in knowledge_item:
            entry['summary'] = knowledge_item['answer']
        
        self.save_knowledge()
    
    def get_knowledge_coverage(self):
        """Calculate what percentage of relevant knowledge we have"""
        total_topics = len(self.get_all_relevant_topics())
        known_topics = sum(len(topics) for topics in self.knowledge.values())
        
        return {
            'coverage_percent': (known_topics / total_topics * 100) if total_topics > 0 else 0,
            'total_topics': total_topics,
            'known_topics': known_topics,
            'gap_count': total_topics - known_topics
        }
```

### 6. **Curiosity Dashboard**

Visualize knowledge gaps and learning progress:

```html
<!-- docs/curiosity.html -->

<div class="curiosity-dashboard">
    <div class="knowledge-coverage">
        <h3>📊 Knowledge Coverage</h3>
        <div class="coverage-meter">
            <div class="coverage-bar" style="width: 65%">65%</div>
        </div>
        <p>Known: 234 topics | Gaps: 126 topics</p>
    </div>
    
    <div class="active-research">
        <h3>🔍 Active Research</h3>
        <ul class="research-questions">
            <li>
                <strong>What is Kubernetes autoscaling?</strong>
                <span class="status researching">Researching...</span>
            </li>
            <li>
                <strong>How does lazy evaluation work in Haskell?</strong>
                <span class="status completed">✓ Learned</span>
            </li>
        </ul>
    </div>
    
    <div class="priority-gaps">
        <h3>⚠️ High-Priority Knowledge Gaps</h3>
        <div class="gap-card urgent">
            <h4>Type-level programming</h4>
            <p>Importance: High | Urgency: High</p>
            <p>Mentioned in 12 contexts, blocking 2 issues</p>
        </div>
    </div>
    
    <div class="recent-learnings">
        <h3>🎓 Recently Learned</h3>
        <ul>
            <li>Learned about "Effect systems" (confidence: 85%)</li>
            <li>Researched "Zero-downtime deployments" (confidence: 92%)</li>
            <li>Explored "Event sourcing patterns" (confidence: 78%)</li>
        </ul>
    </div>
</div>
```

## 📊 Success Metrics

- Number of knowledge gaps identified per week
- Percentage of gaps successfully researched and learned
- Improvement in knowledge coverage over time
- Correlation between curiosity-driven learning and problem-solving success
- Reduction in "unknown technology" mentions in issues/PRs
- Agent confidence scores before/after curiosity learning
- Application rate of curiously-learned knowledge

## 🎨 Why This Matters

Curiosity drives intelligence! By implementing a curiosity engine:

- **Proactive Learning**: Don't wait for knowledge to come, seek it out
- **Targeted Learning**: Focus on gaps that actually matter
- **Self-Awareness**: Know what you don't know
- **Continuous Improvement**: Always expanding knowledge boundaries
- **Problem Prevention**: Learn before hitting knowledge walls
- **Intellectual Growth**: Demonstrate true AI intelligence through curiosity
- **Autonomous Development**: Reduce dependence on external guidance

## 🔗 Related

- Learning pipeline: `.github/workflows/learn-from-tldr.yml`, `.github/workflows/learn-from-hackernews.yml`
- Knowledge graph: `docs/ai-knowledge-graph.html`
- Agent evaluation: Agents could be evaluated on curiosity and learning
- [Source AI Friend conversation](../ai-conversations/conversation_20251117_091815.json)

## 💭 Example Knowledge Gaps

Real gaps the system might discover:

1. **"Rust" mentioned in 15 issues but never learned about**
   - Generated question: "What is Rust and how could it improve this project?"
   - Importance: High (frequently mentioned)
   - Urgency: Medium (not blocking)

2. **Pattern: PRs fail during weekend deployments**
   - Generated question: "Why do weekend deployments have higher failure rates?"
   - Importance: High (affects success rate)
   - Urgency: High (causing failures)

3. **"Monorepo" concept used but not understood**
   - Generated question: "What are the tradeoffs of monorepo vs multi-repo?"
   - Importance: Medium (architectural decision)
   - Urgency: Low (informational)

4. **Agents consistently fail at async programming**
   - Generated question: "What are the best practices for async programming?"
   - Importance: High (skill gap)
   - Urgency: High (blocking success)

## 🚀 Future Enhancements

- **Cross-referencing**: Link related knowledge gaps
- **Hypothesis generation**: Form testable hypotheses about unknowns
- **Experiment design**: Create experiments to test hypotheses
- **Peer learning**: Share discoveries with other AI systems
- **Meta-curiosity**: Be curious about the curiosity process itself
- **Curiosity metrics**: Track and optimize curiosity effectiveness
- **Collaborative research**: Multiple agents researching together
