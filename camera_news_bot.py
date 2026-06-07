import feedparser
import requests
import json
from datetime import datetime, timedelta
from deep_translator import GoogleTranslator
from html.parser import HTMLParser
from config import KAKAO_REST_API_KEY, KAKAO_CLIENT_SECRET, KAKAO_ACCESS_TOKEN, KAKAO_REFRESH_TOKEN

class _HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ' '.join(self.fed).strip()

def strip_html(html):
    s = _HTMLStripper()
    s.feed(html)
    return s.get_data()

def translate_ko(text):
    try:
        return GoogleTranslator(source='auto', target='ko').translate(text[:500])
    except:
        return text

REDDIT_FEEDS = [
    ("photography", "https://www.reddit.com/r/photography/top/.rss?t=week"),
    ("videography", "https://www.reddit.com/r/videography/top/.rss?t=week"),
    ("Cameras", "https://www.reddit.com/r/Cameras/top/.rss?t=week"),
    ("fujifilm", "https://www.reddit.com/r/fujifilm/top/.rss?t=week"),
    ("SonyAlpha", "https://www.reddit.com/r/SonyAlpha/top/.rss?t=week"),
    ("Nikon", "https://www.reddit.com/r/Nikon/top/.rss?t=week"),
    ("canon", "https://www.reddit.com/r/canon/top/.rss?t=week"),
    ("leicaphotos", "https://www.reddit.com/r/leicaphotos/top/.rss?t=week"),
]

YOUTUBE_CHANNELS = [
    ("Sony Alpha", "UCO_6zZ4yAaowrdQCqh5uRGA"),
    ("Canon USA", "UCvqs9r3h9dh87lRHSatDpNg"),
    ("Nikon", "UCcOe4hSkt3We2WEBKknVSNQ"),
    ("Fujifilm Global", "UCXuESiygqNaA-TXZIZXBxPg"),
    ("Sigma", "UCD8CUDMTppteMIi02XXsQ6Q"),
    ("Tamron Japan", "UCJxB6B6hAEPZtSj_DqxEgaQ"),
    ("Viltrox", "UCuxYiOaEKhjzNiLibedo24Q"),
    ("Lens Light", "UCLxdwyzaFeJI09KEiIEkP_g"),
    ("Leica Camera", "UCVmgQawOcdeA9v9o0aukV7A"),
    ("Hasselblad", "UC8k0m7iO0s-aLkVnh9r9VCg"),
    ("Panasonic", "UCZgyCsZQLFF30TCs4uaZFKw"),
    ("DJI", "UCsNGtpqGsyw0U6qEG-WHadA"),
    ("Insta360", "UC3qWcF49rv8VMZO7Vg6kj5w"),
    ("SmallRig", "UC9QwRE3SnmzosZOCubAKhrg"),
    ("TILTA", "UCm4TJjV659kTjeCfTjejjNw"),
    ("Godox", "UCSbeasqU3eAxVgV7nmX-Q-Q"),
    ("Ricoh Imaging", "UCD_djFZ1d24FKaUM237yjew"),
    ("Pentax", "UC2zbbuQZBiciqPbx9-HkIQQ"),
    # 카메라 본체
    ("OM System", "UCOEymkD9VnWM5dZHj08EZVA"),
    ("Lomography", "UCuClVwSDvx65IPPQyFHrs1A"),
    # 렌즈
    ("Tokina", "UCeUa1XN1IJM6hXmwpLGNfIg"),
    ("Laowa", "UCiSXz3Eujt2mx4OYWwO2CwA"),
    ("TTArtisan", "UCJnuZsLW2KOwYjEn_ARaxOA"),
    ("7Artisans", "UCgsdXaCwmb15mCjBVnUzZIQ"),
    ("Samyang", "UCJUhH8nOoZ26flxew8RJBPA"),
    ("Irix", "UCJGUYjgNj1GBxI0c24ttmsA"),
    # 짐벌
    ("Zhiyun", "UCeeYm4DCcKiN6hmKBspX8Ig"),
    ("FeiyuTech", "UC3Lyp3nGiQOVYjnDGJf4LfQ"),
    # 조명
    ("Profoto", "UCG_lWnx3xTDIAW93Zq309Kg"),
    ("Aputure", "UCc0D1yh3TGE8dJSLm9VmEdg"),
    ("Nanlite", "UCnbzznFxZAF3dNTkj-aOW8g"),
    ("Westcott", "UCAYhU-t8F0rbxI_hQLe9spg"),
    # 액세서리
    ("Peak Design", "UCCXxVerycxB08muPJta5WBQ"),
    ("Manfrotto", "UC8uVuYgq2IxTpKLGUaZWy3Q"),
    ("Benro", "UCaZ0qj2KYw84OMjc-WprZug"),
]

