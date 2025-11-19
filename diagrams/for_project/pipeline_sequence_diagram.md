# Pipeline Sequence Diagram

```mermaid
sequenceDiagram
    participant RP as run_pipeline.py
    participant M1 as module_01/main.py
    participant DB as SQLite DB
    participant M2 as module_02/main.py
    participant M3 as module_03/main.py

    RP->>M1: Execute news scraping and aggregation
    M1->>DB: Store scraped data
    DB-->>M1: Data stored
    M1-->>RP: Scraping completed

    RP->>M2: Execute AI bulletin generation
    M2->>DB: Retrieve articles
    DB-->>M2: Articles retrieved
    M2->>M2: Process and generate bulletins
    M2-->>RP: Bulletins generated

    RP->>M3: Execute TTS synthesis
    M3->>M3: Read bulletins and perform TTS
    M3-->>RP: Audio files created