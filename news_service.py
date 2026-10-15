import requests
import xml.etree.ElementTree as ET
import re
import html
from config import Config

# Curated fallback pool of high-yield current affairs topics
FALLBACK_TOPICS = {
    'polity': [
        {"headline": "Supreme Court reviews Collegium System and Judicial Transparency safeguards", "source": "The Hindu", "published": "Today"},
        {"headline": "Electoral reforms debated as Law Commission submits report on simultaneous polls", "source": "Indian Express", "published": "Today"},
        {"headline": "Parliament passes Digital Personal Data Protection framework amendments", "source": "Press Information Bureau", "published": "Today"},
        {"headline": "Inter-State River Water Dispute Bill tabled for expedited dispute tribunals", "source": "LiveMint", "published": "Today"}
    ],
    'world': [
        {"headline": "Global South pushes for multilateral reform at UN General Assembly high-level debate", "source": "Reuters", "published": "Today"},
        {"headline": "G20 leaders agree on framework for cross-border carbon border tax mechanisms", "source": "Financial Times", "published": "Today"},
        {"headline": "Indo-Pacific maritime security dialogue focuses on supply chain resilient corridors", "source": "Nikkei Asia", "published": "Today"},
        {"headline": "Global Semiconductor Alliance addresses export controls and critical mineral dependencies", "source": "Bloomberg", "published": "Today"}
    ],
    'tech': [
        {"headline": "Global AI Safety Consortium proposes mandatory watermarking and red-teaming standards", "source": "TechCrunch", "published": "Today"},
        {"headline": "Critical infrastructure cyber attacks prompt nations to mandate zero-trust security architecture", "source": "Wired", "published": "Today"},
        {"headline": "Commercial space ventures expand satellite constellation deployment amid space debris concerns", "source": "Ars Technica", "published": "Today"},
        {"headline": "Quantum encryption protocols achieve breakthrough in inter-banking financial transactions", "source": "MIT Tech Review", "published": "Today"}
    ],
    'economy': [
        {"headline": "Central banks balance inflation control with employment as interest rate cuts loom", "source": "The Economist", "published": "Today"},
        {"headline": "Renewable energy investments outpace fossil fuels in emerging market transitions", "source": "Bloomberg", "published": "Today"},
        {"headline": "Manufacturing incentive schemes drive high-tech electronics exports to record highs", "source": "Economic Times", "published": "Today"},
        {"headline": "Digital Public Infrastructure and cross-border UPI integration expand across ASEAN", "source": "Business Standard", "published": "Today"}
    ],
    'sports': [
        {"headline": "International Olympic Committee debates inclusion of esports and gender parity guidelines", "source": "BBC Sport", "published": "Today"},
        {"headline": "Global sports governing bodies introduce stricter concussion protocols and player welfare metrics", "source": "The Athletic", "published": "Today"},
        {"headline": "Grassroots athletic development program shows strong medal conversion in Asian Championships", "source": "Sportstar", "published": "Today"}
    ],
    'general': [
        {"headline": "Extreme climate heatwaves highlight municipal urban adaptation and heat action plans", "source": "Guardian", "published": "Today"},
        {"headline": "Higher education institutions overhaul curriculum to balance AI literacy with human ethics", "source": "Times Higher Education", "published": "Today"},
        {"headline": "National health survey indicates rising youth mental health priorities and wellness initiatives", "source": "Hindustan Times", "published": "Today"}
    ]
}

GOOGLE_NEWS_FEEDS = {
    'polity': 'https://news.google.com/rss/headlines/section/topic/NATION?hl=en-IN&gl=IN&ceid=IN:en',
    'world': 'https://news.google.com/rss/headlines/section/topic/WORLD?hl=en-IN&gl=IN&ceid=IN:en',
    'tech': 'https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=en-IN&gl=IN&ceid=IN:en',
    'economy': 'https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-IN&gl=IN&ceid=IN:en',
    'sports': 'https://news.google.com/rss/headlines/section/topic/SPORTS?hl=en-IN&gl=IN&ceid=IN:en',
    'general': 'https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en'
}

def clean_headline(title):
    """Splits headline and trailing source publication name like 'Headline - Source'."""
    title = html.unescape(title.strip())
    parts = re.split(r'\s+-\s+(?=[^-]+$)', title)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return title, 'News Feed'

def fetch_live_headlines(category='general', max_items=10):
    """Fetches real-time headlines using Google News RSS, with curated fallback."""
    category_slug = category.lower()
    feed_url = GOOGLE_NEWS_FEEDS.get(category_slug, GOOGLE_NEWS_FEEDS['general'])
    
    headlines = []
    
    # 1. Attempt Google News RSS (zero API key required, always fresh)
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        resp = requests.get(feed_url, headers=headers, timeout=5)
        if resp.status_code == 200:
            root = ET.fromstring(resp.content)
            for item in root.findall('./channel/item')[:max_items]:
                raw_title = item.findtext('title', '')
                pub_date = item.findtext('pubDate', '')
                link = item.findtext('link', '')
                
                title, source = clean_headline(raw_title)
                
                # Filter out overly short or irrelevant noise
                if len(title.split()) >= 4:
                    headlines.append({
                        'headline': title,
                        'source': source,
                        'published': pub_date[:16] if pub_date else 'Recent',
                        'url': link,
                        'category': category_slug
                    })
    except Exception as e:
        print(f"Live RSS fetch notice: {e}")

    # 2. If RSS didn't yield enough, blend or fallback to curated database
    if len(headlines) < 3:
        fallbacks = FALLBACK_TOPICS.get(category_slug, FALLBACK_TOPICS['general'])
        for fb in fallbacks:
            headlines.append({
                'headline': fb['headline'],
                'source': fb['source'],
                'published': fb['published'],
                'url': '#',
                'category': category_slug
            })
            
    return headlines[:max_items]

def get_random_topic(category='general'):
    import random
    items = fetch_live_headlines(category, max_items=8)
    return random.choice(items) if items else {
        'headline': 'The role of Artificial Intelligence and Ethical Governance in 21st Century Public Administration',
        'source': 'UPSC Think Tank',
        'published': 'Live',
        'url': '#',
        'category': category
    }
