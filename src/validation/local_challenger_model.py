"""
Local Challenger Model Integration (Chunk 3.2.1)
Implements independent validation using Llama 3.1 8B via Ollama
"""
import asyncio
import json
import logging
import time
from typing import Any, Dict, List

import httpx
from pydantic import BaseModel, Field, field_validator

# Configure logging
logger = logging.getLogger(__name__)


class ChallengerResponse(BaseModel):
    """Structured response from challenger model validation"""

    logical_consistency_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Score for logical consistency of reasoning"
    )
    factual_accuracy_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Score for factual accuracy of claims"
    )
    evidence_support_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Score for how well evidence supports conclusions"
    )
    overall_confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall confidence in the insight"
    )
    requires_human_review: bool = Field(
        default=False,
        description="Whether insight requires human review"
    )
    concerns: List[str] = Field(
        default_factory=list,
        description="List of specific concerns identified"
    )
    validation_reasoning: str = Field(
        default="",
        description="Explanation of validation decision"
    )

    @field_validator('requires_human_review')
    @classmethod
    def check_human_review_threshold(cls, v, info):
        """Auto-flag for human review if confidence is low"""
        if info.data and 'overall_confidence' in info.data and info.data['overall_confidence'] < 0.7:
            return True
        return v


class InsightValidationResult(ChallengerResponse):
    """Alias for backward compatibility"""
    pass


class OllamaClient:
    """Client for interacting with Ollama API"""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def generate(self, model: str, prompt: str) -> Dict[str, Any]:
        """Generate response from Ollama model"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise

    async def list_models(self) -> Dict[str, Any]:
        """List available models"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to list Ollama models: {e}")
            raise

    async def pull_model(self, model: str) -> bool:
        """Pull model if not available"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/pull",
                json={"name": model}
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to pull model {model}: {e}")
            return False


class LocalChallengerModel:
    """Local Challenger Model for independent insight validation"""

    def __init__(self, model_name: str = "llama3.1:8b"):
        self.model_name = model_name
        self.is_initialized = False
        self.client = OllamaClient()
        self._initialization_time = None

    async def initialize(self) -> None:
        """Initialize the challenger model"""
        start_time = time.time()

        try:
            # Check if model is available
            models_response = await self.client.list_models()
            available_models = [model['name'] for model in models_response.get('models', [])]

            if self.model_name not in available_models:
                logger.info(f"Model {self.model_name} not found. Attempting to pull...")
                success = await self.client.pull_model(self.model_name)
                if not success:
                    raise Exception(f"Failed to pull model {self.model_name}")

            # Test basic functionality
            test_response = await self.generate_response("Test prompt. Respond with 'OK'.")
            if not test_response:
                raise Exception("Model failed basic response test")

            self.is_initialized = True
            self._initialization_time = time.time() - start_time
            logger.info(f"Challenger model initialized in {self._initialization_time:.2f} seconds")

        except Exception as e:
            logger.error(f"Failed to initialize challenger model: {e}")
            raise

    async def generate_response(self, prompt: str) -> str:
        """Generate basic response from the model"""
        if not self.is_initialized:
            raise RuntimeError("Model not initialized. Call initialize() first.")

        try:
            response = await self.client.generate(self.model_name, prompt)
            return response.get('response', '')
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return ""

    async def _generate_raw_response(self, prompt: str) -> str:
        """Generate raw response with timeout handling"""
        try:
            return await asyncio.wait_for(
                self.generate_response(prompt),
                timeout=2.0
            )
        except asyncio.TimeoutError:
            logger.warning("Challenger response timed out")
            raise

    async def validate_insight(self, insight: Dict[str, Any]) -> InsightValidationResult:
        """Validate an ERA insight for consistency and accuracy"""
        if not self.is_initialized:
            await self.initialize()

        validation_prompt = self._create_validation_prompt(insight)

        try:
            raw_response = await self._generate_raw_response(validation_prompt)
            return self._parse_validation_response(raw_response, insight)

        except asyncio.TimeoutError:
            # Return fallback response on timeout
            return InsightValidationResult(
                logical_consistency_score=0.0,
                factual_accuracy_score=0.0,
                evidence_support_score=0.0,
                overall_confidence=0.0,
                requires_human_review=True,
                concerns=["Validation timed out"],
                validation_reasoning="Unable to validate due to timeout"
            )
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return InsightValidationResult(
                logical_consistency_score=0.0,
                factual_accuracy_score=0.0,
                evidence_support_score=0.0,
                overall_confidence=0.0,
                requires_human_review=True,
                concerns=[f"Validation error: {str(e)}"],
                validation_reasoning="Validation failed due to error"
            )

    def _create_validation_prompt(self, insight: Dict[str, Any]) -> str:
        """Create structured validation prompt for the challenger"""
        insight_text = insight.get('insight', '')
        evidence = insight.get('evidence', [])
        reasoning = insight.get('reasoning', '')

        prompt = f"""
