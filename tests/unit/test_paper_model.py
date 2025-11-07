"""
Unit tests for the Paper model.
"""
import pytest
from datetime import datetime
from fetchers.base import Paper


class TestPaper:
    """Test cases for the Paper class."""

    def test_paper_creation_with_required_fields(self):
        """Test creating a Paper with only required fields."""
        paper = Paper(
            title="Test Paper",
            authors=["Author One", "Author Two"],
            abstract="This is a test abstract.",
            url="https://example.com/paper",
            published_date=datetime(2024, 1, 1),
            source="test"
        )

        assert paper.title == "Test Paper"
        assert paper.authors == ["Author One", "Author Two"]
        assert paper.abstract == "This is a test abstract."
        assert paper.url == "https://example.com/paper"
        assert paper.published_date == datetime(2024, 1, 1)
        assert paper.source == "test"

    def test_paper_creation_with_all_fields(self):
        """Test creating a Paper with all optional fields."""
        paper = Paper(
            title="Complete Paper",
            authors=["Author One"],
            abstract="Complete abstract.",
            url="https://example.com/paper",
            published_date=datetime(2024, 1, 1),
            source="arxiv",
            paper_id="custom-id",
            arxiv_id="2401.00001",
            doi="10.1234/test",
            citations=100,
            venue="NeurIPS 2024",
            pdf_url="https://example.com/paper.pdf",
            keywords=["test", "paper"]
        )

        assert paper.title == "Complete Paper"
        assert paper.paper_id == "custom-id"
        assert paper.arxiv_id == "2401.00001"
        assert paper.doi == "10.1234/test"
        assert paper.citations == 100
        assert paper.venue == "NeurIPS 2024"
        assert paper.pdf_url == "https://example.com/paper.pdf"
        assert paper.keywords == ["test", "paper"]

    def test_paper_id_defaults_to_url(self):
        """Test that paper_id defaults to url when not provided."""
        paper = Paper(
            title="Test",
            authors=["Author"],
            abstract="Abstract",
            url="https://example.com/unique",
            published_date=datetime(2024, 1, 1),
            source="test"
        )

        assert paper.paper_id == "https://example.com/unique"

    def test_keywords_defaults_to_empty_list(self):
        """Test that keywords defaults to empty list when not provided."""
        paper = Paper(
            title="Test",
            authors=["Author"],
            abstract="Abstract",
            url="https://example.com/paper",
            published_date=datetime(2024, 1, 1),
            source="test"
        )

        assert paper.keywords == []

    def test_paper_initial_computed_fields(self):
        """Test that computed fields are initialized to None or 0."""
        paper = Paper(
            title="Test",
            authors=["Author"],
            abstract="Abstract",
            url="https://example.com/paper",
            published_date=datetime(2024, 1, 1),
            source="test"
        )

        assert paper.summary is None
        assert paper.contributions is None
        assert paper.social_score == 0.0
        assert paper.relevance_score == 0.0

    def test_paper_to_dict(self):
        """Test converting Paper to dictionary."""
        published_date = datetime(2024, 1, 1, 12, 0, 0)
        paper = Paper(
            title="Test Paper",
            authors=["Author One", "Author Two"],
            abstract="Test abstract",
            url="https://example.com/paper",
            published_date=published_date,
            source="arxiv",
            paper_id="paper123",
            arxiv_id="2401.00001",
            doi="10.1234/test",
            citations=50,
            venue="Test Venue",
            pdf_url="https://example.com/paper.pdf",
            keywords=["test", "paper"]
        )

        paper_dict = paper.to_dict()

        assert paper_dict['title'] == "Test Paper"
        assert paper_dict['authors'] == ["Author One", "Author Two"]
        assert paper_dict['abstract'] == "Test abstract"
        assert paper_dict['url'] == "https://example.com/paper"
        assert paper_dict['published_date'] == published_date.isoformat()
        assert paper_dict['source'] == "arxiv"
        assert paper_dict['paper_id'] == "paper123"
        assert paper_dict['arxiv_id'] == "2401.00001"
        assert paper_dict['doi'] == "10.1234/test"
        assert paper_dict['citations'] == 50
        assert paper_dict['venue'] == "Test Venue"
        assert paper_dict['pdf_url'] == "https://example.com/paper.pdf"
        assert paper_dict['keywords'] == ["test", "paper"]
        assert paper_dict['summary'] is None
        assert paper_dict['contributions'] is None
        assert paper_dict['social_score'] == 0.0
        assert paper_dict['relevance_score'] == 0.0

    def test_paper_to_dict_with_computed_fields(self):
        """Test to_dict includes computed fields when set."""
        paper = Paper(
            title="Test",
            authors=["Author"],
            abstract="Abstract",
            url="https://example.com/paper",
            published_date=datetime(2024, 1, 1),
            source="test"
        )

        paper.summary = "Test summary"
        paper.contributions = ["Contribution 1", "Contribution 2"]
        paper.social_score = 5.5
        paper.relevance_score = 0.85

        paper_dict = paper.to_dict()

        assert paper_dict['summary'] == "Test summary"
        assert paper_dict['contributions'] == ["Contribution 1", "Contribution 2"]
        assert paper_dict['social_score'] == 5.5
        assert paper_dict['relevance_score'] == 0.85

    def test_paper_repr(self):
        """Test Paper string representation."""
        paper = Paper(
            title="This is a very long title that should be truncated in the repr",
            authors=["Author"],
            abstract="Abstract",
            url="https://example.com/paper",
            published_date=datetime(2024, 1, 1),
            source="arxiv"
        )

        repr_str = repr(paper)

        assert "Paper(title=" in repr_str
        assert "source='arxiv'" in repr_str
        assert len(paper.title) > 50  # Original title is long
        assert "..." in repr_str  # Truncated

    def test_paper_repr_short_title(self):
        """Test Paper repr with short title."""
        paper = Paper(
            title="Short",
            authors=["Author"],
            abstract="Abstract",
            url="https://example.com/paper",
            published_date=datetime(2024, 1, 1),
            source="test"
        )

        repr_str = repr(paper)

        assert "Paper(title='Short" in repr_str
        assert "source='test'" in repr_str

    def test_paper_citations_default(self):
        """Test citations defaults to 0."""
        paper = Paper(
            title="Test",
            authors=["Author"],
            abstract="Abstract",
            url="https://example.com/paper",
            published_date=datetime(2024, 1, 1),
            source="test"
        )

        assert paper.citations == 0

    def test_paper_with_empty_authors_list(self):
        """Test Paper can be created with empty authors list."""
        paper = Paper(
            title="Test",
            authors=[],
            abstract="Abstract",
            url="https://example.com/paper",
            published_date=datetime(2024, 1, 1),
            source="test"
        )

        assert paper.authors == []

    def test_paper_with_long_abstract(self):
        """Test Paper handles long abstracts."""
        long_abstract = "This is a very long abstract. " * 100
        paper = Paper(
            title="Test",
            authors=["Author"],
            abstract=long_abstract,
            url="https://example.com/paper",
            published_date=datetime(2024, 1, 1),
            source="test"
        )

        assert paper.abstract == long_abstract
        assert len(paper.abstract) > 1000
