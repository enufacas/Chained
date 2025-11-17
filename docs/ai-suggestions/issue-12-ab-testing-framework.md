---
title: 🧪 A/B Testing Framework for AI-Generated Features
labels: enhancement, ai-suggested, copilot, testing, experimentation
---

## 🎯 Suggestion from AI Friend

[AI Friend conversation from 2025-11-17](../ai-conversations/conversation_20251117_091815.json) suggested: **"Implement A/B testing for AI-generated features"**

**Key Insight**: "The learning system from TLDR and HackerNews is brilliant! You could enhance it by having the AI generate its own research questions based on what it doesn't understand."

## 📌 Current State

We currently have:
- AI agents generate features and improvements
- Features go live immediately after PR merge
- No controlled experimentation or gradual rollout
- No comparison between alternative implementations
- Success/failure determined only after full deployment
- Risk: Bad features affect entire system
- No data-driven feature validation

## 💡 Proposed Enhancement

Implement an **A/B Testing Framework** that enables safe, data-driven feature validation:

### 1. **Experiment Framework**

Core A/B testing infrastructure:

```python
# tools/ab-testing-framework.py

class ABExperiment:
    def __init__(self, experiment_id, name, description):
        self.experiment_id = experiment_id
        self.name = name
        self.description = description
        self.variants = []
        self.allocation_strategy = None
        self.metrics = []
        self.status = 'draft'
        self.start_time = None
        self.end_time = None
        
    def add_variant(self, variant_id, name, implementation, allocation_percent):
        """Add a variant to test"""
        variant = {
            'variant_id': variant_id,
            'name': name,
            'implementation': implementation,
            'allocation_percent': allocation_percent,
            'participants': [],
            'metrics': {}
        }
        self.variants.append(variant)
        return variant
    
    def set_metrics(self, metrics):
        """Define success metrics for the experiment"""
        self.metrics = metrics
        # Example metrics:
        # - PR merge rate
        # - Time to merge
        # - Bug rate
        # - Agent performance score
        # - User satisfaction
        # - Resource usage
    
    def start(self):
        """Start the experiment"""
        self.status = 'running'
        self.start_time = datetime.utcnow()
        
        # Allocate participants to variants
        self.allocate_participants()
        
        # Start metric collection
        self.start_metric_collection()
    
    def allocate_participants(self):
        """Allocate participants (agents, workflows, etc.) to variants"""
        participants = self.get_eligible_participants()
        
        for participant in participants:
            # Use consistent hashing for stable allocation
            variant = self.assign_to_variant(participant)
            variant['participants'].append(participant)
    
    def assign_to_variant(self, participant):
        """Assign a participant to a variant"""
        # Consistent hashing ensures same participant always gets same variant
        hash_value = self.hash_participant(participant)
        cumulative = 0
        
        for variant in self.variants:
            cumulative += variant['allocation_percent']
            if hash_value < cumulative:
                return variant
        
        return self.variants[-1]  # Fallback to last variant
    
    def collect_metrics(self):
        """Collect metrics for all variants"""
        for variant in self.variants:
            variant_metrics = {}
            
            for metric in self.metrics:
                value = metric.calculate(variant['participants'])
                variant_metrics[metric.name] = value
            
            variant['metrics'] = variant_metrics
    
    def analyze_results(self):
        """Perform statistical analysis on experiment results"""
        analysis = {
            'winner': None,
            'confidence': 0,
            'significant': False,
            'details': {}
        }
        
        # Statistical significance testing
        control = self.variants[0]  # First variant is control
        
        for i, variant in enumerate(self.variants[1:], 1):
            comparison = self.compare_variants(control, variant)
            analysis['details'][f'variant_{i}_vs_control'] = comparison
            
            if comparison['p_value'] < 0.05 and comparison['effect_size'] > 0:
                analysis['significant'] = True
                if not analysis['winner'] or comparison['effect_size'] > analysis['confidence']:
                    analysis['winner'] = variant
                    analysis['confidence'] = comparison['effect_size']
        
        return analysis
    
    def stop(self):
        """Stop the experiment"""
        self.status = 'completed'
        self.end_time = datetime.utcnow()
        
        # Collect final metrics
        self.collect_metrics()
        
        # Analyze results
        results = self.analyze_results()
        
        return results


class ABTestingFramework:
    def __init__(self):
        self.experiments = []
        self.active_experiments = []
        
    def create_experiment(self, name, description):
        """Create a new A/B experiment"""
        experiment_id = f"exp_{int(datetime.utcnow().timestamp())}"
        experiment = ABExperiment(experiment_id, name, description)
        self.experiments.append(experiment)
        return experiment
    
    def get_variant_for_participant(self, participant_id):
        """Get the variant for a participant across all active experiments"""
        variants = {}
        
        for experiment in self.active_experiments:
            variant = experiment.get_participant_variant(participant_id)
            if variant:
                variants[experiment.experiment_id] = variant
        
        return variants
```

