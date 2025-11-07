# ResearchPulse - Technical Documentation

AI-powered research paper aggregator with LLM analysis, social buzz tracking, and daily insights generation. Runs as Docker container, outputs static blog.

## Architecture Overview

**Pipeline**: Fetch → Deduplicate → Filter → Analyze → Rank → Generate Insights → Build Static Site

```
┌─────────────┐
│   Fetchers  │  Multi-source paper collection (arXiv, Semantic Scholar, etc.)
└──────┬──────┘
       ↓
┌─────────────┐
│  Processor  │  Deduplicate, filter by keywords/citations/age, rank by relevance
└──────┬──────┘
       ↓
┌─────────────┐
│  Analyzer   │  LLM-powered summarization and contribution extraction
└──────┬──────┘
       ↓
┌─────────────┐
│  Insights   │  Generate research ideas and identify hot topics
└──────┬──────┘
       ↓
┌─────────────┐
│  Generator  │  Build static HTML site with Jinja2 templates
└─────────────┘
```

## Project Structure

```
ResearchPulse/
├── src/                          # Main source code
│   ├── main.py                   # Entry point and pipeline orchestration
│   ├── processor.py              # Paper filtering, ranking, deduplication
│   ├── analyzer.py               # LLM-powered paper analysis (multi-provider)
│   ├── insights.py               # Research ideas & hot topics generation
│   ├── generator.py              # Static site generation with Jinja2
│   ├── fetchers/                 # Paper source integrations
│   │   ├── base.py               # Paper model & BaseFetcher abstract class
│   │   ├── coordinator.py        # Multi-source fetcher orchestration
│   │   ├── arxiv_fetcher.py      # arXiv API integration
│   │   └── semantic_scholar_fetcher.py  # Semantic Scholar API integration
│   └── social/                   # Social media tracking
│       ├── coordinator.py        # Social tracker orchestration
│       ├── reddit_tracker.py     # Reddit tracking with PRAW
│       ├── github_tracker.py     # GitHub trending repositories
│       ├── hackernews_tracker.py # HackerNews tracking
│       └── google_search_tracker.py  # Google Custom Search for LinkedIn/Twitter
│
├── tests/                        # Comprehensive unit tests (86+ tests)
│   ├── conftest.py               # Shared pytest fixtures
│   ├── unit/
│   │   ├── test_paper_model.py   # Paper data model tests
│   │   ├── test_processor.py     # Processor business logic tests
│   │   ├── test_analyzer.py      # LLM analyzer tests
│   │   ├── test_insights.py      # Insights generator tests
│   │   └── fetchers/
│   │       ├── test_arxiv_fetcher.py
│   │       ├── test_semantic_scholar_fetcher.py
│   │       └── test_fetcher_coordinator.py
│   └── README.md                 # Testing documentation
│
├── config/                       # YAML configurations
│   ├── tracking.yaml             # What to track (keywords, authors, papers)
│   ├── llm.yaml                  # LLM provider settings
│   └── social.yaml               # Social media sources
│
├── templates/                    # Jinja2 HTML templates
│   ├── index.html                # Main landing page
│   ├── daily_feed.html           # Daily paper feed
│   └── static/                   # CSS, JS, assets
│
├── output/                       # Generated static site
│   └── YYYY-MM-DD/               # Daily builds
│
├── pyproject.toml                # Modern Python project config (PEP 621)
├── requirements.txt              # Backwards compatibility
├── Dockerfile                    # Container build
├── docker-compose.yml            # Deployment config
└── .env                          # API keys (never commit!)
```

## Core Components

### 1. Paper Model (`fetchers/base.py`)

**Paper** - Core data structure for research papers
```python
class Paper:
    # Required fields
    title: str
    authors: List[str]
    abstract: str
    url: str
    published_date: datetime
    source: str

    # Optional identifiers
    paper_id: str = url
    arxiv_id: Optional[str]
    doi: Optional[str]

    # Metadata
    citations: int = 0
    venue: Optional[str]
    pdf_url: Optional[str]
    keywords: List[str] = []

    # Computed fields (populated by pipeline)
    summary: Optional[str]
    contributions: Optional[List[str]]
    social_score: float = 0.0
    relevance_score: float = 0.0
```

