import os
import sqlite3
import requests
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, flash, url_for, session, send_from_directory, jsonify
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
import json


from dotenv import load_dotenv
from email_utils import (
    create_verification_token,
    send_verification_email,
    verify_token,
    log_verification_attempt,
    mark_email_verified
)

# Load environment variables
load_dotenv()
# Initialize SQLAlchemy object




app = Flask(__name__)
# your DB config and Company model here...
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///companies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy()
db.init_app(app)

# Initialize database tables
with app.app_context():
    db.create_all()


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    address = db.Column(db.String(300))
    phone = db.Column(db.String(50))
    mobile = db.Column(db.String(50))
    email = db.Column(db.String(100))
    services = db.Column(db.String(300))




def get_company_prompt_data():
    try:
        with app.app_context():
            companies = Company.query.all()
            return [
                {
                    "name": c.name,
                    "website": c.address,
                    "services": c.services.split(", ") if c.services else [],
                    "contact": f"{c.email} | {c.phone or ''} | {c.mobile or ''}"
                }
                for c in companies
            ]
    except Exception as e:
        print(f"Error fetching company data: {str(e)}")
        return []

def create_system_prompt():
    companies_data = get_company_prompt_data()
    return f"""
You are a helpful assistant for business support.

Only answer questions about the following companies:

{json.dumps(companies_data, indent=2)}

If the user's query is not about one of these companies, reply:
"I'm here to assist only with our listed partner companies. Please ask a question related to them."

Stick strictly to this rule.
"""

try:
    from flask_cors import CORS
    CORS(app)
    print("CORS enabled")
except ImportError:
    print("flask-cors not installed. Install with: pip install flask-cors")

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
app.config['APP_NAME'] = os.getenv('APP_NAME', 'Africa House Pakistan')

