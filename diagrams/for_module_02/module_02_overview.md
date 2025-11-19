# Module 02 Overview

```mermaid
graph LR
    A[Database] --> B[Article Retrieval]
    B --> C[Article Processing]
    C --> D[AI Generation]
    D --> E[TTS Formatting]
    E --> F[Validation]
    F --> G[Export]

    subgraph "Main Components"
        H[database/news_reader.py]
        I[gemini_client/]
        J[processor/]
        K[utils/]
    end

    A --> H
    I --> D
    J --> C
    J --> D
    J --> E
    K --> F