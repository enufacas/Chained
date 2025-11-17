"""
Multi-Cloud AI Service for Chained Autonomous Agent System
===========================================================

This module provides a resilient, cost-optimized AI completion service
that automatically fails over between multiple AI providers (OpenAI,
Anthropic, and future local models).

Features:
---------
- Automatic provider failover for high availability
- Cost tracking and optimization
- Task-specific provider selection
- Usage analytics and reporting
- Support for multiple AI providers

Usage Example:
-------------
```python
from multi_cloud_ai_service import MultiCloudAIService, AIServiceConfig, AIProvider

# Initialize service with configuration
ai_service = MultiCloudAIService(
    config=AIServiceConfig(
        primary_provider=AIProvider.ANTHROPIC,
        fallback_providers=[AIProvider.OPENAI],
        cost_optimization=True
    )
)

# Complete a task with automatic provider selection
result = await ai_service.complete(
    prompt="Analyze this code for security issues: ...",
    task_type="analysis",
    max_tokens=2000
)

print(f"Completed with {result['provider']}")
print(f"Cost: ${result['cost']:.4f}")
print(f"Response: {result['text']}")

# Get usage report
report = ai_service.get_usage_report()
print(f"Total cost: ${report['total_cost']:.2f}")
```

Integration with Chained Agents:
--------------------------------
This service can be integrated into agent workflows to provide
resilient AI capabilities:

1. Code analysis: Use ANTHROPIC for deep reasoning
2. Code generation: Use OPENAI for Codex-based generation
3. Simple classification: Use LOCAL models for cost savings
4. Fallback: Automatic failover maintains uptime

Author: @cloud-architect
Date: 2025-11-17
Mission: idea:43 - Cloud Infrastructure Investigation
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import os
import json
from datetime import datetime


class AIProvider(Enum):
    """Supported AI providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"  # Future: local LLM support


@dataclass
class AIServiceConfig:
    """
    Configuration for multi-cloud AI service
    
    Attributes:
        primary_provider: Default provider to use first
        fallback_providers: List of backup providers (in order)
        timeout_seconds: Maximum time to wait for response
        max_retries: Number of retry attempts per provider
        cost_optimization: Enable task-specific provider selection
        cache_enabled: Enable response caching (future)
    """
    primary_provider: AIProvider = AIProvider.ANTHROPIC
    fallback_providers: List[AIProvider] = field(default_factory=list)
    timeout_seconds: int = 30
    max_retries: int = 2
    cost_optimization: bool = True
    cache_enabled: bool = False
    
    def __post_init__(self):
        if not self.fallback_providers:
            self.fallback_providers = [
                AIProvider.OPENAI,
                # AIProvider.LOCAL  # Uncomment when local LLM support added
            ]


