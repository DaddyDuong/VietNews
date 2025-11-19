# Data Flow Diagram

```mermaid
graph LR
    A[RSS Feeds] --> B[Module 01: Scraping/Aggregation]
    B --> C[Metadata (Titles, URLs, Dates)]
    C --> D[SQLite DB]
    D --> E[Content Scraping]
    E --> F[Full Article Content]
    F --> G[SQLite DB]
    G --> H[Module 02: AI Generation]
    H --> I[Processed Articles]
    I --> J[AI Clustering with Gemini]
    J --> K[Generated Bulletin Text]
    K --> L[Formatted Text for TTS (JSON/TXT)]
    L --> M[Module 03: TTS via Google Colab]
    M --> N[Text Input to ZipVoice Notebook]
    N --> O[TTS Synthesis]
    O --> P[WAV Audio Files]