YOUTUBE_API_KEY = "AIzaSyCJzQ_v53-XtNA3GO0Z1TKVCB4xw8C8AkA"

# 카메라 유튜버 (필터 없이 모든 영상 가져옴)
YOUTUBER_CHANNELS = [
    # 영어권
    ("Peter McKinnon", "UC3DkFux8Iv-aYnTRWzwaiBA"),
    ("Potato Jet", "UCNJe8uQhM2G4jJFRWiM89Wg"),
    ("Jared Polin", "UCZG-C5esGZyVfxO2qXa1Zmw"),
    ("The Art of Photography", "UC7T8roVtC_3afWKTOGtLlBA"),
    ("DSLR Video Shooter", "UCMmA0XxraDP7ZVbv4eY3Omg"),
    ("Matt Granger", "UCL5Hf6_JIzb3HpiJQGqs8cQ"),
    ("TheCameraStoreTV", "UCqpOf_Nl5F4tjwlxOVS6h8A"),
    ("DPReview TV", "UCqAtVqKL9GCiJ5q6ZnbVmcg"),
    ("Tony & Chelsea Northrup", "UCIOmtfFGUGYjBUqvVjSIVZA"),
    ("Kai W", "UCJLCeGDHTlCNRyrAEJNNmgA"),
    ("Gordon Laing", "UCwlHqNPOhBHpOEDVBSxKnCQ"),
    ("Sean Tucker", "UCOenHHOPsgBBLG-HQzS3_ow"),
    # 일본
    ("でんがん", "UCAbYNbG6j0mJm5KqjBeXBqg"),
    ("ゆーとびの写真学校", "UCe7fBmGInjMgrNHZkaSLXRg"),
    ("MapCamera公式", "UCxqLUMkFxXRwHqOJ73GgNwA"),
]

