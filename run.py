"""
Sudoora Study Abroad Consultancy
================================
Self-contained Flask app — only requires Flask + requests (both in stdlib sandbox).
Uses Python's built-in sqlite3.

Run:   python run.py
Open:  http://localhost:5000
Admin: http://localhost:5000/admin  (admin / admin123)
"""

import os, sqlite3, json, secrets
from datetime import datetime
from functools import wraps

try:
    import requests as _requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

from flask import (Flask, render_template, request, jsonify,
                   redirect, url_for, session, g)

# ─── App ──────────────────────────────────────────────────────────────────────
app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(24))
DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'studyabroad.db')
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# ─── DB ───────────────────────────────────────────────────────────────────────
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db: db.close()

def query(sql, params=(), one=False):
    cur = get_db().execute(sql, params)
    return cur.fetchone() if one else cur.fetchall()

def execute(sql, params=()):
    db = get_db()
    cur = db.execute(sql, params)
    db.commit()
    return cur.lastrowid

def init_db():
    db = sqlite3.connect(DB_PATH)
    db.executescript("""
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, email TEXT, phone TEXT,
        preferred_country TEXT, preferred_course TEXT,
        budget TEXT, academic_score REAL, message TEXT,
        status TEXT DEFAULT 'new',
        created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS universities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, country TEXT, city TEXT, ranking INTEGER,
        tuition_min INTEGER DEFAULT 0, tuition_max INTEGER DEFAULT 0,
        intake_fall INTEGER DEFAULT 1, intake_spring INTEGER DEFAULT 0,
        intake_summer INTEGER DEFAULT 0,
        popular_courses TEXT, acceptance_rate INTEGER,
        ielts_min REAL, description TEXT
    );
    CREATE TABLE IF NOT EXISTS blog_posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT, category TEXT, country TEXT,
        excerpt TEXT, content TEXT,
        is_published INTEGER DEFAULT 1,
        created_at TEXT DEFAULT (datetime('now'))
    );
    """)
    if db.execute("SELECT COUNT(*) FROM universities").fetchone()[0] == 0:
        unis = [
            ("Massachusetts Institute of Technology","USA","Cambridge",1,55000,60000,1,1,0,"Engineering, Computer Science, Physics",4,7.0,"World's leading tech university."),
            ("Stanford University","USA","Stanford",2,56000,62000,1,0,0,"Computer Science, Business, Engineering",4,7.0,"Silicon Valley's premier university."),
            ("University of Cambridge","UK","Cambridge",3,30000,48000,1,0,0,"Natural Sciences, Engineering, Mathematics",21,7.5,"World-renowned research university."),
            ("University of Oxford","UK","Oxford",4,28000,45000,1,0,0,"Law, Medicine, Philosophy, PPE",17,7.5,"One of the world's oldest universities."),
            ("Imperial College London","UK","London",6,32000,50000,1,0,0,"Engineering, Medicine, Business",14,7.0,"UK's leading STEM university."),
            ("University of Toronto","Canada","Toronto",18,25000,45000,1,0,0,"Business, Engineering, Medicine",43,6.5,"Canada's top research university."),
            ("University of British Columbia","Canada","Vancouver",34,22000,40000,1,0,0,"Forestry, Medicine, Business",52,6.5,"Leading Canadian research university."),
            ("McGill University","Canada","Montreal",46,18000,35000,1,0,0,"Medicine, Law, Engineering",46,6.5,"Canada's top medical university."),
            ("Australian National University","Australia","Canberra",27,30000,48000,1,1,0,"Sciences, Law, Asia Pacific Studies",35,6.5,"Australia's national university."),
            ("University of Melbourne","Australia","Melbourne",33,28000,44000,1,1,0,"Arts, Business, Engineering",40,6.5,"Australia's top-ranked university."),
            ("Technical University of Munich","Germany","Munich",37,0,3000,1,1,0,"Engineering, Natural Sciences, Computer Science",8,6.5,"Germany's top technical university."),
            ("Heidelberg University","Germany","Heidelberg",64,0,1500,1,1,0,"Medicine, Natural Sciences, Humanities",15,6.0,"Germany's oldest university."),
        ]
        db.executemany("""INSERT INTO universities
            (name,country,city,ranking,tuition_min,tuition_max,intake_fall,intake_spring,
             intake_summer,popular_courses,acceptance_rate,ielts_min,description)
             VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""", unis)
    if db.execute("SELECT COUNT(*) FROM blog_posts").fetchone()[0] == 0:
        posts = [
            ("UK Student Visa (Tier 4) Guide 2024","Visa","UK",
             "Everything Indian students need to know about the UK Student Visa.",
             "The UK Student Visa allows international students to study for courses longer than 6 months. You'll need a CAS from your university, proof of English language skills, and financial evidence. Processing time is typically 3-5 weeks from India. Apply online and book a biometric appointment at your nearest VFS centre."),
            ("Top 10 Scholarships for Indian Students in Canada","Scholarships","Canada",
             "Comprehensive list of scholarships for Indian students studying in Canada.",
             "Canada offers numerous scholarships: Vanier Canada Graduate Scholarships ($50,000/year), Lester B. Pearson International Scholarship at University of Toronto (full funding), Ontario Graduate Scholarship, and many university-specific awards. Deadlines typically fall between November and January for fall intake."),
            ("GRE vs GMAT: Which Should You Take?","Test Prep","USA",
             "A detailed comparison to help you decide between GRE and GMAT.",
             "Both GRE and GMAT are accepted by most US business schools. GRE tests verbal reasoning, quantitative reasoning, and analytical writing. GMAT focuses on integrated reasoning and data sufficiency. Many universities now waive test requirements. Check each university's specific requirements before deciding."),
            ("Australia PR After Study: Complete Roadmap","Immigration","Australia",
             "Step-by-step guide to Permanent Residency in Australia after your studies.",
             "Australia's Temporary Graduate Visa (subclass 485) lets you live and work after graduation. Duration depends on qualification level. Regional graduates get up to 5 years. You can then apply for skilled migration via state sponsorship (189/190) or employer sponsorship (186/187)."),
            ("Germany: Study Free at World-Class Universities","Destination","Germany",
             "How Indian students can study in Germany for nearly free.",
             "Most public universities in Germany charge zero tuition fees for international students. You only pay a semester contribution of €150-350, which often includes public transport passes. Germany's engineering and technical programs are world-renowned. TU Munich, RWTH Aachen, and KIT are top choices."),
        ]
        db.executemany("INSERT INTO blog_posts (title,category,country,excerpt,content) VALUES (?,?,?,?,?)", posts)
    db.commit()
    db.close()

