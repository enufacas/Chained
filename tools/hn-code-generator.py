#!/usr/bin/env python3
"""
HN Insights Code Generator

A transformer-inspired code generation system that learns from Hacker News insights
to generate relevant code snippets, tools, and implementations.

Created by @investigate-champion - analytical investigation approach inspired by Ada Lovelace.
Part of the Chained autonomous AI ecosystem.
"""

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import Counter


@dataclass
class CodeTemplate:
    """Represents a code generation template"""
    template_id: str
    category: str  # e.g., "api", "data_processing", "visualization", "ml"
    description: str
    code_template: str
    keywords: List[str]
    source_insights: List[str]  # URLs from HN that inspired this
    usage_count: int = 0
    created_at: str = ""
    
    def matches_keywords(self, text: str) -> float:
        """Calculate keyword match score (0-1)"""
        text_lower = text.lower()
        matches = sum(1 for kw in self.keywords if kw.lower() in text_lower)
        return matches / len(self.keywords) if self.keywords else 0.0


@dataclass
class GeneratedCode:
    """Represents generated code output"""
    code: str
    description: str
    template_used: str
    confidence: float
    source_insights: List[str]
    timestamp: str


class HNCodeGenerator:
    """
    Transformer-inspired code generator that learns from HN insights.
    
    Architecture:
    1. Input Layer: HN insights text processing
    2. Attention Mechanism: Keyword matching and relevance scoring
    3. Generation Layer: Template-based code synthesis
    4. Output Layer: Code validation and formatting
    
    This is a lightweight implementation that simulates transformer behavior
    without requiring heavy ML dependencies.
    """
    
    def __init__(self, data_dir: str = "tools/data/hn_code_gen"):
        """Initialize the code generator"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.templates_file = self.data_dir / "templates.json"
        self.generated_file = self.data_dir / "generated.json"
        
        self.templates: List[CodeTemplate] = []
        self.generated_history: List[GeneratedCode] = []
        
        self._load_data()
        self._initialize_templates()
    
    def _load_data(self):
        """Load existing templates and history"""
        if self.templates_file.exists():
            with open(self.templates_file, 'r') as f:
                data = json.load(f)
                self.templates = [CodeTemplate(**t) for t in data]
        
        if self.generated_file.exists():
            with open(self.generated_file, 'r') as f:
                data = json.load(f)
                self.generated_history = [GeneratedCode(**g) for g in data]
    
    def _save_data(self):
        """Save templates and history"""
        with open(self.templates_file, 'w') as f:
            json.dump([asdict(t) for t in self.templates], f, indent=2)
        
        with open(self.generated_file, 'w') as f:
            json.dump([asdict(g) for g in self.generated_history], f, indent=2)
    
    def _initialize_templates(self):
        """Initialize code templates if none exist"""
        if self.templates:
            return
        
        # Base templates inspired by common HN topics
        base_templates = [
            CodeTemplate(
                template_id="api_wrapper",
                category="api",
                description="Generate API wrapper with rate limiting",
                code_template="""
import requests
import time
from functools import wraps