RSS_FEEDS = [
    ("DPReview", "https://www.dpreview.com/feeds/news"),
    ("Imaging Resource", "https://www.imaging-resource.com/news/feed/"),
    ("DC Watch (일본)", "https://dc.watch.impress.co.jp/data/rss/1.0/dcw/feed.rdf"),
    ("Camera Watch (일본)", "https://camera.watch.impress.co.jp/data/rss/1.0/caw/feed.rdf"),
    ("Brightin Star Reviews", "https://brightinstar.com/blogs/reviews.atom"),
    ("Brightin Star Insights", "https://brightinstar.com/blogs/insights.atom"),
    ("네이버 뉴스 - 카메라 신제품", "https://news.google.com/rss/search?q=%EC%B9%B4%EB%A9%94%EB%9D%BC+%EC%8B%A0%EC%A0%9C%ED%92%88&hl=ko&gl=KR&ceid=KR:ko"),
    ("네이버 뉴스 - 미러리스", "https://news.google.com/rss/search?q=%EB%AF%B8%EB%9F%AC%EB%A6%AC%EC%8A%A4+%EC%B6%9C%EC%8B%9C&hl=ko&gl=KR&ceid=KR:ko"),
    ("네이버 뉴스 - 렌즈 출시", "https://news.google.com/rss/search?q=%EC%B9%B4%EB%A9%94%EB%9D%BC+%EB%A0%8C%EC%A6%88+%EC%B6%9C%EC%8B%9C&hl=ko&gl=KR&ceid=KR:ko"),
    ("네이버 뉴스 - 카메라 악세서리", "https://news.google.com/rss/search?q=%EC%B9%B4%EB%A9%94%EB%9D%BC+%EC%95%85%EC%84%B8%EC%84%9C%EB%A6%AC+%EC%B6%9C%EC%8B%9C&hl=ko&gl=KR&ceid=KR:ko"),
    ("네이버 뉴스 - 조명 출시", "https://news.google.com/rss/search?q=%EC%B9%B4%EB%A9%94%EB%9D%BC+%EC%A1%B0%EB%AA%85+%EC%B6%9C%EC%8B%9C&hl=ko&gl=KR&ceid=KR:ko"),
    ("네이버 뉴스 - 짐벌 출시", "https://news.google.com/rss/search?q=%EC%A7%90%EB%B2%8C+%EC%B6%9C%EC%8B%9C&hl=ko&gl=KR&ceid=KR:ko"),
    ("네이버 뉴스 - 카메라 펌웨어", "https://news.google.com/rss/search?q=%EC%B9%B4%EB%A9%94%EB%9D%BC+%ED%8E%8C%EC%9B%A8%EC%96%B4+%EC%97%85%EB%8D%B0%EC%9D%B4%ED%8A%B8&hl=ko&gl=KR&ceid=KR:ko"),
    ("네이버 뉴스 - 카메라 결함", "https://news.google.com/rss/search?q=%EC%B9%B4%EB%A9%94%EB%9D%BC+%EA%B2%B0%ED%95%A8+%EB%AC%B8%EC%A0%9C&hl=ko&gl=KR&ceid=KR:ko"),
]

def refresh_access_token():
    res = requests.post("https://kauth.kakao.com/oauth/token", data={
        "grant_type": "refresh_token",
        "client_id": KAKAO_REST_API_KEY,
        "client_secret": KAKAO_CLIENT_SECRET,
        "refresh_token": KAKAO_REFRESH_TOKEN,
    })
    data = res.json()
    if "access_token" in data:
        # config.py 업데이트
        new_token = data["access_token"]
        with open("config.py", "r") as f:
            content = f.read()
        content = content.replace(
            f'KAKAO_ACCESS_TOKEN = "{KAKAO_ACCESS_TOKEN}"',
            f'KAKAO_ACCESS_TOKEN = "{new_token}"'
        )
        with open("config.py", "w") as f:
            f.write(content)
        return new_token
    return KAKAO_ACCESS_TOKEN

def fetch_youtube_rss(channels, filter_camera=False, days=7):
    cutoff = datetime.utcnow() - timedelta(days=days)
    videos = []
    for name, channel_id in channels:
        try:
            url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                published = getattr(entry, 'published_parsed', None)
                if published:
                    pub_date = datetime(*published[:6])
                    if pub_date < cutoff:
                        continue
                title = entry.get('title', '')
                if filter_camera and not is_camera_related(title):
                    continue
                video_id = entry.get('yt_videoid', entry.get('id', '').split(':')[-1])
                title_ko = translate_ko(title)
                videos.append(f"[{name}] {title_ko}\n🔗 https://youtu.be/{video_id}")
        except Exception as e:
            print(f"{name} RSS 오류: {e}")
    return videos

def fetch_youtuber_videos():
    return fetch_youtube_rss(YOUTUBER_CHANNELS, filter_camera=False, days=7)

def fetch_top_comments(video_id, max_comments=5):
    try:
        res = requests.get(
            "https://www.googleapis.com/youtube/v3/commentThreads",
            params={
                "key": YOUTUBE_API_KEY,
                "videoId": video_id,
                "part": "snippet",
                "order": "relevance",
                "maxResults": max_comments,
            }
        )
        comments = []
        for item in res.json().get("items", []):
            text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            text = text.strip().replace("\n", " ")
            if len(text) > 20:
                comments.append(translate_ko(text[:200]))
        return comments
    except:
        return []

