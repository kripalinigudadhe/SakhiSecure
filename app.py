from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import mysql.connector
from flask_cors import CORS
import requests, os
import csv 
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
import matplotlib.pyplot as plt
from flask import send_file
from dotenv import load_dotenv
from reportlab.lib.utils import ImageReader
from collections import Counter
from datetime import datetime

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")
PORT = int(os.getenv("PORT", 5000))

if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY not set in .env file")
if not GROQ_MODEL:
    raise ValueError("❌ GROQ_MODEL not set in .env file")

app = Flask(__name__)
CORS(app)
app.secret_key = "sakhi_secure"

# ---------------- MySQL Connection ----------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="kpg123",
    database="sakhi_secure"
)
cursor = db.cursor(dictionary=True)

# ---------------- Signup Route ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        fullname = request.form.get("fullname")
        dob = request.form.get("dob")
        profession = request.form.get("profession")
        area = request.form.get("area")
        city = request.form.get("city")
        state = request.form.get("state")
        email = request.form.get("email")
        phone = request.form.get("phone")
        age = request.form.get("age")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm-password")

        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for("signup"))

        try:
            cursor.execute("""
                INSERT INTO users (fullname, dob, profession, area, city, state, email, phone, age, password)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (fullname, dob, profession, area, city, state, email, phone, age, password))
            db.commit()
            flash("Signup successful! Please login.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            db.rollback()
            flash(f"Error: {str(e)}", "error")
            return redirect(url_for("signup"))

    return render_template("signup.html")

@app.route("/download_report/<int:report_id>")
def download_report(report_id):
    if "user_id" not in session:
        flash("Please login first", "error")
        return redirect(url_for("login"))

    # Fetch report from DB
    cursor.execute("SELECT * FROM reports WHERE id=%s AND user_id=%s", (report_id, session["user_id"]))
    report = cursor.fetchone()
    if not report:
        flash("Report not found!", "error")
        return redirect(url_for("analytics"))

    # Create PDF in memory
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Title / Header
    pdf.setFillColor(colors.HexColor("#ed5c8d"))
    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawCentredString(width/2, height - 50, "SakhiSecure Incident Report")

    # User & Report Info
    pdf.setFillColor(colors.black)
    pdf.setFont("Helvetica-Bold", 12)
    y = height - 100
    line_height = 20
    info_fields = [
        ("Report ID", report['id']),
        ("Incident Type", report['incident_type']),
        ("Location", report['location']),
        ("Date & Time", report['date_time']),
        ("Severity", report['severity']),
        ("Description", report['description']),
        ("Witnesses", report['witnesses']),
        ("Anonymous", "Yes" if report['anonymous'] else "No"),
        ("Follow Up", "Yes" if report['follow_up'] else "No"),
        ("Shared with Community", "Yes" if report['share_community'] else "No")
    ]
    for label, value in info_fields:
        pdf.drawString(50, y, f"{label}: {value}")
        y -= line_height

    # ---------------- Create Charts ----------------
    # Chart 1: Incident Type Distribution
    cursor.execute("SELECT incident_type, COUNT(*) as count FROM reports WHERE user_id=%s GROUP BY incident_type", (session["user_id"],))
    data = cursor.fetchall()
    incident_types = [d['incident_type'] for d in data]
    counts = [d['count'] for d in data]

    plt.figure(figsize=(4,3))
    plt.bar(incident_types, counts, color="#ed5c8d")
    plt.title("Incident Type Distribution")
    plt.tight_layout()
    chart1 = io.BytesIO()
    plt.savefig(chart1, format='png')
    chart1.seek(0)
    plt.close()

    # Chart 2: Severity Breakdown
    cursor.execute("SELECT severity, COUNT(*) as count FROM reports WHERE user_id=%s GROUP BY severity", (session["user_id"],))
    data = cursor.fetchall()
    severity = [d['severity'] for d in data]
    severity_counts = [d['count'] for d in data]

    plt.figure(figsize=(4,3))
    plt.pie(severity_counts, labels=severity, autopct='%1.1f%%', colors=["#ff6b81","#ff92a1","#ffc1d3"])
    plt.title("Severity Breakdown")
    plt.tight_layout()
    chart2 = io.BytesIO()
    plt.savefig(chart2, format='png')
    chart2.seek(0)
    plt.close()

    # Embed charts using ImageReader
    pdf.drawImage(ImageReader(chart1), 50, y - 220, width=250, height=180)
    pdf.drawImage(ImageReader(chart2), 300, y - 220, width=250, height=180)

    # Footer
    pdf.setFont("Helvetica-Oblique", 10)
    pdf.setFillColor(colors.grey)
    pdf.drawCentredString(width/2, 30, "Generated by SakhiSecure — AI for Women’s Safety")

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name=f"report_{report_id}.pdf", mimetype='application/pdf')

# ---------------- Login ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email,password))
        user = cursor.fetchone()
        if user:
            session["user_id"] = user["id"]
            flash(f"Login successful! Welcome {user['fullname']}", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password", "error")
            return redirect(url_for("login"))
    return render_template("login.html")

# ---------------- Logout ----------------
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))

# ---------------- Dashboard ----------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please login first", "error")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()

    # Fetch persistent stats only (from user_stats table)
    cursor.execute("SELECT * FROM user_stats WHERE user_id=%s", (user_id,))
    stats = cursor.fetchone()
    if not stats:
        # Initialize default stats if not exists
        cursor.execute("INSERT INTO user_stats (user_id) VALUES (%s)", (user_id,))
        db.commit()
        cursor.execute("SELECT * FROM user_stats WHERE user_id=%s", (user_id,))
        stats = cursor.fetchone()

    return render_template("dashboard.html", user=user, stats=stats)


@app.route("/update_stat", methods=["POST"])
def update_stat():
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401

    user_id = session["user_id"]
    stat_type = request.form.get("stat_type")
    value = request.form.get("value")

    if stat_type not in ["active_alerts", "safe_zones", "community_reports", "avg_response_time"]:
        return jsonify({"error": "Invalid stat type"}), 400

    cursor.execute(f"""
        UPDATE user_stats SET {stat_type}=%s WHERE user_id=%s
    """, (value, user_id))
    db.commit()

    return jsonify({"success": True, "new_value": value})


# ---------------- Analytics ----------------
# ---------------- Analytics ----------------
@app.route('/analytics')
def analytics():
    if "user_id" not in session:
        flash("Please login first", "error")
        return redirect(url_for("login"))

    user_id = session["user_id"]

    # Fetch reports for logged-in user
    cursor.execute("SELECT * FROM reports WHERE user_id=%s ORDER BY created_at DESC", (user_id,))
    reports = cursor.fetchall()

    # Count severity
    high_risk_count = sum(1 for r in reports if r['severity'].lower() == 'high')
    medium_risk_count = sum(1 for r in reports if r['severity'].lower() == 'medium')
    low_risk_count = sum(1 for r in reports if r['severity'].lower() == 'low')

    # Count incidents by type for this user
    incident_counter = Counter()
    for r in reports:
        incident_type = r.get('incident_type', 'Unknown')
        incident_counter[incident_type] += 1

    incident_types = list(incident_counter.keys())
    incident_counts = list(incident_counter.values())

    return render_template('analytics.html',
                           reports=reports,
                           high_risk_count=high_risk_count,
                           medium_risk_count=medium_risk_count,
                           low_risk_count=low_risk_count,
                           incident_types=incident_types,
                           incident_counts=incident_counts)

# ---------------- Submit Report ----------------
@app.route("/report_incident", methods=["POST"])
def report_incident():
    if "user_id" not in session:
        flash("Please login first", "error")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    incident_type = request.form.get("incident_type")
    location = request.form.get("location")
    date_time = request.form.get("date_time") or None
    severity = request.form.get("severity")
    description = request.form.get("description")
    witnesses = request.form.get("witnesses") or "none"
    anonymous = True if request.form.get("anonymous") else False
    follow_up = True if request.form.get("follow_up") else False
    share_community = True if request.form.get("share_community") else False

    try:
        cursor.execute("""
            INSERT INTO reports (
                user_id, incident_type, location, date_time, severity, description,
                witnesses, anonymous, follow_up, share_community
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id, incident_type, location, date_time, severity, description,
            witnesses, anonymous, follow_up, share_community
        ))
        db.commit()
        flash("Report submitted successfully!", "success")
    except Exception as e:
        db.rollback()
        flash(f"Error submitting report: {str(e)}", "error")

    return redirect(url_for("analytics"))


