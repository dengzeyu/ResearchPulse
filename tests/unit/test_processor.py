"""
Unit tests for the PaperProcessor class.
"""
import pytest
from datetime import datetime, timedelta
from freezegun import freeze_time
from processor import PaperProcessor
from fetchers.base import Paper


class TestPaperProcessor:
    """Test cases for PaperProcessor."""

    @pytest.fixture
    def basic_config(self):
        """Basic processor configuration."""
        return {
            'filters': {
                'min_citations': 5,
                'exclude_keywords': ['quantum', 'biology']
            }
        }

    @pytest.fixture
    def tracking_config(self):
        """Tracking configuration for relevance scoring."""
        return {
            'keywords': [
                {'terms': ['machine learning', 'deep learning']},
                {'terms': ['neural networks', 'transformers']}
            ],
            'authors': [
                {'name': 'Geoffrey Hinton'},
                {'name': 'Yann LeCun'}
            ]
        }

    def test_processor_initialization(self, basic_config):
        """Test PaperProcessor initialization."""
        processor = PaperProcessor(basic_config)

        assert processor.config == basic_config
        assert processor.min_citations == 5
        assert processor.exclude_keywords == ['quantum', 'biology']

    def test_processor_initialization_with_defaults(self):
        """Test PaperProcessor with empty config uses defaults."""
        processor = PaperProcessor({})

        assert processor.min_citations == 5
        assert processor.exclude_keywords == []

    def test_deduplicate_by_paper_id(self):
        """Test deduplication by paper_id."""
        config = {'filters': {}}
        processor = PaperProcessor(config)

        papers = [
            Paper("Title 1", ["Author"], "Abstract", "http://url1.com",
                  datetime.now(), "test", paper_id="paper1"),
            Paper("Title 2", ["Author"], "Abstract", "http://url2.com",
                  datetime.now(), "test", paper_id="paper1"),  # Duplicate
            Paper("Title 3", ["Author"], "Abstract", "http://url3.com",
                  datetime.now(), "test", paper_id="paper2"),
        ]

        unique = processor.deduplicate(papers)

        assert len(unique) == 2
        assert unique[0].title == "Title 1"
        assert unique[1].title == "Title 3"

    def test_deduplicate_by_arxiv_id(self):
        """Test deduplication by arxiv_id."""
        config = {'filters': {}}
        processor = PaperProcessor(config)

        papers = [
            Paper("Title 1", ["Author"], "Abstract", "http://url1.com",
                  datetime.now(), "arxiv", paper_id="p1", arxiv_id="2401.00001"),
            Paper("Title 2", ["Author"], "Abstract", "http://url2.com",
                  datetime.now(), "arxiv", paper_id="p2", arxiv_id="2401.00001"),  # Duplicate
            Paper("Title 3", ["Author"], "Abstract", "http://url3.com",
                  datetime.now(), "arxiv", paper_id="p3", arxiv_id="2401.00002"),
        ]

        unique = processor.deduplicate(papers)

        assert len(unique) == 2
        assert unique[0].arxiv_id == "2401.00001"
        assert unique[1].arxiv_id == "2401.00002"

    def test_deduplicate_by_doi(self):
        """Test deduplication by DOI."""
        config = {'filters': {}}
        processor = PaperProcessor(config)

        papers = [
            Paper("Title 1", ["Author"], "Abstract", "http://url1.com",
                  datetime.now(), "test", paper_id="p1", doi="10.1234/test1"),
            Paper("Title 2", ["Author"], "Abstract", "http://url2.com",
                  datetime.now(), "test", paper_id="p2", doi="10.1234/test1"),  # Duplicate
            Paper("Title 3", ["Author"], "Abstract", "http://url3.com",
                  datetime.now(), "test", paper_id="p3", doi="10.1234/test2"),
        ]

        unique = processor.deduplicate(papers)

        assert len(unique) == 2
        assert unique[0].doi == "10.1234/test1"
        assert unique[1].doi == "10.1234/test2"

    def test_deduplicate_by_normalized_title(self):
        """Test deduplication by normalized title."""
        config = {'filters': {}}
        processor = PaperProcessor(config)

        papers = [
            Paper("Attention Is All You Need", ["Author"], "Abstract", "http://url1.com",
                  datetime.now(), "test", paper_id="p1"),
            Paper("Attention is all you need!", ["Author"], "Abstract", "http://url2.com",
                  datetime.now(), "test", paper_id="p2"),  # Duplicate (normalized)
            Paper("Different Title", ["Author"], "Abstract", "http://url3.com",
                  datetime.now(), "test", paper_id="p3"),
        ]

        unique = processor.deduplicate(papers)

        assert len(unique) == 2
        assert unique[0].paper_id == "p1"
        assert unique[1].paper_id == "p3"

    def test_normalize_title(self):
        """Test title normalization."""
        config = {'filters': {}}
        processor = PaperProcessor(config)

        assert processor._normalize_title("Attention Is All You Need") == "attention is all you need"
        assert processor._normalize_title("BERT: Pre-training...") == "bert pretraining"
        assert processor._normalize_title("  Multiple   Spaces  ") == "multiple spaces"
        assert processor._normalize_title("Special@#$Chars!!!") == "specialchars"

    def test_filter_papers_by_excluded_keywords(self, basic_config):
        """Test filtering papers with excluded keywords."""
        processor = PaperProcessor(basic_config)

        papers = [
            Paper("Machine Learning Paper", ["Author"], "Abstract about ML", "http://url1.com",
                  datetime.now(), "test"),
            Paper("Quantum Computing Paper", ["Author"], "Abstract about quantum", "http://url2.com",
                  datetime.now(), "test"),  # Should be filtered
            Paper("Biology Research", ["Author"], "Abstract", "http://url3.com",
                  datetime.now(), "test"),  # Should be filtered
        ]

        filtered = processor.filter_papers(papers)

        assert len(filtered) == 1
        assert filtered[0].title == "Machine Learning Paper"

    @freeze_time("2024-01-15")
    def test_filter_papers_by_citations_recent(self, basic_config):
        """Test that recent papers (< 7 days) are not filtered by citations."""
        processor = PaperProcessor(basic_config)

        recent_date = datetime(2024, 1, 10)  # 5 days ago
        papers = [
            Paper("Recent Paper", ["Author"], "Abstract", "http://url1.com",
                  recent_date, "test", citations=0),  # Should NOT be filtered (recent)
        ]

        filtered = processor.filter_papers(papers)

        assert len(filtered) == 1

    @freeze_time("2024-01-15")
    def test_filter_papers_by_citations_old_low(self, basic_config):
        """Test that old papers with low citations are filtered."""
        processor = PaperProcessor(basic_config)

        old_date = datetime(2024, 1, 1)  # 14 days ago
        papers = [
            Paper("Old Paper Low Citations", ["Author"], "Abstract", "http://url1.com",
                  old_date, "test", citations=3),  # Should be filtered (old + low citations)
        ]

        filtered = processor.filter_papers(papers)

        assert len(filtered) == 0

    @freeze_time("2024-01-15")
    def test_filter_papers_by_citations_old_high(self, basic_config):
        """Test that old papers with high citations are not filtered."""
        processor = PaperProcessor(basic_config)

        old_date = datetime(2024, 1, 1)  # 14 days ago
        papers = [
            Paper("Old Paper High Citations", ["Author"], "Abstract", "http://url1.com",
                  old_date, "test", citations=100),  # Should NOT be filtered (high citations)
        ]

        filtered = processor.filter_papers(papers)

        assert len(filtered) == 1

    def test_contains_excluded_keywords(self, basic_config):
        """Test excluded keyword detection."""
        processor = PaperProcessor(basic_config)

        assert processor._contains_excluded_keywords("Quantum Computing", "Abstract") is True
        assert processor._contains_excluded_keywords("Title", "Biology research") is True
        assert processor._contains_excluded_keywords("Machine Learning", "Abstract") is False
        assert processor._contains_excluded_keywords("Title", "No excluded words") is False

    def test_calculate_relevance_keyword_in_title(self, tracking_config):
        """Test relevance calculation with keyword in title."""
        config = {'filters': {}}
        processor = PaperProcessor(config)

        paper = Paper("Machine Learning Paper", ["Author"], "Abstract", "http://url.com",
                      datetime.now(), "test")

        score = processor._calculate_relevance(paper, tracking_config)

        assert score >= 5.0  # Title match gives 5 points

    def test_calculate_relevance_keyword_in_abstract(self, tracking_config):
        """Test relevance calculation with keyword in abstract."""
        config = {'filters': {}}
        processor = PaperProcessor(config)

        paper = Paper("Paper Title", ["Author"], "Abstract about deep learning", "http://url.com",
                      datetime.now(), "test")

        score = processor._calculate_relevance(paper, tracking_config)

        assert score >= 2.0  # Abstract match gives 2 points

    def test_calculate_relevance_tracked_author(self, tracking_config):
        """Test relevance calculation with tracked author."""
        config = {'filters': {}}
        processor = PaperProcessor(config)

        paper = Paper("Paper Title", ["Geoffrey Hinton", "Other Author"], "Abstract", "http://url.com",
                      datetime.now(), "test")

        score = processor._calculate_relevance(paper, tracking_config)

        assert score >= 10.0  # Author match gives 10 points

    @freeze_time("2024-01-15 12:00:00")
    def test_calculate_relevance_recent_paper_boost(self, tracking_config):
        """Test that very recent papers get a relevance boost."""
        config = {'filters': {}}
        processor = PaperProcessor(config)

        # Paper from yesterday (1 day old)
        recent_paper = Paper("Machine Learning", ["Author"], "Abstract", "http://url.com",
                            datetime(2024, 1, 14, 12, 0, 0), "test")

        # Paper from 10 days ago
        old_paper = Paper("Machine Learning", ["Author"], "Abstract", "http://url2.com",
                         datetime(2024, 1, 5, 12, 0, 0), "test")

        recent_score = processor._calculate_relevance(recent_paper, tracking_config)
        old_score = processor._calculate_relevance(old_paper, tracking_config)

        # Recent paper should have higher score due to 1.5x boost
        assert recent_score > old_score

    def test_rank_papers_by_relevance(self, tracking_config):
        """Test ranking papers by relevance score."""
        config = {'filters': {}}
        processor = PaperProcessor(config)

        papers = [
            Paper("Unrelated Paper", ["Author"], "Abstract", "http://url1.com",
                  datetime.now(), "test", citations=100),
            Paper("Machine Learning Research", ["Author"], "Abstract", "http://url2.com",
                  datetime.now(), "test", citations=50),
            Paper("Paper by Geoffrey Hinton", ["Geoffrey Hinton"], "Abstract", "http://url3.com",
                  datetime.now(), "test", citations=75),
        ]

        ranked = processor.rank_papers(papers, {}, tracking_config)

        # Paper by tracked author should be ranked highest
        assert "Geoffrey Hinton" in ranked[0].authors
        # Paper with ML keyword should be second
        assert "Machine Learning" in ranked[1].title

    def test_rank_papers_with_social_signals(self, tracking_config):
        """Test ranking papers with social signals."""
        config = {'filters': {}}
        processor = PaperProcessor(config)

        papers = [
            Paper("Paper A", ["Author"], "Abstract", "http://url1.com",
                  datetime.now(), "test", paper_id="paper1"),
            Paper("Paper B", ["Author"], "Abstract", "http://url2.com",
                  datetime.now(), "test", paper_id="paper2"),
        ]

        social_signals = {
            'paper1': {'total_score': 0.0},
            'paper2': {'total_score': 10.0}  # High social engagement
        }

        ranked = processor.rank_papers(papers, social_signals, tracking_config)

        assert ranked[0].paper_id == "paper2"  # Higher social score
        assert ranked[0].social_score == 10.0

    def test_rank_papers_combined_score(self, tracking_config):
        """Test that combined score uses weighted formula."""
        config = {'filters': {}}
        processor = PaperProcessor(config)

        paper = Paper("Machine Learning", ["Author"], "Abstract", "http://url.com",
                     datetime.now(), "test", paper_id="paper1", citations=1000)

        social_signals = {'paper1': {'total_score': 5.0}}

        ranked = processor.rank_papers([paper], social_signals, tracking_config)

        # Check combined score calculation
        expected_score = (
            ranked[0].relevance_score * 0.6 +
            5.0 * 0.3 +
            (1000 / 100.0) * 0.1
        )
        assert ranked[0].combined_score == pytest.approx(expected_score)

    def test_merge_social_signals(self):
        """Test merging social signals into papers."""
        config = {'filters': {}}
        processor = PaperProcessor(config)

        papers = [
            Paper("Paper A", ["Author"], "Abstract", "http://url1.com",
                  datetime.now(), "test", paper_id="paper1"),
            Paper("Paper B", ["Author"], "Abstract", "http://url2.com",
                  datetime.now(), "test", paper_id="paper2"),
        ]

        social_signals = {
            'paper1': {
                'total_score': 8.5,
                'reddit_mentions': 5,
                'github_stars': 100
            }
        }

        processor.merge_social_signals(papers, social_signals)

        assert papers[0].social_score == 8.5
        assert papers[0].social_signals == social_signals['paper1']
        assert papers[1].social_score == 0.0  # No signals

    def test_get_top_papers(self):
        """Test getting top N papers."""
        config = {'filters': {}}
        processor = PaperProcessor(config)

        papers = [
            Paper(f"Paper {i}", ["Author"], "Abstract", f"http://url{i}.com",
                  datetime.now(), "test")
            for i in range(100)
        ]

        top_10 = processor.get_top_papers(papers, limit=10)
        top_50 = processor.get_top_papers(papers, limit=50)

        assert len(top_10) == 10
        assert len(top_50) == 50
        assert top_10[0].title == "Paper 0"

    def test_deduplicate_empty_list(self):
        """Test deduplication with empty list."""
        config = {'filters': {}}
        processor = PaperProcessor(config)

        unique = processor.deduplicate([])

        assert len(unique) == 0

    def test_filter_papers_empty_list(self, basic_config):
        """Test filtering with empty list."""
        processor = PaperProcessor(basic_config)

        filtered = processor.filter_papers([])

        assert len(filtered) == 0

    def test_rank_papers_empty_list(self, tracking_config):
        """Test ranking with empty list."""
        config = {'filters': {}}
        processor = PaperProcessor(config)

        ranked = processor.rank_papers([], {}, tracking_config)

        assert len(ranked) == 0