def fetch_youtube():
    return fetch_youtube_rss(YOUTUBE_CHANNELS, filter_camera=True, days=3)

PRODUCT_KEYWORDS = [
    # 신제품
    "announce", "announced", "launch", "launched", "release", "released",
    "new", "introduce", "introduced", "unveil", "unveiled", "reveal",
    "coming soon", "hands-on", "first look", "officially", "review",
    "accessory", "accessories", "grip", "cage", "strap", "filter",
    "tripod", "monopod", "gimbal", "stabilizer", "flash", "light",
    "trigger", "battery", "charger", "bag", "holster",
    # 기존 제품 이슈
    "issue", "problem", "bug", "defect", "recall", "fix", "broken",
    "firmware", "update", "patch", "error", "fail", "failure",
    "overheating", "autofocus", "af", "shutter", "sensor", "leak",
    "discontinued", "price drop", "price cut", "rebate", "deal", "sale",
    # 한국어
    "발표", "출시", "신제품", "공개", "새로운", "런칭", "리뷰",
    "악세서리", "그립", "케이지", "스트랩", "필터", "삼각대", "짐벌", "조명",
    "펌웨어", "업데이트", "리콜", "결함", "문제", "단종", "가격인하", "할인"
]

CAMERA_BRANDS = [
    "canon", "sony", "nikon", "leica", "panasonic", "hasselblad",
    "fujifilm", "fuji", "sigma", "tamron", "viltrox", "pentax",
    "ricoh", "phase one", "phaseone", "dji", "insta360",
    "smallrig", "tilta", "zhiyun", "godox", "profoto",
    "캐논", "소니", "니콘", "라이카", "파나소닉", "핫셀블라드",
    "후지필름", "시그마", "탐론", "빌트록스", "펜탁스", "리코",
    "페이즈원", "스몰리그", "틸타", "삼양", "지윤", "아풋처",
    "난라이트", "피크디자인", "만프로토",
    "brightin star", "brightinstar",
    "om system", "lomography", "tokina", "laowa", "ttartisan",
    "7artisan", "samyang", "rokinon", "irix", "zhiyun", "feiyu",
    "profoto", "aputure", "nanlite", "westcott",
    "peak design", "manfrotto", "benro", "joby"
]

def is_camera_related(title, strict=True):
    title_lower = title.lower()
    has_brand = any(b in title_lower for b in CAMERA_BRANDS)
    has_product = any(kw in title_lower for kw in PRODUCT_KEYWORDS)
    if strict:
        return has_brand and has_product
    else:
        # Reddit용: 브랜드만 있어도 통과
        return has_brand

def fetch_reddit():
    yesterday = datetime.now() - timedelta(days=1)
    posts = []
    for subreddit, url in REDDIT_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                published = getattr(entry, 'published_parsed', None)
                if published:
                    pub_date = datetime(*published[:6])
                    if pub_date < yesterday:
                        continue
                title = entry.get('title', '')
                if not is_camera_related(title, strict=False):
                    continue
                title_ko = translate_ko(title)
                # 본문 텍스트 추출 (사진 포스트는 본문 없음)
                body = strip_html(entry.get('summary', ''))
                body = ' '.join(body.split())  # 공백 정리
                body_ko = translate_ko(body[:300]) if len(body) > 30 else ""
                link = entry.get('link', '')
                if body_ko:
                    posts.append(f"[Reddit/r/{subreddit}]\n제목: {title_ko}\n내용: {body_ko}\n🔗 {link}")
                else:
                    posts.append(f"[Reddit/r/{subreddit}]\n제목: {title_ko}\n🔗 {link}")
        except Exception as e:
            print(f"Reddit {subreddit} 오류: {e}")
    return posts