class {ClassName}API:
    '''API wrapper for {api_name}'''
    
    def __init__(self, api_key: str, rate_limit: int = 60):
        self.api_key = api_key
        self.rate_limit = rate_limit
        self.last_request_time = 0
    
    def _rate_limit(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            elapsed = time.time() - self.last_request_time
            if elapsed < 1.0 / self.rate_limit:
                time.sleep(1.0 / self.rate_limit - elapsed)
            self.last_request_time = time.time()
            return func(self, *args, **kwargs)
        return wrapper
    
    @_rate_limit
    def fetch(self, endpoint: str) -> dict:
        '''Fetch data from API endpoint'''
        headers = {{'Authorization': f'Bearer {{self.api_key}}'}}
        response = requests.get(f'{{self.base_url}}/{{endpoint}}', headers=headers)
        response.raise_for_status()
        return response.json()
""",
                keywords=["api", "wrapper", "rate limit", "rest", "http"],
                source_insights=[],
                created_at=datetime.now(timezone.utc).isoformat()
            ),
            CodeTemplate(
                template_id="data_analyzer",
                category="data_processing",
                description="Generate data analysis tool",
                code_template="""
import json
from collections import Counter
from typing import List, Dict, Any

class {ClassName}Analyzer:
    '''Analyzer for {data_type} data'''
    
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.data = []
        self._load_data()
    
    def _load_data(self):
        '''Load data from file'''
        with open(self.data_path, 'r') as f:
            self.data = json.load(f)
    
    def analyze_distribution(self, field: str) -> Dict[str, int]:
        '''Analyze value distribution for a field'''
        values = [item.get(field) for item in self.data if field in item]
        return dict(Counter(values))
    
    def filter_by(self, field: str, value: Any) -> List[Dict]:
        '''Filter data by field value'''
        return [item for item in self.data if item.get(field) == value]
    
    def get_statistics(self) -> Dict[str, Any]:
        '''Get basic statistics about the dataset'''
        return {{
            'total_items': len(self.data),
            'fields': list(self.data[0].keys()) if self.data else [],
            'timestamp': '{timestamp}'
        }}
""",
                keywords=["data", "analysis", "statistics", "json", "processing"],
                source_insights=[],
                created_at=datetime.now(timezone.utc).isoformat()
            ),
            CodeTemplate(
                template_id="ml_model_wrapper",
                category="ml",
                description="Generate ML model wrapper with caching",
                code_template="""
import json
import hashlib
from pathlib import Path
from typing import Any, Dict, Optional

class {ClassName}Model:
    '''ML model wrapper with caching for {model_name}'''
    
    def __init__(self, cache_dir: str = '.cache'):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.model = None
    
    def _get_cache_key(self, input_data: str) -> str:
        '''Generate cache key from input'''
        return hashlib.md5(input_data.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[Dict]:
        '''Retrieve cached result if available'''
        cache_file = self.cache_dir / f'{{cache_key}}.json'
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                return json.load(f)
        return None
    
    def _cache_result(self, cache_key: str, result: Dict):
        '''Cache computation result'''
        cache_file = self.cache_dir / f'{{cache_key}}.json'
        with open(cache_file, 'w') as f:
            json.dump(result, f)
    
    def predict(self, input_data: str) -> Dict[str, Any]:
        '''Make prediction with caching'''
        cache_key = self._get_cache_key(input_data)
        
        # Check cache first
        cached = self._get_cached_result(cache_key)
        if cached:
            cached['from_cache'] = True
            return cached
        
        # Compute result
        result = self._compute_prediction(input_data)
        
        # Cache for future use
        self._cache_result(cache_key, result)
        result['from_cache'] = False
        return result
    
    def _compute_prediction(self, input_data: str) -> Dict[str, Any]:
        '''Perform actual model prediction'''
        # TODO: Implement model-specific logic
        return {{'prediction': 'placeholder', 'confidence': 0.0}}
""",
                keywords=["machine learning", "ml", "model", "prediction", "ai"],
                source_insights=[],
                created_at=datetime.now(timezone.utc).isoformat()
            ),
            CodeTemplate(
                template_id="monitoring_tool",
                category="devops",
                description="Generate monitoring and alerting tool",
                code_template="""
import time
import logging
from typing import Dict, Callable, Any
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass
class MetricThreshold:
    name: str
    threshold: float
    comparison: str  # 'gt', 'lt', 'eq'
    
class {ClassName}Monitor:
    '''Monitoring tool for {system_name}'''
    
    def __init__(self, check_interval: int = 60):
        self.check_interval = check_interval
        self.thresholds: Dict[str, MetricThreshold] = {{}}
        self.alerts_triggered: Dict[str, list] = {{}}
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def add_threshold(self, name: str, threshold: float, comparison: str = 'gt'):
        '''Add monitoring threshold'''
        self.thresholds[name] = MetricThreshold(name, threshold, comparison)
        self.alerts_triggered[name] = []
    
    def check_metric(self, name: str, value: float) -> bool:
        '''Check if metric exceeds threshold'''
        if name not in self.thresholds:
            return False
        
        threshold = self.thresholds[name]
        
        if threshold.comparison == 'gt' and value > threshold.threshold:
            return True
        elif threshold.comparison == 'lt' and value < threshold.threshold:
            return True
        elif threshold.comparison == 'eq' and value == threshold.threshold:
            return True
        
        return False
    
    def alert(self, name: str, value: float):
        '''Trigger alert for metric'''
        timestamp = datetime.now(timezone.utc).isoformat()
        alert = {{'metric': name, 'value': value, 'timestamp': timestamp}}
        self.alerts_triggered[name].append(alert)
        self.logger.warning(f'Alert: {{name}} = {{value}} at {{timestamp}}')
    
    def monitor(self, metrics_callback: Callable[[], Dict[str, float]]):
        '''Start monitoring loop'''
        self.logger.info(f'Starting monitor with {{len(self.thresholds)}} thresholds')
        
        while True:
            metrics = metrics_callback()
            
            for name, value in metrics.items():
                if self.check_metric(name, value):
                    self.alert(name, value)
            
            time.sleep(self.check_interval)
""",
                keywords=["monitoring", "devops", "alerts", "metrics", "observability"],
                source_insights=[],
                created_at=datetime.now(timezone.utc).isoformat()
            )
        ]
        
        self.templates = base_templates
        self._save_data()
    
    def analyze_hn_insights(self, learnings_dir: str = "learnings") -> Dict[str, Any]:
        """
        Analyze HN insights to extract patterns and topics.
        
        This simulates the "attention mechanism" of a transformer by
        identifying key topics and their relationships.
        """
        learnings_path = Path(learnings_dir)
        
        # Find recent HN learning files
        hn_files = sorted([
            f for f in learnings_path.glob("hn_*.json")
        ])[-10:]  # Last 10 sessions
        
        topics = Counter()
        titles = []
        descriptions = []
        urls = []
        
        for hn_file in hn_files:
            with open(hn_file, 'r') as f:
                data = json.load(f)
                
                for learning in data.get('learnings', []):
                    title = learning.get('title', '')
                    desc = learning.get('description', '')
                    url = learning.get('url', '')
                    
                    titles.append(title)
                    descriptions.append(desc)
                    urls.append(url)
                    
                    # Extract topics from title
                    # Simple keyword extraction
                    words = re.findall(r'\b\w+\b', title.lower())
                    for word in words:
                        if len(word) > 4:  # Filter short words
                            topics[word] += 1
        
        return {
            'top_topics': topics.most_common(20),
            'total_insights': len(titles),
            'titles': titles,
            'descriptions': descriptions,
            'urls': urls
        }
    
    def generate_code(
        self,
        description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[GeneratedCode]:
        """
        Generate code based on description and context.
        
        This simulates transformer generation by:
        1. Matching description to templates (attention)
        2. Selecting best template (selection)
        3. Filling template with context (generation)
        """
        if context is None:
            context = {}
        
        # Score all templates
        scored_templates = []
        for template in self.templates:
            score = template.matches_keywords(description)
            scored_templates.append((score, template))
        
        # Sort by score
        scored_templates.sort(reverse=True, key=lambda x: x[0])
        
        if not scored_templates or scored_templates[0][0] == 0:
            return None
        
        best_score, best_template = scored_templates[0]
        
        # Generate code by filling template
        class_name = context.get('class_name', 'Generated')
        api_name = context.get('api_name', 'API')
        data_type = context.get('data_type', 'data')
        model_name = context.get('model_name', 'model')
        system_name = context.get('system_name', 'system')
        timestamp = datetime.now(timezone.utc).isoformat()
        
        code = best_template.code_template.format(
            ClassName=class_name,
            api_name=api_name,
            data_type=data_type,
            model_name=model_name,
            system_name=system_name,
            timestamp=timestamp
        )
        
        # Create generated code object
        generated = GeneratedCode(
            code=code.strip(),
            description=f"Generated {best_template.category} code: {best_template.description}",
            template_used=best_template.template_id,
            confidence=best_score,
            source_insights=best_template.source_insights,
            timestamp=timestamp
        )
        
        # Update template usage
        best_template.usage_count += 1
        
        # Record generation
        self.generated_history.append(generated)
        self._save_data()
        
        return generated
    
    def learn_from_insights(self, insights: Dict[str, Any]):
        """
        Learn new patterns from HN insights.
        
        This simulates the learning phase of a transformer by
        creating new templates based on recurring patterns.
        """
        top_topics = dict(insights.get('top_topics', []))
        
        # Check if we should create new templates
        # Based on topic frequency
        for topic, count in top_topics.items():
            if count >= 5:  # Appears in 5+ insights
                # Check if we already have a template for this
                existing = any(
                    topic.lower() in [kw.lower() for kw in t.keywords]
                    for t in self.templates
                )
                
                if not existing:
                    # Create new template
                    new_template = CodeTemplate(
                        template_id=f"{topic}_tool",
                        category="learned",
                        description=f"Tool related to {topic}",
                        code_template=f"""
# Generated code template for {topic}
# Based on HN insights showing {count} mentions

class {topic.title()}Tool:
    '''Tool for working with {topic}'''
    
    def __init__(self):
        self.name = '{topic}'
        self.initialized = True
    
    def process(self, data):
        '''Process {topic}-related data'''
        # TODO: Implement based on use case
        return data
""",
                        keywords=[topic],
                        source_insights=insights.get('urls', [])[:3],
                        created_at=datetime.now(timezone.utc).isoformat()
                    )
                    
                    self.templates.append(new_template)
        
        self._save_data()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get generation statistics"""
        return {
            'total_templates': len(self.templates),
            'total_generated': len(self.generated_history),
            'templates_by_category': Counter(t.category for t in self.templates),
            'most_used_template': max(self.templates, key=lambda t: t.usage_count).template_id if self.templates else None,
            'avg_confidence': sum(g.confidence for g in self.generated_history) / len(self.generated_history) if self.generated_history else 0.0
        }


def main():
    """Main entry point for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='HN Insights Code Generator')
    parser.add_argument('--analyze', action='store_true', help='Analyze HN insights')
    parser.add_argument('--generate', type=str, help='Generate code for description')
    parser.add_argument('--learn', action='store_true', help='Learn from HN insights')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--class-name', type=str, default='Generated', help='Class name for generated code')
    
    args = parser.parse_args()
    
    generator = HNCodeGenerator()
    
    if args.analyze:
        print("📊 Analyzing HN insights...")
        insights = generator.analyze_hn_insights()
        print(f"\nFound {insights['total_insights']} insights")
        print("\nTop topics:")
        for topic, count in insights['top_topics'][:10]:
            print(f"  {topic}: {count}")
    
    elif args.generate:
        print(f"⚡ Generating code for: {args.generate}")
        context = {'class_name': args.class_name}
        generated = generator.generate_code(args.generate, context)
        
        if generated:
            print(f"\n✓ Generated code (confidence: {generated.confidence:.2f})")
            print(f"Template: {generated.template_used}")
            print("\nCode:")
            print("```python")
            print(generated.code)
            print("```")
        else:
            print("✗ No matching template found")
    
    elif args.learn:
        print("🧠 Learning from HN insights...")
        insights = generator.analyze_hn_insights()
        generator.learn_from_insights(insights)
        print(f"✓ Learned {len(generator.templates)} templates")
    
    elif args.stats:
        print("📈 Code Generation Statistics")
        stats = generator.get_statistics()
        print(f"\nTemplates: {stats['total_templates']}")
        print(f"Generated: {stats['total_generated']}")
        print(f"Avg Confidence: {stats['avg_confidence']:.2f}")
        print(f"\nMost used: {stats['most_used_template']}")
        print("\nBy category:")
        for cat, count in stats['templates_by_category'].items():
            print(f"  {cat}: {count}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
