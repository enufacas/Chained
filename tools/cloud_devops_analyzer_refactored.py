#!/usr/bin/env python3
"""
Cloud DevOps Innovation Analyzer - Refactored Version
Organized by: @organize-guru (Robert Martin)
Original by: @investigate-champion
Mission: idea:15 - Cloud DevOps Innovation Investigation

Clean Code Improvements Applied:
- Single Responsibility Principle (each class/method has one job)
- Open/Closed Principle (extensible via configuration)
- Configuration extraction (no hardcoded patterns)
- Reduced cyclomatic complexity
- Improved testability

Usage:
    python3 cloud_devops_analyzer_refactored.py [--source SOURCE] [--format FORMAT]
"""

import json
import os
import sys
from collections import defaultdict, Counter
from datetime import datetime, timezone
from typing import Dict, List, Optional, Protocol
from dataclasses import dataclass


# ============================================================================
# CONFIGURATION (Open/Closed Principle - extend without modifying)
# ============================================================================

@dataclass
class CloudProvider:
    """Cloud provider configuration"""
    name: str
    city: str
    country: str
    aliases: List[str]


@dataclass
class AnalyzerConfig:
    """Centralized configuration for analyzer"""
    
    cloud_providers: List[CloudProvider] = None
    devops_patterns: List[str] = None
    security_keywords: List[str] = None
    
    def __post_init__(self):
        if self.cloud_providers is None:
            self.cloud_providers = [
                CloudProvider('AWS', 'Seattle', 'US', ['aws', 'amazon web services']),
                CloudProvider('Azure', 'Redmond', 'US', ['azure', 'microsoft azure']),
                CloudProvider('Google Cloud', 'San Francisco', 'US', ['gcp', 'google cloud']),
                CloudProvider('Alibaba Cloud', 'Hangzhou', 'CN', ['alibaba cloud']),
                CloudProvider('Tencent Cloud', 'Shenzhen', 'CN', ['tencent cloud']),
            ]
        
        if self.devops_patterns is None:
            self.devops_patterns = [
                'ci/cd', 'infrastructure as code', 'gitops', 'containerization',
                'kubernetes', 'docker', 'microservices', 'serverless',
                'observability', 'monitoring', 'automation', 'security',
                'self-healing', 'distributed systems', 'edge computing'
            ]
        
        if self.security_keywords is None:
            self.security_keywords = [
                'security', 'vulnerability', 'breach', 'ransomware', 'attack',
                'encryption', 'authentication', 'authorization', 'zero-trust',
                'compliance', 'audit', 'penetration test', 'bug bounty'
            ]


# ============================================================================
# DATA LOADING (Single Responsibility)
# ============================================================================

class LearningDataLoader:
    """Responsible only for loading learning data from files"""
    
    def __init__(self, learnings_dir: str = 'learnings'):
        self.learnings_dir = learnings_dir
    
    def load(self, source_filter: Optional[str] = None) -> List[Dict]:
        """
        Load learning data from JSON files
        
        Args:
            source_filter: Optional filter for specific source (e.g., 'hn', 'tldr')
            
        Returns:
            List of loaded data items
        """
        if not os.path.exists(self.learnings_dir):
            print(f"❌ Learning directory not found: {self.learnings_dir}")
            return []
        
        data = []
        files_loaded = 0
        
        for filename in self._get_json_files(source_filter):
            items = self._load_file(filename)
            if items:
                data.extend(items)
                files_loaded += 1
        
        print(f"✅ Loaded {len(data)} items from {files_loaded} files")
        return data
    
    def _get_json_files(self, source_filter: Optional[str]) -> List[str]:
        """Get list of JSON files to load"""
        files = []
        for filename in os.listdir(self.learnings_dir):
            if not filename.endswith('.json'):
                continue
            if source_filter and source_filter.lower() not in filename.lower():
                continue
            files.append(filename)
        return files
    
    def _load_file(self, filename: str) -> List[Dict]:
        """Load a single JSON file"""
        filepath = os.path.join(self.learnings_dir, filename)
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                # Handle different JSON structures
                if 'learnings' in data:
                    return data['learnings']
                elif 'ideas' in data:
                    return data['ideas']
                return []
        except Exception as e:
            print(f"⚠️  Error loading {filename}: {e}")
            return []