# ─── Data ─────────────────────────────────────────────────────────────────────
DESTINATIONS = {
    "USA":{"flag":"🇺🇸","code":"us","universities":4000,"avg_tuition":35000,"living_cost":18000,"visa_fee":185,"visa_type":"F-1 Student Visa","work_permit":"20 hrs/week on campus","pr_pathway":"H-1B → Green Card","popular_courses":["Computer Science","MBA","Engineering","Medicine"],"color":"#3B82F6","intake_months":["September","January"],"top_cities":["New York","Boston","San Francisco","Chicago"],"currency":"USD","language":"English"},
    "UK":{"flag":"🇬🇧","code":"gb","universities":130,"avg_tuition":22000,"living_cost":15000,"visa_fee":490,"visa_type":"Student Visa (Tier 4)","work_permit":"20 hrs/week during term","pr_pathway":"Graduate Route → Skilled Worker","popular_courses":["Law","Finance","Engineering","MBA"],"color":"#EF4444","intake_months":["September","January"],"top_cities":["London","Manchester","Edinburgh","Birmingham"],"currency":"GBP","language":"English"},
    "Canada":{"flag":"🇨🇦","code":"ca","universities":100,"avg_tuition":28000,"living_cost":14000,"visa_fee":150,"visa_type":"Study Permit","work_permit":"20 hrs/week off-campus","pr_pathway":"PGWP → Express Entry","popular_courses":["Engineering","Business","IT","Healthcare"],"color":"#EF4444","intake_months":["September","January","May"],"top_cities":["Toronto","Vancouver","Montreal","Calgary"],"currency":"CAD","language":"English/French"},
    "Australia":{"flag":"🇦🇺","code":"au","universities":43,"avg_tuition":32000,"living_cost":16000,"visa_fee":630,"visa_type":"Student Visa (subclass 500)","work_permit":"48 hrs/fortnight","pr_pathway":"485 Visa → Skilled Migration","popular_courses":["Nursing","Engineering","IT","Business"],"color":"#F59E0B","intake_months":["February","July"],"top_cities":["Sydney","Melbourne","Brisbane","Perth"],"currency":"AUD","language":"English"},
    "Germany":{"flag":"🇩🇪","code":"de","universities":400,"avg_tuition":1500,"living_cost":12000,"visa_fee":75,"visa_type":"National Visa (Type D)","work_permit":"120 full days/year","pr_pathway":"Job Seeker → Blue Card → PR","popular_courses":["Engineering","Computer Science","Automotive","Sciences"],"color":"#10B981","intake_months":["October","April"],"top_cities":["Munich","Berlin","Hamburg","Frankfurt"],"currency":"EUR","language":"German/English"},
    "New Zealand":{"flag":"🇳🇿","code":"nz","universities":8,"avg_tuition":25000,"living_cost":13000,"visa_fee":330,"visa_type":"Student Visa","work_permit":"20 hrs/week during study","pr_pathway":"Post-Study Work → Skilled Migrant","popular_courses":["Agriculture","Tourism","IT","Engineering"],"color":"#8B5CF6","intake_months":["February","July"],"top_cities":["Auckland","Wellington","Christchurch"],"currency":"NZD","language":"English"},
    "Ireland":{"flag":"🇮🇪","code":"ie","universities":34,"avg_tuition":18000,"living_cost":14000,"visa_fee":100,"visa_type":"Student Permission (Stamp 2)","work_permit":"20 hrs/week during term","pr_pathway":"Graduate Programme → Critical Skills","popular_courses":["Pharmacy","Business","Computer Science","Data Analytics"],"color":"#059669","intake_months":["September","January"],"top_cities":["Dublin","Cork","Galway","Limerick"],"currency":"EUR","language":"English"},
    "Singapore":{"flag":"🇸🇬","code":"sg","universities":6,"avg_tuition":20000,"living_cost":17000,"visa_fee":30,"visa_type":"Student's Pass","work_permit":"16 hrs/week during term","pr_pathway":"Employment Pass → PR","popular_courses":["Business","Finance","Engineering","Biomedical"],"color":"#DC2626","intake_months":["August","January"],"top_cities":["Singapore City"],"currency":"SGD","language":"English"},
}
CLIST = list(DESTINATIONS.keys())
FLAG_MAP = {"USA":"🇺🇸","UK":"🇬🇧","Canada":"🇨🇦","Australia":"🇦🇺","Germany":"🇩🇪","New Zealand":"🇳🇿","Ireland":"🇮🇪","Singapore":"🇸🇬"}
LIVING = {"USA":18000,"UK":15000,"Canada":14000,"Australia":16000,"Germany":12000,"New Zealand":13000,"Ireland":14000,"Singapore":17000}
INR = {"USD":83.5,"GBP":106.0,"EUR":90.5,"CAD":61.5,"AUD":54.0,"NZD":50.0,"SGD":62.0}
FALLBACK_NEWS = [
    {"title":"UK Introduces New Graduate Route Visa for International Students","description":"The UK government has extended the Graduate Route visa, allowing students to work for 2 years after graduation.","url":"#","source":"Study Abroad Times","publishedAt":"2024-11-15T10:00:00Z","category":"Visa","country":"UK"},
    {"title":"Canada Announces New Study Permit Cap for 2025","description":"IRCC has announced a temporary cap on study permit approvals for 2025.","url":"#","source":"Global Education News","publishedAt":"2024-11-10T08:30:00Z","category":"Policy","country":"Canada"},
    {"title":"Australia's Post-Study Work Rights Extended to 5 Years","description":"Australia has updated its Temporary Graduate Visa policy for regional university graduates.","url":"#","source":"International Student Hub","publishedAt":"2024-11-08T12:00:00Z","category":"Immigration","country":"Australia"},
    {"title":"Germany Eases Student Visa Process for Indian Applicants","description":"Germany's Federal Foreign Office has streamlined the visa process, reducing processing time to 4-6 weeks.","url":"#","source":"DAAD News","publishedAt":"2024-11-05T09:15:00Z","category":"Visa","country":"Germany"},
    {"title":"IELTS vs TOEFL: Which English Test is Right for You in 2025?","description":"A comprehensive guide comparing IELTS and TOEFL acceptance rates across top universities.","url":"#","source":"EduAdvisor","publishedAt":"2024-11-01T14:00:00Z","category":"Test Prep","country":"General"},
    {"title":"Top 10 Fully Funded Scholarships for Indian Students in 2025","description":"Scholarships offering full tuition, living expenses, and travel grants for Indian students.","url":"#","source":"Scholarship India","publishedAt":"2024-10-28T11:00:00Z","category":"Scholarships","country":"General"},
]
COURSES = ["","Engineering","Computer Science","MBA","Medicine","Arts & Humanities","Business","Law","Data Science","Nursing"]

