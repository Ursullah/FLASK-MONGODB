from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from dotenv import load_dotenv
import os

# Placeholder for send_reset_email to avoid ImportError during development.
# Replace this with a proper implementation or create a separate email_utils.py.
def send_reset_email(*args, **kwargs):
    """No-op placeholder; implement real email sending in production."""
    return None

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET")

# MongoDB setup
app.config["MONGO_URI"] = os.getenv("MONGO_URI")

# Create client
mongo_client = MongoClient(app.config["MONGO_URI"])

# specify the database name
mongo = mongo_client["flaskdb"]

# Initialize serializer for tokens
s = URLSafeTimedSerializer(app.secret_key)

app.logger.info("MongoDB connected successfully!")

# --- Email Config ---
app.config["MAIL_SERVER"] = os.getenv("MAIL_HOST")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "True") == "True"
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER")

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/test_db")
def test_db():
    try:
        # Test collection
        mongo.test_collection.insert_one({"message": "Hello MongoDB"})
        message = mongo.test_collection.find_one({"message": "Hello MongoDB"})
        return jsonify({"status": "success", "message": message["message"]})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        existing = mongo.users.find_one({"email": email})
        if existing:
            flash("User already exists!")
            return redirect(url_for("register"))

        mongo.users.insert_one({"email": email, "password": password})
        flash("Registration successful! You can now log in.")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = mongo.users.find_one({"email": email, "password": password})
        if user:
            session['user'] = email  # store login session
            return redirect(url_for('search'))  # redirect to search page
        else:
            flash("Invalid credentials, try again!")
            return redirect(url_for('login'))  # FIXED

    return render_template('login.html')  # FIXED




@app.route("/forgot", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]
        user = mongo.users.find_one({"email": email})
        if user:
            send_reset_email(email)
            flash("Password reset link sent to your email.")
        else:
            flash("Email not found.")
    return render_template("forgot_password.html")


@app.route("/reset/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        email = s.loads(token, salt='password-reset', max_age=3600)
    except:
        flash("Token expired or invalid.")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":
        new_pass = request.form["password"]
        mongo.users.update_one({"email": email}, {"$set": {"password": new_pass}})
        flash("Password updated successfully!")
        return redirect(url_for("login"))

    return render_template("reset_password.html")

@app.route("/contact", methods=["GET", "POST"])
def contact_form():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        data = {
            "mobile": request.form["mobile"],
            "email": request.form["email"],
            "address": request.form["address"],
            "reg_number": request.form["reg_number"]
        }
        mongo.contacts.insert_one(data)
        flash("Contact saved successfully!")
    return render_template("contact_form.html")


@app.route("/search", methods=["GET", "POST"])
def search():
    if "user" not in session:
        return redirect(url_for("login"))
    
    contact = None
    message = None

    if request.method == "POST":
        reg_no = request.form["reg_number"]
        contact = mongo.contacts.find_one({"reg_number": reg_no})
        if not contact:
            message = "No contact found with that registration number."
    return render_template("search.html", contact=contact, message=message)
