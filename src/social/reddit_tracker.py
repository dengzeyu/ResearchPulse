"""Reddit social media tracker."""
import praw
import os
from typing import List, Dict, Any
import logging
import re

logger = logging.getLogger(__name__)


class RedditTracker:
    """Track paper mentions on Reddit."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get('enabled', True)

        if self.enabled:
            try:
                self.reddit = praw.Reddit(
                    client_id=os.getenv('REDDIT_CLIENT_ID'),
                    client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                    user_agent=os.getenv('REDDIT_USER_AGENT', 'ResearchPulse/1.0')
                )
            except Exception as e:
                logger.error(f"Failed to initialize Reddit client: {e}")
                self.enabled = False

    def track_papers(self, papers: List[Any]) -> Dict[str, Dict[str, Any]]:
        """Track social signals for papers on Reddit."""
        if not self.enabled:
            return {}

        social_signals = {}
        subreddits = self.config.get('subreddits', [])
        min_upvotes = self.config.get('min_upvotes', 50)
        time_filter = self.config.get('time_filter', 'day')

        # Create a map of paper IDs/URLs for matching
        paper_map = {}
        for paper in papers:
            if paper.arxiv_id:
                paper_map[paper.arxiv_id] = paper.paper_id
            if paper.url:
                paper_map[paper.url] = paper.paper_id

        for subreddit_name in subreddits:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)

                # Search for hot posts
                for submission in subreddit.hot(limit=100):
                    if submission.score < min_upvotes:
                        continue

                    # Check if post mentions any of our papers
                    text = f"{submission.title} {submission.selftext} {submission.url}"

                    for identifier, paper_id in paper_map.items():
                        if identifier in text:
                            if paper_id not in social_signals:
                                social_signals[paper_id] = {
                                    'reddit': {
                                        'posts': [],
                                        'total_score': 0,
                                        'total_comments': 0
                                    }
                                }

                            social_signals[paper_id]['reddit']['posts'].append({
                                'title': submission.title,
                                'url': f"https://reddit.com{submission.permalink}",
                                'score': submission.score,
                                'comments': submission.num_comments,
                                'subreddit': subreddit_name
                            })
                            social_signals[paper_id]['reddit']['total_score'] += submission.score
                            social_signals[paper_id]['reddit']['total_comments'] += submission.num_comments

                logger.info(f"Tracked {len(social_signals)} papers on r/{subreddit_name}")

            except Exception as e:
                logger.error(f"Error tracking Reddit for r/{subreddit_name}: {e}")

        return social_signals

    def search_recent_papers(self) -> List[Dict[str, Any]]:
        """Search for recent paper discussions on Reddit."""
        if not self.enabled:
            return []

        papers = []
        subreddits = self.config.get('subreddits', [])
        min_upvotes = self.config.get('min_upvotes', 50)

        arxiv_pattern = re.compile(r'arxiv\.org/abs/(\d+\.\d+)')

        for subreddit_name in subreddits:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)

                for submission in subreddit.hot(limit=100):
                    if submission.score < min_upvotes:
                        continue

                    text = f"{submission.title} {submission.selftext} {submission.url}"
                    arxiv_match = arxiv_pattern.search(text)

                    if arxiv_match:
                        papers.append({
                            'title': submission.title,
                            'arxiv_id': arxiv_match.group(1),
                            'url': submission.url,
                            'reddit_url': f"https://reddit.com{submission.permalink}",
                            'score': submission.score,
                            'comments': submission.num_comments,
                            'subreddit': subreddit_name
                        })

            except Exception as e:
                logger.error(f"Error searching Reddit for r/{subreddit_name}: {e}")

        logger.info(f"Found {len(papers)} paper discussions on Reddit")
        return papers