def fmt_date(s):
    try: return datetime.strptime(s,"%Y-%m-%dT%H:%M:%SZ").strftime("%d %b %Y")
    except: return s

def get_news(n=6):
    key = os.environ.get("NEWS_API_KEY","")
    if key and HAS_REQUESTS:
        try:
            r = _requests.get("https://newsapi.org/v2/everything",
                params={"q":"international students study abroad","language":"en",
                        "sortBy":"publishedAt","pageSize":n,"apiKey":key},timeout=6)
            if r.status_code==200:
                arts=[a for a in r.json().get("articles",[]) if a.get("title") and a.get("description")]
                if arts: return arts[:n]
        except: pass
    return FALLBACK_NEWS[:n]

def get_recs(budget,score,country,course=None,ielts=None):
    rows=[dict(u) for u in query("SELECT * FROM universities ORDER BY ranking")]
    scored=[]
    for u in rows:
        s=0; reasons=[]
        total=(u["tuition_max"] or 0)+LIVING.get(u["country"],15000)
        if budget>=total: s+=40; reasons.append(f"Within your budget of ${budget:,}")
        elif budget>=total*0.85: s+=25; reasons.append("Achievable with scholarships")
        elif budget>=total*0.70: s+=10; reasons.append("Requires financial aid")
        ar=u["acceptance_rate"] or 50
        if score>=90: s+=30 if ar<=10 else 28
        elif score>=80: s+=25 if ar<=20 else 28; reasons.append("Good academic match")
        elif score>=70: s+=25 if ar>=30 else 15
        elif score>=60: s+=25 if ar>=50 else 10
        if country and country not in ("Any","") and u["country"]==country:
            s+=20; reasons.append(f"Your preferred country: {country}")
        elif country in ("Any",""): s+=10
        if ielts and ielts>=(u["ielts_min"] or 6.0): s+=10; reasons.append("IELTS meets requirements")
        elif ielts and ielts<(u["ielts_min"] or 6.0): s-=5
        if course and u["popular_courses"] and course.lower() in u["popular_courses"].lower():
            s+=5; reasons.append(f"{course} is a top program here")
        if u["ranking"] and u["ranking"]<=10: s+=3
        if s>0: scored.append({"u":dict(u),"score":s,"reasons":reasons[:3],"pct":min(int(s/108*100),98),"cost":total})
    scored.sort(key=lambda x:x["score"],reverse=True)
    return scored[:6]

