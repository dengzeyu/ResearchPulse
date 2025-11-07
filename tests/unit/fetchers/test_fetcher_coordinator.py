"""
Unit tests for the FetcherCoordinator class.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

# Skip all tests if arxiv is not installed (optional dependency)
pytest.importorskip("arxiv", reason="arxiv package not installed")

from fetchers.coordinator import FetcherCoordinator
from fetchers.base import Paper


class TestFetcherCoordinator:
    """Test cases for FetcherCoordinator."""

    @pytest.fixture
    def tracking_config(self):
        """Sample tracking configuration."""
        return {
            'keywords': [
                {
                    'area': 'Machine Learning',
                    'terms': ['machine learning', 'deep learning'],
                    'sources': ['arxiv', 'semantic_scholar']
                },
                {
                    'area': 'NLP',
                    'terms': ['natural language processing'],
                    'sources': ['arxiv']
                }
            ],
            'authors': [
                {'name': 'Geoffrey Hinton'},
                {'name': 'Yann LeCun'}
            ],
            'key_papers': [
                {
                    'title': 'Attention Is All You Need',
                    'arxiv_id': '1706.03762'
                }
            ]
        }

    @patch('fetchers.coordinator.ArxivFetcher')
    @patch('fetchers.coordinator.SemanticScholarFetcher')
    def test_coordinator_initialization(self, mock_ss_fetcher, mock_arxiv_fetcher, tracking_config):
        """Test FetcherCoordinator initialization."""
        coordinator = FetcherCoordinator(tracking_config)

        assert coordinator.tracking_config == tracking_config
        assert 'arxiv' in coordinator.fetchers
        assert 'semantic_scholar' in coordinator.fetchers

    @patch('fetchers.coordinator.ArxivFetcher')
    @patch('fetchers.coordinator.SemanticScholarFetcher')
    def test_fetch_all_papers_by_keywords(self, mock_ss_fetcher_class, mock_arxiv_fetcher_class, tracking_config):
        """Test fetching papers by keywords from multiple sources."""
        # Setup mock fetchers
        mock_arxiv = Mock()
        mock_ss = Mock()
        mock_arxiv_fetcher_class.return_value = mock_arxiv
        mock_ss_fetcher_class.return_value = mock_ss

        # Create sample papers
        arxiv_paper = Paper(
            "ArXiv Paper", ["Author"], "Abstract", "http://arxiv.com/1",
            datetime.now(), "arxiv", paper_id="arxiv1"
        )
        ss_paper = Paper(
            "SS Paper", ["Author"], "Abstract", "http://ss.com/1",
            datetime.now(), "semantic_scholar", paper_id="ss1"
        )

        mock_arxiv.fetch_by_keywords.return_value = [arxiv_paper]
        mock_arxiv.fetch_by_author.return_value = []
        mock_ss.fetch_by_keywords.return_value = [ss_paper]
        mock_ss.fetch_by_author.return_value = []
        mock_ss.fetch_by_citation.return_value = []

        coordinator = FetcherCoordinator(tracking_config)
        papers = coordinator.fetch_all_papers()

        # Should have called fetch_by_keywords for each keyword group
        assert mock_arxiv.fetch_by_keywords.call_count >= 2
        assert mock_ss.fetch_by_keywords.call_count >= 1

    @patch('fetchers.coordinator.ArxivFetcher')
    @patch('fetchers.coordinator.SemanticScholarFetcher')
    def test_fetch_all_papers_by_authors(self, mock_ss_fetcher_class, mock_arxiv_fetcher_class, tracking_config):
        """Test fetching papers by authors."""
        # Setup mock fetchers
        mock_arxiv = Mock()
        mock_ss = Mock()
        mock_arxiv_fetcher_class.return_value = mock_arxiv
        mock_ss_fetcher_class.return_value = mock_ss

        # Create sample papers
        author_paper = Paper(
            "Author Paper", ["Geoffrey Hinton"], "Abstract", "http://url.com",
            datetime.now(), "arxiv", paper_id="paper1"
        )

        mock_arxiv.fetch_by_keywords.return_value = []
        mock_arxiv.fetch_by_author.return_value = [author_paper]
        mock_ss.fetch_by_keywords.return_value = []
        mock_ss.fetch_by_author.return_value = []
        mock_ss.fetch_by_citation.return_value = []

        coordinator = FetcherCoordinator(tracking_config)
        papers = coordinator.fetch_all_papers()

        # Should have called fetch_by_author for each author
        assert mock_arxiv.fetch_by_author.call_count == 2  # 2 authors
        assert mock_ss.fetch_by_author.call_count == 2

    @patch('fetchers.coordinator.ArxivFetcher')
    @patch('fetchers.coordinator.SemanticScholarFetcher')
    def test_fetch_all_papers_by_citations(self, mock_ss_fetcher_class, mock_arxiv_fetcher_class, tracking_config):
        """Test fetching papers by citations to key papers."""
        # Setup mock fetchers
        mock_arxiv = Mock()
        mock_ss = Mock()
        mock_arxiv_fetcher_class.return_value = mock_arxiv
        mock_ss_fetcher_class.return_value = mock_ss

        # Create sample papers
        citing_paper = Paper(
            "Citing Paper", ["Author"], "Abstract", "http://url.com",
            datetime.now(), "semantic_scholar", paper_id="citing1"
        )

        mock_arxiv.fetch_by_keywords.return_value = []
        mock_arxiv.fetch_by_author.return_value = []
        mock_ss.fetch_by_keywords.return_value = []
        mock_ss.fetch_by_author.return_value = []
        mock_ss.fetch_by_citation.return_value = [citing_paper]

        coordinator = FetcherCoordinator(tracking_config)
        papers = coordinator.fetch_all_papers()

        # Should have called fetch_by_citation for key papers
        assert mock_ss.fetch_by_citation.call_count == 1
        mock_ss.fetch_by_citation.assert_called_with("arXiv:1706.03762", max_results=30)

    @patch('fetchers.coordinator.ArxivFetcher')
    @patch('fetchers.coordinator.SemanticScholarFetcher')
    def test_fetch_all_papers_aggregates_results(self, mock_ss_fetcher_class, mock_arxiv_fetcher_class, tracking_config):
        """Test that all papers are aggregated from different sources."""
        # Setup mock fetchers
        mock_arxiv = Mock()
        mock_ss = Mock()
        mock_arxiv_fetcher_class.return_value = mock_arxiv
        mock_ss_fetcher_class.return_value = mock_ss

        # Create sample papers from different sources
        paper1 = Paper("Paper 1", ["Author"], "Abstract", "http://url1.com",
                      datetime.now(), "arxiv", paper_id="p1")
        paper2 = Paper("Paper 2", ["Author"], "Abstract", "http://url2.com",
                      datetime.now(), "semantic_scholar", paper_id="p2")
        paper3 = Paper("Paper 3", ["Author"], "Abstract", "http://url3.com",
                      datetime.now(), "arxiv", paper_id="p3")

        mock_arxiv.fetch_by_keywords.return_value = [paper1]
        mock_arxiv.fetch_by_author.return_value = [paper3]
        mock_ss.fetch_by_keywords.return_value = [paper2]
        mock_ss.fetch_by_author.return_value = []
        mock_ss.fetch_by_citation.return_value = []

        coordinator = FetcherCoordinator(tracking_config)
        papers = coordinator.fetch_all_papers()

        # Should aggregate papers from all sources
        assert len(papers) >= 3
        paper_ids = [p.paper_id for p in papers]
        assert "p1" in paper_ids
        assert "p2" in paper_ids
        assert "p3" in paper_ids

    @patch('fetchers.coordinator.ArxivFetcher')
    @patch('fetchers.coordinator.SemanticScholarFetcher')
    def test_fetch_all_papers_empty_config(self, mock_ss_fetcher_class, mock_arxiv_fetcher_class):
        """Test fetching with empty configuration."""
        config = {}

        mock_arxiv = Mock()
        mock_ss = Mock()
        mock_arxiv_fetcher_class.return_value = mock_arxiv
        mock_ss_fetcher_class.return_value = mock_ss

        mock_arxiv.fetch_by_keywords.return_value = []
        mock_arxiv.fetch_by_author.return_value = []
        mock_ss.fetch_by_keywords.return_value = []
        mock_ss.fetch_by_author.return_value = []
        mock_ss.fetch_by_citation.return_value = []

        coordinator = FetcherCoordinator(config)
        papers = coordinator.fetch_all_papers()

        assert papers == []

    @patch('fetchers.coordinator.ArxivFetcher')
    @patch('fetchers.coordinator.SemanticScholarFetcher')
    def test_fetch_all_papers_respects_source_config(self, mock_ss_fetcher_class, mock_arxiv_fetcher_class):
        """Test that only specified sources are used for each keyword group."""
        config = {
            'keywords': [
                {
                    'area': 'ML',
                    'terms': ['machine learning'],
                    'sources': ['arxiv']  # Only arxiv
                }
            ]
        }

        mock_arxiv = Mock()
        mock_ss = Mock()
        mock_arxiv_fetcher_class.return_value = mock_arxiv
        mock_ss_fetcher_class.return_value = mock_ss

        mock_arxiv.fetch_by_keywords.return_value = []
        mock_ss.fetch_by_keywords.return_value = []

        coordinator = FetcherCoordinator(config)
        coordinator.fetch_all_papers()

        # Should only call arxiv fetcher, not semantic scholar
        assert mock_arxiv.fetch_by_keywords.call_count == 1
        assert mock_ss.fetch_by_keywords.call_count == 0

    @patch('fetchers.coordinator.ArxivFetcher')
    @patch('fetchers.coordinator.SemanticScholarFetcher')
    def test_fetch_all_papers_ignores_unknown_sources(self, mock_ss_fetcher_class, mock_arxiv_fetcher_class):
        """Test that unknown sources in config are ignored."""
        config = {
            'keywords': [
                {
                    'area': 'ML',
                    'terms': ['machine learning'],
                    'sources': ['arxiv', 'unknown_source']
                }
            ]
        }

        mock_arxiv = Mock()
        mock_ss = Mock()
        mock_arxiv_fetcher_class.return_value = mock_arxiv
        mock_ss_fetcher_class.return_value = mock_ss

        mock_arxiv.fetch_by_keywords.return_value = []
        mock_ss.fetch_by_keywords.return_value = []

        coordinator = FetcherCoordinator(config)
        papers = coordinator.fetch_all_papers()

        # Should call arxiv but skip unknown_source
        assert mock_arxiv.fetch_by_keywords.call_count == 1

    @patch('fetchers.coordinator.ArxivFetcher')
    @patch('fetchers.coordinator.SemanticScholarFetcher')
    def test_fetch_all_papers_with_no_authors(self, mock_ss_fetcher_class, mock_arxiv_fetcher_class):
        """Test fetching with no authors configured."""
        config = {
            'keywords': [
                {'area': 'ML', 'terms': ['test'], 'sources': ['arxiv']}
            ]
        }

        mock_arxiv = Mock()
        mock_ss = Mock()
        mock_arxiv_fetcher_class.return_value = mock_arxiv
        mock_ss_fetcher_class.return_value = mock_ss

        mock_arxiv.fetch_by_keywords.return_value = []
        mock_arxiv.fetch_by_author.return_value = []
        mock_ss.fetch_by_author.return_value = []

        coordinator = FetcherCoordinator(config)
        coordinator.fetch_all_papers()

        # Should not call fetch_by_author if no authors configured
        assert mock_arxiv.fetch_by_author.call_count == 0
        assert mock_ss.fetch_by_author.call_count == 0

    @patch('fetchers.coordinator.ArxivFetcher')
    @patch('fetchers.coordinator.SemanticScholarFetcher')
    def test_fetch_all_papers_with_no_key_papers(self, mock_ss_fetcher_class, mock_arxiv_fetcher_class):
        """Test fetching with no key papers configured."""
        config = {
            'keywords': [
                {'area': 'ML', 'terms': ['test'], 'sources': ['arxiv']}
            ]
        }

        mock_arxiv = Mock()
        mock_ss = Mock()
        mock_arxiv_fetcher_class.return_value = mock_arxiv
        mock_ss_fetcher_class.return_value = mock_ss

        mock_arxiv.fetch_by_keywords.return_value = []
        mock_ss.fetch_by_keywords.return_value = []
        mock_ss.fetch_by_citation.return_value = []

        coordinator = FetcherCoordinator(config)
        coordinator.fetch_all_papers()

        # Should not call fetch_by_citation if no key papers configured
        assert mock_ss.fetch_by_citation.call_count == 0