@dataclass
class AIResponse:
    """
    Response from AI service
    
    Attributes:
        text: The completion text
        provider: Which provider generated the response
        cost: Estimated cost in USD
        tokens: Total tokens used (input + output)
        latency_ms: Response time in milliseconds
        success: Whether the request succeeded
        error: Error message if failed
        metadata: Additional provider-specific metadata
    """
    text: str
    provider: str
    cost: float
    tokens: int
    latency_ms: float
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class MultiCloudAIService:
    """
    Multi-provider AI service with automatic failover and cost optimization
    
    This service provides resilient AI completions by automatically failing over
    between multiple providers. It tracks usage, optimizes costs, and provides
    detailed analytics.
    
    Example:
        >>> service = MultiCloudAIService()
        >>> result = await service.complete("Analyze this code...")
        >>> print(f"Cost: ${result.cost:.4f}")
    """
    
    def __init__(self, config: Optional[AIServiceConfig] = None):
        """
        Initialize the multi-cloud AI service
        
        Args:
            config: Service configuration (uses defaults if not provided)
        """
        self.config = config or AIServiceConfig()
        self.providers: Dict[AIProvider, Any] = {}
        self.cost_tracker: Dict[str, Dict[str, Any]] = {}
        self.usage_history: List[Dict[str, Any]] = []
        
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize AI provider clients based on available credentials"""
        
        # OpenAI
        if os.getenv('OPENAI_API_KEY'):
            try:
                from openai import AsyncOpenAI
                self.providers[AIProvider.OPENAI] = AsyncOpenAI(
                    api_key=os.getenv('OPENAI_API_KEY'),
                    timeout=self.config.timeout_seconds
                )
                print("✓ OpenAI provider initialized")
            except ImportError:
                print("⚠ OpenAI SDK not installed (pip install openai)")
        else:
            print("⚠ OPENAI_API_KEY not found in environment")
        
        # Anthropic
        if os.getenv('ANTHROPIC_API_KEY'):
            try:
                from anthropic import AsyncAnthropic
                self.providers[AIProvider.ANTHROPIC] = AsyncAnthropic(
                    api_key=os.getenv('ANTHROPIC_API_KEY'),
                    timeout=self.config.timeout_seconds
                )
                print("✓ Anthropic provider initialized")
            except ImportError:
                print("⚠ Anthropic SDK not installed (pip install anthropic)")
        else:
            print("⚠ ANTHROPIC_API_KEY not found in environment")
        
        # Future: Local LLM support
        # if os.getenv('LOCAL_LLM_ENDPOINT'):
        #     self.providers[AIProvider.LOCAL] = LocalLLMClient(...)
        
        if not self.providers:
            raise Exception(
                "No AI providers initialized. Set OPENAI_API_KEY or "
                "ANTHROPIC_API_KEY environment variables."
            )
    
    async def complete(
        self,
        prompt: str,
        task_type: str = "analysis",
        max_tokens: int = 4000,
        temperature: float = 0.7,
        preferred_provider: Optional[AIProvider] = None,
        system_prompt: Optional[str] = None
    ) -> AIResponse:
        """
        Complete AI task with automatic provider selection and failover
        
        Args:
            prompt: The prompt for AI completion
            task_type: Type of task (analysis, generation, classification, etc.)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0-1.0)
            preferred_provider: Override automatic provider selection
            system_prompt: Optional system/instruction prompt
        
        Returns:
            AIResponse with completion text, provider used, cost, and metadata
        
        Raises:
            Exception: If all providers fail
        """
        
        # Determine provider order
        providers_to_try = self._get_provider_order(task_type, preferred_provider)
        
        last_error = None
        for attempt, provider in enumerate(providers_to_try):
            try:
                print(f"Attempting {provider.value} (attempt {attempt + 1}/{len(providers_to_try)})")
                
                result = await self._complete_with_provider(
                    provider=provider,
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system_prompt=system_prompt
                )
                
                # Track successful completion
                self._track_usage(provider, result, task_type)
                
                response = AIResponse(
                    text=result['text'],
                    provider=provider.value,
                    cost=result.get('cost', 0),
                    tokens=result.get('tokens', 0),
                    latency_ms=result.get('latency_ms', 0),
                    success=True,
                    metadata=result.get('metadata', {})
                )
                
                print(f"✓ Success with {provider.value} (cost: ${response.cost:.4f})")
                return response
                
            except Exception as e:
                last_error = e
                print(f"✗ {provider.value} failed: {str(e)[:100]}")
                continue
        
        # All providers failed
        error_msg = f"All AI providers failed. Last error: {last_error}"
        return AIResponse(
            text="",
            provider="none",
            cost=0,
            tokens=0,
            latency_ms=0,
            success=False,
            error=error_msg
        )
    
    def _get_provider_order(
        self,
        task_type: str,
        preferred: Optional[AIProvider]
    ) -> List[AIProvider]:
        """
        Determine order of providers to try based on task type and configuration
        
        Task-Specific Optimization:
        - code_generation: OpenAI (Codex strength)
        - analysis: Anthropic (Claude reasoning strength)
        - classification: Local models (cost savings)
        - default: Primary provider from config
        """
        if preferred and preferred in self.providers:
            # Start with preferred provider
            order = [preferred]
            order.extend([
                p for p in self.config.fallback_providers
                if p != preferred and p in self.providers
            ])
            return order
        
        # Task-specific optimization (if enabled)
        if self.config.cost_optimization:
            if task_type == "code_generation" and AIProvider.OPENAI in self.providers:
                return [
                    p for p in [AIProvider.OPENAI, AIProvider.ANTHROPIC, AIProvider.LOCAL]
                    if p in self.providers
                ]
            elif task_type == "analysis" and AIProvider.ANTHROPIC in self.providers:
                return [
                    p for p in [AIProvider.ANTHROPIC, AIProvider.OPENAI, AIProvider.LOCAL]
                    if p in self.providers
                ]
            elif task_type == "classification" and AIProvider.LOCAL in self.providers:
                return [
                    p for p in [AIProvider.LOCAL, AIProvider.ANTHROPIC, AIProvider.OPENAI]
                    if p in self.providers
                ]
        
        # Default order from config
        order = []
        if self.config.primary_provider in self.providers:
            order.append(self.config.primary_provider)
        
        for provider in self.config.fallback_providers:
            if provider in self.providers and provider not in order:
                order.append(provider)
        
        return order
    
    async def _complete_with_provider(
        self,
        provider: AIProvider,
        prompt: str,
        max_tokens: int,
        temperature: float,
        system_prompt: Optional[str]
    ) -> Dict[str, Any]:
        """Execute completion with specific provider"""
        
        client = self.providers.get(provider)
        if not client:
            raise Exception(f"Provider {provider.value} not initialized")
        
        start_time = asyncio.get_event_loop().time()
        
        if provider == AIProvider.OPENAI:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = await client.chat.completions.create(
                model="gpt-4",  # or "gpt-4-turbo-preview" for cheaper
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            text = response.choices[0].message.content
            tokens = response.usage.total_tokens
            cost = self._estimate_cost(provider, tokens)
            metadata = {
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason
            }
            
        elif provider == AIProvider.ANTHROPIC:
            response = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or "",
                messages=[{"role": "user", "content": prompt}]
            )
            
            text = response.content[0].text
            tokens = response.usage.input_tokens + response.usage.output_tokens
            cost = self._estimate_cost(provider, tokens)
            metadata = {
                "model": response.model,
                "stop_reason": response.stop_reason
            }
        
        else:
            raise NotImplementedError(f"Provider {provider.value} not implemented")
        
        latency_ms = (asyncio.get_event_loop().time() - start_time) * 1000
        
        return {
            'text': text,
            'tokens': tokens,
            'cost': cost,
            'latency_ms': latency_ms,
            'metadata': metadata
        }
    
    def _estimate_cost(self, provider: AIProvider, tokens: int) -> float:
        """
        Estimate cost based on provider pricing (2025 rates)
        
        Pricing estimates:
        - OpenAI GPT-4: $0.03 per 1K tokens (average of input/output)
        - Anthropic Claude-3.5-Sonnet: $0.015 per 1K tokens
        - Local: $0 (compute cost not included)
        """
        
        pricing = {
            AIProvider.OPENAI: 0.00003,  # $0.03 per 1K tokens
            AIProvider.ANTHROPIC: 0.000015,  # $0.015 per 1K tokens
            AIProvider.LOCAL: 0.0  # Free (compute cost separate)
        }
        
        return (tokens / 1000) * pricing.get(provider, 0)
    
    def _track_usage(
        self,
        provider: AIProvider,
        result: Dict[str, Any],
        task_type: str
    ):
        """Track usage statistics for cost optimization"""
        
        provider_key = provider.value
        if provider_key not in self.cost_tracker:
            self.cost_tracker[provider_key] = {
                'requests': 0,
                'tokens': 0,
                'cost': 0.0,
                'latency_ms_avg': 0.0,
                'by_task_type': {}
            }
        
        stats = self.cost_tracker[provider_key]
        stats['requests'] += 1
        stats['tokens'] += result.get('tokens', 0)
        stats['cost'] += result.get('cost', 0)
        
        # Update rolling average latency
        current_avg = stats['latency_ms_avg']
        new_latency = result.get('latency_ms', 0)
        stats['latency_ms_avg'] = (
            (current_avg * (stats['requests'] - 1) + new_latency) 
            / stats['requests']
        )
        
        # Track by task type
        if task_type not in stats['by_task_type']:
            stats['by_task_type'][task_type] = {
                'count': 0,
                'cost': 0.0,
                'tokens': 0
            }
        
        task_stats = stats['by_task_type'][task_type]
        task_stats['count'] += 1
        task_stats['cost'] += result.get('cost', 0)
        task_stats['tokens'] += result.get('tokens', 0)
        
        # Add to history
        self.usage_history.append({
            'timestamp': datetime.utcnow().isoformat(),
            'provider': provider_key,
            'task_type': task_type,
            'tokens': result.get('tokens', 0),
            'cost': result.get('cost', 0),
            'latency_ms': result.get('latency_ms', 0)
        })
    
    def get_usage_report(self) -> Dict[str, Any]:
        """
        Get comprehensive usage statistics across all providers
        
        Returns:
            Dict containing:
            - providers: Per-provider statistics
            - total_cost: Total spend across all providers
            - total_requests: Total number of requests
            - total_tokens: Total tokens processed
            - avg_latency_ms: Average response time
            - cost_by_task_type: Breakdown by task type
        """
        
        total_cost = sum(p['cost'] for p in self.cost_tracker.values())
        total_requests = sum(p['requests'] for p in self.cost_tracker.values())
        total_tokens = sum(p['tokens'] for p in self.cost_tracker.values())
        
        # Calculate average latency weighted by requests
        total_weighted_latency = sum(
            p['latency_ms_avg'] * p['requests']
            for p in self.cost_tracker.values()
        )
        avg_latency = (
            total_weighted_latency / total_requests if total_requests > 0 else 0
        )
        
        # Aggregate cost by task type across all providers
        cost_by_task = {}
        for provider_stats in self.cost_tracker.values():
            for task_type, task_stats in provider_stats.get('by_task_type', {}).items():
                if task_type not in cost_by_task:
                    cost_by_task[task_type] = {
                        'cost': 0.0,
                        'requests': 0,
                        'tokens': 0
                    }
                cost_by_task[task_type]['cost'] += task_stats['cost']
                cost_by_task[task_type]['requests'] += task_stats['count']
                cost_by_task[task_type]['tokens'] += task_stats['tokens']
        
        return {
            'providers': self.cost_tracker,
            'total_cost': total_cost,
            'total_requests': total_requests,
            'total_tokens': total_tokens,
            'avg_latency_ms': avg_latency,
            'cost_by_task_type': cost_by_task,
            'usage_history_count': len(self.usage_history)
        }
    
    def export_usage_history(self, filepath: str):
        """Export usage history to JSON file"""
        with open(filepath, 'w') as f:
            json.dump({
                'exported_at': datetime.utcnow().isoformat(),
                'config': {
                    'primary_provider': self.config.primary_provider.value,
                    'fallback_providers': [p.value for p in self.config.fallback_providers],
                    'cost_optimization': self.config.cost_optimization
                },
                'summary': self.get_usage_report(),
                'history': self.usage_history
            }, f, indent=2)
        
        print(f"✓ Usage history exported to {filepath}")


# Example usage and testing
async def example_usage():
    """
    Example demonstrating multi-cloud AI service usage
    
    This example shows how to:
    1. Initialize the service
    2. Complete various task types
    3. Handle failures gracefully
    4. Get usage reports
    """
    
    print("=" * 60)
    print("Multi-Cloud AI Service Example")
    print("=" * 60)
    
    # Initialize service
    ai_service = MultiCloudAIService(
        config=AIServiceConfig(
            primary_provider=AIProvider.ANTHROPIC,
            fallback_providers=[AIProvider.OPENAI],
            cost_optimization=True
        )
    )
    
    print("\n1. Code Analysis Task")
    print("-" * 60)
    result = await ai_service.complete(
        prompt="""Analyze this Python function for potential issues:

def process_user_input(data):
    user_id = data['user_id']
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query)
""",
        task_type="analysis",
        max_tokens=500,
        system_prompt="You are a security-focused code reviewer."
    )
    
    if result.success:
        print(f"Provider: {result.provider}")
        print(f"Cost: ${result.cost:.4f}")
        print(f"Response: {result.text[:200]}...")
    else:
        print(f"Error: {result.error}")
    
    print("\n2. Code Generation Task")
    print("-" * 60)
    result = await ai_service.complete(
        prompt="Write a Python function to validate email addresses using regex",
        task_type="code_generation",
        max_tokens=300
    )
    
    if result.success:
        print(f"Provider: {result.provider}")
        print(f"Cost: ${result.cost:.4f}")
        print(f"Response: {result.text[:200]}...")
    
    print("\n3. Usage Report")
    print("-" * 60)
    report = ai_service.get_usage_report()
    print(f"Total Cost: ${report['total_cost']:.4f}")
    print(f"Total Requests: {report['total_requests']}")
    print(f"Total Tokens: {report['total_tokens']}")
    print(f"Avg Latency: {report['avg_latency_ms']:.0f}ms")
    
    print("\nCost by Task Type:")
    for task_type, stats in report['cost_by_task_type'].items():
        print(f"  {task_type}:")
        print(f"    Requests: {stats['requests']}")
        print(f"    Cost: ${stats['cost']:.4f}")
        print(f"    Tokens: {stats['tokens']}")
    
    print("\nPer-Provider Statistics:")
    for provider, stats in report['providers'].items():
        print(f"  {provider}:")
        print(f"    Requests: {stats['requests']}")
        print(f"    Cost: ${stats['cost']:.4f}")
        print(f"    Avg Latency: {stats['latency_ms_avg']:.0f}ms")
    
    # Export history
    # ai_service.export_usage_history('/tmp/ai_usage_history.json')


if __name__ == "__main__":
    # Run example
    print("""
    To run this example, set environment variables:
    export OPENAI_API_KEY='your-key'
    export ANTHROPIC_API_KEY='your-key'
    
    Then run: python multi_cloud_ai_service.py
    """)
    
    # Uncomment to run example:
    # asyncio.run(example_usage())
