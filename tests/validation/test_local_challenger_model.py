"""
Tests for Local Challenger Model Integration (Chunk 3.2.1)
TDD Implementation following Red-Green-Refactor cycle
"""
import asyncio
from unittest.mock import patch

import httpx
import pytest

from validation.local_challenger_model import (
    ChallengerResponse,
    InsightValidationResult,
    LocalChallengerModel,
)


def ollama_service_available():
    """Check if Ollama service is available at localhost:11434"""
    try:
        with httpx.Client(timeout=2.0) as client:
            response = client.get("http://localhost:11434/api/tags")
            return response.status_code == 200
    except (httpx.ConnectError, httpx.TimeoutException):
        return False


# Skip tests if Ollama service is not available
skip_if_no_ollama = pytest.mark.skipif(
    not ollama_service_available(),
    reason="Ollama service not available at localhost:11434"
)


class TestLocalChallengerModelInitialization:
    """Test suite for Local Challenger Model initialization"""

    def test_challenger_model_initialization(self):
        """Challenger model loads and responds correctly"""
        # RED: This should fail initially - implementation doesn't exist yet
        challenger = LocalChallengerModel()
        assert challenger is not None
        assert challenger.model_name == "llama3.1:8b"
        assert challenger.is_initialized is False

    @skip_if_no_ollama
    @pytest.mark.asyncio
    async def test_challenger_model_startup(self):
        """Test challenger model startup and health check"""
        challenger = LocalChallengerModel()

        # Should complete initialization within 30 seconds
        start_time = asyncio.get_event_loop().time()
        await challenger.initialize()
        end_time = asyncio.get_event_loop().time()

        assert end_time - start_time < 30.0
        assert challenger.is_initialized is True

    @skip_if_no_ollama
    @pytest.mark.asyncio
    async def test_challenger_basic_response(self):
        """Test basic prompt response capability"""
        challenger = LocalChallengerModel()
        await challenger.initialize()

        response = await challenger.generate_response("What is 2+2?")
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0


class TestChallengerInsightValidation:
    """Test suite for insight validation functionality"""

    @skip_if_no_ollama
    @pytest.mark.asyncio
    async def test_challenger_insight_validation(self):
        """Challenger can evaluate ERA insights for logical consistency"""
        challenger = LocalChallengerModel()
        await challenger.initialize()

        sample_insight = {
            "insight": "Revenue shows 15% monthly growth trend",
            "evidence": ["Month 1: $10,000", "Month 2: $11,500", "Month 3: $13,225"],
            "reasoning": "Consistent month-over-month growth pattern observed"
        }

        validation_result = await challenger.validate_insight(sample_insight)

        assert isinstance(validation_result, InsightValidationResult)
        assert validation_result.logical_consistency_score is not None
        assert 0.0 <= validation_result.logical_consistency_score <= 1.0
        assert validation_result.factual_accuracy_score is not None
        assert validation_result.evidence_support_score is not None

    @skip_if_no_ollama
    @pytest.mark.asyncio
    async def test_challenger_confidence_scoring(self):
        """Challenger returns structured confidence scores"""
        challenger = LocalChallengerModel()
        await challenger.initialize()

        high_quality_insight = {
            "insight": "Strong positive revenue correlation with marketing spend",
            "evidence": ["Q1 Marketing: $5K, Revenue: $50K", "Q2 Marketing: $7K, Revenue: $68K"],
            "reasoning": "Linear relationship observed with R²=0.89"
        }

        result = await challenger.validate_insight(high_quality_insight)

        # Should return structured confidence scores
        assert hasattr(result, 'logical_consistency_score')
        assert hasattr(result, 'factual_accuracy_score')
        assert hasattr(result, 'evidence_support_score')
        assert hasattr(result, 'overall_confidence')

        # Response should be within 2 seconds
        start_time = asyncio.get_event_loop().time()
        await challenger.validate_insight(high_quality_insight)
        end_time = asyncio.get_event_loop().time()
        assert end_time - start_time < 2.0

    @skip_if_no_ollama
    @pytest.mark.asyncio
    async def test_challenger_flags_low_confidence_insights(self):
        """Challenger flags insights with confidence below 0.7 threshold"""
        challenger = LocalChallengerModel()
        await challenger.initialize()

        poor_insight = {
            "insight": "Revenue will definitely increase next month",
            "evidence": ["Last month was good"],
            "reasoning": "I have a feeling"
        }

        result = await challenger.validate_insight(poor_insight)

        # Should flag low confidence
        assert result.overall_confidence < 0.7
        assert result.requires_human_review is True
        assert len(result.concerns) > 0

    @skip_if_no_ollama
    @pytest.mark.asyncio
    async def test_challenger_validates_factual_consistency(self):
        """Challenger identifies factual inconsistencies in insights"""
        challenger = LocalChallengerModel()
        await challenger.initialize()

        inconsistent_insight = {
            "insight": "Revenue decreased by 50%",
            "evidence": ["Jan: $1000", "Feb: $1500", "Mar: $2000"],
            "reasoning": "Significant decline observed"
        }

        result = await challenger.validate_insight(inconsistent_insight)

        # Should detect the inconsistency
        assert result.factual_accuracy_score < 0.5
        assert "inconsistency" in result.concerns[0].lower()


