"""HackerNews tracker."""
import requests
from typing import List, Dict, Any
import logging
import re

logger = logging.getLogger(__name__)


class HackerNewsTracker:
    """Track paper mentions on HackerNews."""

    BASE_URL = "https://hacker-news.firebaseio.com/v0"

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get('enabled', True)
        self.min_score = config.get('min_score', 50)
        self.keywords = [kw.lower() for kw in config.get('keywords', [])]

    def track_papers(self, papers: List[Any]) -> Dict[str, Dict[str, Any]]:
        """Track social signals for papers on HackerNews."""
        if not self.enabled:
            return {}

        social_signals = {}

        # Create a map of paper IDs/URLs for matching
        paper_map = {}
        for paper in papers:
            if paper.arxiv_id:
                paper_map[paper.arxiv_id] = paper.paper_id
            if paper.url:
                paper_map[paper.url] = paper.paper_id

        try:
            # Get top stories
            response = requests.get(f"{self.BASE_URL}/topstories.json", timeout=10)
            response.raise_for_status()
            story_ids = response.json()[:100]  # Get top 100 stories

            for story_id in story_ids:
                story = self._get_story(story_id)
                if not story or story.get('score', 0) < self.min_score:
                    continue

                # Check if story mentions any of our papers
                text = f"{story.get('title', '')} {story.get('url', '')}"

                for identifier, paper_id in paper_map.items():
                    if identifier in text:
                        if paper_id not in social_signals:
                            social_signals[paper_id] = {
                                'hackernews': {
                                    'posts': [],
                                    'total_score': 0,
                                    'total_comments': 0
                                }
                            }

                        social_signals[paper_id]['hackernews']['posts'].append({
                            'title': story['title'],
                            'url': f"https://news.ycombinator.com/item?id={story_id}",
                            'score': story.get('score', 0),
                            'comments': story.get('descendants', 0)
                        })
                        social_signals[paper_id]['hackernews']['total_score'] += story.get('score', 0)
                        social_signals[paper_id]['hackernews']['total_comments'] += story.get('descendants', 0)

            logger.info(f"Tracked {len(social_signals)} papers on HackerNews")

        except Exception as e:
            logger.error(f"Error tracking HackerNews: {e}")

        return social_signals

    def search_recent_papers(self) -> List[Dict[str, Any]]:
        """Search for recent paper discussions on HackerNews."""
        if not self.enabled:
            return []

        papers = []
        arxiv_pattern = re.compile(r'arxiv\.org/abs/(\d+\.\d+)')

        try:
            # Get top stories
            response = requests.get(f"{self.BASE_URL}/topstories.json", timeout=10)
            response.raise_for_status()
            story_ids = response.json()[:100]

            for story_id in story_ids:
                story = self._get_story(story_id)
                if not story or story.get('score', 0) < self.min_score:
                    continue

                text = f"{story.get('title', '')} {story.get('url', '')}"

                # Check for keywords
                if any(kw in text.lower() for kw in self.keywords):
                    arxiv_match = arxiv_pattern.search(text)

                    papers.append({
                        'title': story['title'],
                        'arxiv_id': arxiv_match.group(1) if arxiv_match else None,
                        'url': story.get('url', ''),
                        'hn_url': f"https://news.ycombinator.com/item?id={story_id}",
                        'score': story.get('score', 0),
                        'comments': story.get('descendants', 0)
                    })

        except Exception as e:
            logger.error(f"Error searching HackerNews: {e}")

        logger.info(f"Found {len(papers)} paper discussions on HackerNews")
        return papers

    def _get_story(self, story_id: int) -> Dict[str, Any]:
        """Get a single story by ID."""
        try:
            response = requests.get(f"{self.BASE_URL}/item/{story_id}.json", timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"Error fetching story {story_id}: {e}")
            return {}
