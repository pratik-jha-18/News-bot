import requests
import xml.etree.ElementTree as ET
import os
import time
from datetime import datetime
import re

TELEGRAM_TOKEN = os.environ.get(8773461704:AAEo3P9caJAP7lKCKSOQhjxGbi5tLbZegB8)
CHANNEL_ID = os.environ.get(-1003945175575)

# ============================================
# ALL FREE RSS NEWS SOURCES (No API Key!)
# ============================================

NEWS_SOURCES = {
    "🌍 WORLD NEWS": [
        "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US:en",
        # Google News World
    ],
    "🇮🇳 INDIA TOP NEWS": [
        "https://news.google.com/rss/topics/CAAqIQgKIhtDQkFTRGdvSUwyMHZNRE55YXpBU0FtVnVLQUFQAQ?hl=en-IN&gl=IN&ceid=IN:en",
        # Google News India
    ],
    "🇮🇳 INDIA - NDTV": [
        "https://feeds.feedburner.com/ndtvnews-top-stories",
    ],
    "🇮🇳 INDIA - Times of India": [
        "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
    ],
    "🇮🇳 INDIA - Hindustan Times": [
        "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml",
    ],
    "💼 BUSINESS & ECONOMY": [
        "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pKVGlnQVAB?hl=en-IN&gl=IN&ceid=IN:en",
        # Google News Business India
    ],
    "🏏 SPORTS NEWS": [
        "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp1ZEdvU0FtVnVHZ0pKVGlnQVAB?hl=en-IN&gl=IN&ceid=IN:en",
        # Google News Sports India
    ],
    "💻 TECHNOLOGY": [
        "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pKVGlnQVAB?hl=en-IN&gl=IN&ceid=IN:en",
        # Google News Tech India
    ],
    "🎬 ENTERTAINMENT & BOLLYWOOD": [
        "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNREpxYW5RU0FtVnVHZ0pKVGlnQVAB?hl=en-IN&gl=IN&ceid=IN:en",
        # Google News Entertainment India
    ],
}

# X/Twitter accounts to mention for readers to follow
X_ACCOUNTS = {
    "World News": ["@BBCBreaking", "@Reuters", "@AP"],
    "India News": ["@ndtv", "@theaborhindu", "@timesofindia", "@HTNewsBreaks"],
    "Sports": ["@ESPNcricinfo", "@BCCI", "@SportsTak"],
    "Business": ["@EconomicTimes", "@livaboremint", "@baborloomberg"],
}


def clean_html(text):
    """Remove HTML tags from text"""
    clean = re.sub(r'<[^>]+>', '', text)
    clean = clean.replace('&amp;', '&')
    clean = clean.replace('&lt;', '<')
    clean = clean.replace('&gt;', '>')
    clean = clean.replace('&#39;', "'")
    clean = clean.replace('&quot;', '"')
    return clean.strip()


def fetch_rss_news(url, count=5):
    """Fetch news from any RSS feed"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        root = ET.fromstring(response.content)

        articles = []
        # Handle both RSS and Atom feeds
        # RSS format
        items = root.findall('.//item')
        
        for item in items[:count]:
            title = item.find('title')
            link = item.find('link')
            pub_date = item.find('pubDate')
            source = item.find('source')
            description = item.find('description')

            article = {
                'title': clean_html(title.text) if title is not None and title.text else "No title",
                'link': link.text if link is not None and link.text else "",
                'date': pub_date.text if pub_date is not None else "",
                'source': source.text if source is not None and source.text else "",
                'description': clean_html(description.text)[:150] if description is not None and description.text else ""
            }
            
            # Clean title - remove source name after " - "
            if " - " in article['title']:
                parts = article['title'].rsplit(" - ", 1)
                if len(parts[1]) < 40:  # likely a source name
                    if not article['source']:
                        article['source'] = parts[1]
                    article['title'] = parts[0]
            
            articles.append(article)

        return articles
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []


def format_news_message(category, articles):
    """Format news into a beautiful Telegram message"""
    today = datetime.now().strftime("%d %B %Y")
    
    message = f"{'='*30}\n"
    message += f"📰 *{category}*\n"
    message += f"📅 _{today}_\n"
    message += f"{'='*30}\n\n"

    if not articles:
        message += "❌ No news available right now.\n\n"
        return message

    for i, article in enumerate(articles, 1):
        title = article['title']
        link = article['link']
        source = article['source']
        description = article['description']

        message += f"*{i}.* {title}\n"
        if description and len(description) > 20:
            message += f"   📝 _{description[:120]}..._\n"
        if source:
            message += f"   📌 Source: _{source}_\n"
        if link:
            message += f"   🔗 [Read Full Article]({link})\n"
        message += "\n"

    return message


def send_telegram_message(text):
    """Send message to Telegram channel"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    # Telegram has 4096 char limit, so split if needed
    if len(text) > 4000:
        text = text[:4000] + "\n\n_...continued_"
    
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        response = requests.post(url, json=payload)
        result = response.json()
        if result.get("ok"):
            print(f"✅ Message sent successfully!")
        else:
            print(f"❌ Failed: {result}")
            # Try without markdown if formatting fails
            payload["parse_mode"] = ""
            requests.post(url, json=payload)
        return result
    except Exception as e:
        print(f"Error sending message: {e}")


def send_header():
    """Send a nice header message"""
    today = datetime.now().strftime("%d %B %Y")
    header = f"""
🗞️ *DAILY NEWS BULLETIN* 🗞️
━━━━━━━━━━━━━━━━━━━━
📅 *{today}*
━━━━━━━━━━━━━━━━━━━━

Good Morning! ☀️
Here are today's top headlines from 
India 🇮🇳 and around the World 🌍

_Powered by Google News, NDTV, 
Times of India & more_
"""
    send_telegram_message(header)


def send_footer():
    """Send footer with X/Twitter accounts"""
    footer = """
━━━━━━━━━━━━━━━━━━━━
📱 *FOLLOW FOR LIVE UPDATES ON X:*
━━━━━━━━━━━━━━━━━━━━

🌍 *World:* @BBCBreaking @Reuters @AP
🇮🇳 *India:* @ndtv @the_hindu @timesofindia
🏏 *Sports:* @ESPNcricinfo @BCCI
💼 *Business:* @EconomicTimes @livemint

━━━━━━━━━━━━━━━━━━━━
_📰 News sent daily | Stay informed!_
_Like & Share this channel_ ❤️
"""
    send_telegram_message(footer)


def main():
    print("🚀 Starting Daily News Bot...")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Send Header
    send_header()
    time.sleep(2)

    # Send each category
    for category, urls in NEWS_SOURCES.items():
        print(f"\n📰 Fetching: {category}")
        
        all_articles = []
        for url in urls:
            articles = fetch_rss_news(url, count=5)
            all_articles.extend(articles)
        
        # Remove duplicates based on title
        seen_titles = set()
        unique_articles = []
        for article in all_articles:
            title_lower = article['title'].lower()[:50]
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_articles.append(article)
        
        # Take top 5
        unique_articles = unique_articles[:5]
        
        # Format and send
        message = format_news_message(category, unique_articles)
        send_telegram_message(message)
        print(f"✅ Sent: {category} ({len(unique_articles)} articles)")
        
        time.sleep(3)  # Avoid Telegram rate limits
    
    # Send Footer
    send_footer()
    
    print("\n🎉 All news sent successfully!")


if __name__ == "__main__":
    main()