def cost_calc(country,course,duration):
    tm={"Engineering":{"USA":45000,"UK":28000,"Canada":30000,"Australia":35000,"Germany":2000},
        "MBA":{"USA":55000,"UK":35000,"Canada":35000,"Australia":40000,"Germany":15000},
        "Medicine":{"USA":60000,"UK":38000,"Canada":20000,"Australia":42000,"Germany":3000},
        "Computer Science":{"USA":42000,"UK":26000,"Canada":28000,"Australia":33000,"Germany":2000},
        "Arts & Humanities":{"USA":35000,"UK":22000,"Canada":22000,"Australia":28000,"Germany":1500},
        "Business":{"USA":48000,"UK":30000,"Canada":32000,"Australia":35000,"Germany":12000}}
    d=DESTINATIONS.get(country,{}); tmap=tm.get(course,tm["Engineering"])
    tuition=tmap.get(country,30000); living=d.get("living_cost",15000)
    visa=d.get("visa_fee",200); health={"USA":2000,"UK":470,"Canada":800,"Australia":600,"Germany":1200}.get(country,800)
    return {"country":country,"course_type":course,"duration":duration,
            "annual_tuition":tuition,"annual_living":living,"total_tuition":tuition*duration,
            "total_living":living*duration,"visa_fee":visa,"health_insurance_annual":health,
            "total_health":health*duration,"grand_total":(tuition+living+health)*duration+visa,
            "currency":d.get("currency","USD"),"work_permit":d.get("work_permit","N/A"),
            "inr_rate":INR.get(d.get("currency","USD"),83.5)}

