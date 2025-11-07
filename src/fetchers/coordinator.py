"""Coordinator for all paper fetchers."""
from typing import List, Dict, Any
import logging
from .arxiv_fetcher import ArxivFetcher
from .semantic_scholar_fetcher import SemanticScholarFetcher
from .base import Paper

logger = logging.getLogger(__name__)


class FetcherCoordinator:
    """Coordinates multiple paper fetchers."""

    def __init__(self, tracking_config: Dict[str, Any]):
        self.tracking_config = tracking_config
        self.fetchers = {
            'arxiv': ArxivFetcher(tracking_config),
            'semantic_scholar': SemanticScholarFetcher(tracking_config),
        }

    def fetch_all_papers(self) -> List[Paper]:
        """Fetch papers from all configured sources."""
        all_papers = []

        # Fetch by keywords
        for keyword_group in self.tracking_config.get('keywords', []):
            area = keyword_group.get('area')
            terms = keyword_group.get('terms', [])
            sources = keyword_group.get('sources', ['arxiv'])

            logger.info(f"Fetching papers for area: {area}")

            for source in sources:
                if source in self.fetchers:
                    papers = self.fetchers[source].fetch_by_keywords(terms, max_results=50)
                    all_papers.extend(papers)

        # Fetch by authors
        for author_config in self.tracking_config.get('authors', []):
            author_name = author_config.get('name')
            logger.info(f"Fetching papers for author: {author_name}")

            # Try all fetchers that support author search
            for fetcher in self.fetchers.values():
                papers = fetcher.fetch_by_author(author_name, max_results=20)
                all_papers.extend(papers)

        # Fetch citations to key papers
        for paper_config in self.tracking_config.get('key_papers', []):
            paper_id = paper_config.get('arxiv_id')
            logger.info(f"Fetching citations for: {paper_config.get('title')}")

            # Only Semantic Scholar supports citation tracking
            if 'semantic_scholar' in self.fetchers:
                papers = self.fetchers['semantic_scholar'].fetch_by_citation(
                    f"arXiv:{paper_id}", max_results=30
                )
                all_papers.extend(papers)

        logger.info(f"Total papers fetched: {len(all_papers)}")
        return all_papers
