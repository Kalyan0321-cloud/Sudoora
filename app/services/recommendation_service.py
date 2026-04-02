"""
AI-powered university recommendation engine.
Uses scoring algorithm based on budget, academic score, and preferences.
"""

from app.models import University

COUNTRY_LIVING_COSTS = {
    "USA": 18000, "UK": 15000, "Canada": 14000,
    "Australia": 16000, "Germany": 12000,
    "New Zealand": 13000, "Ireland": 14000, "Singapore": 17000,
}

def get_recommendations(budget: int, academic_score: float, preferred_country: str,
                         preferred_course: str = None, ielts_score: float = None) -> list:
    """
    Generate university recommendations based on student profile.
    
    Scoring factors:
    - Budget compatibility: 40%
    - Academic match: 30%
    - Country preference: 20%
    - Course availability: 10%
    """
    query = University.query

    # If a specific country is preferred, prioritize it
    if preferred_country and preferred_country != "Any":
        all_unis = University.query.all()
        preferred_unis = [u for u in all_unis if u.country == preferred_country]
        other_unis = [u for u in all_unis if u.country != preferred_country]
        universities = preferred_unis + other_unis
    else:
        universities = University.query.all()

    scored = []

    for uni in universities:
        score = 0
        reasons = []

        # --- Budget Score (40 pts) ---
        total_cost = (uni.tuition_max or 0) + COUNTRY_LIVING_COSTS.get(uni.country, 15000)
        if budget >= total_cost:
            score += 40
            reasons.append(f"Within your annual budget of ₹{budget:,}")
        elif budget >= total_cost * 0.85:
            score += 25
            reasons.append("Slightly above budget but achievable with scholarships")
        elif budget >= total_cost * 0.70:
            score += 10
            reasons.append("Requires scholarship support")

        # --- Academic Score (30 pts) ---
        # For India: CGPA/Percentage to acceptance rate mapping
        if academic_score >= 90:
            if uni.acceptance_rate and uni.acceptance_rate <= 10:
                score += 30
                reasons.append("Strong profile for this competitive university")
            else:
                score += 28
        elif academic_score >= 80:
            if uni.acceptance_rate and uni.acceptance_rate <= 20:
                score += 25
                reasons.append("Good academic match")
            else:
                score += 28
                reasons.append("Excellent academic match")
        elif academic_score >= 70:
            if uni.acceptance_rate and uni.acceptance_rate >= 30:
                score += 25
                reasons.append("Good academic match")
            else:
                score += 15
        elif academic_score >= 60:
            if uni.acceptance_rate and uni.acceptance_rate >= 50:
                score += 25
                reasons.append("Good academic match")
            else:
                score += 10

        # --- Country Preference (20 pts) ---
        if preferred_country == uni.country:
            score += 20
            reasons.append(f"Matches your preferred destination: {uni.country}")
        elif preferred_country == "Any":
            score += 10

        # --- IELTS Score compatibility (10 pts) ---
        if ielts_score:
            if ielts_score >= (uni.ielts_min or 6.0):
                score += 10
                reasons.append(f"Your IELTS score meets requirements")
            else:
                score -= 5

        # --- Course match (bonus 5 pts) ---
        if preferred_course and uni.popular_courses:
            if preferred_course.lower() in uni.popular_courses.lower():
                score += 5
                reasons.append(f"{preferred_course} is a top program here")

        # --- Ranking bonus ---
        if uni.ranking and uni.ranking <= 10:
            score += 3
        elif uni.ranking and uni.ranking <= 50:
            score += 1

        if score > 0:
            scored.append({
                'university': uni,
                'score': score,
                'reasons': reasons[:3],  # Top 3 reasons
                'match_percentage': min(int((score / 108) * 100), 98),
                'total_annual_cost': (uni.tuition_max or 0) + COUNTRY_LIVING_COSTS.get(uni.country, 15000),
            })

    # Sort by score descending
    scored.sort(key=lambda x: x['score'], reverse=True)
    return scored[:6]  # Top 6 recommendations


def get_cost_estimate(country: str, course_type: str, duration: int) -> dict:
    """
    Calculate detailed cost estimates for studying abroad.
    """
    from app.services.country_service import STUDY_DESTINATIONS

    dest = STUDY_DESTINATIONS.get(country, {})

    # Tuition by course type (annual, USD)
    tuition_map = {
        "Engineering": {"USA": 45000, "UK": 28000, "Canada": 30000, "Australia": 35000, "Germany": 2000},
        "MBA": {"USA": 55000, "UK": 35000, "Canada": 35000, "Australia": 40000, "Germany": 15000},
        "Medicine": {"USA": 60000, "UK": 38000, "Canada": 20000, "Australia": 42000, "Germany": 3000},
        "Computer Science": {"USA": 42000, "UK": 26000, "Canada": 28000, "Australia": 33000, "Germany": 2000},
        "Arts & Humanities": {"USA": 35000, "UK": 22000, "Canada": 22000, "Australia": 28000, "Germany": 1500},
        "Business": {"USA": 48000, "UK": 30000, "Canada": 32000, "Australia": 35000, "Germany": 12000},
    }

    course_tuition = tuition_map.get(course_type, tuition_map["Engineering"])
    annual_tuition = course_tuition.get(country, 30000)
    annual_living = dest.get('living_cost', 15000)
    visa_fee = dest.get('visa_fee', 200)

    health_insurance = {"USA": 2000, "UK": 470, "Canada": 800, "Australia": 600, "Germany": 1200}.get(country, 800)

    return {
        "country": country,
        "course_type": course_type,
        "duration": duration,
        "annual_tuition": annual_tuition,
        "annual_living": annual_living,
        "total_tuition": annual_tuition * duration,
        "total_living": annual_living * duration,
        "visa_fee": visa_fee,
        "health_insurance_annual": health_insurance,
        "total_health": health_insurance * duration,
        "grand_total": (annual_tuition + annual_living + health_insurance) * duration + visa_fee,
        "currency": dest.get('currency', 'USD'),
        "work_permit": dest.get('work_permit', 'N/A'),
    }
