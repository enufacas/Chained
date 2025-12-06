"""
AI-Native Control Plane - LLM Integration Module

Provides LLM-based intent classification and plan generation using:
- OpenAI GPT-4 (via LangChain)
- Google Gemini (via LangChain)

This replaces the stub keyword-based classification with real AI models.
"""

import json
import logging
import os
from enum import Enum
from typing import Any, Dict, Optional, Tuple

from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.exceptions import OutputParserException
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    GEMINI = "gemini"


class LLMConfig:
    """LLM configuration from environment variables"""

    def __init__(self):
        # Provider selection
        self.provider = LLMProvider(
            os.getenv("LLM_PROVIDER", "gemini").lower()
        )

        # OpenAI config
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        self.openai_temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.0"))

        # Gemini config
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.gemini_temperature = float(os.getenv("GEMINI_TEMPERATURE", "0.0"))

        # Common config
        self.max_retries = int(os.getenv("LLM_MAX_RETRIES", "3"))
        self.timeout = int(os.getenv("LLM_TIMEOUT", "30"))

    def validate(self) -> bool:
        """Validate configuration"""
        if self.provider == LLMProvider.OPENAI:
            if not self.openai_api_key:
                logger.error("OPENAI_API_KEY not set")
                return False
        elif self.provider == LLMProvider.GEMINI:
            if not self.gemini_api_key:
                logger.error("GEMINI_API_KEY not set")
                return False
        return True

    def __repr__(self) -> str:
        return f"LLMConfig(provider={self.provider}, model={self.get_model()})"

    def get_model(self) -> str:
        """Get the model name for current provider"""
        if self.provider == LLMProvider.OPENAI:
            return self.openai_model
        elif self.provider == LLMProvider.GEMINI:
            return self.gemini_model
        return "unknown"


# =============================================================================
# Pydantic Models for Structured Output
# =============================================================================


class IntentClassification(BaseModel):
    """Structured output for intent classification"""

    intent: str = Field(
        description="Classified intent: 'create_app', 'update_app', 'deploy', 'scale', 'delete', 'system_upgrade', 'query_status', or 'unknown'"
    )
    confidence: float = Field(
        description="Confidence score between 0.0 and 1.0",
        ge=0.0,
        le=1.0
    )
    reasoning: str = Field(
        description="Brief explanation of why this intent was chosen"
    )
    extracted_entities: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Key entities extracted from request (app name, region, etc.)"
    )


class PlanGeneration(BaseModel):
    """Structured output for plan generation"""

    plan_steps: list[str] = Field(
        description="Ordered list of steps to execute"
    )
    estimated_duration_seconds: int = Field(
        description="Estimated total duration in seconds",
        ge=1
    )
    required_resources: list[str] = Field(
        description="List of GCP resources needed (e.g., 'gcs_bucket', 'cloud_run_service')"
    )
    risk_level: str = Field(
        description="Risk level: 'low', 'medium', or 'high'"
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Potential issues or warnings"
    )


# =============================================================================
# LLM Client
# =============================================================================


class LLMClient:
    """
    LLM client for intent classification and plan generation.

    Supports OpenAI and Gemini via LangChain.
    """

    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initialize LLM client.

        Args:
            config: LLMConfig instance (creates default if None)
        """
        self.config = config or LLMConfig()

        if not self.config.validate():
            raise ValueError("Invalid LLM configuration")

        # Initialize LangChain chat model
        self.chat_model = self._create_chat_model()

        logger.info(f"LLM client initialized: {self.config}")

    def _create_chat_model(self):
        """Create LangChain chat model based on provider"""
        if self.config.provider == LLMProvider.OPENAI:
            return ChatOpenAI(
                model=self.config.openai_model,
                temperature=self.config.openai_temperature,
                api_key=self.config.openai_api_key,
                max_retries=self.config.max_retries,
                timeout=self.config.timeout,
            )
        elif self.config.provider == LLMProvider.GEMINI:
            return ChatGoogleGenerativeAI(
                model=self.config.gemini_model,
                temperature=self.config.gemini_temperature,
                google_api_key=self.config.gemini_api_key,
                max_retries=self.config.max_retries,
                timeout=self.config.timeout,
            )
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")

    def classify_intent(self, user_request: str) -> IntentClassification:
        """
        Classify user intent using LLM.

        Args:
            user_request: Natural language request from user

        Returns:
            IntentClassification with intent, confidence, and reasoning

        Raises:
            Exception: If LLM invocation fails
        """
        # Create output parser
        parser = PydanticOutputParser(pydantic_object=IntentClassification)

        # Create prompt template
        prompt_template = PromptTemplate(
            template="""You are an AI assistant for a cloud infrastructure control plane.
Your job is to classify the user's intent from their natural language request.

Available intents:
- create_app: User wants to create a new application
- update_app: User wants to update/modify an existing application
- deploy: User wants to deploy an application
- scale: User wants to scale resources up or down
- delete: User wants to delete/remove resources
- system_upgrade: User wants to upgrade the control plane itself
- query_status: User wants to check status/health of resources
- unknown: Intent is unclear or not supported

User request: {user_request}

