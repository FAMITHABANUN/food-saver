from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "foodsaver_final_secure_key"

DB = "foodsaver.db"

# ==========================================
# EMAIL CONFIGURATION
# ==========================================
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
# These lines securely pull the variables you just saved in Render
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

mail = Mail(app)

# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT UNIQUE, password TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS donations(id INTEGER PRIMARY KEY AUTOINCREMENT, user_email TEXT, food_name TEXT, quantity TEXT, location TEXT, status TEXT DEFAULT 'Pending', delivery_boy TEXT DEFAULT '')")
    conn.commit()
    conn.close()

init_db()

# ================= ROUTES =================
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/user_register", methods=["GET", "POST"])
def user_register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password")
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users(name,email,password) VALUES (?,?,?)", (name, email, password))
            conn.commit()
            flash("Registration Successful!")
            return redirect(url_for("user_login"))
        except sqlite3.IntegrityError:
            flash("Email already exists")
        finally:
            conn.close()
    return render_template("user_register.html")

@app.route("/user_login", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password")
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = cur.fetchone()
        conn.close()
        if user:
            session["user"] = user[2]
            return redirect(url_for("donate_food"))
        flash("Invalid email or password")
    return render_template("user_login.html")

@app.route("/donate_food", methods=["GET", "POST"])
def donate_food():
    if "user" not in session:
        return redirect(url_for("user_login"))
    if request.method == "POST":
        food_name = request.form.get("food_name")
        quantity = request.form.get("quantity")
        location = request.form.get("location")
        user_email = session["user"]
        
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("INSERT INTO donations(user_email, food_name, quantity, location) VALUES (?,?,?,?)", (user_email, food_name, quantity, location))
        conn.commit()
        conn.close()

        # This part handles the email sending safely
        try:
            msg = Message(subject="Donation Confirmed", recipients=[user_email])
            msg.body = "Thank you for your donation!"
            mail.send(msg)
        except Exception as e:
            print(f"Note: Email could not be sent, but donation was recorded: {e}")
            
        return redirect(url_for("success"))
    return render_template("donate_food.html")

@app.route("/track_donation")
def track_donation():
    if "user" not in session: return redirect(url_for("user_login"))
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT * FROM donations WHERE user_email=?", (session["user"],))
    data = cur.fetchall()
    conn.close()
    return render_template("track_donation.html", donations=data)

@app.route("/success")
def success(): return render_template("success.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
    