# Initialize Flask-Mail
mail = Mail(app)



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            # Get data from form
            country = request.form['country']
            role = request.form['role']
            email = request.form['email'].lower().strip()
            password = request.form['password']
            password_again = request.form['password_again']
            company_name = request.form['company_name']
            full_name = request.form['full_name']
            mobile_number = request.form['mobile_number']

            # Validation
            if password != password_again:
                flash("Passwords do not match. Please try again.", "error")
                return render_template('Register_page.html')

            if len(password) < 6:
                flash("Password must be at least 6 characters long.", "error")
                return render_template('Register_page.html')

            # Check if email already exists
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            existing_user = cursor.fetchone()

            if existing_user:
                conn.close()
                flash("An account with this email already exists.", "error")
                return render_template('Register_page.html')

            # Generate verification token
            verification_token = create_verification_token(email)
            token_expires = datetime.now() + timedelta(hours=24)

            # Save user to database (unverified)
            cursor.execute('''
                INSERT INTO users (country, role, email, password, company_name, full_name, mobile_number,
                                 email_verified, verification_token, verification_token_expires)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (country, role, email, password, company_name, full_name, mobile_number,
                  False, verification_token, token_expires))

            user_id = cursor.lastrowid
            conn.commit()
            conn.close()

            # Send verification email
            email_sent = send_verification_email(mail, email, full_name, verification_token)

            if email_sent:
                # Log verification attempt
                log_verification_attempt(user_id, email, verification_token)

                # Store email in session for verification page
                session['pending_verification_email'] = email

                return redirect(url_for('verification_sent'))
            else:
                flash("Account created but failed to send verification email. Please contact support.", "warning")
                return redirect(url_for('login'))

        except Exception as e:
            print(f"Signup error: {str(e)}")
            flash("An error occurred during registration. Please try again.", "error")
            return render_template('Register_page.html')

    return render_template('Register_page.html')

@app.route('/verification-sent')
def verification_sent():
    """Page shown after signup to inform user about verification email"""
    email = session.get('pending_verification_email')
    if not email:
        return redirect(url_for('signup'))

    return render_template('verification_sent.html', email=email)

@app.route('/verify-email/<token>')
def verify_email(token):
    """Handle email verification when user clicks the link"""
    try:
        # Verify the token
        email = verify_token(token, expiration=86400)  # 24 hours

        if email:
            # Check if user exists and is not already verified
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('SELECT id, email_verified, full_name FROM users WHERE email = ?', (email,))
            user = cursor.fetchone()

            if user:
                user_id, is_verified, full_name = user

                if is_verified:
                    conn.close()
                    return render_template('verification_result.html',
                                         status='already_verified',
                                         message='Your email is already verified!')

                # Mark email as verified
                success = mark_email_verified(email)
                conn.close()

                if success:
                    # Clear session
                    session.pop('pending_verification_email', None)

                    return render_template('verification_result.html',
                                         status='success',
                                         message='Email verified successfully! You can now log in.',
                                         user_name=full_name)
                else:
                    return render_template('verification_result.html',
                                         status='error',
                                         message='Failed to verify email. Please try again.')
            else:
                conn.close()
                return render_template('verification_result.html',
                                     status='error',
                                     message='User not found.')
        else:
            return render_template('verification_result.html',
                                 status='expired',
                                 message='Verification link has expired. Please register again.')

    except Exception as e:
        print(f"Email verification error: {str(e)}")
        return render_template('verification_result.html',
                             status='error',
                             message='An error occurred during verification.')

@app.route('/resend-verification', methods=['POST'])
def resend_verification():
    """Resend verification email"""
    email = request.form.get('email', '').lower().strip()

    if not email:
        flash("Please provide an email address.", "error")
        return redirect(url_for('signup'))

    try:
        # Check if user exists and is not verified
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, email_verified, full_name FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()

        if user:
            user_id, is_verified, full_name = user

            if is_verified:
                conn.close()
                flash("Email is already verified!", "info")
                return redirect(url_for('login'))

            # Generate new verification token
            verification_token = create_verification_token(email)
            token_expires = datetime.now() + timedelta(hours=24)

            # Update user's verification token
            cursor.execute('''
                UPDATE users
                SET verification_token = ?, verification_token_expires = ?
                WHERE email = ?
            ''', (verification_token, token_expires, email))
            conn.commit()
            conn.close()

            # Send verification email
            email_sent = send_verification_email(mail, email, full_name, verification_token)

            if email_sent:
                log_verification_attempt(user_id, email, verification_token)
                session['pending_verification_email'] = email
                flash("Verification email sent successfully!", "success")
                return redirect(url_for('verification_sent'))
            else:
                flash("Failed to send verification email. Please try again.", "error")
                return redirect(url_for('signup'))
        else:
            conn.close()
            flash("No account found with this email address.", "error")
            return redirect(url_for('signup'))

    except Exception as e:
        print(f"Resend verification error: {str(e)}")
        flash("An error occurred. Please try again.", "error")
        return redirect(url_for('signup'))

@app.route('/login.html', methods=['GET', 'POST'])
def login():
    """Handle user login with email verification check"""
    if request.method == 'POST':
        email = request.form.get('email', '').lower().strip()
        password = request.form.get('password', '')

        # Basic validation
        if not email or not password:
            flash("Please enter both email and password.", "error")
            return render_template('Login_page.html')

        try:
            # Check user credentials
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, email, password, full_name, role, email_verified
                FROM users
                WHERE email = ?
            ''', (email,))
            user = cursor.fetchone()
            conn.close()

            if not user:
                flash("Invalid email or password.", "error")
                return render_template('Login_page.html')

            user_id, db_email, db_password, full_name, role, email_verified = user

            # Check password
            if password != db_password:  # In production, use proper password hashing
                flash("Invalid email or password.", "error")
                return render_template('Login_page.html')

            # Check if email is verified
            if not email_verified:
                session['pending_verification_email'] = email
                flash("Please verify your email before logging in.", "warning")
                return redirect(url_for('verification_sent'))

            # Set session variables for logged in user
            session['user_id'] = user_id
            session['email'] = db_email
            session['full_name'] = full_name
            session['role'] = role
            session['logged_in'] = True

            # Redirect based on role
            if role == 'vendor':
                return redirect('/vendor_dashboard.html')
            else:
                return redirect('/leads_page.html')  # Default for other roles

        except Exception as e:
            print(f"Login error: {str(e)}")
            flash("An error occurred during login. Please try again.", "error")
            return render_template('Login_page.html')

    # GET request - show login form
    return render_template('Login_page.html')

@app.route('/logout')
def logout():
    """Handle user logout"""
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    """Protected dashboard route"""
    if not session.get('logged_in'):
        flash("Please log in to access the dashboard.", "warning")
        return redirect(url_for('login'))

    from datetime import datetime
    current_date = datetime.now().strftime("%B %Y")

    return render_template('dashboard.html', current_date=current_date)

@app.route('/profile')
def profile():
    """User profile route"""
    if not session.get('logged_in'):
        flash("Please log in to access your profile.", "warning")
        return redirect(url_for('login'))

    return render_template('vendor_profile.html')

@app.route('/vendor_dashboard.html')
def vendor_dashboard():
    """Serve vendor dashboard HTML"""
    if not session.get('logged_in'):
        flash("Please log in to access the dashboard.", "warning")
        return redirect(url_for('login'))
    return render_template( 'vendor_dashboard.html')

@app.route('/leads_page.html')
def leads_page():
    """Serve leads page HTML"""
    if not session.get('logged_in'):
        flash("Please log in to access this page.", "warning")
        return redirect(url_for('login'))
    return render_template('leads_page.html')





@app.route('/vendor_profile.html')
def vendor_profile():
    """Serve vendor profile HTML"""
    if not session.get('logged_in'):
        flash("Please log in to access this page.", "warning")
        return redirect(url_for('login'))
    return render_template('vendor_profile.html')

@app.route('/connections_page.html')
def connections_page():
    """Serve connections page HTML"""
    if not session.get('logged_in'):
        flash("Please log in to access this page.", "warning")
        return redirect(url_for('login'))
    return render_template( 'connections_page.html')

@app.route('/images/<path:filename>')
def serve_images(filename):
    """Serve image files"""
    return send_from_directory('static/images', filename)

