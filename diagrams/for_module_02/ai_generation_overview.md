# AI Generation Overview

```mermaid
graph LR
    A[Clustering] --> B[Bulletin Generation]
    B --> C[TTS Formatting]
    C --> D[Validation]
    D --> E[Export]

    subgraph "AI Generation Steps"
        F[Cluster Articles by Topic]
        G[Generate Bulletin with AI]
        H[Format for Text-to-Speech]
        I[Validate Output Quality]
        J[Save to Files]
    end

    A --> F
    B --> G
    C --> H
    D --> I
    E --> J