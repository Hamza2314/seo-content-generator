# ⚖️ Legal SEO Content Generator

An AI-powered Streamlit application that generates SEO-optimized legal content in German, specifically designed for law firms specializing.

## Features

### 📝 Article Generator
- **Automated Content Generation**: Creates comprehensive legal articles on any criminal law topic
- **SEO Keyword Research**: Integrates with SEMrush API to find relevant keywords
- **Legal Verification**: Automatically checks and corrects legal information for accuracy
- **Humanization**: Reduces AI detection while maintaining legal precision
- **Multi-stage Pipeline**:
  1. Outline generation
  2. Content creation
  3. Legal verification
  4. SEO optimization
  5. Humanization

### 🖼️ Image Generator
- Generate professional legal-themed images using DALL-E 3
- Two styles: Realistic and Iconic illustrations
- Customizable size and quality options

## Prerequisites

- Python 3.9+
- API Keys:
  - **Anthropic Claude API** (for content generation)
  - **OpenAI API** (for image generation)
  - **SEMrush API** (for keyword research)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Hamza2314/seo-content-generator.git
cd seo-content-generator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:
```env
CLAUDE_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key
SEMRUSH_API_KEY=your_semrush_api_key
```

## Usage

### Run Locally
```bash
streamlit run app.py
```


## Tech Stack

- **Frontend**: Streamlit
- **AI Models**: 
  - Anthropic Claude Sonnet 4.5 (content generation)
  - OpenAI DALL-E 3 (image generation)
- **SEO**: SEMrush API
- **Language**: Python 3.9+

## Notes

- All generated content is in German
- Optimized for criminal law topics (Strafrecht)
- Articles go through 5-stage quality pipeline
- Legal information is automatically verified for accuracy

## License

Private project - All rights reserved

## Author

Hamza - [GitHub](https://github.com/Hamza2314)