"""
Unit tests for the LLMAnalyzer class.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from analyzer import LLMAnalyzer
from fetchers.base import Paper
from datetime import datetime


class TestLLMAnalyzer:
    """Test cases for LLMAnalyzer."""

    @pytest.fixture
    def claude_config(self):
        """Configuration for Claude provider."""
        return {
            'provider': 'claude',
            'claude': {
                'model': 'claude-3-5-sonnet-20241022'
            },
            'tasks': {
                'summarization': True,
                'key_contributions': True
            }
        }

    @pytest.fixture
    def openai_config(self):
        """Configuration for OpenAI provider."""
        return {
            'provider': 'openai',
            'openai': {
                'model': 'gpt-4-turbo-preview'
            },
            'tasks': {
                'summarization': True,
                'key_contributions': True
            }
        }

    @pytest.fixture
    def sample_paper(self):
        """Create a sample paper for analysis."""
        return Paper(
            title="Attention Is All You Need",
            authors=["Vaswani, Ashish", "Shazeer, Noam"],
            abstract="We propose a new simple network architecture, the Transformer, based solely on attention mechanisms.",
            url="https://arxiv.org/abs/1706.03762",
            published_date=datetime(2017, 6, 12),
            source="arxiv",
            paper_id="paper123"
        )

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('analyzer.Anthropic')
    def test_analyzer_initialization_claude(self, mock_anthropic, claude_config):
        """Test LLMAnalyzer initialization with Claude."""
        analyzer = LLMAnalyzer(claude_config)

        assert analyzer.provider == 'claude'
        assert analyzer.model == 'claude-3-5-sonnet-20241022'
        mock_anthropic.assert_called_once_with(api_key='test-key')

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    @patch('analyzer.OpenAI')
    def test_analyzer_initialization_openai(self, mock_openai, openai_config):
        """Test LLMAnalyzer initialization with OpenAI."""
        analyzer = LLMAnalyzer(openai_config)

        assert analyzer.provider == 'openai'
        assert analyzer.model == 'gpt-4-turbo-preview'
        mock_openai.assert_called_once_with(api_key='test-key')

    @patch.dict('os.environ', {'GOOGLE_API_KEY': 'test-key'})
    @patch('analyzer.genai')
    def test_analyzer_initialization_gemini(self, mock_genai):
        """Test LLMAnalyzer initialization with Gemini."""
        config = {
            'provider': 'gemini',
            'gemini': {'model': 'gemini-pro'}
        }

        analyzer = LLMAnalyzer(config)

        assert analyzer.provider == 'gemini'
        assert analyzer.model == 'gemini-pro'
        mock_genai.configure.assert_called_once_with(api_key='test-key')

    @patch.dict('os.environ', {'OLLAMA_HOST': 'http://localhost:11434'})
    def test_analyzer_initialization_ollama(self):
        """Test LLMAnalyzer initialization with Ollama."""
        config = {
            'provider': 'ollama',
            'ollama': {'model': 'llama2'}
        }

        analyzer = LLMAnalyzer(config)

        assert analyzer.provider == 'ollama'
        assert analyzer.model == 'llama2'
        assert analyzer.ollama_host == 'http://localhost:11434'

    def test_analyzer_initialization_unknown_provider(self):
        """Test LLMAnalyzer raises error for unknown provider."""
        config = {'provider': 'unknown'}

        with pytest.raises(ValueError, match="Unknown LLM provider"):
            LLMAnalyzer(config)

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('analyzer.Anthropic')
    def test_summarize_paper_prompt_format(self, mock_anthropic, claude_config, sample_paper):
        """Test that summarization prompt is properly formatted."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        mock_response = Mock()
        mock_response.content = [Mock(text="Test summary")]
        mock_client.messages.create.return_value = mock_response

        analyzer = LLMAnalyzer(claude_config)
        summary = analyzer._summarize_paper(sample_paper)

        # Verify the prompt was sent
        call_args = mock_client.messages.create.call_args
        prompt = call_args[1]['messages'][0]['content']

        assert "Attention Is All You Need" in prompt
        assert "Vaswani, Ashish" in prompt
        assert "attention mechanisms" in prompt
        assert summary == "Test summary"

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('analyzer.Anthropic')
    def test_extract_contributions_parsing(self, mock_anthropic, claude_config, sample_paper):
        """Test that contributions are properly parsed from bullet points."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        mock_response = Mock()
        mock_response.content = [Mock(text="""
        • First contribution here
        • Second contribution
        - Third contribution with dash
        * Fourth contribution with asterisk
        """)]
        mock_client.messages.create.return_value = mock_response

        analyzer = LLMAnalyzer(claude_config)
        contributions = analyzer._extract_contributions(sample_paper)

        assert len(contributions) == 4
        assert contributions[0] == "First contribution here"
        assert contributions[1] == "Second contribution"
        assert contributions[2] == "Third contribution with dash"
        assert contributions[3] == "Fourth contribution with asterisk"

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('analyzer.Anthropic')
    def test_extract_contributions_limits_to_five(self, mock_anthropic, claude_config, sample_paper):
        """Test that contributions are limited to 5."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        # Create 10 bullet points
        bullet_points = "\n".join([f"• Contribution {i}" for i in range(10)])
        mock_response = Mock()
        mock_response.content = [Mock(text=bullet_points)]
        mock_client.messages.create.return_value = mock_response

        analyzer = LLMAnalyzer(claude_config)
        contributions = analyzer._extract_contributions(sample_paper)

        assert len(contributions) <= 5

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('analyzer.Anthropic')
    def test_analyze_paper_both_tasks(self, mock_anthropic, claude_config, sample_paper):
        """Test analyze_paper performs both summarization and contributions."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        mock_response = Mock()
        mock_response.content = [Mock(text="Test response")]
        mock_client.messages.create.return_value = mock_response

        analyzer = LLMAnalyzer(claude_config)
        analysis = analyzer.analyze_paper(sample_paper)

        assert 'summary' in analysis
        assert 'contributions' in analysis

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('analyzer.Anthropic')
    def test_analyze_paper_summarization_only(self, mock_anthropic, sample_paper):
        """Test analyze_paper with only summarization enabled."""
        config = {
            'provider': 'claude',
            'tasks': {
                'summarization': True,
                'key_contributions': False
            }
        }

        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        mock_response = Mock()
        mock_response.content = [Mock(text="Summary only")]
        mock_client.messages.create.return_value = mock_response

        analyzer = LLMAnalyzer(config)
        analysis = analyzer.analyze_paper(sample_paper)

        assert 'summary' in analysis
        assert 'contributions' not in analysis

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    @patch('analyzer.OpenAI')
    def test_generate_openai(self, mock_openai, openai_config):
        """Test _generate method with OpenAI provider."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="OpenAI response"))]
        mock_client.chat.completions.create.return_value = mock_response

        analyzer = LLMAnalyzer(openai_config)
        result = analyzer._generate("Test prompt")

        assert result == "OpenAI response"
        mock_client.chat.completions.create.assert_called_once()

    @patch.dict('os.environ', {'GOOGLE_API_KEY': 'test-key'})
    @patch('analyzer.genai')
    def test_generate_gemini(self, mock_genai):
        """Test _generate method with Gemini provider."""
        config = {'provider': 'gemini', 'gemini': {'model': 'gemini-pro'}}

        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "Gemini response"
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        analyzer = LLMAnalyzer(config)
        result = analyzer._generate("Test prompt")

        assert result == "Gemini response"

    @patch('analyzer.requests.post')
    def test_generate_ollama(self, mock_post):
        """Test _generate method with Ollama provider."""
        config = {'provider': 'ollama', 'ollama': {'model': 'llama2'}}

        mock_response = Mock()
        mock_response.json.return_value = {'response': 'Ollama response'}
        mock_post.return_value = mock_response

        analyzer = LLMAnalyzer(config)
        result = analyzer._generate("Test prompt")

        assert result == "Ollama response"
        mock_post.assert_called_once()

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('analyzer.Anthropic')
    def test_generate_error_handling(self, mock_anthropic, claude_config):
        """Test _generate handles errors gracefully."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("API Error")

        analyzer = LLMAnalyzer(claude_config)
        result = analyzer._generate("Test prompt")

        assert result == ""  # Returns empty string on error

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('analyzer.Anthropic')
    def test_batch_analyze(self, mock_anthropic, claude_config):
        """Test batch_analyze processes multiple papers."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        mock_response = Mock()
        mock_response.content = [Mock(text="• Contribution 1\n• Contribution 2")]
        mock_client.messages.create.return_value = mock_response

        papers = [
            Paper(f"Paper {i}", ["Author"], "Abstract", f"http://url{i}.com",
                  datetime.now(), "test", paper_id=f"paper{i}")
            for i in range(3)
        ]

        analyzer = LLMAnalyzer(claude_config)
        analyses = analyzer.batch_analyze(papers)

        assert len(analyses) == 3
        assert 'paper0' in analyses
        assert 'paper1' in analyses
        assert 'paper2' in analyses

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('analyzer.Anthropic')
    def test_batch_analyze_respects_max_papers(self, mock_anthropic, claude_config):
        """Test batch_analyze respects max_papers limit."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        mock_response = Mock()
        mock_response.content = [Mock(text="Test")]
        mock_client.messages.create.return_value = mock_response

        papers = [
            Paper(f"Paper {i}", ["Author"], "Abstract", f"http://url{i}.com",
                  datetime.now(), "test", paper_id=f"paper{i}")
            for i in range(100)
        ]

        analyzer = LLMAnalyzer(claude_config)
        analyses = analyzer.batch_analyze(papers, max_papers=10)

        assert len(analyses) == 10

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('analyzer.Anthropic')
    def test_batch_analyze_updates_paper_objects(self, mock_anthropic, claude_config):
        """Test batch_analyze updates paper objects with analysis."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        mock_response = Mock()
        mock_response.content = [Mock(text="Summary text\n• Contribution 1")]
        mock_client.messages.create.return_value = mock_response

        paper = Paper("Test Paper", ["Author"], "Abstract", "http://url.com",
                     datetime.now(), "test", paper_id="paper1")

        analyzer = LLMAnalyzer(claude_config)
        analyzer.batch_analyze([paper])

        assert paper.summary is not None
        assert paper.contributions is not None

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('analyzer.Anthropic')
    def test_analyze_paper_error_handling(self, mock_anthropic, claude_config, sample_paper):
        """Test analyze_paper handles errors gracefully."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("API Error")

        analyzer = LLMAnalyzer(claude_config)
        analysis = analyzer.analyze_paper(sample_paper)

        # Should return dict with empty values when errors occur
        assert 'summary' in analysis
        assert 'contributions' in analysis
        assert analysis['summary'] == ''
        assert analysis['contributions'] == []