def bot(msg):
    m=msg.lower()
    if any(w in m for w in ["visa","permit"]): return "Visa requirements vary by country. UK: £490, Canada: $150, Australia: $630, Germany: €75. Processing takes 4–12 weeks. Our counselors provide end-to-end visa support!"
    if any(w in m for w in ["cost","fee","tuition","expensive","budget"]): return "Study costs vary widely! Germany: ~$13,500/yr total, Canada: ~$42,000/yr, UK: ~$37,000/yr, USA: ~$53,000/yr. Use our Cost Calculator for a personalized breakdown!"
    if any(w in m for w in ["scholarship","funding","grant","fellowship"]): return "Many scholarships available! Chevening (UK), DAAD (Germany, fully funded!), Commonwealth, Ontario Trillium (Canada), Destination Australia. We help you apply for all relevant scholarships!"
    if any(w in m for w in ["canada","pr","express entry","pgwp"]): return "Canada is excellent for PR! PGWP lets you work for up to 3 years post-graduation, then Express Entry PR is very achievable. Many Indian students get PR within 2-3 years of graduating."
    if any(w in m for w in ["germany","free tuition","no fees"]): return "Germany's public universities charge ZERO tuition, even for international students! Just €150-350/semester admin fee. Programs in English available. TU Munich, RWTH Aachen, and KIT are top picks."
    if any(w in m for w in ["ielts","toefl","english","language test"]): return "IELTS 6.5 is the most common requirement. UK universities: 6.5-7.5, Germany: 6.0-6.5, Canada/Australia: 6.5+. TOEFL is also widely accepted. Duolingo accepted by many universities now too!"
    if any(w in m for w in ["gre","gmat","sat","test prep"]): return "GRE for most master's programs, GMAT specifically for MBAs. Many universities now offer test waivers for working professionals or strong academic profiles (85%+). Check individual university requirements."
    if any(w in m for w in ["best country","which country","recommend","suggest"]): return "For PR pathways: Canada & Australia. For free tuition: Germany. For top rankings: USA & UK. For English + affordable: Ireland & New Zealand. For Asia-Pacific: Singapore. Use our AI Advisor for a personalized recommendation!"
    if any(w in m for w in ["hello","hi","hey","namaste","hola"]): return "Hello! 👋 I'm Sudoora AI, your study abroad assistant. I can help with visa info, university shortlisting, cost planning, scholarships, and more. What would you like to know?"
    if any(w in m for w in ["thank","thanks"]): return "You're welcome! Feel free to ask more, or book a free consultation with our expert counselors. Best of luck with your study abroad journey! 🎓"
    return "I can help with visas, costs, scholarships, country comparisons, test prep advice, and more. Could you be more specific? Or call us at +91 98765 43210 for personalized guidance from our expert counselors."

ADMIN_USER=os.environ.get("ADMIN_USERNAME","admin")
ADMIN_PASS=os.environ.get("ADMIN_PASSWORD","admin123")

def admin_required(f):
    @wraps(f)
    def dec(*a,**kw):
        if not session.get("admin"): return redirect(url_for("admin_login"))
        return f(*a,**kw)
    return dec

@app.context_processor
def inject_globals():
    return {"site_name":"Sudoora Consultancy","site_tagline":"Your Gateway to Global Education",
            "countries_list":CLIST,"flag_map":FLAG_MAP,"request":request}

# ─── Routes ───────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    unis=[dict(u) for u in query("SELECT * FROM universities ORDER BY ranking LIMIT 6")]
    return render_template("index.html",destinations=DESTINATIONS,news=get_news(3),
                           format_date=fmt_date,featured_unis=unis)

@app.route("/destinations")
def destinations():
    return render_template("destinations.html",destinations=DESTINATIONS)

@app.route("/destinations/<country_name>")
def destination_detail(country_name):
    if country_name not in DESTINATIONS: return "Not found",404
    unis=[dict(u) for u in query("SELECT * FROM universities WHERE country=? ORDER BY ranking",(country_name,))]
    c=DESTINATIONS[country_name]
    return render_template("destination_detail.html",country_name=country_name,country=c,
                           universities=unis,inr_rate=INR.get(c.get("currency","USD"),83.5))

