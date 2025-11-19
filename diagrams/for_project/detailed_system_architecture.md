# Detailed System Architecture

```mermaid
graph LR
    subgraph Module01 [Module 01: News Scraper & Aggregator]
        M1[main.py]
        C1[config.py]
        subgraph RP1 [rss_parser]
            F1[fetcher.py]
            P1[parser.py]
            CL1[cleaner.py]
        end
        subgraph S1 [scraper]
            CS1[content_scraper.py]
            CC1[content_cleaner.py]
        end
        subgraph DB1 [database]
            DM1[db_manager.py]
            SC1[schema.py]
        end
        subgraph U1 [utils]
            DU1[date_utils.py]
            L1[logger.py]
        end
    end

    subgraph DB [SQLite DB]
    end

    subgraph Module02 [Module 02: AI Bulletin Generator]
        M2[main.py]
        C2[config.py]
        subgraph DB2 [database]
            NR2[news_reader.py]
        end
        subgraph GC2 [gemini_client]
            CL2[client.py]
            PR2[prompts.py]
            SCH2[schemas.py]
        end
        subgraph PROC2 [processor]
            AP2[article_processor.py]
            BG2[bulletin_generator.py]
            TF2[text_formatter.py]
        end
        subgraph U2 [utils]
            DU2[date_utils.py]
            L2[logger.py]
            V2[validator.py]
        end
    end

    subgraph Module03 [Module 03: TTS Automation]
        M3[main.py]
        C3[config.py]
        subgraph CA3 [colab_automation]
            BD3[browser_driver.py]
            AH3[auth_handler.py]
            CI3[colab_interface.py]
            CE3[cell_executor.py]
        end
        subgraph IH3 [input_handler]
            BR3[bulletin_reader.py]
        end
        subgraph OH3 [output_handler]
            AD3[audio_downloader.py]
            FM3[file_manager.py]
        end
        subgraph U3 [utils]
            L3[logger.py]
            DU3[date_utils.py]
            RH3[retry_handler.py]
        end
    end

    A[RSS Feeds] --> Module01
    Module01 --> DB
    DB --> Module02
    Module02 --> B[Text Bulletins]
    B --> Module03
    Module03 --> C[Audio Files (WAV)]