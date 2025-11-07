"""
Unit tests for the SemanticScholarFetcher class.
"""
import pytest
import responses
from datetime import datetime
from freezegun import freeze_time
from fetchers.semantic_scholar_fetcher import SemanticScholarFetcher


class TestSemanticScholarFetcher:
    """Test cases for SemanticScholarFetcher."""

    @pytest.fixture
    def basic_config(self):
        """Basic configuration for SemanticScholarFetcher."""
        return {
            'filters': {
                'max_age_days': 30
            }
        }

    def test_semantic_scholar_fetcher_initialization(self, basic_config):
        """Test SemanticScholarFetcher initialization."""
        fetcher = SemanticScholarFetcher(basic_config)

        assert fetcher.max_age_days == 30
        assert fetcher.BASE_URL == "https://api.semanticscholar.org/graph/v1"

    @freeze_time("2024-01-15")
    @responses.activate
    def test_fetch_by_keywords(self, basic_config):
        """Test fetching papers by keywords."""
        # Mock API response
        responses.add(
            responses.GET,
            "https://api.semanticscholar.org/graph/v1/paper/search",
            json={
                'data': [
                    {
                        'paperId': 'paper123',
                        'title': 'Test Paper',
                        'authors': [{'name': 'Author One'}, {'name': 'Author Two'}],
                        'abstract': 'Test abstract',
                        'publicationDate': '2024-01-10',
                        'citationCount': 50,
                        'venue': 'NeurIPS 2024',
                        'externalIds': {
                            'ArXiv': '2401.00001',
                            'DOI': '10.1234/test'
                        }
                    }
                ]
            },
            status=200
        )

        fetcher = SemanticScholarFetcher(basic_config)
        papers = fetcher.fetch_by_keywords(["machine learning"], max_results=50)

        assert len(papers) == 1
        assert papers[0].title == "Test Paper"
        assert papers[0].authors == ["Author One", "Author Two"]
        assert papers[0].abstract == "Test abstract"
        assert papers[0].arxiv_id == "2401.00001"
        assert papers[0].doi == "10.1234/test"
        assert papers[0].citations == 50
        assert papers[0].venue == "NeurIPS 2024"
        assert papers[0].source == "semantic_scholar"

    @freeze_time("2024-01-15")
    @responses.activate
    def test_fetch_by_keywords_filters_old_papers(self, basic_config):
        """Test that old papers are filtered out."""
        responses.add(
            responses.GET,
            "https://api.semanticscholar.org/graph/v1/paper/search",
            json={
                'data': [
                    {
                        'paperId': 'paper1',
                        'title': 'Recent Paper',
                        'authors': [{'name': 'Author'}],
                        'abstract': 'Abstract',
                        'publicationDate': '2024-01-10',
                        'citationCount': 10,
                        'venue': 'Test',
                        'externalIds': {}
                    },
                    {
                        'paperId': 'paper2',
                        'title': 'Old Paper',
                        'authors': [{'name': 'Author'}],
                        'abstract': 'Abstract',
                        'publicationDate': '2023-01-01',
                        'citationCount': 100,
                        'venue': 'Test',
                        'externalIds': {}
                    }
                ]
            },
            status=200
        )

        fetcher = SemanticScholarFetcher(basic_config)
        papers = fetcher.fetch_by_keywords(["test"], max_results=50)

        assert len(papers) == 1
        assert papers[0].title == "Recent Paper"

    @freeze_time("2024-01-15")
    @responses.activate
    def test_fetch_by_keywords_skips_no_date(self, basic_config):
        """Test that papers without publication date are skipped."""
        responses.add(
            responses.GET,
            "https://api.semanticscholar.org/graph/v1/paper/search",
            json={
                'data': [
                    {
                        'paperId': 'paper1',
                        'title': 'No Date Paper',
                        'authors': [{'name': 'Author'}],
                        'abstract': 'Abstract',
                        'publicationDate': None,
                        'citationCount': 10,
                        'venue': 'Test',
                        'externalIds': {}
                    }
                ]
            },
            status=200
        )

        fetcher = SemanticScholarFetcher(basic_config)
        papers = fetcher.fetch_by_keywords(["test"], max_results=50)

        assert len(papers) == 0

    @freeze_time("2024-01-15")
    @responses.activate
    def test_fetch_by_author(self, basic_config):
        """Test fetching papers by author."""
        # Mock author search response
        responses.add(
            responses.GET,
            "https://api.semanticscholar.org/graph/v1/author/search",
            json={
                'data': [
                    {'authorId': 'author123', 'name': 'Geoffrey Hinton'}
                ]
            },
            status=200
        )

        # Mock author papers response
        responses.add(
            responses.GET,
            "https://api.semanticscholar.org/graph/v1/author/author123/papers",
            json={
                'data': [
                    {
                        'paperId': 'paper123',
                        'title': "Author's Paper",
                        'authors': [{'name': 'Geoffrey Hinton'}],
                        'abstract': 'Test abstract',
                        'publicationDate': '2024-01-10',
                        'citationCount': 100,
                        'venue': 'NeurIPS',
                        'externalIds': {'ArXiv': '2401.00001'}
                    }
                ]
            },
            status=200
        )

        fetcher = SemanticScholarFetcher(basic_config)
        papers = fetcher.fetch_by_author("Geoffrey Hinton", max_results=50)

        assert len(papers) == 1
        assert papers[0].title == "Author's Paper"
        assert "Geoffrey Hinton" in papers[0].authors

    @responses.activate
    def test_fetch_by_author_not_found(self, basic_config):
        """Test fetching papers when author is not found."""
        responses.add(
            responses.GET,
            "https://api.semanticscholar.org/graph/v1/author/search",
            json={'data': []},
            status=200
        )

        fetcher = SemanticScholarFetcher(basic_config)
        papers = fetcher.fetch_by_author("Unknown Author", max_results=50)

        assert len(papers) == 0

    @freeze_time("2024-01-15")
    @responses.activate
    def test_fetch_by_citation(self, basic_config):
        """Test fetching papers that cite a given paper."""
        responses.add(
            responses.GET,
            "https://api.semanticscholar.org/graph/v1/paper/paper123/citations",
            json={
                'data': [
                    {
                        'citingPaper': {
                            'paperId': 'citing1',
                            'title': 'Citing Paper',
                            'authors': [{'name': 'Author'}],
                            'abstract': 'Abstract',
                            'publicationDate': '2024-01-10',
                            'citationCount': 5,
                            'venue': 'Test',
                            'externalIds': {}
                        }
                    }
                ]
            },
            status=200
        )

        fetcher = SemanticScholarFetcher(basic_config)
        papers = fetcher.fetch_by_citation("paper123", max_results=50)

        assert len(papers) == 1
        assert papers[0].title == "Citing Paper"
        assert papers[0].paper_id == "citing1"

    @responses.activate
    def test_fetch_by_keywords_error_handling(self, basic_config):
        """Test error handling in fetch_by_keywords."""
        responses.add(
            responses.GET,
            "https://api.semanticscholar.org/graph/v1/paper/search",
            json={'error': 'API Error'},
            status=500
        )

        fetcher = SemanticScholarFetcher(basic_config)
        papers = fetcher.fetch_by_keywords(["test"], max_results=50)

        # Should return empty list on error
        assert papers == []

    @responses.activate
    def test_fetch_by_author_error_handling(self, basic_config):
        """Test error handling in fetch_by_author."""
        responses.add(
            responses.GET,
            "https://api.semanticscholar.org/graph/v1/author/search",
            json={'error': 'API Error'},
            status=500
        )

        fetcher = SemanticScholarFetcher(basic_config)
        papers = fetcher.fetch_by_author("Author", max_results=50)

        # Should return empty list on error
        assert papers == []

    @responses.activate
    def test_fetch_by_citation_error_handling(self, basic_config):
        """Test error handling in fetch_by_citation."""
        responses.add(
            responses.GET,
            "https://api.semanticscholar.org/graph/v1/paper/paper123/citations",
            json={'error': 'API Error'},
            status=500
        )

        fetcher = SemanticScholarFetcher(basic_config)
        papers = fetcher.fetch_by_citation("paper123", max_results=50)

        # Should return empty list on error
        assert papers == []

    @freeze_time("2024-01-15")
    @responses.activate
    def test_fetch_by_keywords_no_arxiv_id(self, basic_config):
        """Test fetching paper without arXiv ID."""
        responses.add(
            responses.GET,
            "https://api.semanticscholar.org/graph/v1/paper/search",
            json={
                'data': [
                    {
                        'paperId': 'paper123',
                        'title': 'Test Paper',
                        'authors': [{'name': 'Author'}],
                        'abstract': 'Abstract',
                        'publicationDate': '2024-01-10',
                        'citationCount': 10,
                        'venue': 'Test',
                        'externalIds': {}  # No arXiv ID
                    }
                ]
            },
            status=200
        )

        fetcher = SemanticScholarFetcher(basic_config)
        papers = fetcher.fetch_by_keywords(["test"], max_results=50)

        assert len(papers) == 1
        assert papers[0].arxiv_id is None
        assert papers[0].doi is None

    @freeze_time("2024-01-15")
    @responses.activate
    def test_fetch_by_keywords_empty_results(self, basic_config):
        """Test fetching with no results."""
        responses.add(
            responses.GET,
            "https://api.semanticscholar.org/graph/v1/paper/search",
            json={'data': []},
            status=200
        )

        fetcher = SemanticScholarFetcher(basic_config)
        papers = fetcher.fetch_by_keywords(["nonexistent"], max_results=50)

        assert papers == []

    def test_max_age_days_default(self):
        """Test that max_age_days defaults to 30 when not specified."""
        config = {}
        fetcher = SemanticScholarFetcher(config)

        assert fetcher.max_age_days == 30

    @freeze_time("2024-01-15")
    @responses.activate
    def test_fetch_by_citation_skips_no_date(self, basic_config):
        """Test that citing papers without dates are skipped."""
        responses.add(
            responses.GET,
            "https://api.semanticscholar.org/graph/v1/paper/paper123/citations",
            json={
                'data': [
                    {
                        'citingPaper': {
                            'paperId': 'citing1',
                            'title': 'Citing Paper',
                            'authors': [{'name': 'Author'}],
                            'abstract': 'Abstract',
                            'publicationDate': None,
                            'citationCount': 5,
                            'venue': 'Test',
                            'externalIds': {}
                        }
                    }
                ]
            },
            status=200
        )

        fetcher = SemanticScholarFetcher(basic_config)
        papers = fetcher.fetch_by_citation("paper123", max_results=50)

        assert len(papers) == 0
