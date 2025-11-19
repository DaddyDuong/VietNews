# High-Level Architecture

```mermaid
graph LR
    subgraph Inputs
        A[RSS Feeds]
    end

    subgraph Internal
        B[Module 01: News Scraper & Aggregator]
        C[SQLite DB]
        D[Module 02: AI Bulletin Generator]
        E[Module 03: TTS Automation]
    end

    subgraph Outputs
        F[Audio Files (WAV)]
    end

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F