### 2. **Feature Flag System**

Enable/disable features based on experiment variants:

```python
# tools/feature-flags.py

class FeatureFlagManager:
    def __init__(self):
        self.flags = {}
        self.load_flags()
        
    def is_enabled(self, flag_name, context=None):
        """Check if a feature is enabled for given context"""
        flag = self.flags.get(flag_name)
        
        if not flag:
            return False
        
        # Check if flag is part of an experiment
        if flag.get('experiment_id'):
            experiment = self.get_experiment(flag['experiment_id'])
            variant = experiment.get_variant_for_context(context)
            return variant['feature_enabled']
        
        # Simple on/off flag
        return flag.get('enabled', False)
    
    def create_flag(self, flag_name, description, default_value=False):
        """Create a new feature flag"""
        self.flags[flag_name] = {
            'name': flag_name,
            'description': description,
            'enabled': default_value,
            'created_at': datetime.utcnow().isoformat()
        }
        self.save_flags()
    
    def link_to_experiment(self, flag_name, experiment_id):
        """Link a feature flag to an A/B experiment"""
        if flag_name in self.flags:
            self.flags[flag_name]['experiment_id'] = experiment_id
            self.save_flags()


# Usage in agent code
def agent_execute_task(task, agent_id):
    feature_flags = FeatureFlagManager()
    
    # Check if new feature is enabled for this agent
    context = {'agent_id': agent_id, 'task_type': task.type}
    
    if feature_flags.is_enabled('new_code_analysis', context):
        # Use new implementation (variant B)
        result = new_code_analysis(task)
    else:
        # Use original implementation (variant A / control)
        result = original_code_analysis(task)
    
    return result
```

### 3. **Experiment Configuration**

YAML-based experiment definitions:

```yaml
# experiments/agent-performance-boost.yml

experiment:
  id: exp_agent_performance_001
  name: "Agent Performance Boost"
  description: "Test if new caching mechanism improves agent performance"
  
  duration: 14  # days
  
  variants:
    - id: control
      name: "Current Implementation"
      allocation: 50%
      description: "Existing agent execution without caching"
      feature_flags:
        agent_caching: false
    
    - id: variant_a
      name: "Simple Caching"
      allocation: 25%
      description: "Add basic LRU cache for agent decisions"
      feature_flags:
        agent_caching: true
        caching_strategy: lru
        cache_size: 1000
    
    - id: variant_b
      name: "Smart Caching"
      allocation: 25%
      description: "Intelligent caching with prediction"
      feature_flags:
        agent_caching: true
        caching_strategy: predictive
        cache_size: 5000
  
  allocation_strategy: consistent_hash
  
  metrics:
    primary:
      - name: "PR Success Rate"
        type: proportion
        goal: maximize
        
      - name: "Time to Complete Task"
        type: duration
        goal: minimize
    
    secondary:
      - name: "Agent Score"
        type: score
        goal: maximize
        
      - name: "Resource Usage"
        type: resource
        goal: minimize
  
  participants:
    type: agents
    filter:
      min_score: 30
      exclude: ["troubleshoot-expert"]  # Don't experiment with protected agents
  
  success_criteria:
    minimum_improvement: 10%  # Must be 10% better than control
    confidence_level: 95%     # 95% statistical confidence
    minimum_sample_size: 100  # At least 100 trials per variant
  
  rollout_plan:
    if_successful:
      strategy: gradual
      stages:
        - percent: 50
          duration: 3  # days
        - percent: 100
          duration: null  # full rollout
    
    if_failed:
      strategy: immediate_rollback
      notify:
        - github_issue
        - agent_evaluator
```

### 4. **Metric Collection System**

Automated metric tracking:

