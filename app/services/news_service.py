"""
News service using NewsAPI.org.
Get your free API key at: https://newsapi.org
"""

import requests
import os
from datetime import datetime

# Curated fallback news for when API key is not available
FALLBACK_NEWS = [
    {
        "title": "UK Introduces New Graduate Route Visa for International Students",
        "description": "The UK government has extended the Graduate Route visa, allowing international students to stay and work for 2 years after graduation.",
        "url": "#",
        "source": "Study Abroad Times",
        "publishedAt": "2024-11-15T10:00:00Z",
        "category": "Visa",
        "country": "UK",
        "urlToImage": None,
    },
    {
        "title": "Canada Announces New Study Permit Cap for 2025",
        "description": "IRCC has announced a temporary cap on study permit approvals for 2025, affecting international student intake at Canadian colleges.",
        "url": "#",
        "source": "Global Education News",
        "publishedAt": "2024-11-10T08:30:00Z",
        "category": "Policy",
        "country": "Canada",
        "urlToImage": None,
    },
    {
        "title": "Australia's New Post-Study Work Rights Extended to 5 Years",
        "description": "Australia has updated its Temporary Graduate Visa policy, extending work rights for graduates from regional universities to 5 years.",
        "url": "#",
        "source": "International Student Hub",
        "publishedAt": "2024-11-08T12:00:00Z",
        "category": "Immigration",
        "country": "Australia",
        "urlToImage": None,
    },
    {
        "title": "Germany Eases Student Visa Process for Indian Applicants",
        "description": "Germany's Federal Foreign Office has streamlined the visa process for Indian students, reducing processing time to 4-6 weeks.",
        "url": "#",
        "source": "DAAD News",
        "publishedAt": "2024-11-05T09:15:00Z",
        "category": "Visa",
        "country": "Germany",
        "urlToImage": None,
    },
    {
        "title": "IELTS vs TOEFL: Which English Test is Right for You in 2025?",
        "description": "A comprehensive guide comparing IELTS and TOEFL acceptance rates across top universities in USA, UK, Canada, and Australia.",
        "url": "#",
        "source": "EduAdvisor",
        "publishedAt": "2024-11-01T14:00:00Z",
        "category": "Test Prep",
        "country": "General",
        "urlToImage": None,
    },
    {
        "title": "Top 10 Fully Funded Scholarships for Indian Students in 2025",
        "description": "Comprehensive list of scholarships offering full tuition, living expenses, and travel grants for Indian students studying abroad.",
        "url": "#",
        "source": "Scholarship India",
        "publishedAt": "2024-10-28T11:00:00Z",
        "category": "Scholarships",
        "country": "General",
        "urlToImage": None,
    },
]

def get_education_news(query: str = "international students study abroad", page_size: int = 6) -> list:
    """
    Fetch education news from NewsAPI.
    Falls back to curated news if API key is missing.
    """
    api_key = os.environ.get('NEWS_API_KEY', '')

    if not api_key:
        return FALLBACK_NEWS[:page_size]

    try:
        resp = requests.get(
            "https://newsapi.org/v2/everything",
            params={
                "q": query,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": page_size,
                "apiKey": api_key,
            },
            timeout=8
        )
        if resp.status_code == 200:
            data = resp.json()
            articles = data.get('articles', [])
            # Categorize articles
            result = []
            for article in articles:
                if article.get('title') and article.get('description'):
                    article['category'] = _categorize_article(article.get('title', ''))
                    article['country'] = _detect_country(article.get('title', '') + article.get('description', ''))
                    result.append(article)
            return result
    except Exception:
        pass

    return FALLBACK_NEWS[:page_size]

def _categorize_article(title: str) -> str:
    title_lower = title.lower()
    if any(w in title_lower for w in ['visa', 'permit', 'immigration']):
        return 'Visa'
    if any(w in title_lower for w in ['scholarship', 'grant', 'fellowship', 'funding']):
        return 'Scholarships'
    if any(w in title_lower for w in ['ielts', 'toefl', 'gre', 'gmat', 'sat']):
        return 'Test Prep'
    if any(w in title_lower for w in ['policy', 'government', 'regulation', 'cap', 'new rule']):
        return 'Policy'
    return 'General'

def _detect_country(text: str) -> str:
    text_lower = text.lower()
    for country in ['uk', 'britain', 'england', 'united kingdom']:
        if country in text_lower:
            return 'UK'
    for country in ['canada', 'canadian']:
        if country in text_lower:
            return 'Canada'
    for country in ['australia', 'australian']:
        if country in text_lower:
            return 'Australia'
    for country in ['germany', 'german']:
        if country in text_lower:
            return 'Germany'
    for country in ['usa', 'united states', 'american', 'us university']:
        if country in text_lower:
            return 'USA'
    return 'General'

def format_date(date_str: str) -> str:
    """Format ISO date string to readable format."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime("%d %b %Y")
    except:
        return date_str
