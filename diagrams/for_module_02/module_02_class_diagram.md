# Module 02 Class Diagram

```mermaid
classDiagram
    class NewsBulletinModule {
        +NewsReader news_reader
        +ArticleProcessor article_processor
        +TTSFormatter tts_formatter
        +BulletinValidator validator
        +GeminiClient gemini_client
        +BulletinGenerator bulletin_generator
        +run(target_date, use_two_stage)
        -_retrieve_articles(target_date)
        -_process_articles(articles)
        -_generate_bulletin(articles, date_viet, use_two_stage)
        -_format_for_tts(bulletin_data)
        -_validate_output(bulletin_data, tts_text)
        -_save_output(date_iso, bulletin_data, tts_text, validation)
        -_print_summary(bulletin_data, validation)
    }

    class NewsReader {
        +__init__(db_path)
        +get_articles_yesterday(reference_date, min_content_length)
        +get_articles_last_n_days(n_days, reference_date, min_content_length)
        +get_sources_summary(articles)
    }

    class ArticleProcessor {
        +process_articles(articles)
        +deduplicate_articles(articles)
        +filter_by_length(articles, min_length, max_length)
        -clean_content(content)
        -truncate_content(content, max_length)
        -process_article(article)
    }

    class BulletinGenerator {
        +GeminiClient client
        +__init__(gemini_client)
        +cluster_articles(articles, include_thoughts)
        +generate_bulletin(articles, date_vietnamese, min_stories, max_stories, include_thoughts)
        +generate_bulletin_two_stage(articles, date_vietnamese, min_stories, max_stories, include_thoughts)
    }

    class TTSFormatter {
        +format_bulletin(bulletin_text, add_intro, add_outro)
        -format_for_tts(text)
        -normalize_acronyms_and_brands(text)
        -fix_spacing(text)
        -add_pauses(text)
        -split_long_sentences(text, max_length)
    }

    class BulletinValidator {
        +validate_complete(bulletin, full_text)
        -validate_bulletin_structure(bulletin)
        -validate_vietnamese_text(text)
        -validate_tts_compatibility(text)
    }

    class GeminiClient {
        +__init__(api_key, model, fallback_model, generation_config, thinking_config, max_retries, retry_delay, retry_backoff)
        +generate_structured(prompt, schema, system_instruction, include_thoughts)
        +generate_text(prompt, system_instruction, use_thinking)
    }

    NewsBulletinModule --> NewsReader
    NewsBulletinModule --> ArticleProcessor
    NewsBulletinModule --> BulletinGenerator
    NewsBulletinModule --> TTSFormatter
    NewsBulletinModule --> BulletinValidator
    BulletinGenerator --> GeminiClient