You are an expert business analyst tasked with validating AI-generated insights.

INSIGHT TO VALIDATE:
{insight_text}

SUPPORTING EVIDENCE:
{', '.join(evidence) if isinstance(evidence, list) else evidence}

REASONING PROVIDED:
{reasoning}

Please analyze this insight and provide scores (0.0 to 1.0) for:

1. LOGICAL_CONSISTENCY: Does the reasoning logically follow from the evidence?
2. FACTUAL_ACCURACY: Are the claims factually consistent with the evidence?
3. EVIDENCE_SUPPORT: How well does the evidence support the conclusion?

Also identify any CONCERNS and provide overall CONFIDENCE (0.0 to 1.0).

Respond in this exact JSON format:
{{
    "logical_consistency_score": 0.0,
    "factual_accuracy_score": 0.0,
    "evidence_support_score": 0.0,
    "overall_confidence": 0.0,
    "concerns": [],
    "validation_reasoning": ""
}}
"""
        return prompt

    def _parse_validation_response(self, raw_response: str, original_insight: Dict[str, Any]) -> InsightValidationResult:
        """Parse challenger response into structured format"""
        try:
            # Try to extract JSON from response
            start_idx = raw_response.find('{')
            end_idx = raw_response.rfind('}') + 1

            if start_idx != -1 and end_idx > start_idx:
                json_str = raw_response[start_idx:end_idx]
                response_data = json.loads(json_str)

                # Ensure all required fields are present
                response_data.setdefault('logical_consistency_score', 0.5)
                response_data.setdefault('factual_accuracy_score', 0.5)
                response_data.setdefault('evidence_support_score', 0.5)
                response_data.setdefault('overall_confidence', 0.5)
                response_data.setdefault('concerns', [])
                response_data.setdefault('validation_reasoning', 'Parsed from model response')

                # Additional validation logic
                self._apply_validation_heuristics(response_data, original_insight)

                return InsightValidationResult(**response_data)
            else:
                raise ValueError("No valid JSON found in response")

        except Exception as e:
            logger.error(f"Failed to parse validation response: {e}")
            # Return conservative fallback
            return InsightValidationResult(
                logical_consistency_score=0.3,
                factual_accuracy_score=0.3,
                evidence_support_score=0.3,
                overall_confidence=0.3,
                requires_human_review=True,
                concerns=["Failed to parse validation response"],
                validation_reasoning="Fallback validation due to parsing error"
            )

    def _apply_validation_heuristics(self, response_data: Dict[str, Any], original_insight: Dict[str, Any]):
        """Apply additional validation heuristics"""
        insight_text = original_insight.get('insight', '').lower()
        evidence = original_insight.get('evidence', [])
        reasoning = original_insight.get('reasoning', '').lower()

        # Check for obvious inconsistencies
        if 'decrease' in insight_text and 'increase' in reasoning:
            response_data['concerns'].append('Inconsistency between insight and reasoning')
            response_data['factual_accuracy_score'] = min(response_data['factual_accuracy_score'], 0.4)

        # Check evidence quality
        if not evidence or (isinstance(evidence, list) and len(evidence) < 2):
            response_data['concerns'].append('Insufficient evidence provided')
            response_data['evidence_support_score'] = min(response_data['evidence_support_score'], 0.5)

        # Check for overconfident language
        overconfident_terms = ['definitely', 'certainly', 'will', 'guarantee']
        if any(term in insight_text for term in overconfident_terms):
            response_data['concerns'].append('Overconfident language detected')
            response_data['logical_consistency_score'] = min(response_data['logical_consistency_score'], 0.6)

        # Recalculate overall confidence based on individual scores
        scores = [
            response_data['logical_consistency_score'],
            response_data['factual_accuracy_score'],
            response_data['evidence_support_score']
        ]
        response_data['overall_confidence'] = sum(scores) / len(scores)