# ============================================================================
# CLOUD ANALYSIS (Single Responsibility)
# ============================================================================

class CloudPatternAnalyzer:
    """Analyzes cloud infrastructure patterns"""
    
    def __init__(self, config: AnalyzerConfig):
        self.config = config
    
    def analyze(self, data: List[Dict]) -> Dict:
        """
        Analyze cloud-related patterns in data
        
        Returns:
            Dictionary with cloud pattern analysis
        """
        provider_mentions = self._count_provider_mentions(data)
        regional_dist = self._calculate_regional_distribution(provider_mentions)
        cloud_keywords = self._count_cloud_keywords(data)
        
        return {
            'cloud_mentions': cloud_keywords,
            'provider_mentions': provider_mentions,
            'regional_distribution': regional_dist,
            'total_cloud_references': sum(cloud_keywords.values())
        }
    
    def _count_provider_mentions(self, data: List[Dict]) -> Dict[str, int]:
        """Count mentions of each cloud provider"""
        counts = Counter()
        
        for item in data:
            content = str(item).lower()
            for provider in self.config.cloud_providers:
                if self._matches_provider(content, provider):
                    counts[provider.name] += 1
        
        return dict(counts)
    
    def _matches_provider(self, content: str, provider: CloudProvider) -> bool:
        """Check if content mentions a provider"""
        return (provider.name.lower() in content or 
                any(alias in content for alias in provider.aliases))
    
    def _calculate_regional_distribution(self, 
                                        provider_mentions: Dict[str, int]) -> Dict[str, int]:
        """Calculate regional distribution from provider mentions"""
        regional = Counter()
        
        for provider in self.config.cloud_providers:
            if provider.name in provider_mentions:
                regional[provider.city] += provider_mentions[provider.name]
        
        return dict(regional)
    
    def _count_cloud_keywords(self, data: List[Dict]) -> Dict[str, int]:
        """Count cloud-related keywords"""
        keywords = ['cloud', 'infrastructure', 'scalability', 'distributed_systems']
        keyword_map = {
            'cloud': ['cloud'],
            'infrastructure': ['infrastructure'],
            'scalability': ['scaling', 'scalability'],
            'distributed_systems': ['distributed']
        }
        
        counts = Counter()
        for item in data:
            content = str(item).lower()
            for key, patterns in keyword_map.items():
                if any(pattern in content for pattern in patterns):
                    counts[key] += 1
        
        return dict(counts)


# ============================================================================
# DEVOPS ANALYSIS (Single Responsibility)
# ============================================================================

class DevOpsPatternAnalyzer:
    """Analyzes DevOps trends and patterns"""
    
    def __init__(self, config: AnalyzerConfig):
        self.config = config
    
    def analyze(self, data: List[Dict]) -> Dict:
        """
        Analyze DevOps patterns
        
        Returns:
            Dictionary with DevOps analysis
        """
        pattern_mentions = self._count_pattern_mentions(data)
        automation_pct = self._calculate_automation_percentage(data)
        
        return {
            'pattern_mentions': dict(pattern_mentions.most_common(10)),
            'automation_percentage': automation_pct,
            'top_patterns': [p[0] for p in pattern_mentions.most_common(5)],
            'total_patterns_detected': len(pattern_mentions)
        }
    
    def _count_pattern_mentions(self, data: List[Dict]) -> Counter:
        """Count DevOps pattern mentions"""
        counts = Counter()
        
        for item in data:
            content = str(item).lower()
            for pattern in self.config.devops_patterns:
                if pattern in content:
                    counts[pattern] += 1
        
        return counts
    
    def _calculate_automation_percentage(self, data: List[Dict]) -> float:
        """Calculate percentage of items mentioning automation"""
        if not data:
            return 0.0
        
        automation_keywords = ['automat', 'ai', 'ml', 'self-healing']
        automation_count = sum(
            1 for item in data 
            if any(keyword in str(item).lower() for keyword in automation_keywords)
        )
        
        return (automation_count / len(data)) * 100