# ---------------- Pages ----------------
@app.route("/")
def index():
    user = None
    if "user_id" in session:
        cursor.execute("SELECT * FROM users WHERE id=%s", (session["user_id"],))
        user = cursor.fetchone()
    return render_template("index.html", user=user)


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/alert")
def alert():
    return render_template("alert.html")

@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

@app.route("/community")
def community():
    return render_template("community.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/defence")
def defence():
    return render_template("defence.html")

@app.route("/faq")
def faq():
    return render_template("faq.html")
@app.route('/emotion_journal')
def emotion_journal():
    return render_template('emotion.html')

@app.route("/features")
def features():
    return render_template("features.html")

@app.route("/help")
def help_page():
    return render_template("help.html")

@app.route("/incident")
def incident():
    return render_template("incident.html")

@app.route("/prevention")
def prevention():
    return render_template("prevention.html")

@app.route("/report")
def report():
    return render_template("report.html")

@app.route("/resources")
def resources():
    return render_template("resources.html")

@app.route("/safety")
def safety():
    return render_template("safety.html")

@app.route("/schemes")
def schemes():
    return render_template("schemes.html")

@app.route("/time_risk")
def time_risk():
    return render_template("time_risk.html")

@app.route("/news")
def news():
    return render_template("news.html")

@app.route("/partners")
def partners():
    return redirect(url_for('index'))

