"""arXiv paper fetcher."""
import arxiv
from typing import List, Dict, Any
from datetime import datetime, timedelta
from .base import BaseFetcher, Paper
import logging

logger = logging.getLogger(__name__)


class ArxivFetcher(BaseFetcher):
    """Fetcher for arXiv papers."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.max_age_days = config.get('filters', {}).get('max_age_days', 30)
        self.client = arxiv.Client()

    def fetch_by_keywords(self, keywords: List[str], max_results: int = 50) -> List[Paper]:
        """Fetch papers from arXiv by keywords."""
        papers = []

        # Construct search query
        query = ' OR '.join([f'"{kw}"' for kw in keywords])

        try:
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )

            cutoff_date = datetime.now() - timedelta(days=self.max_age_days)

            for result in self.client.results(search):
                # Filter by date
                if result.published.replace(tzinfo=None) < cutoff_date:
                    continue

                paper = Paper(
                    title=result.title,
                    authors=[author.name for author in result.authors],
                    abstract=result.summary,
                    url=result.entry_id,
                    published_date=result.published.replace(tzinfo=None),
                    source='arxiv',
                    arxiv_id=result.entry_id.split('/')[-1],
                    pdf_url=result.pdf_url,
                    keywords=[cat for cat in result.categories],
                )
                papers.append(paper)

            self.logger.info(f"Fetched {len(papers)} papers from arXiv for keywords: {keywords}")

        except Exception as e:
            self.logger.error(f"Error fetching from arXiv: {e}")

        return papers

    def fetch_by_author(self, author_name: str, max_results: int = 50) -> List[Paper]:
        """Fetch papers by author from arXiv."""
        papers = []

        try:
            search = arxiv.Search(
                query=f'au:"{author_name}"',
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )

            cutoff_date = datetime.now() - timedelta(days=self.max_age_days)

            for result in self.client.results(search):
                if result.published.replace(tzinfo=None) < cutoff_date:
                    continue

                paper = Paper(
                    title=result.title,
                    authors=[author.name for author in result.authors],
                    abstract=result.summary,
                    url=result.entry_id,
                    published_date=result.published.replace(tzinfo=None),
                    source='arxiv',
                    arxiv_id=result.entry_id.split('/')[-1],
                    pdf_url=result.pdf_url,
                    keywords=[cat for cat in result.categories],
                )
                papers.append(paper)

            self.logger.info(f"Fetched {len(papers)} papers from arXiv for author: {author_name}")

        except Exception as e:
            self.logger.error(f"Error fetching from arXiv: {e}")

        return papers