# ============================================================================
# SECURITY ANALYSIS (Single Responsibility)
# ============================================================================

class SecurityLandscapeAnalyzer:
    """Analyzes security incidents and best practices"""
    
    def __init__(self, config: AnalyzerConfig):
        self.config = config
    
    def analyze(self, data: List[Dict]) -> Dict:
        """
        Analyze security landscape
        
        Returns:
            Dictionary with security analysis
        """
        keyword_mentions = self._count_security_keywords(data)
        incidents = self._identify_incidents(data)
        best_practices = self._identify_best_practices(data)
        
        return {
            'security_mentions': dict(keyword_mentions.most_common(10)),
            'incident_count': len(incidents),
            'incidents': incidents[:5],
            'best_practices_count': len(best_practices),
            'security_focus_percentage': self._calculate_security_focus(data, keyword_mentions)
        }
    
    def _count_security_keywords(self, data: List[Dict]) -> Counter:
        """Count security keyword mentions"""
        counts = Counter()
        
        for item in data:
            content = str(item).lower()
            for keyword in self.config.security_keywords:
                if keyword in content:
                    counts[keyword] += 1
        
        return counts
    
    def _identify_incidents(self, data: List[Dict]) -> List[Dict]:
        """Identify security incidents"""
        incident_keywords = ['breach', 'hack', 'attack', 'ransomware']
        incidents = []
        
        for item in data:
            content = str(item).lower()
            if any(word in content for word in incident_keywords):
                incidents.append({
                    'title': item.get('title', '') if isinstance(item, dict) else '',
                    'type': 'security_incident',
                    'keywords': [k for k in self.config.security_keywords if k in content]
                })
        
        return incidents
    
    def _identify_best_practices(self, data: List[Dict]) -> List[Dict]:
        """Identify security best practices"""
        practice_keywords = ['best practice', 'security guide', 'hardening']
        practices = []
        
        for item in data:
            content = str(item).lower()
            if any(word in content for word in practice_keywords):
                practices.append({
                    'title': item.get('title', '') if isinstance(item, dict) else '',
                    'type': 'best_practice'
                })
        
        return practices
    
    def _calculate_security_focus(self, data: List[Dict], 
                                  keyword_mentions: Counter) -> float:
        """Calculate percentage of content focused on security"""
        if not data:
            return 0.0
        return (sum(keyword_mentions.values()) / len(data)) * 100


# ============================================================================
# INNOVATION SCORING (Single Responsibility)
# ============================================================================

