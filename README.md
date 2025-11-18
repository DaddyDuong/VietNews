# VietNews - Vietnamese Tech News to Audio Pipeline

An end-to-end automated system that transforms Vietnamese technology news into broadcast-ready audio bulletins using RSS aggregation, AI-powered content generation, and text-to-speech synthesis.

## 🎯 Overview

This pipeline consists of three interconnected modules that work together to:

1. **Module 01**: Scrape and aggregate Vietnamese tech news from multiple RSS sources
2. **Module 02**: Generate AI-powered news bulletins using Google Gemini
3. **Module 03**: Convert bulletins to natural Vietnamese speech via Google Colab TTS

### Pipeline Flow

```
[RSS Feeds] → Module 01 → [SQLite DB] → Module 02 → [Text Bulletins] → Module 03 → [Audio Files]
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Chrome or Chromium browser (for Module 03)
- Google Gemini API key ([Get one here](https://aistudio.google.com/apikey))
- Google account with Colab access

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/DaddyDuong/VietNews.git
   cd VietNews
   ```

2. **Install dependencies**:
   ```bash
   # Install all dependencies at once
   pip install -r module_01/requirements.txt
   pip install -r module_02/requirements.txt
   pip install -r module_03/requirements.txt
   ```

3. **Configure Module 02 (Gemini API)**:
   ```bash
   # Create .env file in module_02
   echo "GEMINI_API_KEY=your_api_key_here" > module_02/.env
   ```

4. **Configure Module 03 (Colab Authentication)**:
   
   **Option A - Cookie-based (Recommended)**:
   - Login to Google Colab in your browser
   - Export cookies to `module_03/colab_cookies.json` using a browser extension
   - [EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie) for Chrome
   
   **Option B - Manual login**:
   - Set `AUTH_METHOD = "manual"` in `module_03/config.py`
   - Browser will open for login during execution

5. **Set Colab Notebook URL** (in `module_03/config.py`):
   ```python
   COLAB_NOTEBOOK_URL = "https://colab.research.google.com/drive/YOUR_NOTEBOOK_ID"
   ```

### Running the Pipeline

**Run everything (recommended)**:
```bash
python run_pipeline.py
```

**Run for a specific date**:
```bash
python run_pipeline.py --date 2025-11-15
```

**Run individual modules**:
```bash
python run_pipeline.py --modules 2 3  # Skip news scraping
python run_pipeline.py --skip-scraping  # Same as above
```

**Dry run (see what would execute)**:
```bash
python run_pipeline.py --dry-run
```

**Continue on errors**:
```bash
python run_pipeline.py --continue-on-error
```

## 📁 Project Structure

```
VietNews/
├── run_pipeline.py           # Master orchestrator (run this!)
├── README.md                 # This file
├── .gitignore               # Git ignore rules
│
├── module_01/               # News Scraper & Aggregator
│   ├── main.py              # Module entry point
│   ├── config.py            # RSS feeds & settings
│   ├── requirements.txt
│   ├── database/            # SQLite operations
│   ├── rss_parser/          # RSS fetching & parsing
│   ├── scraper/             # Web scraping & cleaning
│   ├── utils/               # Utilities
│   └── output/
│       └── news.db          # Article database
│
├── module_02/               # AI Bulletin Generator
│   ├── main.py              # Module entry point
│   ├── config.py            # Gemini & generation settings
│   ├── .env                 # API keys (create this!)
│   ├── requirements.txt
│   ├── database/            # Database reader
│   ├── gemini_client/       # Gemini API client
│   ├── processor/           # Processing & formatting
│   ├── utils/               # Utilities
│   └── output/
│       ├── YYYY-MM-DD.json  # Structured bulletin
│       └── YYYY-MM-DD.txt   # TTS-ready text
│
└── module_03/               # TTS Automation
    ├── main.py              # Module entry point
    ├── config.py            # Colab & browser settings
    ├── colab_cookies.json   # Google auth cookies (create this!)
    ├── requirements.txt
    ├── colab_automation/    # Selenium automation
    ├── input_handler/       # Bulletin reading
    ├── output_handler/      # Audio downloading
    ├── utils/               # Utilities
    ├── logs/                # Execution logs
    └── output/
        └── YYYY-MM-DD.wav   # Generated audio
```

## 🔧 Module Details

### Module 01: News Scraper & Aggregator

**Purpose**: Collect Vietnamese tech news from RSS feeds and scrape full article content.

**Features**:
- Multi-source RSS aggregation (VnExpress, Tuoi Tre, Thanh Nien, Dan Tri, VTV)
- Duplicate detection via link-based deduplication
- Site-specific content extractors
- Video article filtering
- Retry logic with exponential backoff

**Run standalone**:
```bash
cd module_01
python main.py
```

**Configuration**: Edit `module_01/config.py` to:
- Add/remove RSS feeds
- Adjust scraping timeouts
- Set start date for initial collection

**Output**: SQLite database at `module_01/output/news.db`

### Module 02: AI Bulletin Generator

**Purpose**: Transform raw articles into structured, TTS-ready Vietnamese bulletins using Gemini AI.

**Features**:
- Two-stage AI processing (clustering + synthesis)
- Automatic duplicate removal
- Topic clustering and priority scoring
- Vietnamese text normalization for TTS
- Number-to-word conversion (2025 → "hai không hai mươi lăm")
- Acronym expansion (AI → "ây-ai")

