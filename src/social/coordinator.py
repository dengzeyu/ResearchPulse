"""Coordinator for all social media trackers."""
from typing import List, Dict, Any
import logging
from .reddit_tracker import RedditTracker
from .hackernews_tracker import HackerNewsTracker
from .github_tracker import GitHubTracker
from .google_search_tracker import GoogleSearchTracker

logger = logging.getLogger(__name__)


class SocialCoordinator:
    """Coordinates all social media trackers."""

    def __init__(self, social_config: Dict[str, Any]):
        self.config = social_config
        self.trackers = {}

        # Initialize trackers based on config
        if social_config.get('reddit', {}).get('enabled', True):
            self.trackers['reddit'] = RedditTracker(social_config.get('reddit', {}))

        if social_config.get('hackernews', {}).get('enabled', True):
            self.trackers['hackernews'] = HackerNewsTracker(social_config.get('hackernews', {}))

        if social_config.get('github', {}).get('enabled', True):
            self.trackers['github'] = GitHubTracker(social_config.get('github', {}))

        if social_config.get('google_search', {}).get('enabled', True):
            self.trackers['google_search'] = GoogleSearchTracker(social_config.get('google_search', {}))

        logger.info(f"Initialized {len(self.trackers)} social trackers")

    def track_all_papers(self, papers: List[Any]) -> Dict[str, Dict[str, Any]]:
        """Track social signals for all papers across all platforms."""
        all_signals = {}

        for tracker_name, tracker in self.trackers.items():
            logger.info(f"Tracking with {tracker_name}...")
            try:
                signals = tracker.track_papers(papers)

                # Merge signals
                for paper_id, paper_signals in signals.items():
                    if paper_id not in all_signals:
                        all_signals[paper_id] = {}
                    all_signals[paper_id].update(paper_signals)

            except Exception as e:
                logger.error(f"Error tracking with {tracker_name}: {e}")

        # Calculate social scores
        scoring = self.config.get('scoring', {})
        for paper_id, signals in all_signals.items():
            score = 0.0

            if 'reddit' in signals:
                score += signals['reddit']['total_score'] * scoring.get('reddit_upvote', 1.0)
                score += signals['reddit']['total_comments'] * scoring.get('reddit_comment', 0.5)

            if 'hackernews' in signals:
                score += signals['hackernews']['total_score'] * scoring.get('hn_score', 1.0)

            if 'github' in signals:
                score += signals['github']['total_stars'] * scoring.get('github_star', 0.8)

            if 'google_search' in signals:
                score += signals['google_search']['count'] * scoring.get('google_mention', 2.0)

            signals['total_score'] = score

        logger.info(f"Tracked social signals for {len(all_signals)} papers")
        return all_signals

    def search_trending_papers(self) -> List[Dict[str, Any]]:
        """Search for trending papers across all platforms."""
        all_papers = []

        for tracker_name, tracker in self.trackers.items():
            if not hasattr(tracker, 'search_recent_papers'):
                continue

            logger.info(f"Searching for papers with {tracker_name}...")
            try:
                papers = tracker.search_recent_papers()
                all_papers.extend(papers)
            except Exception as e:
                logger.error(f"Error searching with {tracker_name}: {e}")

        logger.info(f"Found {len(all_papers)} trending papers across social media")
        return all_papers