**BaseFetcher** - Abstract base class for all paper sources
- `fetch_by_keywords(keywords, max_results)` - Search by terms
- `fetch_by_author(author_name, max_results)` - Author search
- `fetch_by_citation(paper_id, max_results)` - Citation tracking

### 2. Fetchers (`fetchers/`)

**ArxivFetcher** - arXiv.org integration
- Keywords and author search
- Date filtering (configurable max_age_days)
- Returns papers with arXiv IDs and PDF links

**SemanticScholarFetcher** - Semantic Scholar API
- Keywords, authors, and citation search
- Extracts DOI, citation counts, venue
- Two-step author lookup (search author → get papers)

**FetcherCoordinator** - Multi-source orchestration
- Fetches from all configured sources
- Handles keywords, authors, and key paper citations
- Aggregates results from multiple fetchers

### 3. Processor (`processor.py`)

**PaperProcessor** - Filtering, ranking, and deduplication

**Deduplication**: Removes duplicates by
- Paper ID
- arXiv ID
- DOI
- Normalized title (lowercase, no punctuation)

**Filtering**: Removes papers with
- Excluded keywords (configurable blacklist)
- Low citations (for papers >7 days old)

**Ranking**: Scores papers by
- **Relevance** (60%): Keyword matches in title/abstract, tracked authors
- **Social signals** (30%): Reddit mentions, GitHub stars, etc.
- **Citations** (10%): Raw citation count

**Recency boost**: Papers get 1.5x boost if <1 day old, 1.3x if <3 days, 1.1x if <7 days

### 4. LLM Analyzer (`analyzer.py`)

**LLMAnalyzer** - Multi-provider LLM integration

**Supported Providers**:
- **Claude** (Anthropic) - claude-3-5-sonnet-20241022
- **OpenAI** - gpt-4-turbo-preview
- **Gemini** (Google) - gemini-pro
- **Ollama** - Local models (llama2, etc.)

**Tasks**:
- `analyze_paper()` - Full paper analysis
- `_summarize_paper()` - 2-3 sentence summary
- `_extract_contributions()` - 3-5 key contributions as bullet points
- `batch_analyze()` - Process multiple papers (max 50)

**Error Handling**: Returns empty strings on API failures, logs errors

### 5. Insights Generator (`insights.py`)

**InsightsGenerator** - Meta-analysis and trend identification

**Features**:
- `generate_research_ideas()` - 5 novel research ideas from top 20 papers
- `identify_hot_topics()` - 3 emerging trends from top 30 papers
- Keyword extraction and counting
- LLM-powered trend synthesis

**Output Format**:
```python
# Research Ideas
[{
    'title': 'Idea Title',
    'description': '2-3 sentence explanation',
    'impact': '1 sentence on potential impact'
}]

# Hot Topics
[{
    'name': 'Topic Name',
    'summary': '2-3 sentence trend explanation',
    'evidence': 'Number of papers and key examples'
}]
```

### 6. Social Trackers (`social/`)

**RedditTracker** - Reddit discussion tracking
- Searches configured subreddits
- Extracts arXiv IDs from posts/comments
- Tracks upvotes and comments

**GitHubTracker** - GitHub repository tracking
- Trending repos by topics
- Extracts arXiv IDs from README/descriptions
- Tracks stars and activity

**HackerNewsTracker** - HackerNews discussion tracking
- Algolia API for story search
- Tracks points and comments

**GoogleSearchTracker** - LinkedIn/Twitter content access
- Google Custom Search API (100 free queries/day)
- Configurable site-specific searches
- Tracks mentions and engagement

**SocialCoordinator** - Aggregates social signals
- Merges signals from all platforms
- Calculates total social score
- Links papers by arXiv ID

### 7. Static Site Generator (`generator.py`)

**StaticSiteGenerator** - HTML blog generation

**Features**:
- Daily feed pages with Jinja2 templates
- Paper cards with AI summaries
- Research ideas section
- Hot topics section
- Social buzz indicators
- Responsive design with Tailwind CSS

