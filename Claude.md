# ResearchPulse

AI-powered research paper aggregator that captures the pulse of scientific research. Generates daily insights, research ideas, and trending topics. Runs as a Docker container and publishes to a stylish static blog.

## Core Structure

```
/
├── src/
│   ├── fetchers/
│   │   ├── arxiv.py       # arXiv API
│   │   ├── scholar.py     # Google Scholar
│   │   ├── semantic.py    # Semantic Scholar
│   │   ├── pubmed.py      # PubMed
│   │   ├── author.py      # Track specific authors
│   │   ├── citations.py   # Track paper citations
│   │   └── journals.py    # Scrape journal websites
│   ├── social/
│   │   ├── reddit.py      # Reddit API (free via PRAW)
│   │   ├── hackernews.py  # HackerNews API (free)
│   │   ├── github.py      # GitHub trending (free)
│   │   └── twitter.py     # Twitter/X (optional, paid)
│   ├── analyzer.py        # LLM-powered paper analysis
│   ├── insights.py        # Generate research ideas & hot topics
│   ├── processor.py       # Filter, rank, deduplicate papers
│   └── generator.py       # Static site generation
├── templates/
│   ├── index.html         # Blog homepage template
│   ├── daily.html         # Daily feed page template
│   └── paper.html         # Individual paper card
├── config/
│   ├── tracking.yaml      # Keywords, authors, papers, journals to track
│   ├── llm.yaml           # LLM provider configs
│   └── social.yaml        # Social media configs
├── output/                # Generated static site
├── .env                   # API keys and secrets
├── .env.example           # Example configuration
├── Dockerfile
└── docker-compose.yml
```

## Architecture

### 1. Paper Collection
**Academic Sources:**
- arXiv API
- Google Scholar (via `scholarly` or SerpAPI)
- Semantic Scholar API
- PubMed API

**Social Signals:**
- **Reddit API** (free, via PRAW) - r/MachineLearning, r/science, r/ArtificialIntelligence
- **HackerNews API** (free) - paper discussions and trending research
- **Twitter/X** (optional, requires paid API $100+/month) - research hashtags
- **arXiv trackbacks** (free) - papers linking to arXiv
- **GitHub trending** (free) - research repos and paper implementations

### 2. AI Analysis
**LLM Integration (configurable):**
- **Claude** (Anthropic API)
- **GPT-4** (OpenAI API)
- **Gemini** (Google API)
- **Ollama** (local models)

**Analysis Tasks:**
- Summarize papers (3-5 sentences)
- Extract key contributions
- Identify methodology & results
- Generate research ideas (5 per day)
- Detect hot topics & trends

### 3. Static Site Generation
**Output:** Stylish blog-style static website
- Daily feed pages
- Paper cards with AI summaries
- Research ideas section
- Trending topics dashboard
- Social buzz indicators

## Key Components

**src/analyzer.py**
```python
class LLMAnalyzer:
    def __init__(self, provider: str = "claude")  # claude|openai|gemini|ollama

    def summarize_paper(self, paper: Paper) -> str
    def extract_contributions(self, paper: Paper) -> List[str]
    def generate_research_ideas(self, papers: List[Paper]) -> List[str]
    def identify_hot_topics(self, papers: List[Paper]) -> List[Topic]
```

**src/insights.py**
```python
def generate_daily_insights(papers: List[Paper], social_data: dict) -> Insights:
    """Generate 5 research ideas and hot topics"""

def rank_by_social_buzz(papers: List[Paper], social_data: dict) -> List[Paper]:
    """Rank papers by social media mentions"""
```

**src/generator.py**
```python
def generate_static_site(feed: DailyFeed, output_dir: str):
    """Generate static HTML/CSS/JS blog"""
```

**src/fetchers/author.py**
```python
class AuthorTracker:
    def fetch_author_papers(self, author: str, days: int) -> List[Paper]:
        """Fetch recent papers by specific author"""
```

**src/fetchers/citations.py**
```python
class CitationTracker:
    def fetch_citing_papers(self, arxiv_id: str, days: int) -> List[Paper]:
        """Fetch papers citing a key paper"""
```

**src/fetchers/journals.py**
```python
class JournalScraper:
    def fetch_journal_papers(self, journal_url: str, sections: List[str]) -> List[Paper]:
        """Scrape latest papers from journal website"""
```

**src/social/reddit.py**
```python
class RedditFetcher:
    def get_trending_papers(self, subreddits: List[str], min_upvotes: int) -> List[Post]:
        """Fetch trending papers from subreddits using PRAW (free)"""
```

**src/social/hackernews.py**
```python
class HackerNewsFetcher:
    def get_trending_papers(self, keywords: List[str], min_points: int) -> List[Story]:
        """Fetch trending papers from HN (free API)"""
```

**src/social/github.py**
```python
class GitHubFetcher:
    def get_trending_repos(self, topics: List[str]) -> List[Repo]:
        """Fetch trending ML repos with paper implementations (free)"""

    def get_arxiv_implementations(self, min_stars: int) -> List[Repo]:
        """Find GitHub repos implementing arXiv papers"""
```

**src/social/twitter.py** (optional)
```python
class TwitterFetcher:
    def get_trending_papers(self, hashtags: List[str]) -> List[Tweet]:
        """Requires paid Twitter API access ($100+/month)"""
```

## Configuration

