# Detailed Article Processing

```mermaid
graph LR
    A[Date Selection] --> B[Article Retrieval]
    B --> C[Article Processing Pipeline]
    C --> D[Deduplication]
    D --> E[Length Filtering]

    subgraph "Retrieval Functions"
        F[NewsReader.get_articles_yesterday]
        G[NewsReader.get_articles_last_n_days]
        H[NewsReader.get_sources_summary]
    end

    subgraph "Processing Functions"
        I[ArticleProcessor.process_articles]
        J[ArticleProcessor.clean_content]
        K[ArticleProcessor.truncate_content]
        L[ArticleProcessor.process_article]
    end

    subgraph "Deduplication Functions"
        M[ArticleProcessor.deduplicate_articles]
    end

    subgraph "Filtering Functions"
        N[ArticleProcessor.filter_by_length]
    end

    B --> F
    B --> G
    B --> H

    C --> I
    I --> J
    I --> K
    I --> L

    D --> M
    E --> N