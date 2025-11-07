"""Google Custom Search tracker for LinkedIn, Twitter, etc."""
from googleapiclient.discovery import build
import os
from typing import List, Dict, Any
import logging
import re

logger = logging.getLogger(__name__)


class GoogleSearchTracker:
    """Track paper mentions using Google Custom Search."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get('enabled', True)
        self.daily_query_limit = config.get('daily_query_limit', 80)
        self.queries_used = 0

        if self.enabled:
            api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
            engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')

            if not api_key or not engine_id:
                logger.warning("Google Search API credentials not found")
                self.enabled = False
            else:
                try:
                    self.service = build("customsearch", "v1", developerKey=api_key)
                    self.engine_id = engine_id
                except Exception as e:
                    logger.error(f"Failed to initialize Google Search: {e}")
                    self.enabled = False

    def track_papers(self, papers: List[Any]) -> Dict[str, Dict[str, Any]]:
        """Track paper mentions across web using Google Search."""
        if not self.enabled or self.queries_used >= self.daily_query_limit:
            return {}

        social_signals = {}

        for paper in papers[:10]:  # Limit to top 10 papers to conserve quota
            if self.queries_used >= self.daily_query_limit:
                break

            if not paper.arxiv_id:
                continue

            try:
                query = f"arxiv.org/abs/{paper.arxiv_id}"
                result = self.service.cse().list(
                    q=query,
                    cx=self.engine_id,
                    num=10
                ).execute()

                self.queries_used += 1

                mentions = []
                for item in result.get('items', []):
                    mentions.append({
                        'title': item.get('title'),
                        'url': item.get('link'),
                        'snippet': item.get('snippet'),
                        'source': self._extract_domain(item.get('link', ''))
                    })

                if mentions:
                    social_signals[paper.paper_id] = {
                        'google_search': {
                            'mentions': mentions,
                            'count': len(mentions)
                        }
                    }

            except Exception as e:
                logger.warning(f"Error searching for paper {paper.arxiv_id}: {e}")

        logger.info(f"Tracked {len(social_signals)} papers via Google Search (queries used: {self.queries_used})")
        return social_signals

    def search_recent_papers(self) -> List[Dict[str, Any]]:
        """Search for recent paper discussions across platforms."""
        if not self.enabled or self.queries_used >= self.daily_query_limit:
            return []

        papers = []
        search_targets = self.config.get('search_targets', [])
        arxiv_pattern = re.compile(r'arxiv\.org/abs/(\d+\.\d+)')

        for target in search_targets:
            if self.queries_used >= self.daily_query_limit:
                break

            site = target.get('site')
            queries = target.get('queries', [])
            max_results = target.get('max_results', 10)

            for query in queries:
                if self.queries_used >= self.daily_query_limit:
                    break

                try:
                    full_query = f"site:{site} {query}" if site else query
                    result = self.service.cse().list(
                        q=full_query,
                        cx=self.engine_id,
                        num=min(max_results, 10)
                    ).execute()

                    self.queries_used += 1

                    for item in result.get('items', []):
                        text = f"{item.get('title', '')} {item.get('snippet', '')} {item.get('link', '')}"
                        arxiv_match = arxiv_pattern.search(text)

                        papers.append({
                            'title': item.get('title'),
                            'arxiv_id': arxiv_match.group(1) if arxiv_match else None,
                            'url': item.get('link'),
                            'snippet': item.get('snippet'),
                            'source': self._extract_domain(item.get('link', ''))
                        })

                except Exception as e:
                    logger.error(f"Error searching '{query}': {e}")

        logger.info(f"Found {len(papers)} papers via Google Search (queries used: {self.queries_used})")
        return papers

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return 'unknown'