class InnovationScoreCalculator:
    """Calculates innovation scores based on trend analysis"""
    
    WEIGHTS = {
        'ai_ml': 0.4,
        'automation': 0.3,
        'emerging_tech': 0.3
    }
    
    AI_ML_KEYWORDS = ['ai', 'ml', 'machine learning', 'gpt', 'llm']
    AUTOMATION_KEYWORDS = ['automat', 'self-healing', 'intelligent', 'smart']
    EMERGING_KEYWORDS = ['edge computing', 'serverless', 'webassembly', 'quantum']
    
    def calculate(self, data: List[Dict]) -> Dict:
        """
        Calculate innovation score
        
        Returns:
            Dictionary with innovation metrics
        """
        if not data:
            return self._empty_metrics()
        
        total = len(data)
        ai_ml = self._count_keywords(data, self.AI_ML_KEYWORDS)
        automation = self._count_keywords(data, self.AUTOMATION_KEYWORDS)
        emerging = self._count_keywords(data, self.EMERGING_KEYWORDS)
        
        return {
            'innovation_score': self._calculate_score(ai_ml, automation, emerging, total),
            'ai_ml_adoption': (ai_ml / total) * 100,
            'automation_level': (automation / total) * 100,
            'emerging_tech_adoption': (emerging / total) * 100
        }
    
    def _count_keywords(self, data: List[Dict], keywords: List[str]) -> int:
        """Count items containing any of the keywords"""
        return sum(
            1 for item in data 
            if any(keyword in str(item).lower() for keyword in keywords)
        )
    
    def _calculate_score(self, ai_ml: int, automation: int, 
                        emerging: int, total: int) -> float:
        """Calculate weighted innovation score"""
        return (
            (ai_ml / total * self.WEIGHTS['ai_ml']) +
            (automation / total * self.WEIGHTS['automation']) +
            (emerging / total * self.WEIGHTS['emerging_tech'])
        ) * 100
    
    def _empty_metrics(self) -> Dict:
        """Return empty metrics structure"""
        return {
            'innovation_score': 0.0,
            'ai_ml_adoption': 0.0,
            'automation_level': 0.0,
            'emerging_tech_adoption': 0.0
        }


# ============================================================================
# REPORT GENERATION (Single Responsibility)
# ============================================================================

class ReportGenerator:
    """Generates analysis reports in different formats"""
    
    def __init__(self, agent_name: str = '@organize-guru'):
        self.agent_name = agent_name
    
    def generate(self, analyses: Dict, output_format: str = 'text') -> str:
        """
        Generate comprehensive report
        
        Args:
            analyses: Dictionary containing all analysis results
            output_format: 'text' or 'json'
            
        Returns:
            Formatted report string
        """
        if output_format == 'json':
            return self._generate_json_report(analyses)
        return self._generate_text_report(analyses)
    
    def _generate_json_report(self, analyses: Dict) -> str:
        """Generate JSON format report"""
        report = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'analyzer': self.agent_name,
            'mission': 'idea:15',
            **analyses
        }
        return json.dumps(report, indent=2)
    
    def _generate_text_report(self, analyses: Dict) -> str:
        """Generate text format report"""
        lines = []
        lines.extend(self._generate_header())
        lines.extend(self._generate_cloud_section(analyses['cloud_analysis']))
        lines.extend(self._generate_devops_section(analyses['devops_analysis']))
        lines.extend(self._generate_security_section(analyses['security_analysis']))
        lines.extend(self._generate_innovation_section(analyses['innovation_metrics']))
        lines.extend(self._generate_footer())
        return '\n'.join(lines)
    
    def _generate_header(self) -> List[str]:
        """Generate report header"""
        return [
            "=" * 80,
            "🎯 CLOUD DEVOPS INNOVATION ANALYSIS REPORT",
            f"Generated by: {self.agent_name}",
            f"Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "Mission: idea:15 - Cloud DevOps Innovation (Refactored)",
            "=" * 80,
            ""
        ]
    
    def _generate_cloud_section(self, analysis: Dict) -> List[str]:
        """Generate cloud analysis section"""
        lines = [
            "📊 CLOUD INFRASTRUCTURE ANALYSIS",
            "-" * 80,
            f"Total Cloud References: {analysis['total_cloud_references']}",
            "",
            "Cloud Providers:"
        ]
        
        for provider, count in sorted(
            analysis['provider_mentions'].items(),
            key=lambda x: x[1],
            reverse=True
        ):
            lines.append(f"  • {provider}: {count} mentions")
        
        lines.extend(["", "Regional Distribution:"])
        for region, count in sorted(
            analysis['regional_distribution'].items(),
            key=lambda x: x[1],
            reverse=True
        ):
            lines.append(f"  • {region}: {count} mentions")
        
        lines.append("")
        return lines
    
    def _generate_devops_section(self, analysis: Dict) -> List[str]:
        """Generate DevOps analysis section"""
        return [
            "🔧 DEVOPS TRENDS ANALYSIS",
            "-" * 80,
            f"Patterns Detected: {analysis['total_patterns_detected']}",
            f"Automation Level: {analysis['automation_percentage']:.1f}%",
            "",
            "Top DevOps Patterns:",
            *[f"  • {pattern}: {count} mentions" 
              for pattern, count in analysis['pattern_mentions'].items()],
            ""
        ]
    
    def _generate_security_section(self, analysis: Dict) -> List[str]:
        """Generate security analysis section"""
        return [
            "🔒 SECURITY LANDSCAPE ANALYSIS",
            "-" * 80,
            f"Security Incidents: {analysis['incident_count']}",
            f"Best Practices: {analysis['best_practices_count']}",
            f"Security Focus: {analysis['security_focus_percentage']:.1f}%",
            ""
        ]
    
    def _generate_innovation_section(self, metrics: Dict) -> List[str]:
        """Generate innovation metrics section"""
        return [
            "🚀 INNOVATION METRICS",
            "-" * 80,
            f"Innovation Score: {metrics['innovation_score']:.1f}/100",
            f"AI/ML Adoption: {metrics['ai_ml_adoption']:.1f}%",
            f"Automation Level: {metrics['automation_level']:.1f}%",
            f"Emerging Tech: {metrics['emerging_tech_adoption']:.1f}%",
            ""
        ]
    
    def _generate_footer(self) -> List[str]:
        """Generate report footer"""
        return [
            "=" * 80,
            "✅ ANALYSIS COMPLETE",
            f"Refactored by {self.agent_name} applying clean code principles",
            "=" * 80
        ]


