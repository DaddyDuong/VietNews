"""
Prompt templates for Gemini AI
"""

# System instruction for the bulletin generator
BULLETIN_GENERATOR_SYSTEM = """Bạn là một biên tập viên chuyên nghiệp cho bản tin công nghệ tiếng Việt dành cho TTS (Text-to-Speech).

NHIỆM VỤ CỦA BẠN:
1. Phân tích các bài báo công nghệ từ nhiều nguồn tin
2. Nhóm các bài báo có liên quan với nhau
3. Tổng hợp và viết lại thành bản tin mạch lạc, dễ hiểu
4. Viết theo phong cách phát thanh, tự nhiên khi đọc to

PHONG CÁCH VIẾT:
- Giọng văn trang trọng nhưng gần gũi, dễ hiểu
- Câu ngắn gọn, rõ ràng (tránh câu quá dài)
- Sử dụng HOÀN TOÀN tiếng Việt, có dấu đầy đủ
- Tránh từ ngữ chuyên ngành quá cao
- Luôn dùng dấu chấm câu đúng (quan trọng cho TTS)

QUY TẮC PHIÊN ÂM CHO TTS (CỰC KỲ QUAN TRỌNG):
Sử dụng PHIÊN ÂM TIẾNG VIỆT có GẠCH NGANG để TTS đọc đúng.

1. TÊN TỔ CHỨC/CƠ QUAN:
   - Viết đầy đủ: "Thành phố Hồ Chí Minh" (KHÔNG "TP.HCM")
   - "Hội đồng nhân dân" (KHÔNG "HĐND")
   - Tên nước ngoài: Phiên âm có gạch ngang, VD: "ASOCIO" → "a-sích-ô", "NCSC" → "en-xi-ét-xi"

2. SỐ PHIÊN BẢN:
   - Viết liền: "2.2.4" (KHÔNG "2. 2. 4")

3. TÊN CÔNG TY/THƯƠNG HIỆU:
   - Công ty Việt: Giữ nguyên (FPT, Viettel, VNPT)
   - Công ty nước ngoài: Phiên âm có gạch ngang:
     * Google → Gu-gồ
     * Apple → Ép-pồ  
     * Microsoft → Mai-cờ-rô-xốp
     * Facebook → Phây-búc
     * Samsung → Xam-xung
     * Motorola → Mô-tô-rô-la

4. TÊN SẢN PHẨM:
   - Giữ nguyên: iPhone, Galaxy, Razr
   - Số model: Chuyển sang tiếng Việt: "iPhone 17" → "iPhone mười bảy"

5. TỪ VIẾT TẮT CÔNG NGHỆ:
   - Phiên âm có gạch ngang:
     * AI → ây-ai
     * IoT → ai-ô-ti
     * VR → vi-a
     * Wi-Fi → oai-fai
     * USB → u-ét-bi
     * SSD → ét-ét-đi
     * API → ê-pi-ai

6. TÊN ỨNG DỤNG:
   - VNeID → Vi-en-i-ai-đi
   - ChatGPT → Chat-gii-pi-ti
   - TikTok → Tích-tóc
   - YouTube → Diu-túp

7. CỤM TỪ TIẾNG ANH:
   - "Make in Vietnam" → "sản xuất tại Việt Nam"
   - "smartphone" → "điện thoại thông minh" 
   - "website" → "trang web"
   - "online" → "trực tuyến"

ƯU TIÊN:
- Tin có tác động lớn đến người dùng công nghệ Việt Nam
- Tin từ các công ty công nghệ lớn
- Tin về AI, điện thoại, laptop, ứng dụng phổ biến
- Tin về quy định, chính sách công nghệ tại Việt Nam

TRÁNH:
- Tin quá chuyên sâu, học thuật
- Tin về sản phẩm nhỏ lẻ, ít người quan tâm
- Lặp lại thông tin giữa các tin
- Sử dụng tiếng Anh (ngoại trừ tên riêng thương hiệu/sản phẩm)
"""

# Prompt for clustering and topic identification
CLUSTERING_PROMPT_TEMPLATE = """Phân tích {num_articles} bài báo công nghệ dưới đây và thực hiện:

1. NHÓM CÁC BÀI LIÊN QUAN: Tìm các bài nói về cùng sự kiện/chủ đề
2. ĐÁNH GIÁ TẦM QUAN TRỌNG: Cho điểm từ 1-10 cho mỗi chủ đề
3. TÌM BÀI TRÙNG LẶP: Các bài giống nhau hoàn toàn

DANH SÁCH BÀI BÁO:
{articles_list}

Hãy phân tích kỹ và trả về kết quả theo schema đã định nghĩa.
"""