**Run standalone**:
```bash
cd module_02
python main.py --date yesterday
```

**Configuration**: Edit `module_02/config.py` to:
- Adjust generation parameters (temperature, tokens)
- Set min/max stories per bulletin
- Customize Vietnamese formatting

**Output**:
- JSON: `module_02/output/YYYY-MM-DD.json` (structured data)
- TXT: `module_02/output/YYYY-MM-DD.txt` (TTS-ready)

### Module 03: TTS Automation via Google Colab

**Purpose**: Automate Vietnamese TTS generation using a Google Colab notebook.

**Features**:
- Selenium-based browser automation
- Cookie-based Google authentication
- Colab runtime management
- Automatic cell execution
- Audio download and organization

**Run standalone**:
```bash
cd module_03
python main.py --date yesterday
```

**Configuration**: Edit `module_03/config.py` to:
- Set Colab notebook URL
- Configure authentication method
- Adjust timeouts and cell indices
- Enable/disable headless mode

**Output**: WAV audio file at `module_03/output/YYYY-MM-DD.wav`

## 🔄 Typical Workflow

### Daily Automated Execution (via cron)

```bash
# Add to crontab (crontab -e)
0 6 * * * cd /path/to/VietNews && /usr/bin/python3 run_pipeline.py >> /var/log/vietnews.log 2>&1
```

This runs the full pipeline daily at 6 AM and logs output.

### Manual Execution

**Generate today's bulletin**:
```bash
python run_pipeline.py --date today
```

**Regenerate bulletin for existing data** (skip scraping):
```bash
python run_pipeline.py --date 2025-11-15 --skip-scraping
```

**Debug with visible browser**:
```bash
python run_pipeline.py --no-headless
```

## 🛠️ Troubleshooting

### Module 01 Issues

**Problem**: No articles scraped  
**Solution**: Check RSS feed URLs in `config.py`, verify internet connection

**Problem**: Content extraction fails  
**Solution**: Website structure may have changed; update selectors in `scraper/content_scraper.py`

### Module 02 Issues

**Problem**: `GEMINI_API_KEY not found`  
**Solution**: Create `module_02/.env` with your API key

**Problem**: Insufficient articles  
**Solution**: Module automatically falls back to 2-day aggregation; check database has articles

**Problem**: API quota exceeded  
**Solution**: Wait for quota reset or upgrade Gemini API plan

### Module 03 Issues

**Problem**: Authentication fails  
**Solution**: 
- Re-export cookies from browser
- Switch to manual authentication: `--auth-method manual`

**Problem**: Colab runtime timeout  
**Solution**: Increase `COLAB_RUNTIME_CONNECT_TIMEOUT` in config.py

**Problem**: Cell execution fails  
**Solution**: 
- Verify cell indices in config.py match your notebook
- Run with `--no-headless` to see what's happening

**Problem**: Audio download fails  
**Solution**: Check Colab output path and download permissions

### General Issues

**Problem**: Pipeline stops mid-execution  
**Solution**: Use `--continue-on-error` to proceed despite failures

**Problem**: Date parsing errors  
**Solution**: Use ISO format `YYYY-MM-DD` for dates

## 📊 Output Examples

### Bulletin JSON Structure
```json
{
  "date": "2025-11-15",
  "date_vietnamese": "ngày 15 tháng 11 năm 2025",
  "stories": [
    {
      "title": "Google ra mắt Gemini 2.0",
      "priority": 9,
      "content": "Google vừa công bố...",
      "sources": ["vnexpress", "tuoitre"]
    }
  ]
}
```

### Bulletin TXT Format (TTS-ready)
```
Bản tin công nghệ ngày 15 tháng 11 năm 2025

Tin nổi bật đầu tiên: Google ra mắt Gemini hai chấm không

Google vừa công bố phiên bản Gemini hai chấm không...
```

## 🔐 Security & Privacy

- **API Keys**: Store in `.env` files (not tracked by git)
- **Cookies**: Store in `colab_cookies.json` (not tracked by git)
- **Database**: Contains only public news articles
- **Logs**: May contain URLs and metadata (review before sharing)

## 📝 License

This project is provided as-is for educational and personal use.

## 🤝 Contributing

This is an academic project. For questions or improvements:
1. Check existing issues
2. Create detailed bug reports
3. Submit pull requests with clear descriptions

## 📧 Contact

- Repository: [DaddyDuong/VietNews](https://github.com/DaddyDuong/VietNews)
- Issues: [GitHub Issues](https://github.com/DaddyDuong/VietNews/issues)

## 🙏 Acknowledgments

- **VnExpress, Tuoi Tre, Thanh Nien, Dan Tri, VTV**: News sources
- **Google Gemini**: AI bulletin generation
- **ZipVoice**: Vietnamese TTS model
- **BeautifulSoup, Selenium, feedparser**: Core libraries

## 📚 Additional Resources

- [Gemini API Documentation](https://ai.google.dev/docs)
- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [Google Colab Guide](https://colab.research.google.com/)

## 🔄 Version History

- **v1.0** (2025-11): Initial release with 3-module pipeline

## 🎯 Roadmap

- [ ] Multi-language support
- [ ] Alternative TTS providers
- [ ] Web dashboard for monitoring
- [ ] Email notification system
- [ ] Podcast RSS feed generation
- [ ] Incremental scraping optimization
- [ ] Distributed execution support

---

**Made with ❤️ for Vietnamese tech news enthusiasts**