Analyze the request and provide:
1. The most likely intent
2. Confidence score (0.0 to 1.0)
3. Brief reasoning for your classification
4. Any key entities mentioned (app name, region, etc.)

{format_instructions}""",
            input_variables=["user_request"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        # Create chain
        chain = prompt_template | self.chat_model | parser

        try:
            # Invoke LLM
            result = chain.invoke({"user_request": user_request})
            logger.info(
                f"Intent classified: {result.intent} (confidence: {result.confidence})"
            )
            return result

        except OutputParserException as e:
            logger.error(f"Failed to parse LLM output: {e}")
            # Fallback to low-confidence unknown
            return IntentClassification(
                intent="unknown",
                confidence=0.3,
                reasoning=f"Failed to parse LLM response: {str(e)}",
            )

        except Exception as e:
            logger.error(f"LLM invocation failed: {e}", exc_info=True)
            raise

    def generate_plan(
        self,
        intent: str,
        user_request: str,
        context: Optional[Dict[str, Any]] = None
    ) -> PlanGeneration:
        """
        Generate execution plan using LLM.

        Args:
            intent: Classified intent (e.g., 'create_app')
            user_request: Original user request
            context: Additional context (existing apps, policies, etc.)

        Returns:
            PlanGeneration with steps, duration, resources, and risks

        Raises:
            Exception: If LLM invocation fails
        """
        # Create output parser
        parser = PydanticOutputParser(pydantic_object=PlanGeneration)

        # Format context
        context_str = ""
        if context:
            context_str = f"\nAdditional context:\n{json.dumps(context, indent=2)}"

        # Create prompt template
        prompt_template = PromptTemplate(
            template="""You are an AI assistant for a cloud infrastructure control plane.
Generate a detailed execution plan for the following request.

Intent: {intent}
User request: {user_request}{context_str}

Generate a plan that includes:
1. Ordered list of specific steps (e.g., "Create GCS bucket", "Upload HTML files")
2. Estimated total duration in seconds
3. List of GCP resources needed
4. Risk level (low/medium/high)
5. Any warnings or potential issues

Be specific and actionable. Each step should be clear enough for a machine to execute.

{format_instructions}""",
            input_variables=["intent", "user_request", "context_str"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        # Create chain
        chain = prompt_template | self.chat_model | parser

        try:
            # Invoke LLM
            result = chain.invoke({
                "intent": intent,
                "user_request": user_request,
                "context_str": context_str,
            })
            logger.info(
                f"Plan generated: {len(result.plan_steps)} steps, "
                f"{result.estimated_duration_seconds}s, risk={result.risk_level}"
            )
            return result

        except OutputParserException as e:
            logger.error(f"Failed to parse LLM output: {e}")
            # Fallback to minimal plan
            return PlanGeneration(
                plan_steps=["Failed to generate detailed plan"],
                estimated_duration_seconds=60,
                required_resources=[],
                risk_level="high",
                warnings=[f"Plan generation failed: {str(e)}"],
            )

        except Exception as e:
            logger.error(f"LLM invocation failed: {e}", exc_info=True)
            raise


# =============================================================================
# Convenience Functions
# =============================================================================


def classify_intent_with_llm(user_request: str) -> Tuple[str, float]:
    """
    Classify intent using LLM (convenience function).

    Args:
        user_request: Natural language request

    Returns:
        Tuple of (intent, confidence)
    """
    client = LLMClient()
    result = client.classify_intent(user_request)
    return result.intent, result.confidence


def generate_plan_with_llm(
    intent: str,
    user_request: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate plan using LLM (convenience function).

    Args:
        intent: Classified intent
        user_request: Original user request
        context: Additional context

    Returns:
        Plan dictionary
    """
    client = LLMClient()
    result = client.generate_plan(intent, user_request, context)
    return result.dict()


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Example usage
    print("\n=== LLM Intent Classification Example ===\n")

    # Test requests
    test_requests = [
        "Create a new blog website with React",
        "Deploy my application to production",
        "Scale my API service to handle more traffic",
        "Delete the old test environment",
        "What's the status of my deployment?",
    ]

    client = LLMClient()

    for request in test_requests:
        print(f"Request: {request}")
        try:
            result = client.classify_intent(request)
            print(f"  Intent: {result.intent}")
            print(f"  Confidence: {result.confidence:.2f}")
            print(f"  Reasoning: {result.reasoning}")
            print()
        except Exception as e:
            print(f"  Error: {e}\n")

    # Test plan generation
    print("\n=== LLM Plan Generation Example ===\n")
    request = "Create a blog website"
    print(f"Request: {request}\n")
    try:
        classification = client.classify_intent(request)
        plan = client.generate_plan(
            intent=classification.intent,
            user_request=request,
            context={"available_regions": ["us-central1", "us-east1"]}
        )
        print(f"Plan Steps:")
        for i, step in enumerate(plan.plan_steps, 1):
            print(f"  {i}. {step}")
        print(f"\nEstimated Duration: {plan.estimated_duration_seconds}s")
        print(f"Risk Level: {plan.risk_level}")
        if plan.warnings:
            print(f"Warnings: {', '.join(plan.warnings)}")
    except Exception as e:
        print(f"Error: {e}")