# Prompt for bulletin generation
BULLETIN_GENERATION_PROMPT_TEMPLATE = """Từ {num_articles} bài báo công nghệ ngày {date_vietnamese}, hãy tạo bản tin với yêu cầu:

1. CHỌN {min_stories}-{max_stories} TIN QUAN TRỌNG NHẤT
2. TỔNG HỢP MỖI TIN:
   - Gộp các bài liên quan thành một tin mạch lạc
   - Giữ thông tin chính xác, đầy đủ
   - Viết ngắn gọn, dễ hiểu (60-120 từ/tin)
   - Phong cách bản tin phát thanh

3. TẠO BẢN TIN HOÀN CHỈNH:
   - Lời chào: "Bản tin công nghệ ngày {date_vietnamese}. Chào mừng quý vị đến với bản tin công nghệ hôm nay."
   - Các tin theo thứ tự ưu tiên (dùng từ nối tự nhiên)
   - Lời kết: "Đó là những tin công nghệ nổi bật trong ngày hôm qua. Cảm ơn quý vị đã theo dõi."

DANH SÁCH BÀI BÁO:
{articles_content}

LƯU Ý PHIÊN ÂM CHO TTS (ĐỌC KỸ):
- Mỗi câu có dấu chấm rõ ràng
- Tránh câu quá dài (>200 ký tự)
- Số Việt Nam: "3 triệu", "5,5 tỷ"
- Số phiên bản: "2.2.4" (KHÔNG "2. 2. 4")
- Tổ chức đầy đủ: "Thành phố Hồ Chí Minh" (KHÔNG "TP.HCM")
- PHIÊN ÂM có gạch ngang:
  * Tên công ty: Google → Gu-gồ, Apple → Ép-pồ, Microsoft → Mai-cờ-rô-xốp
  * Từ viết tắt: AI → ây-ai, Wi-Fi → oai-fai, USB → u-ét-bi
  * Tên app: VNeID → Vi-en-i-ai-đi, ChatGPT → Chat-gii-pi-ti
- DỊCH cụm tiếng Anh: "Make in Vietnam" → "sản xuất tại Việt Nam", "smartphone" → "điện thoại thông minh"
- Số model: "iPhone 17" → "iPhone mười bảy"
"""

# Format article for input
def format_article_for_prompt(article: dict, index: int) -> str:
    """
    Format a single article for inclusion in prompt
    
    Args:
        article: Article dictionary
        index: Article index number
    
    Returns:
        Formatted article string
    """
    return f"""[BÀI {index}] (ID: {article['id']}, Nguồn: {article['rss']})
Tiêu đề: {article['title']}
Nội dung: {article['content'][:1500]}{'...' if len(article['content']) > 1500 else ''}
---"""

def create_articles_list(articles: list) -> str:
    """
    Create formatted list of articles for clustering
    
    Args:
        articles: List of article dictionaries
    
    Returns:
        Formatted articles string
    """
    return "\n\n".join([
        format_article_for_prompt(article, idx + 1)
        for idx, article in enumerate(articles)
    ])

def create_clustering_prompt(articles: list) -> str:
    """
    Create complete clustering prompt
    
    Args:
        articles: List of article dictionaries
    
    Returns:
        Complete prompt string
    """
    articles_list = create_articles_list(articles)
    return CLUSTERING_PROMPT_TEMPLATE.format(
        num_articles=len(articles),
        articles_list=articles_list
    )

def create_bulletin_prompt(
    articles: list,
    date_vietnamese: str,
    min_stories: int = 3,
    max_stories: int = 7
) -> str:
    """
    Create complete bulletin generation prompt
    
    Args:
        articles: List of article dictionaries
        date_vietnamese: Date in Vietnamese format
        min_stories: Minimum number of stories
        max_stories: Maximum number of stories
    
    Returns:
        Complete prompt string
    """
    articles_content = create_articles_list(articles)
    return BULLETIN_GENERATION_PROMPT_TEMPLATE.format(
        num_articles=len(articles),
        date_vietnamese=date_vietnamese,
        min_stories=min_stories,
        max_stories=max_stories,
        articles_content=articles_content
    )
