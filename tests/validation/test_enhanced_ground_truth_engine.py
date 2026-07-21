"""
Tests for Enhanced Ground Truth Engine with Pattern Injection (Chunk 3.2.2)
TDD Implementation following Red-Green-Refactor cycle
"""
import polars as pl

from validation.enhanced_ground_truth_engine import (
    EnhancedGroundTruthEngine,
    GeneratedDataset,
    PatternType,
)


class TestEnhancedGroundTruthEngineInitialization:
    """Test suite for Enhanced Ground Truth Engine initialization"""

    def test_enhanced_gte_initialization(self):
        """Enhanced GTE initializes correctly"""
        # RED: This should fail initially - implementation doesn't exist yet
        gte = EnhancedGroundTruthEngine()
        assert gte is not None
        assert hasattr(gte, 'supported_patterns')
        assert PatternType.TREND_INJECTION in gte.supported_patterns
        assert PatternType.NO_SIGNAL in gte.supported_patterns
        assert PatternType.SEASONAL in gte.supported_patterns

    def test_gte_pattern_registry(self):
        """Test pattern registration and discovery"""
        gte = EnhancedGroundTruthEngine()

        # Should have pattern generators for each type
        assert hasattr(gte, 'pattern_generators')
        assert PatternType.TREND_INJECTION in gte.pattern_generators
        assert PatternType.NO_SIGNAL in gte.pattern_generators
        assert PatternType.SEASONAL in gte.pattern_generators


class TestTrendInjectionPattern:
    """Test suite for trend injection pattern generation"""

    def test_trend_injection_linear_growth(self):
        """TDG can inject linear revenue growth patterns"""
        gte = EnhancedGroundTruthEngine()

        pattern_config = {
            "pattern_type": PatternType.TREND_INJECTION,
            "trend_type": "linear",
            "growth_rate": 0.15,  # 15% monthly growth
            "baseline_revenue": 10000,
            "duration_months": 12,
            "noise_level": 0.05
        }

        dataset = gte.generate_dataset(pattern_config)

        assert isinstance(dataset, GeneratedDataset)
        assert dataset.metadata.pattern_type == PatternType.TREND_INJECTION
        assert dataset.metadata.expected_trend_detection is True
        assert abs(dataset.metadata.expected_growth_rate - 0.15) < 0.01

        # Verify actual trend in data
        revenue_data = dataset.data['revenue'].to_list()
        assert len(revenue_data) == 12

        # Check growth trend (allowing for noise)
        actual_growth_rates = []
        for i in range(1, len(revenue_data)):
            growth_rate = (revenue_data[i] - revenue_data[i-1]) / revenue_data[i-1]
            actual_growth_rates.append(growth_rate)

        avg_growth = sum(actual_growth_rates) / len(actual_growth_rates)
        assert abs(avg_growth - 0.15) < 0.05  # Within noise tolerance

    def test_trend_injection_exponential_growth(self):
        """Test exponential growth pattern injection"""
        gte = EnhancedGroundTruthEngine()

        pattern_config = {
            "pattern_type": PatternType.TREND_INJECTION,
            "trend_type": "exponential",
            "growth_rate": 0.20,
            "baseline_revenue": 5000,
            "duration_months": 6,
            "noise_level": 0.02
        }

        dataset = gte.generate_dataset(pattern_config)

        # Verify exponential characteristics
        revenue_data = dataset.data['revenue'].to_list()

        # Exponential should show increasing growth rates
        growth_rates = []
        for i in range(1, len(revenue_data)):
            growth_rate = (revenue_data[i] - revenue_data[i-1]) / revenue_data[i-1]
            growth_rates.append(growth_rate)

        # Later periods should have higher growth rates
        early_avg = sum(growth_rates[:2]) / 2
        late_avg = sum(growth_rates[-2:]) / 2
        assert late_avg > early_avg

    def test_pattern_metadata_preservation(self):
        """Generated data preserves pattern type and expected outcomes"""
        gte = EnhancedGroundTruthEngine()

        pattern_config = {
            "pattern_type": PatternType.TREND_INJECTION,
            "trend_type": "linear",
            "growth_rate": 0.10,
            "baseline_revenue": 8000,
            "duration_months": 8
        }

        dataset = gte.generate_dataset(pattern_config)

        # Verify metadata completeness
        assert dataset.metadata.pattern_type == PatternType.TREND_INJECTION
        assert dataset.metadata.expected_trend_detection is True
        assert dataset.metadata.expected_growth_rate == 0.10
        assert dataset.metadata.generation_timestamp is not None
        assert dataset.metadata.validation_criteria is not None
        assert 'trend_accuracy_threshold' in dataset.metadata.validation_criteria


