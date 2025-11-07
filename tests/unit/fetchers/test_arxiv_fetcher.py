"""
Unit tests for the ArxivFetcher class.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
from freezegun import freeze_time
from fetchers.arxiv_fetcher import ArxivFetcher
from fetchers.base import Paper


class TestArxivFetcher:
    """Test cases for ArxivFetcher."""

    @pytest.fixture
    def basic_config(self):
        """Basic configuration for ArxivFetcher."""
        return {
            'filters': {
                'max_age_days': 30
            }
        }

    @patch('fetchers.arxiv_fetcher.arxiv.Client')
    def test_arxiv_fetcher_initialization(self, mock_client, basic_config):
        """Test ArxivFetcher initialization."""
        fetcher = ArxivFetcher(basic_config)

        assert fetcher.max_age_days == 30
        mock_client.assert_called_once()

    @freeze_time("2024-01-15")
    @patch('fetchers.arxiv_fetcher.arxiv.Client')
    @patch('fetchers.arxiv_fetcher.arxiv.Search')
    def test_fetch_by_keywords(self, mock_search, mock_client_class, basic_config):
        """Test fetching papers by keywords."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Create mock result
        mock_result = Mock()
        mock_result.title = "Test Paper"
        mock_result.authors = [Mock(name="Author One"), Mock(name="Author Two")]
        mock_result.summary = "Test abstract"
        mock_result.entry_id = "https://arxiv.org/abs/2401.00001"
        mock_result.published = datetime(2024, 1, 10)
        mock_result.pdf_url = "https://arxiv.org/pdf/2401.00001.pdf"
        mock_result.categories = ["cs.LG", "cs.AI"]

        mock_client.results.return_value = [mock_result]

        fetcher = ArxivFetcher(basic_config)
        papers = fetcher.fetch_by_keywords(["machine learning", "deep learning"], max_results=50)

        assert len(papers) == 1
        assert papers[0].title == "Test Paper"
        assert papers[0].authors == ["Author One", "Author Two"]
        assert papers[0].abstract == "Test abstract"
        assert papers[0].arxiv_id == "2401.00001"
        assert papers[0].source == "arxiv"
        assert papers[0].keywords == ["cs.LG", "cs.AI"]

    @freeze_time("2024-01-15")
    @patch('fetchers.arxiv_fetcher.arxiv.Client')
    @patch('fetchers.arxiv_fetcher.arxiv.Search')
    def test_fetch_by_keywords_filters_old_papers(self, mock_search, mock_client_class, basic_config):
        """Test that old papers are filtered out."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Create papers - one recent, one old
        recent_result = Mock()
        recent_result.title = "Recent Paper"
        recent_result.authors = [Mock(name="Author")]
        recent_result.summary = "Abstract"
        recent_result.entry_id = "https://arxiv.org/abs/2401.00001"
        recent_result.published = datetime(2024, 1, 10)  # 5 days ago
        recent_result.pdf_url = "https://arxiv.org/pdf/2401.00001.pdf"
        recent_result.categories = ["cs.LG"]

        old_result = Mock()
        old_result.title = "Old Paper"
        old_result.authors = [Mock(name="Author")]
        old_result.summary = "Abstract"
        old_result.entry_id = "https://arxiv.org/abs/2023.00001"
        old_result.published = datetime(2023, 1, 1)  # > 30 days ago
        old_result.pdf_url = "https://arxiv.org/pdf/2023.00001.pdf"
        old_result.categories = ["cs.LG"]

        mock_client.results.return_value = [recent_result, old_result]

        fetcher = ArxivFetcher(basic_config)
        papers = fetcher.fetch_by_keywords(["test"], max_results=50)

        assert len(papers) == 1
        assert papers[0].title == "Recent Paper"

    @patch('fetchers.arxiv_fetcher.arxiv.Client')
    @patch('fetchers.arxiv_fetcher.arxiv.Search')
    def test_fetch_by_keywords_query_format(self, mock_search, mock_client_class, basic_config):
        """Test that keywords are properly formatted in the query."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.results.return_value = []

        fetcher = ArxivFetcher(basic_config)
        fetcher.fetch_by_keywords(["machine learning", "deep learning"], max_results=50)

        # Verify Search was called with proper query
        call_args = mock_search.call_args
        assert '"machine learning" OR "deep learning"' in str(call_args)

    @freeze_time("2024-01-15")
    @patch('fetchers.arxiv_fetcher.arxiv.Client')
    @patch('fetchers.arxiv_fetcher.arxiv.Search')
    def test_fetch_by_author(self, mock_search, mock_client_class, basic_config):
        """Test fetching papers by author."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Create mock result
        mock_result = Mock()
        mock_result.title = "Author's Paper"
        mock_result.authors = [Mock(name="Geoffrey Hinton")]
        mock_result.summary = "Test abstract"
        mock_result.entry_id = "https://arxiv.org/abs/2401.00001"
        mock_result.published = datetime(2024, 1, 10)
        mock_result.pdf_url = "https://arxiv.org/pdf/2401.00001.pdf"
        mock_result.categories = ["cs.LG"]

        mock_client.results.return_value = [mock_result]

        fetcher = ArxivFetcher(basic_config)
        papers = fetcher.fetch_by_author("Geoffrey Hinton", max_results=50)

        assert len(papers) == 1
        assert papers[0].title == "Author's Paper"
        assert "Geoffrey Hinton" in papers[0].authors

    @patch('fetchers.arxiv_fetcher.arxiv.Client')
    @patch('fetchers.arxiv_fetcher.arxiv.Search')
    def test_fetch_by_author_query_format(self, mock_search, mock_client_class, basic_config):
        """Test that author query is properly formatted."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.results.return_value = []

        fetcher = ArxivFetcher(basic_config)
        fetcher.fetch_by_author("Geoffrey Hinton", max_results=50)

        # Verify Search was called with author query
        call_args = mock_search.call_args
        assert 'au:"Geoffrey Hinton"' in str(call_args)

    @patch('fetchers.arxiv_fetcher.arxiv.Client')
    @patch('fetchers.arxiv_fetcher.arxiv.Search')
    def test_fetch_by_keywords_error_handling(self, mock_search, mock_client_class, basic_config):
        """Test error handling in fetch_by_keywords."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.results.side_effect = Exception("API Error")

        fetcher = ArxivFetcher(basic_config)
        papers = fetcher.fetch_by_keywords(["test"], max_results=50)

        # Should return empty list on error
        assert papers == []

    @patch('fetchers.arxiv_fetcher.arxiv.Client')
    @patch('fetchers.arxiv_fetcher.arxiv.Search')
    def test_fetch_by_author_error_handling(self, mock_search, mock_client_class, basic_config):
        """Test error handling in fetch_by_author."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.results.side_effect = Exception("API Error")

        fetcher = ArxivFetcher(basic_config)
        papers = fetcher.fetch_by_author("Author Name", max_results=50)

        # Should return empty list on error
        assert papers == []

    @patch('fetchers.arxiv_fetcher.arxiv.Client')
    @patch('fetchers.arxiv_fetcher.arxiv.Search')
    def test_fetch_by_keywords_empty_results(self, mock_search, mock_client_class, basic_config):
        """Test fetching with no results."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.results.return_value = []

        fetcher = ArxivFetcher(basic_config)
        papers = fetcher.fetch_by_keywords(["nonexistent keyword"], max_results=50)

        assert papers == []

    def test_max_age_days_default(self):
        """Test that max_age_days defaults to 30 when not specified."""
        config = {}

        with patch('fetchers.arxiv_fetcher.arxiv.Client'):
            fetcher = ArxivFetcher(config)

        assert fetcher.max_age_days == 30

    @freeze_time("2024-01-15")
    @patch('fetchers.arxiv_fetcher.arxiv.Client')
    @patch('fetchers.arxiv_fetcher.arxiv.Search')
    def test_arxiv_id_extraction(self, mock_search, mock_client_class, basic_config):
        """Test that arXiv ID is properly extracted from entry_id."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_result = Mock()
        mock_result.title = "Test"
        mock_result.authors = [Mock(name="Author")]
        mock_result.summary = "Abstract"
        mock_result.entry_id = "https://arxiv.org/abs/2401.12345v2"  # With version
        mock_result.published = datetime(2024, 1, 10)
        mock_result.pdf_url = "https://arxiv.org/pdf/2401.12345.pdf"
        mock_result.categories = ["cs.LG"]

        mock_client.results.return_value = [mock_result]

        fetcher = ArxivFetcher(basic_config)
        papers = fetcher.fetch_by_keywords(["test"], max_results=50)

        assert papers[0].arxiv_id == "2401.12345v2"