**Outputs**:
- `output/YYYY-MM-DD/index.html` - Daily feed
- `output/index.html` - Main landing page
- JSON data files for each day

## Data Pipeline Flow

### main.py - Pipeline Orchestration

```python
def run_pipeline():
    # 1. Load configurations
    tracking_config = load_yaml('config/tracking.yaml')
    llm_config = load_yaml('config/llm.yaml')
    social_config = load_yaml('config/social.yaml')

    # 2. Fetch papers from all sources
    coordinator = FetcherCoordinator(tracking_config)
    papers = coordinator.fetch_all_papers()  # arXiv, Semantic Scholar

    # 3. Track social signals
    social_coordinator = SocialCoordinator(social_config)
    social_signals = social_coordinator.track_all_papers(papers)

    # 4. Process papers
    processor = PaperProcessor(tracking_config)
    papers = processor.deduplicate(papers)
    papers = processor.filter_papers(papers)
    papers = processor.rank_papers(papers, social_signals, tracking_config)
    top_papers = processor.get_top_papers(papers, limit=50)

    # 5. LLM Analysis
    analyzer = LLMAnalyzer(llm_config)
    analyses = analyzer.batch_analyze(top_papers)

    # 6. Generate insights
    insights_gen = InsightsGenerator(llm_config)
    research_ideas = insights_gen.generate_research_ideas(top_papers)
    hot_topics = insights_gen.identify_hot_topics(top_papers)

    # 7. Build static site
    generator = StaticSiteGenerator()
    generator.generate_daily_feed(top_papers, research_ideas, hot_topics)
```

## Configuration

### tracking.yaml - What to track
```yaml
keywords:
  - area: "Machine Learning"
    terms: ["transformers", "LLMs", "attention mechanisms"]
    sources: ["arxiv", "semantic_scholar"]

  - area: "Computer Vision"
    terms: ["diffusion models", "image generation"]
    sources: ["arxiv"]

authors:
  - name: "Yoshua Bengio"
  - name: "Geoffrey Hinton"
  - name: "Yann LeCun"

key_papers:  # Track citations to influential papers
  - title: "Attention Is All You Need"
    arxiv_id: "1706.03762"

filters:
  min_citations: 5
  max_age_days: 30
  exclude_keywords: ["quantum", "biology"]  # Domain filtering
```

### llm.yaml - AI provider configuration
```yaml
provider: claude  # claude | openai | gemini | ollama

claude:
  model: claude-3-5-sonnet-20241022

openai:
  model: gpt-4-turbo-preview

gemini:
  model: gemini-pro

ollama:
  model: llama2

tasks:
  summarization: true
  key_contributions: true

research_ideas:
  count: 5
  prompt: "Focus on practical applications and novel combinations"

hot_topics:
  count: 3
  prompt: "Identify breakthrough trends and emerging research areas"
```

### social.yaml - Social media sources
```yaml
reddit:
  enabled: true
  subreddits: ["MachineLearning", "deeplearning", "artificial"]
  min_upvotes: 50

github:
  enabled: true
  topics: ["machine-learning", "deep-learning", "transformers"]
  track_paper_implementations: true

hackernews:
  enabled: true
  min_points: 50

google_search:
  enabled: true
  api_quota: 100  # Free tier daily limit
  search_targets:
    - site: "linkedin.com"
      queries: ["machine learning paper", "arxiv.org"]
    - site: "twitter.com OR site:x.com"
      queries: ["arxiv.org/abs", "new paper"]
```

## Development Setup

### Installation

```bash
# Clone repository
git clone https://github.com/dengzeyu/ResearchPulse.git
cd ResearchPulse

# Install with pip (modern Python packaging)
pip install -e .              # Main dependencies only
pip install -e ".[test]"      # With test dependencies
pip install -e ".[dev]"       # With all dev tools (black, ruff, mypy)
pip install -e ".[arxiv]"     # With optional arXiv support
pip install -e ".[all]"       # With all optional dependencies

# Note: arXiv is optional due to dependency issues on some systems
# The project works fully without it using Semantic Scholar
```

### Environment Variables (.env)