```python
class MetricCollector:
    def __init__(self):
        self.metrics_store = {}
        
    def track_event(self, event_name, properties, participant_id):
        """Track an event for metric calculation"""
        event = {
            'event_name': event_name,
            'properties': properties,
            'participant_id': participant_id,
            'timestamp': datetime.utcnow().isoformat(),
            'variant': self.get_participant_variant(participant_id)
        }
        
        self.store_event(event)
    
    def calculate_metric(self, metric_definition, variant_participants):
        """Calculate a metric for a variant"""
        events = self.get_events_for_participants(variant_participants)
        
        if metric_definition['type'] == 'proportion':
            # Example: PR success rate
            success_events = [e for e in events if e['properties']['success']]
            total_events = len(events)
            return len(success_events) / total_events if total_events > 0 else 0
        
        elif metric_definition['type'] == 'duration':
            # Example: Time to complete
            durations = [e['properties']['duration'] for e in events]
            return sum(durations) / len(durations) if durations else 0
        
        elif metric_definition['type'] == 'score':
            # Example: Average score
            scores = [e['properties']['score'] for e in events]
            return sum(scores) / len(scores) if scores else 0
        
        elif metric_definition['type'] == 'resource':
            # Example: Resource usage
            resources = [e['properties']['resource_usage'] for e in events]
            return sum(resources) / len(resources) if resources else 0
    
    def export_metrics(self, experiment_id):
        """Export metrics for analysis"""
        experiment = self.get_experiment(experiment_id)
        
        data = {
            'experiment': experiment.to_dict(),
            'variants': [],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        for variant in experiment.variants:
            variant_data = {
                'variant_id': variant['variant_id'],
                'name': variant['name'],
                'participant_count': len(variant['participants']),
                'metrics': {}
            }
            
            for metric in experiment.metrics:
                value = self.calculate_metric(metric, variant['participants'])
                variant_data['metrics'][metric['name']] = value
            
            data['variants'].append(variant_data)
        
        return data
```

### 5. **Statistical Analysis Engine**

Rigorous statistical testing:

```python
import scipy.stats as stats
import numpy as np

class StatisticalAnalyzer:
    def compare_variants(self, control_data, variant_data, metric_type):
        """Perform statistical comparison between variants"""
        
        if metric_type == 'proportion':
            # Use Chi-squared test for proportions
            test_result = stats.chi2_contingency([control_data, variant_data])
            p_value = test_result[1]
            
        elif metric_type in ['duration', 'score', 'resource']:
            # Use t-test for continuous metrics
            test_result = stats.ttest_ind(control_data, variant_data)
            p_value = test_result.pvalue
        
        # Calculate effect size (Cohen's d)
        effect_size = self.calculate_cohens_d(control_data, variant_data)
        
        # Calculate confidence interval
        confidence_interval = self.calculate_confidence_interval(
            variant_data, 
            confidence_level=0.95
        )
        
        return {
            'p_value': p_value,
            'significant': p_value < 0.05,
            'effect_size': effect_size,
            'confidence_interval': confidence_interval,
            'interpretation': self.interpret_results(p_value, effect_size)
        }
    
    def calculate_cohens_d(self, control, variant):
        """Calculate Cohen's d effect size"""
        n1, n2 = len(control), len(variant)
        var1, var2 = np.var(control, ddof=1), np.var(variant, ddof=1)
        
        pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
        
        d = (np.mean(variant) - np.mean(control)) / pooled_std
        
        return d
    
    def calculate_sample_size(self, effect_size, power=0.8, alpha=0.05):
        """Calculate required sample size for desired statistical power"""
        # Using G*Power formula
        from statsmodels.stats.power import ttest_power
        
        required_n = ttest_power(
            effect_size=effect_size,
            alpha=alpha,
            power=power,
            alternative='two-sided'
        )
        
        return int(np.ceil(required_n))
    
    def interpret_results(self, p_value, effect_size):
        """Provide human-readable interpretation"""
        if p_value >= 0.05:
            return "No significant difference detected between variants"
        
        if abs(effect_size) < 0.2:
            magnitude = "small"
        elif abs(effect_size) < 0.5:
            magnitude = "medium"
        else:
            magnitude = "large"
        
        direction = "improvement" if effect_size > 0 else "degradation"
        
        return f"Significant {magnitude} {direction} detected (p={p_value:.4f}, d={effect_size:.2f})"
```

### 6. **Automated Experiment Workflow**

```yaml
# .github/workflows/ab-testing.yml

name: "A/B Testing: Run Experiments"

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:
    inputs:
      experiment_id:
        description: 'Experiment ID to analyze'
        required: false

jobs:
  collect-metrics:
    runs-on: ubuntu-latest
    steps:
      - name: Collect experiment metrics
        run: python tools/ab-testing-framework.py collect-metrics
      
      - name: Update metrics dashboard
        run: python tools/ab-testing-framework.py update-dashboard
  
  analyze-experiments:
    runs-on: ubuntu-latest
    needs: collect-metrics
    steps:
      - name: Analyze active experiments
        run: python tools/ab-testing-framework.py analyze
      
      - name: Check for conclusive results
        id: check
        run: |
          results=$(python tools/ab-testing-framework.py check-completion)
          echo "has_winners=$results" >> $GITHUB_OUTPUT
      
      - name: Generate experiment report
        if: steps.check.outputs.has_winners == 'true'
        run: python tools/ab-testing-framework.py generate-report
      
      - name: Create decision issue
        if: steps.check.outputs.has_winners == 'true'
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: python tools/ab-testing-framework.py create-decision-issue
```