@app.route("/universities")
def universities():
    cf=request.args.get("country",""); intake=request.args.get("intake","")
    mt=request.args.get("max_tuition",""); qs=request.args.get("q","")
    sql="SELECT * FROM universities WHERE 1=1"; params=[]
    if cf: sql+=" AND country=?"; params.append(cf)
    if intake=="fall": sql+=" AND intake_fall=1"
    elif intake=="spring": sql+=" AND intake_spring=1"
    if mt:
        try: sql+=" AND tuition_max<=?"; params.append(int(mt))
        except: pass
    if qs: sql+=" AND (name LIKE ? OR popular_courses LIKE ?)"; params+=[f"%{qs}%",f"%{qs}%"]
    sql+=" ORDER BY ranking"
    unis=[dict(u) for u in query(sql,params)]
    countries=[r[0] for r in query("SELECT DISTINCT country FROM universities ORDER BY country")]
    return render_template("universities.html",universities=unis,countries=countries,
                           filters={"country":cf,"intake":intake,"max_tuition":int(mt) if mt else 0,"q":qs})

@app.route("/cost-calculator",methods=["GET","POST"])
def cost_calculator():
    result=None; fd={}
    if request.method=="POST":
        fd=request.form.to_dict()
        try: result=cost_calc(fd.get("country","USA"),fd.get("course_type","Engineering"),int(fd.get("duration","2")))
        except: pass
    return render_template("cost_calculator.html",result=result,form_data=fd,
                           dest_list=CLIST,courses=COURSES[1:],
                           durations=[("1","1 Year"),("2","2 Years"),("3","3 Years"),("4","4 Years")])

@app.route("/recommend",methods=["GET","POST"])
def recommend():
    recs=[]; submitted=False; fd={}
    if request.method=="POST":
        fd=request.form.to_dict(); submitted=True
        try:
            budget=int(fd.get("budget",30000)); score=float(fd.get("academic_score",70))
            country=fd.get("preferred_country","Any"); course=fd.get("preferred_course","")
            ielts=fd.get("ielts_score",""); ielts=float(ielts) if ielts else None
            recs=get_recs(budget,score,country,course,ielts)
        except: pass
    return render_template("recommend.html",recommendations=recs,submitted=submitted,
                           form_data=fd,dest_list=CLIST,flag_map=FLAG_MAP,courses=COURSES)

@app.route("/intakes")
def intakes():
    cf=request.args.get("country","")
    sql="SELECT * FROM universities WHERE 1=1"; params=[]
    if cf: sql+=" AND country=?"; params.append(cf)
    unis=[dict(u) for u in query(sql+" ORDER BY country,ranking",params)]
    countries=[r[0] for r in query("SELECT DISTINCT country FROM universities ORDER BY country")]
    return render_template("intakes.html",universities=unis,countries=countries,country_filter=cf)

@app.route("/blog")
def blog():
    cat=request.args.get("category",""); country=request.args.get("country","")
    sql="SELECT * FROM blog_posts WHERE is_published=1"; params=[]
    if cat: sql+=" AND category=?"; params.append(cat)
    if country: sql+=" AND country=?"; params.append(country)
    posts=[dict(p) for p in query(sql+" ORDER BY created_at DESC",params)]
    return render_template("blog.html",db_posts=posts,api_news=get_news(6),
                           format_date=fmt_date,category=cat,country=country)

@app.route("/blog/<int:post_id>")
def blog_post(post_id):
    p=query("SELECT * FROM blog_posts WHERE id=?",(post_id,),one=True)
    if not p: return "Not found",404
    p=dict(p)
    related=[dict(r) for r in query("SELECT * FROM blog_posts WHERE country=? AND id!=? LIMIT 3",(p["country"],post_id))]
    return render_template("blog_post.html",post=p,related=related)

@app.route("/contact",methods=["GET","POST"])
def contact():
    success=False; errors={}; fd={}
    if request.method=="POST":
        fd=request.form.to_dict()
        if not fd.get("name","").strip(): errors["name"]="Name is required"
        if not fd.get("email","").strip() or "@" not in fd.get("email",""): errors["email"]="Valid email required"
        if not fd.get("phone","").strip(): errors["phone"]="Phone is required"
        if not errors:
            score=None
            try: score=float(fd["academic_score"]) if fd.get("academic_score") else None
            except: pass
            execute("INSERT INTO leads(name,email,phone,preferred_country,preferred_course,budget,academic_score,message) VALUES(?,?,?,?,?,?,?,?)",
                    (fd["name"],fd["email"],fd["phone"],fd.get("preferred_country",""),fd.get("preferred_course",""),fd.get("budget",""),score,fd.get("message","")))
            success=True
    return render_template("contact.html",success=success,errors=errors,form_data=fd,
                           dest_list=CLIST,courses=COURSES)