class TestNoSignalPattern:
    """Test suite for no-signal pattern generation"""

    def test_no_signal_pattern_generation(self):
        """TDG can generate pure noise datasets"""
        gte = EnhancedGroundTruthEngine()

        pattern_config = {
            "pattern_type": PatternType.NO_SIGNAL,
            "baseline_revenue": 12000,
            "variance": 2000,
            "duration_months": 10,
            "random_seed": 42  # For reproducible testing
        }

        dataset = gte.generate_dataset(pattern_config)

        assert dataset.metadata.pattern_type == PatternType.NO_SIGNAL
        assert dataset.metadata.expected_trend_detection is False
        assert dataset.metadata.expected_pattern_confidence < 0.5

        # Verify data characteristics
        revenue_data = dataset.data['revenue'].to_list()

        # Should have no significant trend
        from scipy import stats
        months = list(range(len(revenue_data)))
        slope, intercept, r_value, p_value, std_err = stats.linregress(months, revenue_data)

        # R-squared should be very low (no correlation)
        r_squared = r_value ** 2
        assert r_squared < 0.1  # Less than 10% variance explained

    def test_no_signal_statistical_properties(self):
        """No-signal data has proper statistical properties"""
        gte = EnhancedGroundTruthEngine()

        pattern_config = {
            "pattern_type": PatternType.NO_SIGNAL,
            "baseline_revenue": 10000,
            "variance": 1500,
            "duration_months": 24,
            "random_seed": 123
        }

        dataset = gte.generate_dataset(pattern_config)
        revenue_data = dataset.data['revenue'].to_list()

        # Check mean and variance are approximately correct
        import statistics
        mean_revenue = statistics.mean(revenue_data)
        std_revenue = statistics.stdev(revenue_data)

        assert abs(mean_revenue - 10000) < 500  # Within reasonable bounds
        assert abs(std_revenue - 1500) < 300    # Within reasonable bounds

    def test_era_false_pattern_rejection(self):
        """ERA should not hallucinate patterns in no-signal data"""
        # This test will be implemented when ERA integration is complete
        # For now, we verify the data generation meets requirements
        gte = EnhancedGroundTruthEngine()

        pattern_config = {
            "pattern_type": PatternType.NO_SIGNAL,
            "baseline_revenue": 15000,
            "variance": 3000,
            "duration_months": 12
        }

        dataset = gte.generate_dataset(pattern_config)

        # Metadata should indicate no patterns expected
        assert dataset.metadata.expected_insights == []
        assert dataset.metadata.expected_pattern_confidence < 0.5