@app.route('/')
def index():
    return render_template('Main_page.html')

@app.route('/ai_assistant')
def ai_assistant_page():
    return render_template('ai_assistant.html')



# API Configuration
API_KEY = "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"

# Available models on OpenRouter (try these in order)
MODELS = [
    "google/gemma-2-9b-it:free",              # Free Gemma model (try first)
    "microsoft/phi-3-mini-128k-instruct:free", # Free Phi model
    "meta-llama/llama-3.2-3b-instruct:free",  # Free Llama model (rate limited)
    "huggingface/meta-llama/Llama-3.2-1B-Instruct", # Alternative free model
    "openai/gpt-3.5-turbo",                   # Paid OpenAI model (last resort)
]

MODEL = MODELS[0]  # Use the first model by default

def try_ai_request(user_message, system_prompt=None, models_to_try=None):
    """Try AI request with different models until one works"""
    if models_to_try is None:
        models_to_try = MODELS

    for model in models_to_try:
        try:
            print(f"Trying model: {model}")

            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }

            data = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt or "You are a helpful AI assistant for Africa House Pakistan. Answer only business-related questions."},
                    {"role": "user", "content": user_message}
                ]
            }

            response = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                   headers=headers,
                                   json=data,
                                   timeout=30)

            print(f"Model {model} - Response Status: {response.status_code}")

            if response.status_code == 200:
                response_data = response.json()
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    ai_reply = response_data["choices"][0]["message"]["content"]
                    print(f"Success with model: {model}")
                    return {"reply": ai_reply, "model_used": model}
            elif response.status_code == 429:
                print(f"Model {model} rate limited (429) - trying next model")
                continue
            else:
                print(f"Model {model} failed with status {response.status_code}: {response.text}")

        except Exception as e:
            print(f"Model {model} failed with error: {str(e)}")
            continue

    fallback_response = """I'm currently experiencing high demand and some technical difficulties. However, I can still help you with:

• Finding buyers and suppliers across Africa and Pakistan
• Trade opportunities and market insights
• Business connections and networking
• Export/import guidance

Please try asking your question again in a moment, or contact our support team for immediate assistance."""

    return {"reply": fallback_response, "model_used": "fallback"}

# Test route to check if Flask is working
@app.route('/test', methods=['GET'])
def test():
    return jsonify({"status": "Flask is working!", "message": "API endpoint is accessible"})

# Test POST route
@app.route('/test_post', methods=['POST'])
def test_post():
    return jsonify({"status": "POST is working!", "received_data": request.get_json()})

@app.route('/ask', methods=['POST'])
def ask():
    print("=== AI ASK ENDPOINT CALLED ===")
    try:
        # Log the incoming request
        print(f"Request method: {request.method}")
        print(f"Request headers: {dict(request.headers)}")
        print(f"Request data: {request.get_data()}")

        # Get user message from request
        if not request.json or 'message' not in request.json:
            print("ERROR: No message provided in request")
            return jsonify({"error": "No message provided"}), 400

        user_message = request.json['message'].strip()
        print(f"User message received: '{user_message}'")

        if not user_message:
            print("ERROR: Empty message")
            return jsonify({"error": "Empty message"}), 400

        # Check API key
        if not API_KEY:
            print("ERROR: API_KEY is not set")
            return jsonify({"error": "API configuration error"}), 500

        print(f"Trying AI request with message: {user_message}")

        # Try the AI request with multiple models
        # Create dynamic system prompt from DB
        print("Creating system prompt with company data...")
        system_prompt = create_system_prompt()
        print(f"System prompt created. Length: {len(system_prompt)} characters")
        print(f"System prompt preview: {system_prompt[:200]}...")

        # Call AI with prompt + message
        print("Calling AI with company data...")
        result = try_ai_request(user_message, system_prompt=system_prompt)


        if "reply" in result:
            model_used = result.get('model_used', 'unknown')
            print(f"Response generated! Model used: {model_used}")
            print(f"AI Reply: {result['reply']}")
            return jsonify({"reply": result["reply"], "model_used": model_used})
        else:
            # This shouldn't happen with our fallback, but just in case
            print(f"Unexpected result: {result}")
            return jsonify({"error": "Unable to generate response. Please try again."}), 500

    except requests.exceptions.Timeout:
        print("ERROR: Request timeout")
        return jsonify({"error": "Request timeout. Please try again."}), 500
    except requests.exceptions.ConnectionError as e:
        print(f"ERROR: Connection error: {str(e)}")
        return jsonify({"error": "Cannot connect to AI service. Please check your internet connection."}), 500
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Request error: {str(e)}")
        return jsonify({"error": "Network error. Please check your connection."}), 500
    except KeyError as e:
        print(f"ERROR: Key error: {str(e)}")
        return jsonify({"error": "Invalid response format from AI service."}), 500
    except Exception as e:
        print(f"ERROR: Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "An unexpected error occurred. Please try again."}), 500


if __name__ == '__main__':
    
    app.run(debug=True)
