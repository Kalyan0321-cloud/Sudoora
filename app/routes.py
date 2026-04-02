from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, flash, abort
from app import db
from app.models import Lead, University, BlogPost
from app.forms import ContactForm, RecommendationForm, CostCalculatorForm, AdminLoginForm
from app.services.country_service import get_all_destinations, get_country_details, get_exchange_rates
from app.services.news_service import get_education_news, format_date
from app.services.recommendation_service import get_recommendations, get_cost_estimate
from functools import wraps
import os

main = Blueprint('main', __name__)

# ─── Admin Auth Decorator ─────────────────────────────────────────────────────

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('main.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ─── Public Routes ────────────────────────────────────────────────────────────

@main.route('/')
def index():
    destinations = get_all_destinations()
    news = get_education_news(page_size=3)
    featured_unis = University.query.order_by(University.ranking).limit(6).all()
    form = ContactForm()
    return render_template('index.html',
                           destinations=destinations,
                           news=news,
                           format_date=format_date,
                           featured_unis=featured_unis,
                           form=form)

@main.route('/destinations')
def destinations():
    dest_data = get_all_destinations()
    return render_template('destinations.html', destinations=dest_data)

@main.route('/destinations/<country_name>')
def destination_detail(country_name):
    dest_data = get_all_destinations()
    if country_name not in dest_data:
        abort(404)
    country = get_country_details(country_name)
    universities = University.query.filter_by(country=country_name).order_by(University.ranking).all()
    rates = get_exchange_rates()
    inr_rate = rates.get(country.get('currency', 'USD'), 83.5)
    return render_template('destination_detail.html',
                           country_name=country_name,
                           country=country,
                           universities=universities,
                           inr_rate=inr_rate)

@main.route('/universities')
def universities():
    country_filter = request.args.get('country', '')
    intake_filter = request.args.get('intake', '')
    max_tuition = request.args.get('max_tuition', type=int, default=0)
    query_str = request.args.get('q', '')

    query = University.query

    if country_filter:
        query = query.filter_by(country=country_filter)
    if intake_filter == 'fall':
        query = query.filter_by(intake_fall=True)
    elif intake_filter == 'spring':
        query = query.filter_by(intake_spring=True)
    if max_tuition:
        query = query.filter(University.tuition_max <= max_tuition)
    if query_str:
        query = query.filter(
            University.name.ilike(f'%{query_str}%') |
            University.popular_courses.ilike(f'%{query_str}%')
        )

    unis = query.order_by(University.ranking).all()
    countries = db.session.query(University.country).distinct().all()
    countries = [c[0] for c in countries]

    return render_template('universities.html',
                           universities=unis,
                           countries=countries,
                           filters={'country': country_filter, 'intake': intake_filter,
                                    'max_tuition': max_tuition, 'q': query_str})

@main.route('/cost-calculator', methods=['GET', 'POST'])
def cost_calculator():
    form = CostCalculatorForm()
    result = None
    rates = get_exchange_rates()

    if form.validate_on_submit():
        result = get_cost_estimate(
            country=form.country.data,
            course_type=form.course_type.data,
            duration=int(form.duration.data)
        )
        currency = result.get('currency', 'USD')
        result['inr_rate'] = rates.get(currency, 83.5)

    return render_template('cost_calculator.html', form=form, result=result)

@main.route('/recommend', methods=['GET', 'POST'])
def recommend():
    form = RecommendationForm()
    recommendations = []
    submitted = False

    if form.validate_on_submit():
        submitted = True
        recommendations = get_recommendations(
            budget=form.budget.data,
            academic_score=form.academic_score.data,
            preferred_country=form.preferred_country.data,
            preferred_course=form.preferred_course.data,
            ielts_score=form.ielts_score.data,
        )

    return render_template('recommend.html', form=form,
                           recommendations=recommendations, submitted=submitted)

@main.route('/intakes')
def intakes():
    country_filter = request.args.get('country', '')
    query = University.query
    if country_filter:
        query = query.filter_by(country=country_filter)
    unis = query.order_by(University.country, University.ranking).all()
    countries = db.session.query(University.country).distinct().all()
    countries = [c[0] for c in countries]
    return render_template('intakes.html', universities=unis, countries=countries,
                           country_filter=country_filter)

@main.route('/blog')
def blog():
    category = request.args.get('category', '')
    country = request.args.get('country', '')
    api_news = get_education_news(page_size=6)

    query = BlogPost.query.filter_by(is_published=True)
    if category:
        query = query.filter_by(category=category)
    if country:
        query = query.filter_by(country=country)

    db_posts = query.order_by(BlogPost.created_at.desc()).all()
    return render_template('blog.html', db_posts=db_posts, api_news=api_news,
                           format_date=format_date, category=category, country=country)

@main.route('/blog/<int:post_id>')
def blog_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    related = BlogPost.query.filter(
        BlogPost.country == post.country, BlogPost.id != post.id
    ).limit(3).all()
    return render_template('blog_post.html', post=post, related=related)

@main.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    success = False
    if form.validate_on_submit():
        lead = Lead(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            preferred_country=form.preferred_country.data,
            preferred_course=form.preferred_course.data,
            budget=form.budget.data,
            academic_score=form.academic_score.data,
            message=form.message.data,
        )
        db.session.add(lead)
        db.session.commit()
        success = True
    return render_template('contact.html', form=form, success=success)

# ─── AJAX / API Endpoints ─────────────────────────────────────────────────────

@main.route('/api/universities')
def api_universities():
    """JSON endpoint for dynamic university search."""
    country = request.args.get('country', '')
    q = request.args.get('q', '')
    max_tuition = request.args.get('max_tuition', type=int, default=0)

    query = University.query
    if country:
        query = query.filter_by(country=country)
    if q:
        query = query.filter(
            University.name.ilike(f'%{q}%') |
            University.popular_courses.ilike(f'%{q}%')
        )
    if max_tuition:
        query = query.filter(University.tuition_max <= max_tuition)

    unis = query.order_by(University.ranking).limit(20).all()
    return jsonify([u.to_dict() for u in unis])

@main.route('/api/country/<country_name>')
def api_country(country_name):
    """JSON endpoint for country details."""
    data = get_country_details(country_name)
    return jsonify(data)

@main.route('/api/exchange-rates')
def api_exchange_rates():
    """JSON endpoint for exchange rates."""
    rates = get_exchange_rates()
    return jsonify(rates)

@main.route('/api/cost-estimate')
def api_cost_estimate():
    """JSON endpoint for cost estimation."""
    country = request.args.get('country', 'USA')
    course = request.args.get('course', 'Engineering')
    duration = int(request.args.get('duration', 2))
    result = get_cost_estimate(country, course, duration)
    return jsonify(result)

@main.route('/api/lead', methods=['POST'])
def api_lead():
    """AJAX endpoint for lead submission."""
    data = request.json or {}
    if not all(k in data for k in ['name', 'email', 'phone']):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    lead = Lead(
        name=data.get('name'),
        email=data.get('email'),
        phone=data.get('phone'),
        preferred_country=data.get('preferred_country', ''),
        message=data.get('message', ''),
    )
    db.session.add(lead)
    db.session.commit()
    return jsonify({'success': True, 'message': "Thank you! We'll contact you shortly."})

@main.route('/api/chatbot', methods=['POST'])
def api_chatbot():
    """Simple FAQ chatbot endpoint."""
    data = request.json or {}
    message = data.get('message', '').lower()
    response = _get_bot_response(message)
    return jsonify({'response': response})

def _get_bot_response(message: str) -> str:
    """Simple rule-based FAQ bot."""
    faqs = {
        ('ielts', 'english test', 'language requirement'): "Most universities require IELTS 6.0-7.5. The exact score depends on the university and course. UK universities typically need 6.5-7.5, while German universities accept 6.0-6.5.",
        ('visa', 'apply'): "Visa requirements vary by country. Generally you need: admission letter, financial proof, language scores, passport, and photos. Processing takes 4-12 weeks. Our counselors can guide you through the process!",
        ('cost', 'fees', 'tuition', 'expensive'): "Study costs vary widely! Germany has nearly free tuition (€0-3000/year), while the USA costs $30,000-60,000/year. Canada ($20,000-40,000) and UK (£15,000-35,000) are in between. Use our Cost Calculator for a personalized estimate!",
        ('scholarship', 'funding', 'financial aid'): "Yes! Many scholarships are available for Indian students: Chevening (UK), DAAD (Germany), Commonwealth, Ontario Trillium (Canada), and many university-specific scholarships. Contact us for personalized scholarship guidance.",
        ('canada', 'pr', 'permanent residence'): "Canada is one of the best countries for PR after studies! The Post-Graduate Work Permit (PGWP) allows you to work for up to 3 years, and you can then apply for Express Entry PR.",
        ('germany', 'free', 'no tuition'): "Germany's public universities charge zero tuition fees, even for international students! You only pay a semester contribution of around €150-350, which often includes public transport passes.",
        ('gre', 'gmat', 'test'): "For USA/Canada: GRE is for most master's programs, GMAT is specifically for MBA programs. Many universities now waive GRE/GMAT for experienced professionals or strong academic profiles.",
        ('best country', 'recommend', 'which country'): "The best country depends on your goals! For jobs: Canada & Australia offer easiest PR. For low cost: Germany. For top rankings: USA & UK. For English + jobs: Canada. Use our AI Recommender for personalized suggestions!",
        ('hello', 'hi', 'hey'): "Hello! 👋 I'm GlobEd AI, your study abroad assistant. I can help you with visa info, cost estimates, scholarship guidance, and more. What would you like to know?",
        ('thank', 'thanks'): "You're welcome! Feel free to ask any other questions. You can also book a free consultation with our expert counselors! 😊",
    }

    for keywords, response in faqs.items():
        if any(kw in message for kw in keywords):
            return response

    return "I can help you with information about study destinations, visa requirements, costs, scholarships, and more. Could you be more specific? Or contact our counselors for personalized guidance at +91-XXXXXXXXXX."

# ─── Admin Routes ─────────────────────────────────────────────────────────────

@main.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('main.admin_dashboard'))

    form = AdminLoginForm()
    error = None
    if form.validate_on_submit():
        if (form.username.data == os.environ.get('ADMIN_USERNAME', 'admin') and
                form.password.data == os.environ.get('ADMIN_PASSWORD', 'admin123')):
            session['admin_logged_in'] = True
            return redirect(url_for('main.admin_dashboard'))
        error = 'Invalid credentials'

    return render_template('admin/login.html', form=form, error=error)

