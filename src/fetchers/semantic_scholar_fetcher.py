"""Semantic Scholar paper fetcher."""
from typing import List, Dict, Any
from datetime import datetime, timedelta
import requests
from .base import BaseFetcher, Paper
import logging
import os

logger = logging.getLogger(__name__)


class SemanticScholarFetcher(BaseFetcher):
    """Fetcher for Semantic Scholar papers."""

    BASE_URL = "https://api.semanticscholar.org/graph/v1"

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = os.getenv('SEMANTIC_SCHOLAR_API_KEY')
        self.max_age_days = config.get('filters', {}).get('max_age_days', 30)
        self.headers = {}
        if self.api_key:
            self.headers['x-api-key'] = self.api_key

    def fetch_by_keywords(self, keywords: List[str], max_results: int = 50) -> List[Paper]:
        """Fetch papers by keywords."""
        papers = []
        query = ' '.join(keywords)

        try:
            url = f"{self.BASE_URL}/paper/search"
            params = {
                'query': query,
                'limit': max_results,
                'fields': 'title,authors,abstract,url,publicationDate,citationCount,venue,externalIds'
            }

            response = requests.get(url, params=params, headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            cutoff_date = datetime.now() - timedelta(days=self.max_age_days)

            for item in data.get('data', []):
                if not item.get('publicationDate'):
                    continue

                pub_date = datetime.strptime(item['publicationDate'], '%Y-%m-%d')
                if pub_date < cutoff_date:
                    continue

                # Get arXiv ID if available
                arxiv_id = None
                external_ids = item.get('externalIds', {})
                if external_ids and 'ArXiv' in external_ids:
                    arxiv_id = external_ids['ArXiv']

                paper = Paper(
                    title=item.get('title', ''),
                    authors=[a.get('name', '') for a in item.get('authors', [])],
                    abstract=item.get('abstract', ''),
                    url=f"https://www.semanticscholar.org/paper/{item['paperId']}",
                    published_date=pub_date,
                    source='semantic_scholar',
                    paper_id=item['paperId'],
                    arxiv_id=arxiv_id,
                    doi=external_ids.get('DOI') if external_ids else None,
                    citations=item.get('citationCount', 0),
                    venue=item.get('venue', ''),
                )
                papers.append(paper)

            self.logger.info(f"Fetched {len(papers)} papers from Semantic Scholar for keywords: {keywords}")

        except Exception as e:
            self.logger.error(f"Error fetching from Semantic Scholar: {e}")

        return papers

    def fetch_by_author(self, author_name: str, max_results: int = 50) -> List[Paper]:
        """Fetch papers by author."""
        papers = []

        try:
            # First, search for the author
            url = f"{self.BASE_URL}/author/search"
            params = {'query': author_name, 'limit': 1}

            response = requests.get(url, params=params, headers=self.headers, timeout=30)
            response.raise_for_status()
            author_data = response.json()

            if not author_data.get('data'):
                self.logger.warning(f"Author not found: {author_name}")
                return papers

            author_id = author_data['data'][0]['authorId']

            # Fetch author's papers
            url = f"{self.BASE_URL}/author/{author_id}/papers"
            params = {
                'limit': max_results,
                'fields': 'title,authors,abstract,url,publicationDate,citationCount,venue,externalIds'
            }

            response = requests.get(url, params=params, headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            cutoff_date = datetime.now() - timedelta(days=self.max_age_days)

            for item in data.get('data', []):
                if not item.get('publicationDate'):
                    continue

                pub_date = datetime.strptime(item['publicationDate'], '%Y-%m-%d')
                if pub_date < cutoff_date:
                    continue

                external_ids = item.get('externalIds', {})
                arxiv_id = external_ids.get('ArXiv') if external_ids else None

                paper = Paper(
                    title=item.get('title', ''),
                    authors=[a.get('name', '') for a in item.get('authors', [])],
                    abstract=item.get('abstract', ''),
                    url=f"https://www.semanticscholar.org/paper/{item['paperId']}",
                    published_date=pub_date,
                    source='semantic_scholar',
                    paper_id=item['paperId'],
                    arxiv_id=arxiv_id,
                    doi=external_ids.get('DOI') if external_ids else None,
                    citations=item.get('citationCount', 0),
                    venue=item.get('venue', ''),
                )
                papers.append(paper)

            self.logger.info(f"Fetched {len(papers)} papers from Semantic Scholar for author: {author_name}")

        except Exception as e:
            self.logger.error(f"Error fetching from Semantic Scholar: {e}")

        return papers

    def fetch_by_citation(self, paper_id: str, max_results: int = 50) -> List[Paper]:
        """Fetch papers citing a given paper."""
        papers = []

        try:
            url = f"{self.BASE_URL}/paper/{paper_id}/citations"
            params = {
                'limit': max_results,
                'fields': 'title,authors,abstract,url,publicationDate,citationCount,venue,externalIds'
            }

            response = requests.get(url, params=params, headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            cutoff_date = datetime.now() - timedelta(days=self.max_age_days)

            for item in data.get('data', []):
                citing_paper = item.get('citingPaper', {})
                if not citing_paper.get('publicationDate'):
                    continue

                pub_date = datetime.strptime(citing_paper['publicationDate'], '%Y-%m-%d')
                if pub_date < cutoff_date:
                    continue

                external_ids = citing_paper.get('externalIds', {})
                arxiv_id = external_ids.get('ArXiv') if external_ids else None

                paper = Paper(
                    title=citing_paper.get('title', ''),
                    authors=[a.get('name', '') for a in citing_paper.get('authors', [])],
                    abstract=citing_paper.get('abstract', ''),
                    url=f"https://www.semanticscholar.org/paper/{citing_paper['paperId']}",
                    published_date=pub_date,
                    source='semantic_scholar',
                    paper_id=citing_paper['paperId'],
                    arxiv_id=arxiv_id,
                    doi=external_ids.get('DOI') if external_ids else None,
                    citations=citing_paper.get('citationCount', 0),
                    venue=citing_paper.get('venue', ''),
                )
                papers.append(paper)

            self.logger.info(f"Fetched {len(papers)} citing papers from Semantic Scholar")

        except Exception as e:
            self.logger.error(f"Error fetching citations from Semantic Scholar: {e}")

        return papers
