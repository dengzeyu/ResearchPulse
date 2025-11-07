"""
Unit tests for the InsightsGenerator class.
"""
import pytest
from unittest.mock import Mock, patch
from insights import InsightsGenerator
from fetchers.base import Paper
from datetime import datetime


class TestInsightsGenerator:
    """Test cases for InsightsGenerator."""

    @pytest.fixture
    def basic_config(self):
        """Basic configuration for insights generator."""
        return {
            'provider': 'claude',
            'claude': {'model': 'claude-3-5-sonnet-20241022'},
            'research_ideas': {
                'count': 5,
                'prompt': 'Focus on practical applications.'
            },
            'hot_topics': {
                'count': 3,
                'prompt': 'Identify breakthrough trends.'
            }
        }

    @pytest.fixture
    def sample_papers(self):
        """Create sample papers with summaries."""
        papers = []
        for i in range(5):
            paper = Paper(
                title=f"Paper {i}: Machine Learning Research",
                authors=[f"Author {i}"],
                abstract=f"Abstract for paper {i} about transformers and attention mechanisms.",
                url=f"http://url{i}.com",
                published_date=datetime.now(),
                source="test",
                paper_id=f"paper{i}",
                keywords=["machine learning", "transformers", "attention"]
            )
            paper.summary = f"Summary of paper {i}"
            papers.append(paper)
        return papers

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('insights.Anthropic')
    def test_insights_initialization_claude(self, mock_anthropic, basic_config):
        """Test InsightsGenerator initialization with Claude."""
        generator = InsightsGenerator(basic_config)

        assert generator.provider == 'claude'
        assert generator.model == 'claude-3-5-sonnet-20241022'
        mock_anthropic.assert_called_once_with(api_key='test-key')

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    @patch('insights.OpenAI')
    def test_insights_initialization_openai(self, mock_openai):
        """Test InsightsGenerator initialization with OpenAI."""
        config = {
            'provider': 'openai',
            'openai': {'model': 'gpt-4-turbo-preview'}
        }

        generator = InsightsGenerator(config)

        assert generator.provider == 'openai'
        assert generator.model == 'gpt-4-turbo-preview'
        mock_openai.assert_called_once_with(api_key='test-key')

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('insights.Anthropic')
    def test_generate_research_ideas_empty_papers(self, mock_anthropic, basic_config):
        """Test generate_research_ideas with empty paper list."""
        generator = InsightsGenerator(basic_config)

        ideas = generator.generate_research_ideas([])

        assert ideas == []

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('insights.Anthropic')
    def test_generate_research_ideas_prompt_format(self, mock_anthropic, basic_config, sample_papers):
        """Test that research ideas prompt is properly formatted."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        mock_response = Mock()
        mock_response.content = [Mock(text="**Idea 1**\nDescription: Test\nWhy it matters: Impact")]
        mock_client.messages.create.return_value = mock_response

        generator = InsightsGenerator(basic_config)
        ideas = generator.generate_research_ideas(sample_papers)

        # Verify the prompt was sent
        call_args = mock_client.messages.create.call_args
        prompt = call_args[1]['messages'][0]['content']

        assert "generate 5 novel research ideas" in prompt
        assert "Paper 0: Machine Learning Research" in prompt
        assert "Focus on practical applications" in prompt

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('insights.Anthropic')
    def test_generate_research_ideas_limits_papers(self, mock_anthropic, basic_config):
        """Test that research ideas generation limits to top 20 papers."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        mock_response = Mock()
        mock_response.content = [Mock(text="")]
        mock_client.messages.create.return_value = mock_response

        # Create 30 papers
        papers = [
            Paper(f"Paper {i}", ["Author"], "Abstract", f"http://url{i}.com",
                  datetime.now(), "test", paper_id=f"paper{i}")
            for i in range(30)
        ]

        generator = InsightsGenerator(basic_config)
        generator.generate_research_ideas(papers)

        # Check prompt only includes top 20
        call_args = mock_client.messages.create.call_args
        prompt = call_args[1]['messages'][0]['content']

        assert "20. Paper 19" in prompt
        assert "21. Paper 20" not in prompt

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('insights.Anthropic')
    def test_parse_research_ideas(self, mock_anthropic, basic_config, sample_papers):
        """Test parsing research ideas from LLM response."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        llm_response = """