### 7. **Visualization Dashboard**

```html
<!-- docs/ab-testing.html -->

<div class="ab-testing-dashboard">
    <div class="active-experiments">
        <h3>🧪 Active Experiments</h3>
        
        <div class="experiment-card">
            <h4>Agent Performance Boost</h4>
            <div class="progress">
                <span class="label">Progress:</span>
                <div class="progress-bar">
                    <div class="fill" style="width: 65%">65%</div>
                </div>
                <span class="days-remaining">5 days remaining</span>
            </div>
            
            <div class="variants">
                <div class="variant control">
                    <h5>Control (50%)</h5>
                    <div class="metrics">
                        <div class="metric">
                            <span class="label">Success Rate:</span>
                            <span class="value">72%</span>
                        </div>
                        <div class="metric">
                            <span class="label">Avg Time:</span>
                            <span class="value">4.2 min</span>
                        </div>
                    </div>
                </div>
                
                <div class="variant test winning">
                    <h5>Smart Caching (25%) 🏆</h5>
                    <div class="metrics">
                        <div class="metric">
                            <span class="label">Success Rate:</span>
                            <span class="value">84%</span>
                            <span class="improvement">+12%</span>
                        </div>
                        <div class="metric">
                            <span class="label">Avg Time:</span>
                            <span class="value">3.1 min</span>
                            <span class="improvement">-26%</span>
                        </div>
                    </div>
                    <div class="significance">
                        <span class="badge">p < 0.01</span>
                        <span class="badge">d = 0.68</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="experiment-history">
        <h3>📊 Experiment Results</h3>
        <table>
            <thead>
                <tr>
                    <th>Experiment</th>
                    <th>Winner</th>
                    <th>Improvement</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Agent Performance Boost</td>
                    <td>Smart Caching</td>
                    <td>+12%</td>
                    <td><span class="badge rolled-out">Rolled Out</span></td>
                </tr>
                <tr>
                    <td>Learning Priority System</td>
                    <td>Impact-Based</td>
                    <td>+23%</td>
                    <td><span class="badge rolled-out">Rolled Out</span></td>
                </tr>
            </tbody>
        </table>
    </div>
</div>
```

## 📊 Success Metrics

- Number of experiments run per month
- Percentage of experiments with conclusive results
- Average improvement from winning variants
- Reduction in feature rollback rate
- Time saved by avoiding bad features
- Confidence in feature decisions
- ROI of experimentation program

## 🎨 Why This Matters

Test before you commit! By implementing A/B testing:

- **Risk Mitigation**: Test features safely before full rollout
- **Data-Driven Decisions**: Choose based on evidence, not gut feeling
- **Continuous Optimization**: Always improving through experimentation
- **Learn What Works**: Build institutional knowledge about successful patterns
- **Avoid Costly Mistakes**: Catch bad ideas before they impact everyone
- **Demonstrate Rigor**: Show scientific approach to AI development
- **Faster Innovation**: Experiment boldly, knowing you can measure results

## 🔗 Related

- What-If Simulator: `issue-8-what-if-simulator.md` (complementary prediction approach)
- Agent evaluator: `.github/workflows/agent-evaluator.yml`
- Feature flags could integrate with agent profiles
- [Source AI Friend conversation](../ai-conversations/conversation_20251117_091815.json)

## 💭 Example Experiments

Ideas to A/B test:

1. **Agent Caching Strategy**
   - Control: No caching
   - Variant A: Simple LRU cache
   - Variant B: Predictive caching
   - Metric: Task completion time

2. **Code Review Approach**
   - Control: Current CodeQL rules
   - Variant A: Stricter rules
   - Variant B: ML-enhanced review
   - Metric: Bug rate in merged PRs

3. **Learning Application Rate**
   - Control: Apply 3 learnings/week
   - Variant A: Apply 5 learnings/week
   - Variant B: Apply 10 learnings/week
   - Metric: Feature quality and velocity

4. **Agent Spawning Cadence**
   - Control: 1 agent/week
   - Variant A: 2 agents/week
   - Variant B: 3 agents/week
   - Metric: Overall agent ecosystem health

## 🚀 Future Enhancements

- **Multi-armed bandits**: Dynamic allocation optimization
- **Bayesian experiments**: Faster convergence to conclusions
- **Sequential testing**: Stop experiments early when results are clear
- **Interaction effects**: Test combinations of features
- **Personalization**: Different features for different contexts
- **Automated decision-making**: Auto-rollout winners
