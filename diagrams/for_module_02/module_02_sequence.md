# Module 02 Sequence Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant M as NewsBulletinModule
    participant NR as NewsReader
    participant AP as ArticleProcessor
    participant BG as BulletinGenerator
    participant TF as TTSFormatter
    participant BV as BulletinValidator

    U->>M: run(target_date)
    M->>M: Determine target date
    M->>NR: get_articles_yesterday()
    NR-->>M: articles
    alt Not enough articles
        M->>NR: get_articles_last_n_days(n=2)
        NR-->>M: articles
    end
    M->>AP: process_articles(articles)
    AP->>AP: clean_content()
    AP->>AP: deduplicate_articles()
    AP->>AP: filter_by_length()
    AP-->>M: processed_articles
    M->>BG: generate_bulletin_two_stage()
    BG->>BG: cluster_articles()
    BG->>BG: generate_bulletin()
    BG-->>M: bulletin_data
    M->>TF: format_bulletin()
    TF->>TF: format_for_tts()
    TF-->>M: tts_text
    M->>BV: validate_complete()
    BV-->>M: validation_result
    M->>M: _save_output()
    M->>M: _print_summary()