# ============================================================================
# MAIN ANALYZER (Coordination only)
# ============================================================================

class CloudDevOpsAnalyzer:
    """
    Main analyzer coordinating all analysis components
    (Single responsibility: Coordination only)
    """
    
    def __init__(self, learnings_dir: str = 'learnings', 
                 config: Optional[AnalyzerConfig] = None):
        self.config = config or AnalyzerConfig()
        self.loader = LearningDataLoader(learnings_dir)
        self.cloud_analyzer = CloudPatternAnalyzer(self.config)
        self.devops_analyzer = DevOpsPatternAnalyzer(self.config)
        self.security_analyzer = SecurityLandscapeAnalyzer(self.config)
        self.innovation_calculator = InnovationScoreCalculator()
        self.report_generator = ReportGenerator('@organize-guru')
        self.data = []
    
    def load_data(self, source_filter: Optional[str] = None) -> int:
        """Load learning data"""
        self.data = self.loader.load(source_filter)
        return len(self.data)
    
    def analyze(self) -> Dict:
        """Run all analyses and return results"""
        return {
            'data_sources': len(self.data),
            'cloud_analysis': self.cloud_analyzer.analyze(self.data),
            'devops_analysis': self.devops_analyzer.analyze(self.data),
            'security_analysis': self.security_analyzer.analyze(self.data),
            'innovation_metrics': self.innovation_calculator.calculate(self.data)
        }
    
    def generate_report(self, output_format: str = 'text') -> str:
        """Generate analysis report"""
        analyses = self.analyze()
        return self.report_generator.generate(analyses, output_format)


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Cloud DevOps Innovation Analyzer (Refactored)'
    )
    parser.add_argument('--source', help='Filter by source (hn, tldr, github)')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                       help='Output format')
    parser.add_argument('--dir', default='learnings',
                       help='Learning data directory')
    
    args = parser.parse_args()
    
    # Initialize and run analyzer
    analyzer = CloudDevOpsAnalyzer(args.dir)
    
    print(f"🎯 Cloud DevOps Innovation Analyzer (@organize-guru refactored)")
    print(f"Loading data from: {args.dir}")
    print()
    
    count = analyzer.load_data(args.source)
    if count == 0:
        print("❌ No data loaded")
        return 1
    
    print(f"Analyzing {count} items...")
    print()
    
    report = analyzer.generate_report(args.format)
    print(report)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
