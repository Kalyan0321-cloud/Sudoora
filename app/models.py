from app import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Lead(db.Model):
    """Student lead/inquiry model."""
    __tablename__ = 'leads'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    preferred_country = db.Column(db.String(50))
    preferred_course = db.Column(db.String(100))
    budget = db.Column(db.String(50))
    academic_score = db.Column(db.Float)
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default='new')  # new, contacted, enrolled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Lead {self.name}>'

class University(db.Model):
    """University data model."""
    __tablename__ = 'universities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(100))
    ranking = db.Column(db.Integer)
    tuition_min = db.Column(db.Integer, default=0)  # USD/year
    tuition_max = db.Column(db.Integer, default=0)
    intake_fall = db.Column(db.Boolean, default=True)
    intake_spring = db.Column(db.Boolean, default=False)
    intake_summer = db.Column(db.Boolean, default=False)
    popular_courses = db.Column(db.Text)
    acceptance_rate = db.Column(db.Integer)
    ielts_min = db.Column(db.Float)
    description = db.Column(db.Text)
    website = db.Column(db.String(200))
    is_featured = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'country': self.country,
            'city': self.city,
            'ranking': self.ranking,
            'tuition_min': self.tuition_min,
            'tuition_max': self.tuition_max,
            'intake_fall': self.intake_fall,
            'intake_spring': self.intake_spring,
            'intake_summer': self.intake_summer,
            'popular_courses': self.popular_courses,
            'acceptance_rate': self.acceptance_rate,
            'ielts_min': self.ielts_min,
            'description': self.description,
        }

class BlogPost(db.Model):
    """Blog post model."""
    __tablename__ = 'blog_posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50))
    country = db.Column(db.String(50))
    excerpt = db.Column(db.Text)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_published = db.Column(db.Boolean, default=True)

class Admin(UserMixin, db.Model):
    """Admin user model."""
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
