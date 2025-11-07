# ResearchPulse

AI-powered research paper aggregator with LLM analysis, social buzz tracking, and daily insights generation. Runs as Docker container, outputs static blog.

## Project Structure

```
src/
├── fetchers/      # Paper sources: arXiv, Scholar, Semantic Scholar, PubMed, journals, authors, citations
├── social/        # Social signals: Reddit, HackerNews, GitHub, Google Custom Search
├── analyzer.py    # LLM analysis (Claude/GPT-4/Gemini/Ollama)
├── insights.py    # Generate research ideas & hot topics
├── processor.py   # Filter, rank, deduplicate
└── generator.py   # Static site generation

config/
├── tracking.yaml  # Keywords, authors, papers, journals
├── llm.yaml       # LLM provider settings
└── social.yaml    # Social media sources

templates/         # HTML templates for static site
output/            # Generated blog
```

## Data Pipeline

**1. Collect** → **2. Analyze** → **3. Generate**

### 1. Paper Collection

**Academic Sources** (API-based):
- arXiv, Google Scholar, Semantic Scholar, PubMed
- Track: keywords, specific authors, citations, journal websites

**Social Signals** (all free):
- Reddit (PRAW), HackerNews, GitHub trending
- Google Custom Search: LinkedIn/Twitter/Medium (100 free queries/day)

### 2. LLM Analysis

**Providers**: Claude, GPT-4, Gemini, Ollama (configurable)

**Tasks**: Summarize papers → Extract contributions → Generate 5 research ideas → Identify hot topics

### 3. Static Site Output

Blog with: Daily feed | Paper cards (AI summaries) | Research ideas | Hot topics | Social buzz

## Configuration

**config/tracking.yaml** - What to track
```yaml
keywords:
  - area: "Machine Learning"
    terms: ["transformers", "LLMs", "diffusion models"]
    sources: ["arxiv", "google_scholar"]

authors:
  - name: "Yoshua Bengio"
  - name: "Geoffrey Hinton"

key_papers:  # Track citations
  - title: "Attention Is All You Need"
    arxiv_id: "1706.03762"

journals:
  - name: "Nature"
  - name: "Science"
```

**config/social.yaml** - Social sources
```yaml
reddit:
  subreddits: ["MachineLearning", "deeplearning"]
  min_upvotes: 50

github:
  topics: ["machine-learning", "deep-learning"]
  track_paper_implementations: true

google_search:  # 100 free/day
  search_targets:
    - site: "linkedin.com"
      queries: ["machine learning paper", "arxiv.org"]
    - site: "twitter.com OR site:x.com"
      queries: ["arxiv.org/abs"]
```

**config/llm.yaml** - AI provider
```yaml
provider: claude  # claude|openai|gemini|ollama
tasks:
  summarization: true
  research_ideas: true
  hot_topics: true
```

## Environment Setup

**.env** (API keys - never commit!)
```bash
# LLM (choose one)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
OLLAMA_HOST=http://localhost:11434

# Paper sources (optional)
SERPAPI_KEY=...                    # Google Scholar
SEMANTIC_SCHOLAR_KEY=...

# Social (free)
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
GITHUB_TOKEN=...                   # Optional, higher rate limits
GOOGLE_SEARCH_API_KEY=...          # 100 free/day
GOOGLE_SEARCH_ENGINE_ID=...
```

**docker-compose.yml**
```yaml
services:
  research-pulse:
    build: .
    env_file: .env
    volumes:
      - ./output:/app/output
      - ./config:/app/config
```

## Quick Start

```bash
# 1. Setup
cp .env.example .env          # Add your API keys
nano config/tracking.yaml     # Configure what to track

# 2. Run
docker-compose up -d          # Start container
docker logs -f research-pulse # View logs

# 3. Deploy
# Static site in ./output ready for nginx/GitHub Pages
```

## Daily Pipeline

Fetch (keywords/authors/citations/journals + social buzz) → Deduplicate → LLM analyze → Rank by relevance+buzz → Generate insights → Build static site

**Output**: `output/YYYY-MM-DD/index.html`
- Hot topics (LLM-identified trends)
- 5 research ideas (LLM-generated)
- Ranked papers with AI summaries
- Social buzz indicators

## Notes

- All API keys in `.env` (never commit!)
- Free tier: 100 Google searches/day, unlimited Reddit/HN/GitHub
- LLM costs vary: Claude/GPT-4 ~$0.01-0.10 per paper analyzed
- Static output = deploy anywhere (nginx, GitHub Pages, S3)