class TestSeasonalPattern:
    """Test suite for seasonal pattern injection"""

    def test_seasonal_pattern_injection(self):
        """Inject seasonal revenue spike pattern for Q4"""
        gte = EnhancedGroundTruthEngine()

        pattern_config = {
            "pattern_type": PatternType.SEASONAL,
            "baseline_revenue": 50000,
            "peak_months": [10, 11],  # November, December (0-indexed)
            "peak_multiplier": 2.5,   # 250% of baseline
            "duration_months": 12
        }

        dataset = gte.generate_dataset(pattern_config)

        assert dataset.metadata.pattern_type == PatternType.SEASONAL
        assert dataset.metadata.expected_seasonal_detection is True
        assert dataset.metadata.expected_peak_months == [10, 11]

        # Verify seasonal spikes
        revenue_data = dataset.data['revenue'].to_list()

        # November and December should be significantly higher
        nov_revenue = revenue_data[10]  # Month 11 (0-indexed)
        dec_revenue = revenue_data[11]  # Month 12 (0-indexed)
        baseline_months = [revenue_data[i] for i in range(12) if i not in [10, 11]]
        avg_baseline = sum(baseline_months) / len(baseline_months)

        assert nov_revenue > 2.0 * avg_baseline  # At least 2x baseline
        assert dec_revenue > 2.0 * avg_baseline  # At least 2x baseline

    def test_seasonal_pattern_with_multiple_peaks(self):
        """Test seasonal pattern with multiple peak periods"""
        gte = EnhancedGroundTruthEngine()

        pattern_config = {
            "pattern_type": PatternType.SEASONAL,
            "baseline_revenue": 30000,
            "peak_months": [4, 5, 10, 11],  # Summer (May, June) and Winter (Nov, Dec) peaks
            "peak_multiplier": 1.8,
            "duration_months": 12
        }

        dataset = gte.generate_dataset(pattern_config)
        revenue_data = dataset.data['revenue'].to_list()

        # All peak months should be elevated
        peak_revenues = [revenue_data[i] for i in [4, 5, 10, 11]]  # 0-indexed
        non_peak_revenues = [revenue_data[i] for i in range(12) if i not in [4, 5, 10, 11]]

        avg_peak = sum(peak_revenues) / len(peak_revenues)
        avg_non_peak = sum(non_peak_revenues) / len(non_peak_revenues)

        assert avg_peak > 1.5 * avg_non_peak  # Peak periods significantly higher

    def test_seasonal_metadata_completeness(self):
        """Seasonal pattern metadata includes all required fields"""
        gte = EnhancedGroundTruthEngine()

        pattern_config = {
            "pattern_type": PatternType.SEASONAL,
            "baseline_revenue": 40000,
            "peak_months": [11, 12],
            "peak_multiplier": 3.0,
            "duration_months": 12
        }

        dataset = gte.generate_dataset(pattern_config)

        # Verify comprehensive metadata
        assert hasattr(dataset.metadata, 'expected_seasonal_detection')
        assert hasattr(dataset.metadata, 'expected_peak_months')
        assert hasattr(dataset.metadata, 'expected_peak_multiplier')
        assert dataset.metadata.expected_insights is not None
        assert len(dataset.metadata.expected_insights) > 0

        # Should include specific seasonal insights
        insights = dataset.metadata.expected_insights
        seasonal_insight = next((i for i in insights if 'seasonal' in i.lower()), None)
        assert seasonal_insight is not None


class TestPatternValidationIntegration:
    """Test pattern validation and ERA integration"""

    def test_pattern_validation_criteria_generation(self):
        """Each pattern generates appropriate validation criteria"""
        gte = EnhancedGroundTruthEngine()

        patterns_to_test = [
            {
                "pattern_type": PatternType.TREND_INJECTION,
                "trend_type": "linear",
                "growth_rate": 0.12
            },
            {
                "pattern_type": PatternType.NO_SIGNAL,
                "baseline_revenue": 10000
            },
            {
                "pattern_type": PatternType.SEASONAL,
                "peak_months": [11, 12],
                "peak_multiplier": 2.0
            }
        ]

        for config in patterns_to_test:
            dataset = gte.generate_dataset(config)

            assert dataset.metadata.validation_criteria is not None
            assert isinstance(dataset.metadata.validation_criteria, dict)
            assert len(dataset.metadata.validation_criteria) > 0

    def test_dataset_era_compatibility(self):
        """Generated datasets are compatible with ERA input format"""
        gte = EnhancedGroundTruthEngine()

        pattern_config = {
            "pattern_type": PatternType.TREND_INJECTION,
            "trend_type": "linear",
            "growth_rate": 0.10,
            "baseline_revenue": 10000,
            "duration_months": 6
        }

        dataset = gte.generate_dataset(pattern_config)

        # Should generate proper eCommerce data structure
        required_columns = ['date', 'revenue', 'orders', 'sessions']
        for column in required_columns:
            assert column in dataset.data.columns

        # Data should be properly typed
        assert dataset.data['date'].dtype in [pl.Date, pl.Datetime]
        assert dataset.data['revenue'].dtype in [pl.Float64, pl.Float32, pl.Int64]

    def test_multi_metric_pattern_injection(self):
        """Patterns can be injected across multiple business metrics"""
        gte = EnhancedGroundTruthEngine()

        pattern_config = {
            "pattern_type": PatternType.TREND_INJECTION,
            "trend_type": "linear",
            "growth_rate": 0.08,
            "baseline_revenue": 8000,
            "duration_months": 8,
            "correlate_metrics": ["orders", "sessions"]  # Revenue growth should correlate
        }

        dataset = gte.generate_dataset(pattern_config)

        # All correlated metrics should show similar growth patterns
        revenue_data = dataset.data['revenue'].to_list()
        orders_data = dataset.data['orders'].to_list()

        # Calculate correlations
        from scipy.stats import pearsonr
        correlation, p_value = pearsonr(revenue_data, orders_data)

        assert correlation > 0.7  # Strong positive correlation
        assert p_value < 0.05     # Statistically significant
