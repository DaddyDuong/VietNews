# Module 02 Data Flow

```mermaid
graph LR
    A[Database Articles] --> B[Raw Articles List]
    B --> C[Processed Articles]
    C --> D[Clustered Topics]
    D --> E[Bulletin Data]
    E --> F[TTS Text]
    F --> G[Validated Output]
    G --> H[Saved Files]

    subgraph "Data Transformations"
        I[ArticleProcessor.process_articles]
        J[BulletinGenerator.cluster_articles]
        K[BulletinGenerator.generate_bulletin_two_stage]
        L[TTSFormatter.format_bulletin]
        M[BulletinValidator.validate_complete]
        N[NewsBulletinModule._save_output]
    end

    B --> I
    I --> C
    C --> J
    J --> D
    D --> K
    K --> E
    E --> L
    L --> F
    F --> M
    M --> G
    G --> N
    N --> H