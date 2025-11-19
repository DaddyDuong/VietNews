# General System Overview

```mermaid
graph LR
    A[RSS Feeds] --> B[Module 01: News Scraper & Aggregator]
    B --> C[SQLite DB]
    C --> D[Module 02: AI Bulletin Generator]
    D --> E[Text Bulletins]
    E --> F[Module 03: TTS Automation]
    F --> G[Audio Files (WAV)]