**Novel Transformer Architecture**
Description: A new approach to attention mechanisms that reduces computational complexity.
Why it matters: Could enable training of much larger models efficiently.

**Cross-Modal Learning Framework**
Description: Combining vision and language models for better understanding.
Why it matters: Improves performance on multimodal tasks.
"""

        mock_response = Mock()
        mock_response.content = [Mock(text=llm_response)]
        mock_client.messages.create.return_value = mock_response

        generator = InsightsGenerator(basic_config)
        ideas = generator.generate_research_ideas(sample_papers)

        assert len(ideas) == 2
        assert ideas[0]['title'] == "Novel Transformer Architecture"
        assert "attention mechanisms" in ideas[0]['description']
        assert "larger models" in ideas[0]['impact']
        assert ideas[1]['title'] == "Cross-Modal Learning Framework"

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('insights.Anthropic')
    def test_identify_hot_topics_empty_papers(self, mock_anthropic, basic_config):
        """Test identify_hot_topics with empty paper list."""
        generator = InsightsGenerator(basic_config)

        topics = generator.identify_hot_topics([])

        assert topics == []

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('insights.Anthropic')
    def test_identify_hot_topics_keyword_extraction(self, mock_anthropic, basic_config, sample_papers):
        """Test that hot topics uses keyword extraction."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        mock_response = Mock()
        mock_response.content = [Mock(text="**Topic**\nSummary: Test\nEvidence: 5 papers")]
        mock_client.messages.create.return_value = mock_response

        generator = InsightsGenerator(basic_config)
        topics = generator.identify_hot_topics(sample_papers)

        # Verify the prompt includes keywords
        call_args = mock_client.messages.create.call_args
        prompt = call_args[1]['messages'][0]['content']

        assert "Common keywords appearing:" in prompt
        assert "machine learning" in prompt.lower() or "transformers" in prompt.lower()

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('insights.Anthropic')
    def test_identify_hot_topics_limits_papers(self, mock_anthropic, basic_config):
        """Test that hot topics limits to top 30 papers."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        mock_response = Mock()
        mock_response.content = [Mock(text="")]
        mock_client.messages.create.return_value = mock_response

        # Create 40 papers
        papers = [
            Paper(f"Paper {i}", ["Author"], "Abstract", f"http://url{i}.com",
                  datetime.now(), "test", paper_id=f"paper{i}", keywords=["test"])
            for i in range(40)
        ]

        generator = InsightsGenerator(basic_config)
        generator.identify_hot_topics(papers)

        # Check prompt only includes top 30
        call_args = mock_client.messages.create.call_args
        prompt = call_args[1]['messages'][0]['content']

        assert "30. Paper 29" in prompt
        assert "31. Paper 30" not in prompt

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('insights.Anthropic')
    def test_parse_hot_topics(self, mock_anthropic, basic_config, sample_papers):
        """Test parsing hot topics from LLM response."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        llm_response = """
**Large Language Models**
Summary: Rapid advancement in model size and capability with GPT and BERT variants.
Evidence: 15 papers focusing on this area, including breakthrough results.

