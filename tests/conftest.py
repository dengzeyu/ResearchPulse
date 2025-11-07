"""
Shared pytest fixtures for ResearchPulse tests.
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import pytest

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fetchers.base import Paper


@pytest.fixture
def sample_paper():
    """Create a sample Paper object for testing."""
    return Paper(
        title="Attention Is All You Need",
        authors=["Vaswani, Ashish", "Shazeer, Noam"],
        abstract="We propose a new simple network architecture based on attention mechanisms.",
        url="https://arxiv.org/abs/1706.03762",
        published_date=datetime(2017, 6, 12),
        source="arxiv",
        paper_id="paper123",
        arxiv_id="1706.03762",
        doi="10.48550/arXiv.1706.03762",
        citations=50000,
        venue="NeurIPS 2017",
        pdf_url="https://arxiv.org/pdf/1706.03762.pdf",
        keywords=["transformers", "attention", "neural networks"]
    )


@pytest.fixture
def sample_papers():
    """Create a list of sample Paper objects for testing."""
    return [
        Paper(
            title="Attention Is All You Need",
            authors=["Vaswani, Ashish"],
            abstract="We propose transformers.",
            url="https://arxiv.org/abs/1706.03762",
            published_date=datetime(2017, 6, 12),
            source="arxiv",
            paper_id="paper1",
            arxiv_id="1706.03762",
            citations=50000,
            keywords=["transformers"]
        ),
        Paper(
            title="BERT: Pre-training of Deep Bidirectional Transformers",
            authors=["Devlin, Jacob"],
            abstract="We introduce BERT for NLP tasks.",
            url="https://arxiv.org/abs/1810.04805",
            published_date=datetime(2018, 10, 11),
            source="arxiv",
            paper_id="paper2",
            arxiv_id="1810.04805",
            citations=40000,
            keywords=["bert", "nlp"]
        ),
        Paper(
            title="GPT-3: Language Models are Few-Shot Learners",
            authors=["Brown, Tom"],
            abstract="We show that scaling up language models improves performance.",
            url="https://arxiv.org/abs/2005.14165",
            published_date=datetime(2020, 5, 28),
            source="arxiv",
            paper_id="paper3",
            arxiv_id="2005.14165",
            citations=30000,
            keywords=["gpt", "language models"]
        )
    ]


@pytest.fixture
def recent_date():
    """Return a recent date (7 days ago)."""
    return datetime.now() - timedelta(days=7)


@pytest.fixture
def old_date():
    """Return an old date (2 years ago)."""
    return datetime.now() - timedelta(days=730)


@pytest.fixture
def sample_tracking_config():
    """Return a sample tracking configuration."""
    return {
        'keywords': ['machine learning', 'deep learning', 'neural networks'],
        'excluded_keywords': ['quantum', 'biology'],
        'min_citations': 10,
        'authors': ['Geoffrey Hinton', 'Yann LeCun'],
        'categories': ['cs.LG', 'cs.AI']
    }


@pytest.fixture
def sample_llm_config():
    """Return a sample LLM configuration."""
    return {
        'provider': 'anthropic',
        'model': 'claude-3-sonnet-20240229',
        'api_key': 'test-api-key',
        'temperature': 0.7,
        'max_tokens': 1024
    }


@pytest.fixture
def sample_social_config():
    """Return a sample social media configuration."""
    return {
        'reddit': {
            'enabled': True,
            'subreddits': ['MachineLearning', 'artificial'],
            'client_id': 'test-client-id',
            'client_secret': 'test-secret',
            'user_agent': 'test-agent'
        },
        'github': {
            'enabled': True,
            'token': 'test-token',
            'topics': ['machine-learning', 'deep-learning']
        }
    }


@pytest.fixture
def mock_paper_dict():
    """Return a dictionary representation of a paper for API mocking."""
    return {
        'id': 'paper123',
        'title': 'Test Paper',
        'authors': ['Author One', 'Author Two'],
        'abstract': 'This is a test abstract.',
        'url': 'https://example.com/paper',
        'published_date': '2024-01-01',
        'citations': 100,
        'categories': ['cs.LG'],
        'keywords': ['test', 'paper']
    }