**config/llm.yaml**
```yaml
provider: claude  # claude|openai|gemini|ollama
models:
  claude: claude-3-5-sonnet-20241022
  openai: gpt-4-turbo
  gemini: gemini-pro
  ollama: llama3.1:8b
tasks:
  summarization: true
  research_ideas: true
  hot_topics: true
```

**config/tracking.yaml**
```yaml
# Track by keywords
keywords:
  - area: "Machine Learning"
    terms: ["neural networks", "transformers", "LLMs", "diffusion models"]
    sources: ["arxiv", "google_scholar", "semantic_scholar"]
  - area: "Quantum Computing"
    terms: ["quantum algorithms", "qubits", "quantum error correction"]
    sources: ["arxiv", "nature", "science"]

# Track specific authors
authors:
  - name: "Yoshua Bengio"
    affiliations: ["Mila", "University of Montreal"]
  - name: "Geoffrey Hinton"
    affiliations: ["Google", "University of Toronto"]
  - name: "Yann LeCun"
    affiliations: ["Meta", "NYU"]

# Track papers citing these influential works
key_papers:
  - title: "Attention Is All You Need"
    arxiv_id: "1706.03762"
    track_citations: true
  - title: "BERT: Pre-training of Deep Bidirectional Transformers"
    arxiv_id: "1810.04805"
    track_citations: true

# Track specific journals
journals:
  - name: "Nature"
    url: "https://www.nature.com"
    sections: ["articles", "letters"]
  - name: "Science"
    url: "https://www.science.org"
  - name: "Nature Machine Intelligence"
    url: "https://www.nature.com/natmachintell"
  - name: "JMLR"
    url: "https://jmlr.org"
```

**config/social.yaml**
```yaml
# Free sources (always enabled)
reddit:
  enabled: true
  subreddits:
    - "MachineLearning"
    - "deeplearning"
    - "ArtificialIntelligence"
    - "computervision"
    - "LanguageTechnology"
  min_upvotes: 50
  track_keywords: ["paper", "research", "arxiv"]

hackernews:
  enabled: true
  keywords: ["paper", "research", "arxiv", "machine learning"]
  min_points: 100
  check_interval_hours: 6

github:
  enabled: true
  topics: ["machine-learning", "deep-learning", "artificial-intelligence"]
  track_paper_implementations: true  # Repos with arXiv links
  min_stars: 50

# Optional paid sources
twitter:
  enabled: false  # Requires paid API ($100+/month)
  hashtags: ["#MachineLearning", "#AI", "#DeepLearning", "#NeurIPS", "#ICLR"]
  track_users: ["ylecun", "goodfellow_ian", "karpathy"]
```

## Docker Deployment

**Dockerfile**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

**docker-compose.yml**
```yaml
services:
  research-pulse:
    build: .
    env_file:
      - .env
    volumes:
      - ./output:/app/output
      - ./config:/app/config
    restart: always
```

## Configuration Files

**.env** (API keys and secrets)
```bash
# LLM APIs (choose one or more)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
OLLAMA_HOST=http://localhost:11434

# Paper Sources
SERPAPI_KEY=...
SEMANTIC_SCHOLAR_KEY=...

# Social Media (Free APIs)
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
REDDIT_USER_AGENT=ResearchPulse/1.0
GITHUB_TOKEN=...  # Optional, increases rate limits

# Optional Paid APIs
TWITTER_BEARER_TOKEN=...  # Requires paid plan ($100+/month)

# Journal Scraping (if needed)
SPRINGER_API_KEY=...
ELSEVIER_API_KEY=...
```

**.env.example** (Template for users)
```bash
# Copy this to .env and fill in your keys
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
SERPAPI_KEY=
# ... (all keys with empty values)
```

## Deployment

```bash
# 1. Setup environment
cp .env.example .env
# Edit .env with your API keys

# 2. Configure tracking
# Edit config/tracking.yaml with your keywords, authors, papers, journals

# 3. Build container
docker-compose build

# 4. Run container
docker-compose up -d

# 5. View logs
docker logs -f research-pulse

# 6. Serve static output
docker run -p 8080:80 -v ./output:/usr/share/nginx/html nginx
```

## Daily Workflow

1. **Fetch papers** from multiple sources:
   - Keyword searches (arXiv, Google Scholar, Semantic Scholar, PubMed)
   - Author publications (tracked authors)
   - Citation tracking (papers citing key works)
   - Journal websites (Nature, Science, etc.)
2. **Collect social data** from Reddit, HackerNews, GitHub (all free APIs)
3. **Deduplicate & filter** papers
4. **Analyze with LLM**: summarize, extract insights
5. **Rank papers** by relevance + social buzz + author reputation
6. **Generate insights**: 5 research ideas + hot topics
7. **Build static site** with styled templates
8. **Deploy to server** (nginx/GitHub Pages)

## Output Example

**Daily Feed Page:**
```
📅 ResearchPulse - Nov 7, 2024

🔥 Hot Topics
- Multimodal LLMs for vision-language tasks
- Quantum error correction breakthroughs
- AI safety alignment research

💡 Research Ideas
1. Combining RL with diffusion models for robotics
2. Cross-lingual reasoning in small language models
...

📄 Papers (Ranked by Relevance + Buzz)
[Paper Card: Title, Authors, Summary, Social Mentions, ArXiv Link]
```

## Security

- Store all API keys in `.env` file (never commit to git)
- Add `.env` to `.gitignore`
- Use `.env.example` as template (no real keys)
- Use read-only volumes for config in Docker
- Rate limit API calls to avoid abuse
- Validate and sanitize external data
- Run container as non-root user
