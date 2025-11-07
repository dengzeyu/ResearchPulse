"""Base class for paper fetchers."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Paper:
    """Represents a research paper."""

    def __init__(
        self,
        title: str,
        authors: List[str],
        abstract: str,
        url: str,
        published_date: datetime,
        source: str,
        paper_id: str = None,
        arxiv_id: str = None,
        doi: str = None,
        citations: int = 0,
        venue: str = None,
        pdf_url: str = None,
        keywords: List[str] = None,
    ):
        self.title = title
        self.authors = authors
        self.abstract = abstract
        self.url = url
        self.published_date = published_date
        self.source = source
        self.paper_id = paper_id or url
        self.arxiv_id = arxiv_id
        self.doi = doi
        self.citations = citations
        self.venue = venue
        self.pdf_url = pdf_url
        self.keywords = keywords or []

        # Will be populated later
        self.summary = None
        self.contributions = None
        self.social_score = 0.0
        self.relevance_score = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert paper to dictionary."""
        return {
            'title': self.title,
            'authors': self.authors,
            'abstract': self.abstract,
            'url': self.url,
            'published_date': self.published_date.isoformat(),
            'source': self.source,
            'paper_id': self.paper_id,
            'arxiv_id': self.arxiv_id,
            'doi': self.doi,
            'citations': self.citations,
            'venue': self.venue,
            'pdf_url': self.pdf_url,
            'keywords': self.keywords,
            'summary': self.summary,
            'contributions': self.contributions,
            'social_score': self.social_score,
            'relevance_score': self.relevance_score,
        }

    def __repr__(self):
        return f"Paper(title='{self.title[:50]}...', source='{self.source}')"


class BaseFetcher(ABC):
    """Abstract base class for paper fetchers."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def fetch_by_keywords(self, keywords: List[str], max_results: int = 50) -> List[Paper]:
        """Fetch papers by keywords."""
        pass

    @abstractmethod
    def fetch_by_author(self, author_name: str, max_results: int = 50) -> List[Paper]:
        """Fetch papers by author."""
        pass

    def fetch_by_citation(self, paper_id: str, max_results: int = 50) -> List[Paper]:
        """Fetch papers citing a given paper. Not all sources support this."""
        self.logger.warning(f"{self.__class__.__name__} does not support citation tracking")
        return []
