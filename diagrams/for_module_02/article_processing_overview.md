# Article Processing Overview

```mermaid
graph LR
    A[Date Selection] --> B[Article Retrieval]
    B --> C[Article Cleaning]
    C --> D[Deduplication]
    D --> E[Length Filtering]

    subgraph "Processing Steps"
        F[Determine Target Date]
        G[Query Database]
        H[Clean Content & Titles]
        I[Remove Duplicates]
        J[Filter by Content Length]
    end

    A --> F
    B --> G
    C --> H
    D --> I
    E --> J