class TestChallengerResponseParsing:
    """Test suite for structured response parsing"""

    def test_challenger_response_model_validation(self):
        """Test ChallengerResponse model structure"""
        response_data = {
            "logical_consistency_score": 0.85,
            "factual_accuracy_score": 0.90,
            "evidence_support_score": 0.80,
            "overall_confidence": 0.85,
            "requires_human_review": False,
            "concerns": [],
            "validation_reasoning": "Insight is well-supported by evidence"
        }

        response = ChallengerResponse(**response_data)
        assert response.logical_consistency_score == 0.85
        assert response.overall_confidence == 0.85
        assert response.requires_human_review is False

    def test_challenger_response_validation_rules(self):
        """Test response model validation constraints"""
        # Should reject invalid confidence scores
        with pytest.raises(ValueError):
            ChallengerResponse(
                logical_consistency_score=1.5,  # Invalid - above 1.0
                factual_accuracy_score=0.9,
                evidence_support_score=0.8,
                overall_confidence=0.9
            )

        with pytest.raises(ValueError):
            ChallengerResponse(
                logical_consistency_score=-0.1,  # Invalid - below 0.0
                factual_accuracy_score=0.9,
                evidence_support_score=0.8,
                overall_confidence=0.9
            )


class TestChallengerPerformance:
    """Test suite for performance requirements"""

    @skip_if_no_ollama
    @pytest.mark.asyncio
    async def test_challenger_performance_benchmark(self):
        """Test challenger meets performance requirements"""
        challenger = LocalChallengerModel()
        await challenger.initialize()

        # Test multiple validations for performance consistency
        insights = [
            {"insight": f"Test insight {i}", "evidence": [f"Data point {i}"], "reasoning": f"Reasoning {i}"}
            for i in range(5)
        ]

        response_times = []
        for insight in insights:
            start_time = asyncio.get_event_loop().time()
            await challenger.validate_insight(insight)
            end_time = asyncio.get_event_loop().time()
            response_times.append(end_time - start_time)

        # All responses should be under 2 seconds
        assert all(time < 2.0 for time in response_times)

        # Average response time should be reasonable
        avg_time = sum(response_times) / len(response_times)
        assert avg_time < 1.5  # Average under 1.5 seconds


class TestChallengerIntegration:
    """Integration tests for challenger model with existing systems"""

    @skip_if_no_ollama
    @pytest.mark.asyncio
    async def test_challenger_integration_with_validation_pipeline(self):
        """Test integration with existing validation pipeline"""
        challenger = LocalChallengerModel()
        await challenger.initialize()

        # Should integrate with validation config
        from validation.validation_config_loader import ValidationConfigLoader
        config = ValidationConfigLoader()

        # Challenger should be configurable via validation config
        assert hasattr(config, 'challenger_settings')

    @pytest.mark.asyncio
    async def test_challenger_error_handling(self):
        """Test challenger handles errors gracefully"""
        challenger = LocalChallengerModel()

        # Should handle initialization failure gracefully
        with patch('validation.local_challenger_model.OllamaClient') as mock_client:
            mock_client.side_effect = Exception("Connection failed")

            with pytest.raises(Exception):
                await challenger.initialize()

            assert challenger.is_initialized is False

    @skip_if_no_ollama
    @pytest.mark.asyncio
    async def test_challenger_timeout_handling(self):
        """Test challenger handles timeouts appropriately"""
        challenger = LocalChallengerModel()
        await challenger.initialize()

        # Should timeout appropriately for slow responses
        with patch.object(challenger, '_generate_raw_response') as mock_generate:
            mock_generate.side_effect = asyncio.TimeoutError()

            result = await challenger.validate_insight({
                "insight": "Test",
                "evidence": ["Test"],
                "reasoning": "Test"
            })

            # Should return fallback response on timeout
            assert result.overall_confidence == 0.0
            assert result.requires_human_review is True
