"""Integration tests for Scrapy spiders.

These tests actually run the spiders with limited crawling to verify:
1. Spiders can start without errors
2. Settings are configured correctly
3. Pipelines work correctly
4. No deprecation warnings are raised
"""

import subprocess
from pathlib import Path

import pytest


class TestSpiderIntegration:
    """Integration tests for running spiders."""

    @pytest.fixture
    def project_root(self) -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent

    def test_quality_farm_supply_spider_runs_without_errors(
        self, project_root: Path, tmp_path: Path
    ):
        """Test that the quality_farm_supply spider can start without configuration errors.

        This test runs the spider with closespider_pagecount=1 to limit
        crawling to just one page, verifying that:
        - The spider starts successfully
        - Settings are valid (no CONCURRENT_REQUESTS_PER_IP error)
        - Pipelines don't raise errors on initialization
        - No critical warnings or errors occur during startup
        """
        output_file = tmp_path / "test_output.json"

        # Run the spider with limited pages to avoid long test times
        # Note: This may fail to crawl due to network restrictions but
        # should not fail due to configuration errors
        result = subprocess.run(
            [
                "python",
                "-m",
                "scrapy",
                "crawl",
                "quality_farm_supply",
                "-o",
                str(output_file),
                "-s",
                "CLOSESPIDER_PAGECOUNT=1",  # Limit to 1 page
                "-s",
                "LOG_LEVEL=INFO",
            ],
            cwd=project_root,
            capture_output=True,
            text=True,
        )

        # Combine stdout and stderr for checking
        output = result.stdout + "\n" + result.stderr
        output_lower = output.lower()

        # Check for critical configuration errors that should not happen
        assert "valueerror" not in output_lower or (
            "valueerror" in output_lower
            and "concurrent_requests_per_ip" not in output_lower
        ), (
            f"Spider raised ValueError about CONCURRENT_REQUESTS_PER_IP\n"
            f"Output: {output}"
        )

        # Should not have the CONCURRENT_REQUESTS_PER_IP error specifically
        assert (
            "does not support concurrent_requests_per_ip" not in output_lower
        ), f"CONCURRENT_REQUESTS_PER_IP error found\nOutput: {output}"

        # Should not have these critical errors at startup
        assert "scraper slot not assigned" not in output_lower, (
            "Scraper slot error (indicates startup failure)\n" f"Output: {output}"
        )
        assert "'scheduler' object has no attribute" not in output_lower, (
            "Scheduler attribute error (indicates startup failure)\n" f"Output: {output}"
        )
        assert "error caught on signal handler" not in output_lower, (
            "Signal handler error\n" f"Output: {output}"
        )

        # Should not have these deprecation warnings
        assert "concurrent_requests_per_ip setting is deprecated" not in output_lower, (
            "CONCURRENT_REQUESTS_PER_IP deprecation warning found\n" f"Output: {output}"
        )
        assert (
            "pipeline.process_item() requires a spider argument" not in output_lower
        ), f"Pipeline spider argument deprecation warning found\nOutput: {output}"
        assert (
            "pipeline.open_spider() requires a spider argument" not in output_lower
        ), f"Pipeline open_spider deprecation warning found\nOutput: {output}"
        assert (
            "pipeline.close_spider() requires a spider argument" not in output_lower
        ), f"Pipeline close_spider deprecation warning found\nOutput: {output}"

        # Check that spider opened successfully (indicates proper configuration)
        assert "spider opened" in output_lower, (
            f"Spider did not open successfully\nOutput: {output}"
        )

    def test_spider_list_command_works(self, project_root: Path):
        """Test that the 'scrapy list' command works and shows expected spiders."""
        result = subprocess.run(
            ["python", "-m", "scrapy", "list"],
            cwd=project_root,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"scrapy list failed: {result.stderr}"

        # Should list our spiders
        assert "quality_farm_supply" in result.stdout, (
            "quality_farm_supply spider not listed"
        )

    def test_spider_settings_no_deprecated_options(self, project_root: Path):
        """Test that spider settings don't use deprecated options."""
        from scrapers import settings

        # Check that deprecated setting is not present
        assert not hasattr(settings, "CONCURRENT_REQUESTS_PER_IP"), (
            "CONCURRENT_REQUESTS_PER_IP should not be in settings (deprecated)"
        )

        # Check that the non-deprecated alternative is present
        assert hasattr(settings, "CONCURRENT_REQUESTS_PER_DOMAIN"), (
            "CONCURRENT_REQUESTS_PER_DOMAIN should be in settings"
        )

    def test_pipelines_use_modern_api(self, project_root: Path):
        """Test that pipelines use the modern Scrapy API (from_crawler)."""
        from scrapers.pipelines import UnityCatalogWriterPipeline, ValidationPipeline

        # Both pipelines should have from_crawler classmethod
        assert hasattr(ValidationPipeline, "from_crawler"), (
            "ValidationPipeline should have from_crawler method"
        )
        assert hasattr(UnityCatalogWriterPipeline, "from_crawler"), (
            "UnityCatalogWriterPipeline should have from_crawler method"
        )

        # Check that from_crawler is a classmethod
        assert isinstance(
            ValidationPipeline.__dict__["from_crawler"], classmethod
        ), "ValidationPipeline.from_crawler should be a classmethod"

        assert isinstance(
            UnityCatalogWriterPipeline.__dict__["from_crawler"], classmethod
        ), "UnityCatalogWriterPipeline.from_crawler should be a classmethod"
