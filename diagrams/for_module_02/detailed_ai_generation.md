# Detailed AI Generation

```mermaid
graph LR
    A[Clustering] --> B[Bulletin Generation]
    B --> C[TTS Formatting]
    C --> D[Validation]
    D --> E[Export]

    subgraph "Clustering Functions"
        F[BulletinGenerator.cluster_articles]
        G[GeminiClient.generate_structured]
        H[CLUSTERING_SCHEMA]
    end

    subgraph "Bulletin Generation Functions"
        I[BulletinGenerator.generate_bulletin_two_stage]
        J[BulletinGenerator.generate_bulletin]
        K[create_bulletin_prompt]
        L[BULLETIN_SCHEMA]
    end

    subgraph "TTS Formatting Functions"
        M[TTSFormatter.format_bulletin]
        N[TTSFormatter.format_for_tts]
        O[TTSFormatter.normalize_acronyms_and_brands]
        P[TTSFormatter.fix_spacing]
        Q[TTSFormatter.add_pauses]
    end

    subgraph "Validation Functions"
        R[BulletinValidator.validate_complete]
        S[BulletinValidator.validate_bulletin_structure]
        T[BulletinValidator.validate_vietnamese_text]
        U[BulletinValidator.validate_tts_compatibility]
    end

    subgraph "Export Functions"
        V[NewsBulletinModule._save_output]
    end

    A --> F
    F --> G
    F --> H

    B --> I
    B --> J
    J --> K
    J --> L

    C --> M
    M --> N
    N --> O
    N --> P
    N --> Q

    D --> R
    R --> S
    R --> T
    R --> U

    E --> V