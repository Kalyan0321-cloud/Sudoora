"""
Country data service using REST Countries API and World Bank API.
REST Countries: https://restcountries.com (free, no key needed)
World Bank: https://api.worldbank.org (free, no key needed)
"""

import requests
from functools import lru_cache

# Curated study destination data with real API augmentation
STUDY_DESTINATIONS = {
    "USA": {
        "flag": "🇺🇸", "code": "us",
        "universities": 4000,
        "avg_tuition": 35000,
        "living_cost": 18000,
        "visa_fee": 185,
        "visa_type": "F-1 Student Visa",
        "work_permit": "20 hrs/week on campus",
        "pr_pathway": "H-1B → Green Card",
        "popular_courses": ["Computer Science", "MBA", "Engineering", "Medicine"],
        "color": "#3B82F6",
        "intake_months": ["September", "January"],
        "top_cities": ["New York", "Boston", "San Francisco", "Chicago"],
        "currency": "USD",
        "language": "English",
    },
    "UK": {
        "flag": "🇬🇧", "code": "gb",
        "universities": 130,
        "avg_tuition": 22000,
        "living_cost": 15000,
        "visa_fee": 490,
        "visa_type": "Student Visa (Tier 4)",
        "work_permit": "20 hrs/week during term",
        "pr_pathway": "Graduate Route → Skilled Worker",
        "popular_courses": ["Law", "Finance", "Engineering", "MBA"],
        "color": "#EF4444",
        "intake_months": ["September", "January"],
        "top_cities": ["London", "Manchester", "Edinburgh", "Birmingham"],
        "currency": "GBP",
        "language": "English",
    },
    "Canada": {
        "flag": "🇨🇦", "code": "ca",
        "universities": 100,
        "avg_tuition": 28000,
        "living_cost": 14000,
        "visa_fee": 150,
        "visa_type": "Study Permit",
        "work_permit": "20 hrs/week off-campus",
        "pr_pathway": "PGWP → Express Entry",
        "popular_courses": ["Engineering", "Business", "IT", "Healthcare"],
        "color": "#EF4444",
        "intake_months": ["September", "January", "May"],
        "top_cities": ["Toronto", "Vancouver", "Montreal", "Calgary"],
        "currency": "CAD",
        "language": "English/French",
    },
    "Australia": {
        "flag": "🇦🇺", "code": "au",
        "universities": 43,
        "avg_tuition": 32000,
        "living_cost": 16000,
        "visa_fee": 630,
        "visa_type": "Student Visa (subclass 500)",
        "work_permit": "48 hrs/fortnight",
        "pr_pathway": "485 Visa → Skilled Migration",
        "popular_courses": ["Nursing", "Engineering", "IT", "Business"],
        "color": "#F59E0B",
        "intake_months": ["February", "July"],
        "top_cities": ["Sydney", "Melbourne", "Brisbane", "Perth"],
        "currency": "AUD",
        "language": "English",
    },
    "Germany": {
        "flag": "🇩🇪", "code": "de",
        "universities": 400,
        "avg_tuition": 1500,
        "living_cost": 12000,
        "visa_fee": 75,
        "visa_type": "National Visa (Type D)",
        "work_permit": "120 full days/year",
        "pr_pathway": "Job Seeker → Blue Card → PR",
        "popular_courses": ["Engineering", "Computer Science", "Automotive", "Sciences"],
        "color": "#10B981",
        "intake_months": ["October", "April"],
        "top_cities": ["Munich", "Berlin", "Hamburg", "Frankfurt"],
        "currency": "EUR",
        "language": "German/English",
    },
    "New Zealand": {
        "flag": "🇳🇿", "code": "nz",
        "universities": 8,
        "avg_tuition": 25000,
        "living_cost": 13000,
        "visa_fee": 330,
        "visa_type": "Student Visa",
        "work_permit": "20 hrs/week during study",
        "pr_pathway": "Post-Study Work → Skilled Migrant",
        "popular_courses": ["Agriculture", "Tourism", "IT", "Engineering"],
        "color": "#8B5CF6",
        "intake_months": ["February", "July"],
        "top_cities": ["Auckland", "Wellington", "Christchurch"],
        "currency": "NZD",
        "language": "English",
    },
    "Ireland": {
        "flag": "🇮🇪", "code": "ie",
        "universities": 34,
        "avg_tuition": 18000,
        "living_cost": 14000,
        "visa_fee": 100,
        "visa_type": "Student Permission (Stamp 2)",
        "work_permit": "20 hrs/week during term",
        "pr_pathway": "Graduate Programme → Critical Skills",
        "popular_courses": ["Pharmacy", "Business", "Computer Science", "Data Analytics"],
        "color": "#059669",
        "intake_months": ["September", "January"],
        "top_cities": ["Dublin", "Cork", "Galway", "Limerick"],
        "currency": "EUR",
        "language": "English",
    },
    "Singapore": {
        "flag": "🇸🇬", "code": "sg",
        "universities": 6,
        "avg_tuition": 20000,
        "living_cost": 17000,
        "visa_fee": 30,
        "visa_type": "Student's Pass",
        "work_permit": "16 hrs/week during term",
        "pr_pathway": "Employment Pass → PR",
        "popular_courses": ["Business", "Finance", "Engineering", "Biomedical"],
        "color": "#DC2626",
        "intake_months": ["August", "January"],
        "top_cities": ["Singapore City"],
        "currency": "SGD",
        "language": "English",
    },
}

@lru_cache(maxsize=32)
def get_country_details(country_name: str) -> dict:
    """Fetch real country data from REST Countries API."""
    base = STUDY_DESTINATIONS.get(country_name, {})
    try:
        code = base.get('code', country_name.lower()[:2])
        resp = requests.get(
            f"https://restcountries.com/v3.1/alpha/{code}",
            timeout=5
        )
        if resp.status_code == 200:
            data = resp.json()[0]
            base['population'] = data.get('population', 'N/A')
            base['region'] = data.get('region', 'N/A')
            base['capital'] = data.get('capital', ['N/A'])[0]
            # Use the flag from API as backup
            base['flag_url'] = data.get('flags', {}).get('png', '')
    except Exception:
        pass
    return base

def get_all_destinations() -> dict:
    """Return all study destinations with enriched data."""
    return STUDY_DESTINATIONS

def get_world_bank_gdp(country_code: str) -> float:
    """Fetch GDP per capita from World Bank API."""
    try:
        url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/NY.GDP.PCAP.CD?format=json&mrv=1"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if len(data) > 1 and data[1]:
                return data[1][0].get('value', 0)
    except Exception:
        pass
    return 0

def get_exchange_rates(base_currency: str = "USD") -> dict:
    """Get exchange rates - returns INR conversion rates."""
    # Fallback rates (approximate as of 2024)
    fallback = {
        "USD": 83.5, "GBP": 106.0, "EUR": 90.5,
        "CAD": 61.5, "AUD": 54.0, "NZD": 50.0,
        "SGD": 62.0
    }
    try:
        import os
        api_key = os.environ.get('EXCHANGE_API_KEY', '')
        if api_key:
            resp = requests.get(
                f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD",
                timeout=5
            )
            if resp.status_code == 200:
                data = resp.json()
                rates = data.get('conversion_rates', {})
                inr_rate = rates.get('INR', 83.5)
                return {k: round(inr_rate / rates[k], 2) for k in fallback if k in rates}
    except Exception:
        pass
    return fallback
