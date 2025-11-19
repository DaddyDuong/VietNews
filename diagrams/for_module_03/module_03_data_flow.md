# Module 03 Data Flow

Short: Data flow for Module 03 (from text bulletins to WAV audio output).

```mermaid
graph LR
    A[Text Bulletins] --> B[Read Bulletin]
    B --> C[Init Browser]
    C --> D[Authenticate]
    D --> E[Open Colab]
    E --> F[Connect Runtime]
    F --> G[Insert Text]
    G --> H[Execute Cells]
    H --> I[Download Audio]
    I --> J[WAV Audio Files]
```
