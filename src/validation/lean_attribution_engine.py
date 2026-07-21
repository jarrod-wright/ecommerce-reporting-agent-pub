"""
Lean Attribution Analysis Engine (Chunk 3.2.4)
Implements lightweight feature attribution for insight explainability
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
import polars as pl


@dataclass
class AttributionResult:
    """Result of feature attribution analysis"""
    feature_importance: Dict[str, float]
    top_features: List[Tuple[str, float]]
    attribution_explanation: str
    confidence_score: float


class LeanAttributionEngine:
    """Lightweight attribution engine using gradient-based methods"""

    def __init__(self):
        self.max_features = 5
        self.performance_threshold = 0.1  # 10% overhead limit

    def analyze_feature_importance(self,
                                 data: pl.DataFrame,
                                 target_metric: str,
                                 features: Optional[List[str]] = None) -> AttributionResult:
        """Analyze feature importance for target metric"""

        if features is None:
            features = [col for col in data.columns if col != target_metric]

        # Simple correlation-based attribution (faster than SHAP)
        importance_scores = {}
        target_values = data[target_metric].to_numpy()

        for feature in features:
            try:
                feature_values = data[feature].to_numpy()
                if len(feature_values) > 1 and np.var(feature_values) > 0:
                    correlation = np.corrcoef(feature_values, target_values)[0, 1]
                    importance_scores[feature] = abs(correlation) if not np.isnan(correlation) else 0.0
                else:
                    importance_scores[feature] = 0.0
            except:
                importance_scores[feature] = 0.0

        # Get top features
        sorted_features = sorted(importance_scores.items(), key=lambda x: x[1], reverse=True)
        top_features = sorted_features[:self.max_features]

        # Generate explanation
        explanation = self._generate_attribution_explanation(top_features)

        # Calculate confidence based on feature importance distribution
        confidence = self._calculate_attribution_confidence(importance_scores)

        return AttributionResult(
            feature_importance=importance_scores,
            top_features=top_features,
            attribution_explanation=explanation,
            confidence_score=confidence
        )

    def _generate_attribution_explanation(self, top_features: List[Tuple[str, float]]) -> str:
        """Generate human-readable attribution explanation"""
        if not top_features:
            return "No significant feature attributions found."

        explanations = []
        for feature, importance in top_features[:3]:  # Top 3 features
            percentage = importance * 100
            if importance > 0.5:
                strength = "strongly"
            elif importance > 0.3:
                strength = "moderately"
            else:
                strength = "weakly"

            explanations.append(f"{feature} {strength} influences the outcome ({percentage:.1f}%)")

        return "Key attributions: " + ", ".join(explanations)

    def _calculate_attribution_confidence(self, importance_scores: Dict[str, float]) -> float:
        """Calculate confidence in attribution results"""
        scores = list(importance_scores.values())
        if not scores:
            return 0.0

        # Higher confidence when there are clear dominant features
        max_score = max(scores)
        score_variance = np.var(scores) if len(scores) > 1 else 0

        # Confidence increases with max score and score variance
        confidence = min(max_score + score_variance * 0.5, 1.0)
        return confidence

    def validate_attribution_accuracy(self,
                                    attribution_result: AttributionResult,
                                    ground_truth_features: List[str]) -> float:
        """Validate attribution accuracy against known ground truth"""
        predicted_features = [feature for feature, _ in attribution_result.top_features]

        # Calculate overlap with ground truth
        correct_predictions = len(set(predicted_features) & set(ground_truth_features))
        total_predictions = len(predicted_features)

        if total_predictions == 0:
            return 0.0

        return correct_predictions / total_predictions