@main.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('main.index'))

@main.route('/admin')
@admin_required
def admin_dashboard():
    leads = Lead.query.order_by(Lead.created_at.desc()).all()
    total_leads = Lead.query.count()
    new_leads = Lead.query.filter_by(status='new').count()
    total_unis = University.query.count()
    total_posts = BlogPost.query.count()
    return render_template('admin/dashboard.html',
                           leads=leads, total_leads=total_leads,
                           new_leads=new_leads, total_unis=total_unis,
                           total_posts=total_posts)

@main.route('/admin/leads')
@admin_required
def admin_leads():
    leads = Lead.query.order_by(Lead.created_at.desc()).all()
    return render_template('admin/leads.html', leads=leads)

@main.route('/admin/lead/<int:lead_id>/status', methods=['POST'])
@admin_required
def update_lead_status(lead_id):
    lead = Lead.query.get_or_404(lead_id)
    lead.status = request.form.get('status', 'new')
    db.session.commit()
    return redirect(url_for('main.admin_leads'))

@main.route('/admin/universities')
@admin_required
def admin_universities():
    unis = University.query.order_by(University.ranking).all()
    return render_template('admin/universities.html', universities=unis)

@main.context_processor
def inject_globals():
    """Make these available in all templates."""
    return {
        'site_name': 'GlobEd Consultancy',
        'site_tagline': 'Your Gateway to Global Education',
        'countries_list': ['USA', 'UK', 'Canada', 'Australia', 'Germany',
                           'New Zealand', 'Ireland', 'Singapore'],
    }