def fetch_news():
    yesterday = datetime.now() - timedelta(days=1)
    articles = []
    for source, url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                published = getattr(entry, 'published_parsed', None)
                if published:
                    pub_date = datetime(*published[:6])
                    if pub_date < yesterday:
                        continue
                title = entry.get('title', '')
                if not is_camera_related(title):
                    continue
                link = entry.get('link', '')
                if source.startswith("네이버"):
                    articles.append(f"[{source}] {title}\n🔗 {link}")
                else:
                    title_ko = translate_ko(title)
                    articles.append(f"[{source}] {title_ko}\n🔗 {link}")
        except Exception as e:
            print(f"{source} 오류: {e}")
    return articles

def send_kakao_message(token, text):
    res = requests.post(
        "https://kapi.kakao.com/v2/api/talk/memo/default/send",
        headers={"Authorization": f"Bearer {token}"},
        data={
            "template_object": json.dumps({
                "object_type": "text",
                "text": text,
                "link": {"web_url": "https://www.dpreview.com"}
            })
        }
    )
    if res.status_code == 401:
        print("토큰 만료, 갱신 중...")
        new_token = refresh_access_token()
        res = requests.post(
            "https://kapi.kakao.com/v2/api/talk/memo/default/send",
            headers={"Authorization": f"Bearer {new_token}"},
            data={
                "template_object": json.dumps({
                    "object_type": "text",
                    "text": text,
                    "link": {"web_url": "https://www.dpreview.com"}
                })
            }
        )
    return res.json()

def split_messages(text, limit=9000):
    """9000자 초과 시 여러 메시지로 분리"""
    if len(text) <= limit:
        return [text]
    messages = []
    lines = text.split("\n\n")
    current = ""
    for line in lines:
        if len(current) + len(line) + 2 > limit:
            messages.append(current.strip())
            current = line
        else:
            current += "\n\n" + line if current else line
    if current:
        messages.append(current.strip())
    return messages

def main():
    print("카메라 뉴스 수집 중...")
    articles = fetch_news()
    videos = fetch_youtube()
    youtuber_videos = fetch_youtuber_videos()
    reddit_posts = fetch_reddit()

    today = datetime.now().strftime('%Y-%m-%d')
    sections = []

    if articles or videos:
        items = articles + videos
        sections.append("📰 신제품 소식\n" + "\n\n".join(items))

    if youtuber_videos:
        sections.append("🎬 카메라 유튜버 최신 영상\n" + "\n\n".join(youtuber_videos))

    if reddit_posts:
        sections.append("💬 커뮤니티 반응 (Reddit)\n" + "\n\n".join(reddit_posts))

    if not sections:
        messages = [f"📷 카메라 뉴스 ({today})\n\n오늘은 새로운 소식이 없습니다."]
    else:
        header = f"📷 카메라 뉴스 ({today})\n신제품 {len(articles)+len(videos)}개 / 유튜버 {len(youtuber_videos)}개 / Reddit {len(reddit_posts)}개"
        # 섹션별로 쪼개서 각각 9000자 넘으면 분할
        messages = [header]
        for section in sections:
            messages.extend(split_messages(section))

    # HTML 대시보드 생성
    html_content = generate_html(articles, videos, youtuber_videos, reddit_posts, today)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("index.html 생성 완료")

    total = len(messages)
    print(f"카카오톡 전송 중... (총 {total}개 메시지)")
    for i, msg in enumerate(messages):
        result = send_kakao_message(KAKAO_ACCESS_TOKEN, msg)
        if result.get("result_code") == 0:
            print(f"  {i+1}/{total} 전송 성공")
        else:
            print(f"  {i+1}/{total} 전송 실패: {result}")