@app.route("/api/universities")
def api_universities():
    cf=request.args.get("country",""); q=request.args.get("q",""); mt=request.args.get("max_tuition","")
    sql="SELECT * FROM universities WHERE 1=1"; params=[]
    if cf: sql+=" AND country=?"; params.append(cf)
    if q: sql+=" AND (name LIKE ? OR popular_courses LIKE ?)"; params+=[f"%{q}%",f"%{q}%"]
    if mt:
        try: sql+=" AND tuition_max<=?"; params.append(int(mt))
        except: pass
    return jsonify([dict(u) for u in query(sql+" ORDER BY ranking LIMIT 20",params)])

@app.route("/api/exchange-rates")
def api_exchange_rates():
    return jsonify(INR)

@app.route("/api/cost-estimate")
def api_cost_estimate():
    return jsonify(cost_calc(request.args.get("country","USA"),
                             request.args.get("course","Engineering"),
                             int(request.args.get("duration","2"))))

@app.route("/api/lead",methods=["POST"])
def api_lead():
    d=request.json or {}
    if not all(k in d for k in ["name","email","phone"]):
        return jsonify({"success":False,"error":"Missing fields"}),400
    execute("INSERT INTO leads(name,email,phone,preferred_country,message) VALUES(?,?,?,?,?)",
            (d["name"],d["email"],d["phone"],d.get("preferred_country",""),d.get("message","")))
    return jsonify({"success":True,"message":"Thank you! We'll contact you within 24 hours. 🎓"})

@app.route("/api/chatbot",methods=["POST"])
def api_chatbot():
    return jsonify({"response":bot((request.json or {}).get("message",""))})

@app.route("/admin/login",methods=["GET","POST"])
def admin_login():
    error=None
    if session.get("admin"): return redirect(url_for("admin_dashboard"))
    if request.method=="POST":
        if request.form.get("username")==ADMIN_USER and request.form.get("password")==ADMIN_PASS:
            session["admin"]=True; return redirect(url_for("admin_dashboard"))
        error="Invalid credentials."
    return render_template("admin/login_simple.html",error=error)

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin",None); return redirect(url_for("index"))

@app.route("/admin")
@admin_required
def admin_dashboard():
    tl=query("SELECT COUNT(*) FROM leads",one=True)[0]
    nl=query("SELECT COUNT(*) FROM leads WHERE status='new'",one=True)[0]
    tu=query("SELECT COUNT(*) FROM universities",one=True)[0]
    tp=query("SELECT COUNT(*) FROM blog_posts",one=True)[0]
    leads=[dict(l) for l in query("SELECT * FROM leads ORDER BY created_at DESC LIMIT 10")]
    return render_template("admin/dashboard_simple.html",leads=leads,total_leads=tl,new_leads=nl,total_unis=tu,total_posts=tp)

@app.route("/admin/leads")
@admin_required
def admin_leads():
    return render_template("admin/leads_simple.html",leads=[dict(l) for l in query("SELECT * FROM leads ORDER BY created_at DESC")])

@app.route("/admin/lead/<int:lid>/status",methods=["POST"])
@admin_required
def update_lead_status(lid):
    execute("UPDATE leads SET status=? WHERE id=?",(request.form.get("status","new"),lid))
    return redirect(url_for("admin_leads"))

@app.route("/admin/universities")
@admin_required
def admin_universities():
    return render_template("admin/unis_simple.html",universities=[dict(u) for u in query("SELECT * FROM universities ORDER BY ranking")])

if __name__=="__main__":
    init_db()
    print("\n" + "="*55)
    print("  🌍 Sudoora Study Abroad Consultancy")
    print("  🚀 Starting: http://localhost:5000")
    print("  🔐 Admin:    http://localhost:5000/admin")
    print("     Login:    admin / admin123")
    print("="*55 + "\n")
    app.run(debug=True,host="0.0.0.0",port=5000)