**Multimodal AI**
Summary: Integration of vision, text, and audio in unified models.
Evidence: 8 papers demonstrating cross-modal learning techniques.
"""

        mock_response = Mock()
        mock_response.content = [Mock(text=llm_response)]
        mock_client.messages.create.return_value = mock_response

        generator = InsightsGenerator(basic_config)
        topics = generator.identify_hot_topics(sample_papers)

        assert len(topics) == 2
        assert topics[0]['name'] == "Large Language Models"
        assert "model size" in topics[0]['summary']
        assert "15 papers" in topics[0]['evidence']
        assert topics[1]['name'] == "Multimodal AI"

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('insights.Anthropic')
    def test_generate_error_handling(self, mock_anthropic, basic_config):
        """Test _generate handles errors gracefully."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("API Error")

        generator = InsightsGenerator(basic_config)
        result = generator._generate("Test prompt")

        assert result == ""  # Returns empty string on error

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('insights.Anthropic')
    def test_generate_research_ideas_error_handling(self, mock_anthropic, basic_config, sample_papers):
        """Test generate_research_ideas handles errors gracefully."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("API Error")

        generator = InsightsGenerator(basic_config)
        ideas = generator.generate_research_ideas(sample_papers)

        assert ideas == []

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('insights.Anthropic')
    def test_identify_hot_topics_error_handling(self, mock_anthropic, basic_config, sample_papers):
        """Test identify_hot_topics handles errors gracefully."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("API Error")

        generator = InsightsGenerator(basic_config)
        topics = generator.identify_hot_topics(sample_papers)

        assert topics == []

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    @patch('insights.OpenAI')
    def test_generate_openai(self, mock_openai):
        """Test _generate with OpenAI provider."""
        config = {'provider': 'openai', 'openai': {'model': 'gpt-4'}}

        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="OpenAI response"))]
        mock_client.chat.completions.create.return_value = mock_response

        generator = InsightsGenerator(config)
        result = generator._generate("Test prompt")

        assert result == "OpenAI response"

    @patch.dict('os.environ', {'GOOGLE_API_KEY': 'test-key'})
    @patch('insights.genai')
    def test_generate_gemini(self, mock_genai):
        """Test _generate with Gemini provider."""
        config = {'provider': 'gemini', 'gemini': {'model': 'gemini-pro'}}

        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "Gemini response"
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        generator = InsightsGenerator(config)
        result = generator._generate("Test prompt")

        assert result == "Gemini response"

    @patch('insights.requests.post')
    def test_generate_ollama(self, mock_post):
        """Test _generate with Ollama provider."""
        config = {'provider': 'ollama', 'ollama': {'model': 'llama2'}}

        mock_response = Mock()
        mock_response.json.return_value = {'response': 'Ollama response'}
        mock_post.return_value = mock_response

        generator = InsightsGenerator(config)
        result = generator._generate("Test prompt")

        assert result == "Ollama response"

    def test_parse_research_ideas_incomplete_data(self):
        """Test parsing research ideas with incomplete data."""
        config = {'provider': 'claude'}

        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            with patch('insights.Anthropic'):
                generator = InsightsGenerator(config)

        # Response with incomplete idea (missing impact)
        response = """
**Incomplete Idea**
Description: This idea has no impact statement.
"""

        ideas = generator._parse_research_ideas(response)

        assert len(ideas) == 1
        assert ideas[0]['title'] == "Incomplete Idea"
        assert 'description' in ideas[0]
        # impact field might not be present

    def test_parse_hot_topics_incomplete_data(self):
        """Test parsing hot topics with incomplete data."""
        config = {'provider': 'claude'}

        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            with patch('insights.Anthropic'):
                generator = InsightsGenerator(config)

        # Response with incomplete topic (missing evidence)
        response = """
**Incomplete Topic**
Summary: This topic has no evidence.
"""

        topics = generator._parse_hot_topics(response)

        assert len(topics) == 1
        assert topics[0]['name'] == "Incomplete Topic"
        assert 'summary' in topics[0]

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key', 'ANTHROPIC_BASE_URL': 'https://custom.anthropic.com'})
    @patch('insights.Anthropic')
    def test_claude_custom_base_url_from_env(self, mock_anthropic):
        """Test Claude initialization with custom base URL from environment variable."""
        config = {'provider': 'claude', 'claude': {'model': 'claude-3-5-sonnet-20241022'}}
        generator = InsightsGenerator(config)

        assert generator.provider == 'claude'
        mock_anthropic.assert_called_once_with(api_key='test-key', base_url='https://custom.anthropic.com')

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('insights.Anthropic')
    def test_claude_custom_base_url_from_config(self, mock_anthropic):
        """Test Claude initialization with custom base URL from config file."""
        config = {
            'provider': 'claude',
            'claude': {
                'model': 'claude-3-5-sonnet-20241022',
                'base_url': 'https://config.anthropic.com'
            }
        }
        generator = InsightsGenerator(config)

        assert generator.provider == 'claude'
        mock_anthropic.assert_called_once_with(api_key='test-key', base_url='https://config.anthropic.com')

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key', 'ANTHROPIC_BASE_URL': 'https://env.anthropic.com'})
    @patch('insights.Anthropic')
    def test_claude_env_base_url_precedence(self, mock_anthropic):
        """Test that environment variable takes precedence over config file for Claude."""
        config = {
            'provider': 'claude',
            'claude': {
                'model': 'claude-3-5-sonnet-20241022',
                'base_url': 'https://config.anthropic.com'
            }
        }
        generator = InsightsGenerator(config)

        assert generator.provider == 'claude'
        # Environment variable should take precedence
        mock_anthropic.assert_called_once_with(api_key='test-key', base_url='https://env.anthropic.com')

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key', 'OPENAI_BASE_URL': 'https://custom.openai.com'})
    @patch('insights.OpenAI')
    def test_openai_custom_base_url_from_env(self, mock_openai):
        """Test OpenAI initialization with custom base URL from environment variable."""
        config = {'provider': 'openai', 'openai': {'model': 'gpt-4-turbo-preview'}}
        generator = InsightsGenerator(config)

        assert generator.provider == 'openai'
        mock_openai.assert_called_once_with(api_key='test-key', base_url='https://custom.openai.com')

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    @patch('insights.OpenAI')
    def test_openai_custom_base_url_from_config(self, mock_openai):
        """Test OpenAI initialization with custom base URL from config file."""
        config = {
            'provider': 'openai',
            'openai': {
                'model': 'gpt-4-turbo-preview',
                'base_url': 'https://config.openai.com'
            }
        }
        generator = InsightsGenerator(config)

        assert generator.provider == 'openai'
        mock_openai.assert_called_once_with(api_key='test-key', base_url='https://config.openai.com')

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key', 'OPENAI_BASE_URL': 'https://env.openai.com'})
    @patch('insights.OpenAI')
    def test_openai_env_base_url_precedence(self, mock_openai):
        """Test that environment variable takes precedence over config file for OpenAI."""
        config = {
            'provider': 'openai',
            'openai': {
                'model': 'gpt-4-turbo-preview',
                'base_url': 'https://config.openai.com'
            }
        }
        generator = InsightsGenerator(config)

        assert generator.provider == 'openai'
        # Environment variable should take precedence
        mock_openai.assert_called_once_with(api_key='test-key', base_url='https://env.openai.com')

    def test_ollama_custom_base_url_from_config(self):
        """Test Ollama initialization with custom base URL from config file."""
        config = {
            'provider': 'ollama',
            'ollama': {
                'model': 'llama2',
                'base_url': 'http://custom.ollama.host:11434'
            }
        }
        generator = InsightsGenerator(config)

        assert generator.provider == 'ollama'
        assert generator.ollama_host == 'http://custom.ollama.host:11434'

    @patch.dict('os.environ', {'OLLAMA_HOST': 'http://env.ollama.host:11434'})
    def test_ollama_env_precedence_over_config(self):
        """Test that OLLAMA_HOST environment variable takes precedence over config."""
        config = {
            'provider': 'ollama',
            'ollama': {
                'model': 'llama2',
                'base_url': 'http://config.ollama.host:11434'
            }
        }
        generator = InsightsGenerator(config)

        assert generator.provider == 'ollama'
        # Environment variable should take precedence
        assert generator.ollama_host == 'http://env.ollama.host:11434'