def generate_html(articles, videos, youtuber_videos, reddit_posts, today):
    def make_items_html(items):
        html = ""
        for item in items:
            lines = item.strip().split("\n")
            title = lines[0]
            link = ""
            body = ""
            comments = []
            for line in lines[1:]:
                if line.startswith("🔗"):
                    link = line.replace("🔗", "").strip()
                elif line.startswith("💬"):
                    continue
                elif line.startswith("  ·"):
                    comments.append(line.replace("  ·", "").strip())
                else:
                    body += line + " "
            html += f'<div class="card">'
            if link:
                html += f'<a href="{link}" target="_blank" class="title">{title}</a>'
            else:
                html += f'<div class="title">{title}</div>'
            if body.strip():
                html += f'<div class="body">{body.strip()}</div>'
            if comments:
                html += '<div class="comments">'
                for c in comments:
                    html += f'<div class="comment">💬 {c}</div>'
                html += '</div>'
            html += '</div>'
        return html

    news_html = make_items_html(articles + videos)
    youtuber_html = make_items_html(youtuber_videos)
    reddit_html = make_items_html(reddit_posts)

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>📷 카메라 뉴스 {today}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, sans-serif; background: #f0f2f5; color: #1a1a1a; }}
  header {{ background: #1a1a2e; color: white; padding: 20px; text-align: center; }}
  header h1 {{ font-size: 1.5em; }}
  header p {{ color: #aaa; margin-top: 6px; font-size: 0.9em; }}
  .tabs {{ display: flex; background: white; border-bottom: 2px solid #e0e0e0; position: sticky; top: 0; z-index: 10; }}
  .tab {{ flex: 1; padding: 14px; text-align: center; cursor: pointer; font-size: 0.9em; border-bottom: 3px solid transparent; }}
  .tab.active {{ border-bottom-color: #1a1a2e; font-weight: bold; color: #1a1a2e; }}
  .section {{ display: none; padding: 16px; max-width: 800px; margin: 0 auto; }}
  .section.active {{ display: block; }}
  .card {{ background: white; border-radius: 12px; padding: 16px; margin-bottom: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }}
  .title {{ font-size: 1em; font-weight: 600; color: #1a1a2e; text-decoration: none; display: block; margin-bottom: 6px; }}
  .title:hover {{ color: #4a90e2; }}
  .body {{ font-size: 0.85em; color: #555; line-height: 1.5; margin-top: 6px; }}
  .comments {{ margin-top: 10px; border-top: 1px solid #f0f0f0; padding-top: 8px; }}
  .comment {{ font-size: 0.82em; color: #666; padding: 4px 0; }}
  .empty {{ text-align: center; color: #aaa; padding: 40px; }}
  .stats {{ display: flex; justify-content: center; gap: 20px; padding: 12px; background: white; margin-bottom: 16px; border-radius: 12px; }}
  .stat {{ text-align: center; }}
  .stat-num {{ font-size: 1.4em; font-weight: bold; color: #1a1a2e; }}
  .stat-label {{ font-size: 0.75em; color: #888; }}
</style>
</head>
<body>
<header>
  <h1>📷 카메라 뉴스</h1>
  <p>{today} 업데이트</p>
</header>
<div class="tabs">
  <div class="tab active" onclick="showTab(0)">📰 신제품</div>
  <div class="tab" onclick="showTab(1)">🎬 유튜버</div>
  <div class="tab" onclick="showTab(2)">💬 Reddit</div>
</div>
<div id="s0" class="section active">
  <div class="stats">
    <div class="stat"><div class="stat-num">{len(articles)+len(videos)}</div><div class="stat-label">신제품 소식</div></div>
    <div class="stat"><div class="stat-num">{len(youtuber_videos)}</div><div class="stat-label">유튜버 영상</div></div>
    <div class="stat"><div class="stat-num">{len(reddit_posts)}</div><div class="stat-label">Reddit 반응</div></div>
  </div>
  {news_html if news_html else '<div class="empty">오늘은 새로운 소식이 없습니다.</div>'}
</div>
<div id="s1" class="section">
  {youtuber_html if youtuber_html else '<div class="empty">오늘은 새로운 영상이 없습니다.</div>'}
</div>
<div id="s2" class="section">
  {reddit_html if reddit_html else '<div class="empty">오늘은 새로운 Reddit 글이 없습니다.</div>'}
</div>
<script>
function showTab(i) {{
  document.querySelectorAll('.tab').forEach((t,j) => t.classList.toggle('active', i===j));
  document.querySelectorAll('.section').forEach((s,j) => s.classList.toggle('active', i===j));
}}
</script>
</body>
</html>"""

if __name__ == "__main__":
    main()