@app.route("/privacy")
def privacy():
    return redirect(url_for('about'))

@app.route("/terms")
def terms():
    return redirect(url_for('about'))

@app.route("/forgot_password")
def forgot_password():
    return redirect(url_for("login"))

@app.route("/profile")
def profile():
    if "user_id" not in session:
        flash("Please login first", "error")
        return redirect(url_for("login"))
    
    cursor.execute("SELECT * FROM users WHERE id=%s", (session["user_id"],))
    user = cursor.fetchone()
    return render_template("profile.html", user=user)

@app.route('/predictive_analysis', methods=['GET', 'POST'])
def predictive_analysis():
    prediction = None
    details = {}

    if request.method == 'POST':
        time_of_day = request.form.get('time_of_day')
        location_type = request.form.get('location_type')
        incidents = int(request.form.get('incidents'))
        streetlights = request.form.get('streetlights')
        police_patrol = request.form.get('police_patrol')
        crowd_level = request.form.get('crowd_level')
        distance = float(request.form.get('distance'))

        # Load dataset
        data = []
        with open('safety_data.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)

        # Basic rule-based prediction (no ML)
        score = 0
        if incidents > 7: score += 3
        elif incidents > 4: score += 2
        elif incidents > 2: score += 1

        if streetlights == "no": score += 2
        if police_patrol == "low": score += 2
        elif police_patrol == "medium": score += 1
        if crowd_level == "low": score += 2
        elif crowd_level == "medium": score += 1
        if time_of_day == "night": score += 3
        elif time_of_day == "evening": score += 1
        if distance > 3: score += 2
        elif distance > 2: score += 1

        if score >= 8:
            prediction = "High Risk"
        elif score >= 5:
            prediction = "Medium Risk"
        else:
            prediction = "Low Risk"

        details = {
            "time": time_of_day,
            "location": location_type,
            "incidents": incidents,
            "streetlights": streetlights,
            "police": police_patrol,
            "crowd": crowd_level,
            "distance": distance
        }

    return render_template("predictive_analysis.html", prediction=prediction, details=details)

@app.route("/volunteer", methods=["GET", "POST"])
def volunteer():
    if request.method == "POST":
        fullname = request.form["vol-name"]
        email = request.form["vol-email"]
        phone = request.form["vol-phone"]
        city = request.form["vol-city"]
        area_interest = request.form["vol-area"]
        message = request.form["vol-message"]
        updates = 1 if request.form.get("updates") else 0

        try:
            cursor.execute("""
                INSERT INTO volunteers (fullname, email, phone, city, area_interest, message, updates)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (fullname, email, phone, city, area_interest, message, updates))
            db.commit()
            flash("✅ Your application has been submitted. We’ll look forward to working with you!", "success")
        except Exception as e:
            db.rollback()
            print(e)
            flash("❌ Something went wrong! Please try again.", "error")

        return redirect(url_for("volunteer"))

    # Fetch registered volunteers
    cursor.execute("SELECT * FROM volunteers ORDER BY id DESC")
    volunteers = cursor.fetchall()

    return render_template("volunteer.html", volunteers=volunteers)


# ---------------- API for chatbot ----------------
@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message")
    if not message:
        return jsonify({"error": "Message is required"}), 400

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "You are SakhiSecure Women Assistant."},
            {"role": "user", "content": message}
        ],
        "max_tokens": 500,
        "temperature": 0.2
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json=payload
        )
        response.raise_for_status()
        data = response.json()
        reply = data.get("choices", [{}])[0].get("message", {}).get("content", "No content")
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- Run the app ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=True)
