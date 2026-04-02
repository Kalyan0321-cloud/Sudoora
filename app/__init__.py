from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    login_manager.login_view = 'main.admin_login'

    from app.routes import main
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()
        _seed_initial_data()

    return app

def _seed_initial_data():
    """Seed database with initial university and blog data if empty."""
    from app.models import University, BlogPost
    if University.query.count() == 0:
        universities = [
            University(name="Massachusetts Institute of Technology", country="USA",
                       city="Cambridge", ranking=1, tuition_min=55000, tuition_max=60000,
                       intake_fall=True, intake_spring=True, intake_summer=False,
                       popular_courses="Engineering, Computer Science, Physics",
                       acceptance_rate=4, ielts_min=7.0, description="World's leading tech university."),
            University(name="University of Toronto", country="Canada",
                       city="Toronto", ranking=18, tuition_min=25000, tuition_max=45000,
                       intake_fall=True, intake_spring=False, intake_summer=False,
                       popular_courses="Business, Engineering, Medicine",
                       acceptance_rate=43, ielts_min=6.5, description="Canada's top research university."),
            University(name="University of Oxford", country="UK",
                       city="Oxford", ranking=3, tuition_min=28000, tuition_max=45000,
                       intake_fall=True, intake_spring=False, intake_summer=False,
                       popular_courses="Law, Medicine, Philosophy, PPE",
                       acceptance_rate=17, ielts_min=7.5, description="One of the world's oldest universities."),
            University(name="Australian National University", country="Australia",
                       city="Canberra", ranking=27, tuition_min=30000, tuition_max=48000,
                       intake_fall=True, intake_spring=True, intake_summer=False,
                       popular_courses="Sciences, Law, Asia Pacific Studies",
                       acceptance_rate=35, ielts_min=6.5, description="Australia's national university."),
            University(name="Technical University of Munich", country="Germany",
                       city="Munich", ranking=37, tuition_min=0, tuition_max=3000,
                       intake_fall=True, intake_spring=True, intake_summer=False,
                       popular_courses="Engineering, Natural Sciences, Computer Science",
                       acceptance_rate=8, ielts_min=6.5, description="Germany's top technical university."),
            University(name="Stanford University", country="USA",
                       city="Stanford", ranking=2, tuition_min=56000, tuition_max=62000,
                       intake_fall=True, intake_spring=False, intake_summer=False,
                       popular_courses="Computer Science, Business, Engineering",
                       acceptance_rate=4, ielts_min=7.0, description="Silicon Valley's premier university."),
            University(name="University of British Columbia", country="Canada",
                       city="Vancouver", ranking=34, tuition_min=22000, tuition_max=40000,
                       intake_fall=True, intake_spring=False, intake_summer=False,
                       popular_courses="Forestry, Medicine, Business",
                       acceptance_rate=52, ielts_min=6.5, description="Leading Canadian research university."),
            University(name="Imperial College London", country="UK",
                       city="London", ranking=6, tuition_min=32000, tuition_max=50000,
                       intake_fall=True, intake_spring=False, intake_summer=False,
                       popular_courses="Engineering, Medicine, Business",
                       acceptance_rate=14, ielts_min=7.0, description="UK's leading STEM university."),
            University(name="University of Melbourne", country="Australia",
                       city="Melbourne", ranking=33, tuition_min=28000, tuition_max=44000,
                       intake_fall=True, intake_spring=True, intake_summer=False,
                       popular_courses="Arts, Business, Engineering",
                       acceptance_rate=40, ielts_min=6.5, description="Australia's top-ranked university."),
            University(name="Heidelberg University", country="Germany",
                       city="Heidelberg", ranking=64, tuition_min=0, tuition_max=1500,
                       intake_fall=True, intake_spring=True, intake_summer=False,
                       popular_courses="Medicine, Natural Sciences, Humanities",
                       acceptance_rate=15, ielts_min=6.0, description="Germany's oldest university."),
            University(name="McGill University", country="Canada",
                       city="Montreal", ranking=46, tuition_min=18000, tuition_max=35000,
                       intake_fall=True, intake_spring=False, intake_summer=False,
                       popular_courses="Medicine, Law, Engineering",
                       acceptance_rate=46, ielts_min=6.5, description="Canada's top medical university."),
            University(name="University of Cambridge", country="UK",
                       city="Cambridge", ranking=2, tuition_min=30000, tuition_max=48000,
                       intake_fall=True, intake_spring=False, intake_summer=False,
                       popular_courses="Natural Sciences, Engineering, Mathematics",
                       acceptance_rate=21, ielts_min=7.5, description="World-renowned research university."),
        ]
        for u in universities:
            db.session.add(u)

    if BlogPost.query.count() == 0:
        posts = [
            BlogPost(title="UK Student Visa (Tier 4) Guide 2024",
                     category="Visa", country="UK",
                     excerpt="Everything Indian students need to know about applying for a UK Student Visa.",
                     content="The UK Student Visa (formerly Tier 4) allows international students to study in the UK for courses longer than 6 months. You'll need a Confirmation of Acceptance for Studies (CAS) from your university, proof of English language skills, financial evidence, and more..."),
            BlogPost(title="Top 10 Scholarships for Indian Students in Canada",
                     category="Scholarships", country="Canada",
                     excerpt="Comprehensive list of scholarships available to Indian students studying in Canada.",
                     content="Canada offers numerous scholarships for international students. The Vanier Canada Graduate Scholarships, Lester B. Pearson International Scholarship at University of Toronto, and many university-specific awards are available..."),
            BlogPost(title="GRE vs GMAT: Which Should You Take for MBA in USA?",
                     category="Test Prep", country="USA",
                     excerpt="A detailed comparison to help you decide between GRE and GMAT for your MBA application.",
                     content="Both GRE and GMAT are accepted by most US business schools. The GRE tests verbal reasoning, quantitative reasoning, and analytical writing. The GMAT focuses on integrated reasoning, quantitative, verbal, and analytical writing..."),
            BlogPost(title="Australia PR After Study: Complete Roadmap",
                     category="Immigration", country="Australia",
                     excerpt="Step-by-step guide to getting Permanent Residency in Australia after your studies.",
                     content="Australia's Temporary Graduate Visa (subclass 485) allows international students to live and work in Australia after graduation. The stay duration depends on your qualification level and study location..."),
            BlogPost(title="Germany: Study Free at World-Class Universities",
                     category="Destination", country="Germany",
                     excerpt="How Indian students can study in Germany for nearly free tuition.",
                     content="Most public universities in Germany charge no tuition fees even for international students. Students only pay a semester contribution (around €150-€350). Germany's strong engineering and technical programs attract thousands of Indian students annually..."),
        ]
        for p in posts:
            db.session.add(p)

    db.session.commit()
