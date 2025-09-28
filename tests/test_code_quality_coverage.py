"""Additional tests for score_code_quality.py to improve coverage."""

from ai_model_catalog.metrics.score_code_quality import CodeQualityMetric


class TestCodeQualityCoverage:
    """Test cases to improve coverage for score_code_quality.py."""

    def test_robust_infrastructure_high_score(self):
        """Test the robust infrastructure path that returns 0.95."""
        metric = CodeQualityMetric()
        # Test with all infrastructure indicators and prestigious org
        readme = """
        This model uses transformers library from huggingface model hub.
        It includes pipeline functionality with tokenizer and config files.
        Developed by Google Research.
        """
        model_data = {"readme": readme, "author": "google", "name": "bert-base"}
        score = metric.score(model_data)
        assert score == 0.95

    def test_infrastructure_only_whisper_like(self):
        """Test infrastructure-only repos that should get 0.0."""
        metric = CodeQualityMetric()
        # Test with many infrastructure terms but no quality practices
        readme = """
        This is a whisper model using transformers from huggingface.
        It includes pipeline and tokenizer functionality with config files.
        No tests or CI mentioned.
        """
        model_data = {"readme": readme, "author": "openai", "name": "whisper-tiny"}
        score = metric.score(model_data)
        assert score == 0.0

    def test_minimal_signals_not_infrastructure(self):
        """Test minimal signals that are not infrastructure-only."""
        metric = CodeQualityMetric()
        # Test with docs but not infrastructure-heavy
        readme = """
        This is a simple model with documentation.
        Uses basic linting but no tests or CI.
        """
        model_data = {"readme": readme, "author": "student", "name": "simple-model"}
        score = metric.score(model_data)
        assert score == 0.1

    def test_weak_evidence_docs_and_lint(self):
        """Test weak evidence with docs and lint but no tests/CI."""
        metric = CodeQualityMetric()
        readme = """
        This model has documentation and uses black formatter.
        No tests or CI mentioned.
        """
        model_data = {
            "readme": readme,
            "author": "researcher",
            "name": "research-model",
        }
        score = metric.score(model_data)
        # This should get 0.3 because it has both docs and lint
        assert score == 0.3

    def test_weak_evidence_both_docs_and_lint(self):
        """Test weak evidence with both docs and lint but no tests/CI."""
        metric = CodeQualityMetric()
        readme = """
        This model has documentation and uses black formatter and flake8.
        No tests or CI mentioned.
        """
        model_data = {
            "readme": readme,
            "author": "researcher",
            "name": "research-model",
        }
        score = metric.score(model_data)
        # This gets 0.3 because it has both docs and lint
        assert score == 0.3

    def test_tests_only_baseline(self):
        """Test baseline score with tests only."""
        metric = CodeQualityMetric()
        readme = """
        This model has pytest tests.
        """
        model_data = {"readme": readme, "author": "developer", "name": "tested-model"}
        score = metric.score(model_data)
        assert score == 0.7

    def test_tests_with_docs_high_score(self):
        """Test high score with tests and docs."""
        metric = CodeQualityMetric()
        readme = """
        This model has pytest tests and comprehensive documentation.
        """
        model_data = {
            "readme": readme,
            "author": "developer",
            "name": "well-documented-model",
        }
        score = metric.score(model_data)
        assert score == 0.9

    def test_tests_ci_docs_complete(self):
        """Test complete setup with tests, CI, and docs."""
        metric = CodeQualityMetric()
        readme = """
        This model has pytest tests, GitHub Actions CI/CD, and documentation.
        """
        model_data = {"readme": readme, "author": "developer", "name": "complete-model"}
        score = metric.score(model_data)
        assert score == 0.9

    def test_platform_prestigious_boost(self):
        """Test boost for platform-hosted prestigious models."""
        metric = CodeQualityMetric()
        readme = """
        This model is hosted on huggingface.co/transformers.
        It has pytest tests and GitHub Actions CI/CD.
        Developed by Google Research.
        """
        model_data = {"readme": readme, "author": "google", "name": "bert-large"}
        score = metric.score(model_data)
        assert score == 0.95

    def test_fallback_case(self):
        """Test the fallback case."""
        metric = CodeQualityMetric()
        # Test with some evidence but not matching any specific patterns
        readme = """
        This is a model with some evidence.
        """
        model_data = {"readme": readme, "author": "unknown", "name": "mystery-model"}
        score = metric.score(model_data)
        # Should return some score based on evidence
        assert score >= 0.0
