import os
import sqlite3
import requests
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, flash, url_for, session, send_from_directory, jsonify, g 
from werkzeug.utils import secure_filename
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
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

# Configure Flask for proper URL generation
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key_here_change_this_in_production')
app.config['SERVER_NAME'] = None  # Let Flask auto-detect
app.config['PREFERRED_URL_SCHEME'] = 'http'


db = SQLAlchemy()
db.init_app(app)

# Initialize database tables (only if they don't exist)
with app.app_context():
    # Check if company table exists
    inspector = inspect(db.engine)
    if not inspector.has_table('company'):
        print("Creating company table...")
        db.create_all()
    else:
        print("Company table already exists")


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
You are a helpful AI assistant for Africa House Pakistan Trade Portal. You help users find information about our partner companies.

Here are our registered partner companies with their details:

{json.dumps(companies_data, indent=2)}

INSTRUCTIONS:
1. If a user asks about a company that IS in the above list, provide detailed information about that company including their services, contact details, and website but everything should be in bullets line below line.

2. If a user asks about a company that is NOT in the above list, politely inform them: "I don't have information about that company in our current partner database. However, I can help you with information about our registered partner companies: [list the company names]."

3. For general questions about services or industries, suggest relevant companies from our partner list.

4. Always be helpful and provide specific details when the company is in our database.

5. If asked to list all companies, provide a nice formatted list with their main services.

6. maximum characters for response is 250. must follow it.

