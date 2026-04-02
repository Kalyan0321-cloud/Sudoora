from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, TelField, SelectField, TextAreaField, FloatField, IntegerField
from wtforms.validators import DataRequired, Email, Optional, NumberRange

COUNTRY_CHOICES = [
    ('', 'Select Country'),
    ('USA', 'United States'),
    ('UK', 'United Kingdom'),
    ('Canada', 'Canada'),
    ('Australia', 'Australia'),
    ('Germany', 'Germany'),
    ('New Zealand', 'New Zealand'),
    ('Ireland', 'Ireland'),
    ('Singapore', 'Singapore'),
    ('Any', 'No Preference'),
]

COURSE_CHOICES = [
    ('', 'Select Course'),
    ('Engineering', 'Engineering'),
    ('Computer Science', 'Computer Science'),
    ('MBA', 'MBA / Business'),
    ('Medicine', 'Medicine'),
    ('Arts & Humanities', 'Arts & Humanities'),
    ('Business', 'Business'),
    ('Law', 'Law'),
    ('Architecture', 'Architecture'),
    ('Data Science', 'Data Science'),
    ('Nursing', 'Nursing'),
]

BUDGET_CHOICES = [
    ('', 'Select Budget'),
    ('20000', 'Under $20,000/year'),
    ('30000', '$20,000 - $30,000/year'),
    ('45000', '$30,000 - $45,000/year'),
    ('60000', '$45,000 - $60,000/year'),
    ('75000', 'Above $60,000/year'),
]

class ContactForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()])
    email = EmailField('Email Address', validators=[DataRequired(), Email()])
    phone = TelField('Phone Number', validators=[DataRequired()])
    preferred_country = SelectField('Preferred Country', choices=COUNTRY_CHOICES, validators=[Optional()])
    preferred_course = SelectField('Preferred Course', choices=COURSE_CHOICES, validators=[Optional()])
    budget = SelectField('Annual Budget (USD)', choices=BUDGET_CHOICES, validators=[Optional()])
    academic_score = FloatField('Academic Score (%)', validators=[Optional(), NumberRange(0, 100)])
    message = TextAreaField('Message', validators=[Optional()])

class RecommendationForm(FlaskForm):
    budget = IntegerField('Annual Budget (USD)', validators=[DataRequired(), NumberRange(5000, 200000)])
    academic_score = FloatField('Academic Score (%)', validators=[DataRequired(), NumberRange(40, 100)])
    preferred_country = SelectField('Preferred Country', choices=COUNTRY_CHOICES)
    preferred_course = SelectField('Preferred Course', choices=COURSE_CHOICES)
    ielts_score = FloatField('IELTS Score', validators=[Optional(), NumberRange(3.0, 9.0)])

class CostCalculatorForm(FlaskForm):
    country = SelectField('Destination Country', choices=COUNTRY_CHOICES[1:], validators=[DataRequired()])
    course_type = SelectField('Course Type', choices=COURSE_CHOICES[1:], validators=[DataRequired()])
    duration = SelectField('Duration (Years)', choices=[
        ('1', '1 Year'), ('2', '2 Years'), ('3', '3 Years'), ('4', '4 Years')
    ], validators=[DataRequired()])

class AdminLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