```bash
# LLM Provider (choose one)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
OLLAMA_HOST=http://localhost:11434

# Paper Sources (optional, most are free)
SEMANTIC_SCHOLAR_API_KEY=...  # Optional, higher rate limits

# Social Media (all free)
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
REDDIT_USER_AGENT=researchpulse/1.0

GITHUB_TOKEN=...  # Optional, 60 req/hr without, 5000/hr with

GOOGLE_SEARCH_API_KEY=...      # 100 free queries/day
GOOGLE_SEARCH_ENGINE_ID=...
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/unit/test_processor.py -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=html

# Run only unit tests
pytest tests/unit/ -v

# Run tests by marker
pytest -m unit
```

**Test Coverage**: 86+ tests covering:
- Paper model (12 tests)
- Processor (24 tests) - deduplication, filtering, ranking
- Analyzer (18 tests) - multi-provider LLM support
- Insights (18 tests) - research ideas and hot topics
- Fetchers (14+ tests) - API integrations with mocking

All tests use mocked APIs (no real API calls) and freezegun for deterministic time-based testing.

### Docker Deployment

```bash
# Build and run
docker-compose up -d

# View logs
docker logs -f research-pulse

# Stop
docker-compose down
```

**docker-compose.yml**:
```yaml
version: '3.8'
services:
  research-pulse:
    build: .
    env_file: .env
    volumes:
      - ./output:/app/output
      - ./config:/app/config
    restart: unless-stopped
    environment:
      - TZ=UTC
```

## Daily Operation

### Automated Schedule

The pipeline runs daily at a configured time (default: 9 AM UTC):

```python
# In main.py
import schedule

schedule.every().day.at("09:00").do(run_pipeline)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Manual Run

```bash
# Run pipeline once
python src/main.py

# Or with Docker
docker exec research-pulse python src/main.py
```

### Output

**Generated Files**:
```
output/
├── index.html                    # Main landing page
├── 2024-01-15/
│   ├── index.html                # Daily feed
│   ├── papers.json               # Raw paper data
│   ├── insights.json             # Research ideas & hot topics
│   └── social.json               # Social signals
└── static/
    ├── style.css
    └── script.js
```

## Key Algorithms

### Deduplication Algorithm

```python
def deduplicate(papers):
    seen_ids = set()      # Paper IDs, arXiv IDs, DOIs
    seen_titles = set()   # Normalized titles

    for paper in papers:
        # Check all identifier types
        if paper.paper_id in seen_ids: continue
        if paper.arxiv_id in seen_ids: continue
        if paper.doi in seen_ids: continue

        # Check normalized title
        normalized = normalize_title(paper.title)
        if normalized in seen_titles: continue

        # Add all identifiers
        seen_ids.update([paper.paper_id, paper.arxiv_id, paper.doi])
        seen_titles.add(normalized)
        yield paper
```

### Relevance Scoring

```python
def calculate_relevance(paper, config):
    score = 0.0

    # Keyword matching
    for keyword in config['keywords']:
        if keyword in paper.title.lower():
            score += 5.0  # Title match
        if keyword in paper.abstract.lower():
            score += 2.0  # Abstract match

    # Author matching
    for tracked_author in config['authors']:
        if tracked_author in paper.authors:
            score += 10.0  # Tracked author

    # Recency boost
    age_days = (datetime.now() - paper.published_date).days
    if age_days <= 1: score *= 1.5
    elif age_days <= 3: score *= 1.3
    elif age_days <= 7: score *= 1.1

    return score
```

### Combined Ranking

```python
def rank_papers(papers, social_signals, config):
    for paper in papers:
        relevance = calculate_relevance(paper, config)
        social = social_signals.get(paper.paper_id, {}).get('total_score', 0)

        # Weighted combination
        paper.combined_score = (
            relevance * 0.6 +
            social * 0.3 +
            (paper.citations / 100.0) * 0.1
        )

    return sorted(papers, key=lambda p: p.combined_score, reverse=True)