7. respond like a professional.
8. never include this symbol in your response "*".
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
            mobile_number =  request.form['country_code'] + request.form['mobile']


            print(f"Signup attempt for email: {email}")
            print(f"Form data received: country={country}, role={role}, full_name={full_name}")

            # Validation
            if password != password_again:
                flash("Passwords do not match. Please try again.", "error")
                return render_template('Register_page.html')

            if len(password) < 6:
                flash("Password must be at least 6 characters long.", "error")
                return render_template('Register_page.html')

            # Check if email already exists (check for verified users only)
            print(f"Checking if email {email} already exists...")
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()

            # First, clean up any duplicate unverified accounts for this email
            cursor.execute('DELETE FROM users WHERE email = ? AND email_verified = 0', (email,))
            deleted_count = cursor.rowcount
            if deleted_count > 0:
                print(f"Cleaned up {deleted_count} unverified duplicate accounts for {email}")

            # Now check if there's a verified account with this email
            cursor.execute('SELECT id FROM users WHERE email = ? AND email_verified = 1', (email,))
            existing_verified_user = cursor.fetchone()

            print(f"Existing verified user query result: {existing_verified_user}")

            if existing_verified_user:
                print(f"Verified account with email {email} already exists")
                conn.close()
                flash("An account with this email already exists and is verified.", "error")
                return render_template('Register_page.html')

            print(f"Email {email} is available for registration...")

            # Generate verification token
            verification_token = create_verification_token(email)
            token_expires = datetime.now() + timedelta(hours=24)

            # Save user to database (unverified)
            print(f"Inserting new user into database...")
            cursor.execute('''
                INSERT INTO users (country, role, email, password, company_name, full_name, mobile_number,
                                 email_verified, verification_token, verification_token_expires)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (country, role, email, password, company_name, full_name, mobile_number,
                  False, verification_token, token_expires))

            user_id = cursor.lastrowid
            print(f"User inserted successfully with ID: {user_id}")
            conn.commit()
            conn.close()

            # Send verification email
            print("Attempting to send verification email...")
            email_sent = send_verification_email(mail, email, full_name, verification_token)

            if email_sent:
                print("Verification email sent successfully")
                # Log verification attempt
                log_verification_attempt(user_id, email, verification_token)

                # Store email in session for verification page
                session['pending_verification_email'] = email

                return redirect(url_for('verification_sent'))
            else:
                print("Failed to send verification email")
                # Store email in session for manual verification
                session['pending_verification_email'] = email
                session['verification_failed'] = True
                flash("Account created successfully! However, we couldn't send the verification email due to a network issue. You can try to resend it from the verification page.", "warning")
                return redirect(url_for('verification_sent'))

        except Exception as e:
            print(f"Signup error: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")

            # Check if it's a database constraint error
            if "UNIQUE constraint failed" in str(e) or "email" in str(e).lower():
                flash("An account with this email already exists.", "error")
            elif "verification" in str(e).lower():
                flash("Error sending verification email. Please try again.", "error")
            else:
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

@app.route('/manual-verification', methods=['GET', 'POST'])
def manual_verification():
    """Manual verification page for users who can't use email links"""
    if request.method == 'POST':
        email = request.form.get('email', '').lower().strip()
        token = request.form.get('token', '').strip()

        if not email or not token:
            flash("Please provide both email and verification token.", "error")
            return render_template('manual_verification.html')

        try:
            # Verify the token manually
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()

            # Check if user exists with this email and token
            cursor.execute('''
                SELECT id, verification_token, verification_token_expires
                FROM users
                WHERE email = ? AND verification_token = ?
            ''', (email, token))

            user = cursor.fetchone()

            if not user:
                flash("Invalid email or verification token.", "error")
                conn.close()
                return render_template('manual_verification.html')

            user_id, db_token, expires = user

            # Check if token has expired
            if expires and datetime.now() > datetime.fromisoformat(expires):
                flash("Verification token has expired. Please register again.", "error")
                conn.close()
                return render_template('manual_verification.html')

            # Verify the user
            cursor.execute('''
                UPDATE users
                SET email_verified = 1, verification_token = NULL, verification_token_expires = NULL
                WHERE id = ?
            ''', (user_id,))

            conn.commit()
            conn.close()

            flash("Email verified successfully! You can now login.", "success")
            return redirect(url_for('login'))

        except Exception as e:
            print(f"Manual verification error: {str(e)}")
            flash("An error occurred during verification. Please try again.", "error")
            return render_template('manual_verification.html')

    return render_template('manual_verification.html')

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
            print(f"Attempting to resend verification email to {email}...")
            email_sent = send_verification_email(mail, email, full_name, verification_token)

            if email_sent:
                print("Verification email resent successfully")
                log_verification_attempt(user_id, email, verification_token)
                session['pending_verification_email'] = email
                flash("Verification email sent successfully!", "success")
                return redirect(url_for('verification_sent'))
            else:
                print("Failed to resend verification email")
                session['pending_verification_email'] = email
                flash("Failed to send verification email due to a network issue. Your account is created and ready - you can try again or contact support for manual verification.", "warning")
                return redirect(url_for('verification_sent'))
        else:
            conn.close()
            flash("No account found with this email address.", "error")
            return redirect(url_for('signup'))

    except Exception as e:
        print(f"Resend verification error: {str(e)}")
        flash("An error occurred. Please try again.", "error")
        return redirect(url_for('signup'))

def get_logged_in_user(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, full_name, email, mobile_number,company_name FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {'id': row[0], 'name': row[1], 'email': row[2], 'mobile_number': row[3], 'company_name': row[4]}
    return None
import json
@app.route('/vendor_profile', methods=['GET', 'POST'])
def vendor_profile():
    if 'user_id' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = get_logged_in_user(user_id)
    print("Logged in user:", user_id)

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT company_logo, product_images, product_description,
               company_name, location, industry, about_us, products_and_services,
               email, phone, website
        FROM company_profiles
        WHERE user_id = ?
    """, (user_id,))
    profile = cursor.fetchone()
    company_logo = profile[0] if profile else None
    product_images = profile[1].split(',') if profile and profile[1] else []
    product_description = profile[2] if profile else ''

    # Safely unpack profile data
    company_logo = profile[0] if profile else None
    product_images = profile[1].split(',') if profile and profile[1] else []
    product_description = profile[2] if profile else ''
    company_name = profile[3] if profile else ''
    location = profile[4] if profile else ''
    industry = profile[5] if profile else ''
    about_us = profile[6] if profile else ''
    products_and_services = profile[7] if profile else ''
    email = profile[8] if profile else ''
    phone = profile[9] if profile else ''
    website = profile[10] if profile else ''

    if request.method == 'POST':
        uploaded_logo = request.files.get('company_logo')
        logo_url = company_logo

        if uploaded_logo and uploaded_logo.filename:
            filename = secure_filename(uploaded_logo.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_logo.save(path)
            logo_url = url_for('static', filename='uploads/' + filename)

        product_image_urls = []
        for i in range(1, 6):
            image = request.files.get(f'product_image{i}')
            if image and image.filename:
                imgname = secure_filename(image.filename)
                imgpath = os.path.join(app.config['UPLOAD_FOLDER'], imgname)
                image.save(imgpath)
                product_image_urls.append(url_for('static', filename='uploads/' + imgname))

        # Get text input values
        description = request.form.get('product_description')
        company_name = request.form.get('company_name')
        location = request.form.get('location')
        industry = request.form.get('industry')
        about_us = request.form.get('about_us')
        products_and_services = request.form.get('products_and_services')
        email = request.form.get('email')
        phone = request.form.get('phone')
        website = request.form.get('website')

        cursor.execute("SELECT id FROM company_profiles WHERE user_id = ?", (user_id,))
        exists = cursor.fetchone()

        if exists:
            cursor.execute("""
                UPDATE company_profiles 
                SET company_logo = ?, 
                    product_images = ?, 
                    product_description = ?, 
                    company_name = ?, 
                    location = ?, 
                    industry = ?, 
                    about_us = ?, 
                    products_and_services = ?, 
                    email = ?, 
                    phone = ?, 
                    website = ?, 
                    last_updated = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (
                logo_url, ','.join(product_image_urls), description,
                company_name, location, industry,
                about_us, products_and_services, email, phone, website, user_id
            ))
        else:
            cursor.execute("""
                INSERT INTO company_profiles (
                    user_id, company_logo, product_images, product_description,
                    company_name, location, industry, about_us, products_and_services,
                    email, phone, website
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, logo_url, ','.join(product_image_urls), description,
                company_name, location, industry, about_us, products_and_services,
                email, phone, website
            ))

        conn.commit()
        flash("Company profile updated successfully!", "success")
        return redirect(url_for('vendor_profile'))

    conn.close()
    products_and_services = profile[7] if profile else '[]'
    try:
        products = json.loads(products_and_services)
    except Exception:
        products = []
    print("Products passed to template:", products)
    return render_template(
        'vendor_profile.html',
        company_logo=company_logo,
        product_images=product_images,
        product_description=product_description,
        company_name=company_name,
        location=location,
        industry=industry,
        about_us=about_us,
        products_and_services=products_and_services,
        products=products,  # pass as Python list
        email=email,
        phone=phone,
        website=website,
        user=user
)

@app.route('/update_vendor_profile', methods=['POST'])
def update_vendor_profile():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    user_id = session['user_id']
    print("User ID:", user_id)
    print("Form data received:", dict(request.form))
    company_name = request.form.get('company_name', '')
    product_description = request.form.get('product_description', '')
    location = request.form.get('location', '')
    industry = request.form.get('industry', '')
    about_us = request.form.get('about_us', '')
    email = request.form.get('email', '')
    phone = request.form.get('phone', '')
    website = request.form.get('website', '')
    products_and_services = request.form.get('products_and_services', '')

    uploaded_logo = request.files.get('company_logo')
    logo_url = None
    if uploaded_logo and uploaded_logo.filename:
        filename = secure_filename(uploaded_logo.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        uploaded_logo.save(path)
        logo_url = url_for('static', filename='uploads/' + filename)
# Save logo_url in your UPDATE/INSERT SQL
    product_image_urls = []
    for i in range(1, 6):  # Adjust range for your max number of images
        image = request.files.get(f'product_image{i}')
        if image and image.filename:
            imgname = secure_filename(image.filename)
            imgpath = os.path.join(app.config['UPLOAD_FOLDER'], imgname)
            image.save(imgpath)
            product_image_urls.append(url_for('static', filename='uploads/' + imgname))
    product_images = ','.join(product_image_urls)

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        # Check if profile exists
        cursor.execute("SELECT id FROM company_profiles WHERE user_id = ?", (user_id,))
        exists = cursor.fetchone()
        if exists:
            cursor.execute("""
                UPDATE company_profiles
                SET   product_images = ?, company_logo = ?, company_name = ?, location = ?, industry = ?, about_us = ?, email = ?, phone = ?, website = ?,products_and_services = ?, last_updated = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (
                product_images, logo_url, company_name, location, industry, about_us, email, phone, website, products_and_services, user_id
            ))
        else:
            cursor.execute("""
                INSERT INTO company_profiles (
                    user_id, product_images = ?, company_logo, company_name, location, industry, about_us, email, phone, website, products_and_services, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                user_id, product_images, logo_url, company_name, location, industry, about_us, email, phone, website, products_and_services
            ))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error updating vendor profile: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/vendor_profile.html')
def redirect_vendor_profile_html():
    return redirect(url_for('vendor_profile'))


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



@app.route('/vendor_dashboard.html')
def vendor_dashboard():
    """Serve vendor dashboard HTML"""
    if not session.get('logged_in'):
        flash("Please log in to access the dashboard.", "warning")
        return redirect(url_for('login'))
    return render_template( 'vendor_dashboard.html')








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

            # Debug: Log what we're sending to AI
            print(f"Sending to AI - User message: {user_message}")
            print(f"System prompt being used: {len(system_prompt) if system_prompt else 0} characters")

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
                    print(f"AI Response: {ai_reply[:200]}...")
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
        print(f"System prompt preview: {system_prompt[:300]}...")

        # Debug: Check if companies data is in the prompt
        companies_count = system_prompt.count('"name":')
        print(f"Number of companies in system prompt: {companies_count}")

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


app.secret_key = 'your_secret_key' # Required for session & flash
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)



DATABASE_USER = 'database.db'
DATABASE_PARTNER = 'companies.db'

def get_user_db():
    db = getattr(g, '_user_db', None)
    if db is None:
        db = g._user_db = sqlite3.connect(DATABASE_USER)
        db.row_factory = sqlite3.Row
    return db

def get_partner_db():
    db = getattr(g, '_partner_db', None)
    if db is None:
        db = g._partner_db = sqlite3.connect(DATABASE_PARTNER)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connections(exception):
    user_db = getattr(g, '_user_db', None)
    if user_db:
        user_db.close()
    partner_db = getattr(g, '_partner_db', None)
    if partner_db:
        partner_db.close()

@app.route('/connections_page')
def connections_page():
    if not session.get('logged_in'):
        flash("Please log in to access this page.", "warning")
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    user_db = get_user_db()
    cur = user_db.execute("SELECT industry FROM company_profiles WHERE user_id = ?", (user_id,))
    row = cur.fetchone()

    if not row:
        return "Your company profile was not found", 404

    user_industry = row['industry']
    print(f"user_industry: '{user_industry}'")

    partner_db = get_partner_db()
    try:
        cur2 = partner_db.execute(
            "SELECT * FROM company WHERE LOWER(TRIM(industry)) = LOWER(TRIM(?))",
            (user_industry,)
        )
        similar_companies = cur2.fetchall()
    except sqlite3.Error as e:
        return f"Database error: {e}", 500

    return render_template(
        'connections_page.html',
        industry=user_industry,
        similar_companies=similar_companies
    )


@app.route('/leads_page', methods=['GET'])
def leads_page():
    if not session.get('logged_in'):
        flash("Please log in to access this page.", "warning")
        return redirect(url_for('login'))

    query = request.args.get('query', '').strip().lower()
    partner_db = get_partner_db()

    # Common stopwords to ignore
    stopwords = {'i', 'the', 'of', 'want', 'to', 'and', 'a', 'start', 'in','export','import', 'for', 'on', 'at', 'is'}

    if query:
        # Split query and filter out stopwords
        words = [word for word in query.split() if word not in stopwords]

        if not words:
            search_results = []  # No meaningful words left
        else:
            like_clauses = " OR ".join([
                "(LOWER(name) LIKE ? OR LOWER(industry) LIKE ? OR LOWER(services) LIKE ?)"
                for _ in words
            ])
            params = []
            for word in words:
                like_word = f"%{word}%"
                params.extend([like_word, like_word, like_word])

            cur = partner_db.execute(f"""
                SELECT * FROM company
                WHERE {like_clauses}
            """, tuple(params))
            search_results = cur.fetchall()
    else:
        cur = partner_db.execute("SELECT * FROM company LIMIT 20")
        search_results = cur.fetchall()

    return render_template('leads_page.html', search_results=search_results, query=query)

def init_db():
    conn = sqlite3.connect('contact_messages.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            company_name TEXT NOT NULL,
            email TEXT NOT NULL,
            purpose TEXT NOT NULL,
            subject TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()


# ---------- Routes ----------
@app.route('/contact')
def contact_us():
    return render_template('contact_us.html')


@app.route('/submit_contact_form', methods=['POST'])
def submit_contact_form():
    try:
        data = request.form
        name = data.get('name')
        company_name = data.get('companyName')
        email = data.get('email')
        purpose = data.get('purpose')
        subject = data.get('subject')

        if not all([name, company_name, email, purpose, subject]):
            return jsonify({'success': False, 'message': 'All fields are required'}), 400

        conn = sqlite3.connect('contact_messages.db')
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO contact_messages (name, company_name, email, purpose, subject)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, company_name, email, purpose, subject))
        conn.commit()
        conn.close()

        return jsonify({'success': True})
    except Exception as e:
        print("Error:", e)
        return jsonify({'success': False, 'message': str(e)}), 500




if __name__ == '__main__':
    
    app.run(debug=True)
