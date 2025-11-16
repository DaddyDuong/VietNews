"""
JSON schemas for Gemini structured output
"""

# Schema for individual story in the bulletin
STORY_SCHEMA = {
    "type": "object",
    "properties": {
        "topic": {
            "type": "string",
            "description": "Tên chủ đề của tin tức (ngắn gọn, 3-8 từ)"
        },
        "priority": {
            "type": "integer",
            "description": "Mức độ ưu tiên từ 1-10 (10 = quan trọng nhất)",
            "minimum": 1,
            "maximum": 10
        },
        "content": {
            "type": "string",
            "description": "Nội dung tin tức đã tổng hợp, viết theo phong cách bản tin phát thanh tiếng Việt, dễ đọc và tự nhiên"
        },
        "sources": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Danh sách các nguồn tin (rss identifiers)"
        },
        "keywords": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Các từ khóa chính của tin này (3-5 từ)"
        }
    },
    "required": ["topic", "priority", "content", "sources"]
}

# Schema for the complete bulletin
BULLETIN_SCHEMA = {
    "type": "object",
    "properties": {
        "bulletin_date": {
            "type": "string",
            "description": "Ngày của bản tin (định dạng YYYY-MM-DD)"
        },
        "summary": {
            "type": "string",
            "description": "Tóm tắt ngắn gọn về các tin chính trong ngày (1-2 câu)"
        },
        "total_articles_processed": {
            "type": "integer",
            "description": "Tổng số bài báo đã xử lý"
        },
        "stories": {
            "type": "array",
            "items": STORY_SCHEMA,
            "description": "Danh sách các tin đã tổng hợp, sắp xếp theo độ ưu tiên từ cao đến thấp",
            "minItems": 1
        },
        "full_bulletin": {
            "type": "string",
            "description": "Toàn bộ nội dung bản tin hoàn chỉnh, sẵn sàng cho TTS, bao gồm lời chào, các tin tức, và lời kết"
        }
    },
    "required": ["bulletin_date", "summary", "total_articles_processed", "stories", "full_bulletin"]
}

# Schema for topic clustering (preprocessing step)
CLUSTERING_SCHEMA = {
    "type": "object",
    "properties": {
        "clusters": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Tên chủ đề chung"
                    },
                    "article_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Danh sách ID các bài báo thuộc chủ đề này"
                    },
                    "importance_score": {
                        "type": "integer",
                        "description": "Điểm đánh giá tầm quan trọng (1-10)",
                        "minimum": 1,
                        "maximum": 10
                    },
                    "reason": {
                        "type": "string",
                        "description": "Lý do đánh giá mức độ quan trọng"
                    }
                },
                "required": ["topic", "article_ids", "importance_score"]
            }
        },
        "duplicates": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "primary_id": {
                        "type": "integer",
                        "description": "ID bài chính (đầy đủ nhất)"
                    },
                    "duplicate_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "ID các bài trùng lặp"
                    }
                },
                "required": ["primary_id", "duplicate_ids"]
            }
        }
    },
    "required": ["clusters"]
}
