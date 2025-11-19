# Module 02 Detailed Architecture

```mermaid
graph LR
    subgraph "Main Entry Point"
        A[main.py]
        B[NewsBulletinModule]
    end

    subgraph "Database Layer"
        C[database/news_reader.py]
        D[NewsReader]
        E[get_articles_yesterday]
        F[get_articles_last_n_days]
        G[get_sources_summary]
    end

    subgraph "Gemini Client"
        H[gemini_client/client.py]
        I[GeminiClient]
        J[generate_structured]
        K[generate_text]
        L[gemini_client/prompts.py]
        M[create_bulletin_prompt]
        N[create_clustering_prompt]
        O[gemini_client/schemas.py]
        P[BULLETIN_SCHEMA]
        Q[CLUSTERING_SCHEMA]
    end

    subgraph "Processor Layer"
        R[processor/article_processor.py]
        S[ArticleProcessor]
        T[process_articles]
        U[deduplicate_articles]
        V[filter_by_length]
        W[processor/bulletin_generator.py]
        X[BulletinGenerator]
        Y[cluster_articles]
        Z[generate_bulletin_two_stage]
        AA[processor/text_formatter.py]
        BB[TTSFormatter]
        CC[format_bulletin]
        DD[normalize_acronyms_and_brands]
    end

    subgraph "Utils Layer"
        EE[utils/date_utils.py]
        FF[get_yesterday]
        GG[format_date_vietnamese]
        HH[utils/logger.py]
        II[setup_logger]
        JJ[utils/validator.py]
        KK[BulletinValidator]
        LL[validate_complete]
        MM[validate_vietnamese_text]
    end

    A --> B
    B --> D
    B --> S
    B --> X
    B --> BB
    B --> KK

    C --> D
    D --> E
    D --> F
    D --> G

    H --> I
    I --> J
    I --> K
    L --> M
    L --> N
    O --> P
    O --> Q

    R --> S
    S --> T
    S --> U
    S --> V
    W --> X
    X --> Y
    X --> Z
    AA --> BB
    BB --> CC
    BB --> DD

    EE --> FF
    EE --> GG
    HH --> II
    JJ --> KK
    KK --> LL
    KK --> MM