```

## API Rate Limits & Costs

### Free Services
- **arXiv**: Unlimited (rate-limited to 3 req/sec)
- **Semantic Scholar**: 5000 requests/5 minutes (free)
- **Reddit**: 60 requests/minute (free with authentication)
- **GitHub**: 60 requests/hour (5000 with token)
- **HackerNews**: Unlimited (Algolia API)
- **Google Custom Search**: 100 queries/day (free tier)

### Paid Services
- **Claude**: ~$0.01-0.03 per paper (Sonnet 3.5)
- **GPT-4**: ~$0.03-0.10 per paper (varies by model)
- **Gemini**: ~$0.001-0.01 per paper (Pro model)
- **Ollama**: Free (local inference)

**Daily Cost Estimate** (50 papers/day with Claude):
- Paper analysis: ~$0.50-1.50
- Insights generation: ~$0.10-0.30
- **Total**: ~$0.60-1.80/day = $18-54/month

## Deployment Options

### 1. Docker (Recommended)
```bash
docker-compose up -d
```
**Pros**: Isolated, reproducible, easy to scale
**Cons**: Requires Docker

### 2. Systemd Service
```ini
[Unit]
Description=ResearchPulse
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/path/to/ResearchPulse
ExecStart=/usr/bin/python3 src/main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### 3. Kubernetes
Scale horizontally with multiple fetcher/analyzer pods

### 4. Cloud Functions
Deploy as scheduled functions on AWS Lambda, Google Cloud Functions, or Azure Functions

## Static Site Hosting

The generated `output/` directory is a static site that can be hosted anywhere:

- **GitHub Pages**: Free, automatic deployment
- **Netlify/Vercel**: Free tier, CDN, custom domains
- **AWS S3 + CloudFront**: Cheap, scalable
- **Nginx**: Self-hosted

```bash
# Example: Deploy to GitHub Pages
git subtree push --prefix output origin gh-pages
```

## Troubleshooting

### Common Issues

**1. API Key Errors**
```bash
# Check .env file
cat .env | grep API_KEY

# Test API connection
python -c "from anthropic import Anthropic; print(Anthropic(api_key='...').messages.create(...))"
```

**2. Dependency Issues**
```bash
# Rebuild from scratch
pip install -e ".[dev]" --force-reinstall --no-cache-dir
```

**3. No Papers Found**
- Check `config/tracking.yaml` keywords are not too specific
- Verify date range (max_age_days)
- Check fetcher logs for API errors

**4. LLM Analysis Failing**
- Verify API keys in .env
- Check rate limits
- Review error logs in console

## Performance Optimization

### Batch Processing
- Analyze papers in batches (max 50)
- Use concurrent requests where possible
- Cache LLM responses

### Caching Strategy
```python
# Cache paper summaries
@functools.lru_cache(maxsize=1000)
def get_paper_summary(paper_id):
    # Avoid re-analyzing same papers
    pass
```

### Database Option
For large-scale deployments, consider adding PostgreSQL or MongoDB to store:
- Historical papers
- Analysis results
- Social signals over time

## Contributing

```bash
# Setup development environment
pip install -e ".[dev]"

# Run tests before committing
pytest tests/

# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

## Security Best Practices

1. **Never commit .env files** - Add to .gitignore
2. **Use environment variables** - Not hardcoded API keys
3. **Validate user inputs** - Sanitize config files
4. **Rate limit API calls** - Respect provider limits
5. **Keep dependencies updated** - Regular security patches

```bash
# Check for security issues
pip install safety
safety check
```

## Future Enhancements

- [ ] Add more paper sources (PubMed, bioRxiv, SSRN)
- [ ] Email/Slack notifications for high-value papers
- [ ] Paper recommendation engine based on reading history
- [ ] Multi-language support for international papers
- [ ] Mobile-responsive PWA
- [ ] GraphQL API for custom integrations
- [ ] Paper similarity clustering
- [ ] Automated paper reading and note-taking

## License

GNU General Public License v3.0 or later (GPL-3.0-or-later) - See LICENSE file for details

This project is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

## Support

- GitHub Issues: https://github.com/dengzeyu/ResearchPulse/issues
- Documentation: This file (Claude.md)
- Test Suite: See tests/README.md
