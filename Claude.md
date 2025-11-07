# Paper Feed

AI-powered research paper aggregator that generates daily insights, research ideas, and trending topics. Runs as a Docker container and publishes to a static blog.

## Core Structure

```
/
├── src/
│   ├── fetchers/          # Paper sources (arXiv, Google Scholar, Semantic Scholar, PubMed)
│   ├── social/            # Social media APIs (Twitter/X, Reddit, HackerNews)
│   ├── analyzer.py        # LLM-powered paper analysis
│   ├── insights.py        # Generate research ideas & hot topics
│   ├── processor.py       # Filter, rank, deduplicate papers
│   └── generator.py       # Static site generation
├── templates/
│   ├── index.html         # Blog homepage template
│   ├── daily.html         # Daily feed page template
│   └── paper.html         # Individual paper card
├── config/
│   ├── queries.yaml       # Research areas & keywords
│   ├── llm.yaml           # LLM provider configs
│   └── social.yaml        # Social media configs
├── output/                # Generated static site
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
- Twitter/X API - trending research hashtags
- Reddit API - r/MachineLearning, r/science posts
- HackerNews API - paper discussions

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

**src/social/twitter.py**
```python
class TwitterFetcher:
    def get_trending_papers(self, hashtags: List[str]) -> List[Tweet]
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

**config/queries.yaml**
```yaml
areas:
  - name: "Machine Learning"
    keywords: ["neural networks", "transformers", "LLMs"]
    sources: ["arxiv", "google_scholar"]
  - name: "Quantum Computing"
    keywords: ["quantum algorithms", "qubits"]
    sources: ["arxiv", "semantic_scholar"]
```

**config/social.yaml**
```yaml
twitter:
  hashtags: ["#MachineLearning", "#AI", "#DeepLearning"]
reddit:
  subreddits: ["MachineLearning", "deeplearning", "ArtificialIntelligence"]
hackernews:
  keywords: ["paper", "research", "arxiv"]
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
  paper-feed:
    build: .
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - TWITTER_API_KEY=${TWITTER_API_KEY}
      - REDDIT_API_KEY=${REDDIT_API_KEY}
    volumes:
      - ./output:/app/output
      - ./config:/app/config
    restart: always
```

## Environment Variables

```bash
# LLM APIs (choose one or more)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
OLLAMA_HOST=http://localhost:11434  # For local models

# Paper Sources
SERPAPI_KEY=...
SEMANTIC_SCHOLAR_KEY=...

# Social Media
TWITTER_API_KEY=...
TWITTER_API_SECRET=...
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
```

## Deployment

```bash
# Build container
docker-compose build

# Run with environment variables
docker-compose up -d

# View logs
docker logs -f paper-feed

# Serve static output
docker run -p 8080:80 -v ./output:/usr/share/nginx/html nginx
```

## Daily Workflow

1. **Fetch papers** from academic sources (last 24h)
2. **Collect social data** from Twitter/Reddit/HN
3. **Analyze with LLM**: summarize, extract insights
4. **Rank papers** by relevance + social buzz
5. **Generate insights**: 5 research ideas + hot topics
6. **Build static site** with styled templates
7. **Deploy to server** (nginx/GitHub Pages)

## Output Example

**Daily Feed Page:**
```
📅 Research Feed - Nov 7, 2024

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

- Store all API keys in environment variables
- Use read-only volumes for config
- Rate limit API calls
- Validate external data
- Run container as non-root user
