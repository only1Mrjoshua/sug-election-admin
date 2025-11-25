from flask import Flask, request, jsonify, render_template_string, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import bcrypt
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'iauweiyvbiueyckuahsfdyrstvdKYWRIURIVTABSDFHCDVJQWT2648hfjbs'  # Change this in production!

# MongoDB configuration
MONGO_URI = "mongodb+srv://only1MrJoshua:LovuLord2025@cluster0.9jqnavg.mongodb.net/?appName=Cluster0/election_db"  # Update with your MongoDB URI
DATABASE_NAME = "election_db"

# Initialize MongoDB
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'
login_manager.login_message = 'Please log in to access this page.'

# Admin credentials (in production, store hashed passwords in database)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = bcrypt.hashpw("obonguni2025".encode('utf-8'), bcrypt.gensalt())

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(username):
    if username == ADMIN_USERNAME:
        return User(username)
    return None

def init_db():
    """Initialize database with required collections"""
    # Create collections if they don't exist
    collections = ['voters', 'candidates', 'votes', 'election_settings']
    
    for collection in collections:
        if collection not in db.list_collection_names():
            db.create_collection(collection)
    
    # Initialize election settings
    if db.election_settings.count_documents({}) == 0:
        db.election_settings.insert_one({
            'election_status': 'not_started',  # not_started, ongoing, paused, ended
            'start_time': None,
            'end_time': None,
            'created_at': datetime.utcnow()
        })
    
    # Add some sample candidates if none exist
    if db.candidates.count_documents({}) == 0:
        sample_candidates = [
            {
                'name': 'John Doe',
                'position': 'President',
                'department': 'Computer Science',
                'created_at': datetime.utcnow()
            },
            {
                'name': 'Jane Smith',
                'position': 'President',
                'department': 'Political Science',
                'created_at': datetime.utcnow()
            },
            {
                'name': 'Mike Johnson',
                'position': 'Vice President',
                'department': 'Economics',
                'created_at': datetime.utcnow()
            }
        ]
        db.candidates.insert_many(sample_candidates)

# Initialize database
init_db()

# Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and bcrypt.checkpw(password.encode('utf-8'), ADMIN_PASSWORD_HASH):
            user = User(username)
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin_home'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
    
    login_html = '''
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Login - Obong University SRC Elections</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary-red: #D13D39;
            --primary-green: #2C8A45;
            --primary-yellow: #EBBF00;
            --dark-red: #b32b2b;
            --light-red: #f8e6e5;
            --light-green: #e8f5e9;
            --light-yellow: #fff9e6;
            --dark-gray: #333;
            --medium-gray: #666;
            --light-gray: #f5f5f5;
            --white: #ffffff;
            --shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            --radius: 12px;
            --transition: all 0.3s ease;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, var(--primary-red) 0%, var(--dark-red) 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .login-container {
            background: var(--white);
            border-radius: var(--radius);
            padding: 40px;
            box-shadow: var(--shadow);
            width: 100%;
            max-width: 450px;
            text-align: center;
        }
        
        .university-info {
            margin-bottom: 30px;
        }
        
        .university-info h1 {
            color: var(--primary-red);
            font-size: 2rem;
            margin-bottom: 8px;
            font-weight: 800;
        }
        
        .university-info .subtitle {
            color: var(--primary-green);
            font-size: 1.1rem;
            font-weight: 600;
        }
        
        .admin-badge {
            background: linear-gradient(135deg, var(--primary-red) 0%, var(--dark-red) 100%);
            color: var(--white);
            padding: 10px 20px;
            border-radius: 30px;
            font-weight: 600;
            font-size: 0.9rem;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 25px;
        }
        
        .form-group {
            margin-bottom: 20px;
            text-align: left;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: var(--dark-gray);
        }
        
        .input-group {
            position: relative;
        }
        
        .input-group i {
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--medium-gray);
        }
        
        input[type="text"],
        input[type="password"] {
            width: 100%;
            padding: 15px 15px 15px 45px;
            border: 2px solid var(--light-gray);
            border-radius: 8px;
            font-size: 16px;
            transition: var(--transition);
        }
        
        input[type="text"]:focus,
        input[type="password"]:focus {
            outline: none;
            border-color: var(--primary-red);
            box-shadow: 0 0 0 3px rgba(209, 61, 57, 0.1);
        }
        
        .btn {
            background: linear-gradient(135deg, var(--primary-red) 0%, var(--dark-red) 100%);
            color: var(--white);
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: var(--transition);
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            box-shadow: 0 4px 8px rgba(209, 61, 57, 0.3);
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(209, 61, 57, 0.4);
        }
        
        .alert {
            padding: 15px 20px;
            border-radius: var(--radius);
            margin-bottom: 25px;
            display: flex;
            align-items: center;
            gap: 15px;
            text-align: left;
        }
        
        .alert-error {
            background: var(--light-red);
            border-left: 5px solid var(--primary-red);
            color: var(--primary-red);
        }
        
        .alert-success {
            background: var(--light-green);
            border-left: 5px solid var(--primary-green);
            color: var(--primary-green);
        }
        
        .login-footer {
            margin-top: 25px;
            color: var(--medium-gray);
            font-size: 0.9rem;
        }
        
        @media (max-width: 480px) {
            .login-container {
                padding: 30px 20px;
            }
            
            .university-info h1 {
                font-size: 1.7rem;
            }
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="university-info">
            <h1>OBONG UNIVERSITY</h1>
            <div class="subtitle">SRC Elections 2025</div>
        </div>
        
        <div class="admin-badge">
            <i class="fas fa-shield-alt"></i>
            ADMIN LOGIN
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'error' if category == 'error' else 'success' }}">
                        <i class="fas fa-{{ 'exclamation-circle' if category == 'error' else 'check-circle' }}"></i>
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <form method="POST">
            <div class="form-group">
                <label for="username">Username</label>
                <div class="input-group">
                    <i class="fas fa-user"></i>
                    <input type="text" id="username" name="username" required placeholder="Enter admin username">
                </div>
            </div>
            
            <div class="form-group">
                <label for="password">Password</label>
                <div class="input-group">
                    <i class="fas fa-lock"></i>
                    <input type="password" id="password" name="password" required placeholder="Enter admin password">
                </div>
            </div>
            
            <button type="submit" class="btn">
                <i class="fas fa-sign-in-alt"></i>
                Login to Dashboard
            </button>
        </form>
    </div>
</body>
</html>
    '''
    
    return render_template_string(login_html)

@app.route('/admin/logout')
@login_required
def admin_logout():
    """Admin logout"""
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('admin_login'))

@app.route('/')
@login_required
def admin_home():
    """Admin dashboard home page"""
    # Get election status
    election_settings = db.election_settings.find_one({})
    
    return f'''
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard - Obong University SRC Elections</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{
            --primary-red: #D13D39;
            --primary-green: #2C8A45;
            --primary-yellow: #EBBF00;
            --dark-red: #b32b2b;
            --light-red: #f8e6e5;
            --light-green: #e8f5e9;
            --light-yellow: #fff9e6;
            --dark-gray: #333;
            --medium-gray: #666;
            --light-gray: #f5f5f5;
            --white: #ffffff;
            --shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            --radius: 12px;
            --transition: all 0.3s ease;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #f9f9f9 0%, #f0f0f0 100%);
            min-height: 100vh;
            padding: 20px;
            color: var(--dark-gray);
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: var(--white);
            padding: 25px 30px;
            border-radius: var(--radius) var(--radius) 0 0;
            margin-bottom: 0;
            box-shadow: var(--shadow);
            border-bottom: 4px solid var(--primary-red);
        }}
        
        .university-info h1 {{
            color: var(--primary-red);
            font-size: 2.2rem;
            margin-bottom: 8px;
            font-weight: 800;
            letter-spacing: -0.5px;
        }}
        
        .university-info .subtitle {{
            color: var(--primary-green);
            font-size: 1.2rem;
            font-weight: 600;
        }}
        
        .admin-section {{
            display: flex;
            align-items: center;
            gap: 20px;
        }}
        
        .election-status {{
            background: {{
                'not_started': 'var(--medium-gray)',
                'ongoing': 'var(--primary-green)',
                'paused': 'var(--primary-yellow)',
                'ended': 'var(--primary-red)'
            }}[election_settings.get('election_status', 'not_started')];
            color: var(--white);
            padding: 10px 20px;
            border-radius: 30px;
            font-weight: 600;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 8px;
            text-transform: uppercase;
        }}
        
        .admin-badge {{
            background: linear-gradient(135deg, var(--primary-red) 0%, var(--dark-red) 100%);
            color: var(--white);
            padding: 12px 24px;
            border-radius: 30px;
            font-weight: 600;
            font-size: 1rem;
            display: flex;
            align-items: center;
            gap: 8px;
            box-shadow: 0 4px 8px rgba(209, 61, 57, 0.3);
        }}
        
        .logout-btn {{
            background: transparent;
            border: 2px solid var(--primary-red);
            color: var(--primary-red);
            padding: 10px 20px;
            border-radius: 30px;
            font-weight: 600;
            cursor: pointer;
            transition: var(--transition);
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .logout-btn:hover {{
            background: var(--primary-red);
            color: var(--white);
        }}
        
        .main-content {{
            display: grid;
            grid-template-columns: 280px 1fr;
            gap: 25px;
            margin-top: 25px;
        }}
        
        .sidebar {{
            background: var(--white);
            border-radius: var(--radius);
            padding: 25px;
            box-shadow: var(--shadow);
            height: fit-content;
            position: sticky;
            top: 25px;
        }}
        
        .nav-item {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 16px 20px;
            margin-bottom: 10px;
            border-radius: 10px;
            cursor: pointer;
            transition: var(--transition);
            font-weight: 600;
            color: var(--medium-gray);
        }}
        
        .nav-item:hover {{
            background: var(--light-yellow);
            color: var(--dark-gray);
        }}
        
        .nav-item.active {{
            background: linear-gradient(135deg, var(--primary-red) 0%, var(--dark-red) 100%);
            color: var(--white);
            box-shadow: 0 4px 12px rgba(209, 61, 57, 0.3);
        }}
        
        .content-area {{
            background: var(--white);
            border-radius: var(--radius);
            padding: 30px;
            box-shadow: var(--shadow);
            min-height: 600px;
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
            animation: fadeIn 0.5s ease;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .page-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 2px solid var(--light-gray);
        }}
        
        .page-title {{
            color: var(--primary-red);
            font-size: 1.8rem;
            font-weight: 700;
        }}
        
        .page-description {{
            color: var(--medium-gray);
            font-size: 1.1rem;
            margin-bottom: 25px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: var(--white);
            border-radius: var(--radius);
            padding: 25px;
            box-shadow: var(--shadow);
            border-left: 5px solid var(--primary-red);
            transition: var(--transition);
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        }}
        
        .stat-card.green {{
            border-left-color: var(--primary-green);
        }}
        
        .stat-card.yellow {{
            border-left-color: var(--primary-yellow);
        }}
        
        .stat-icon {{
            font-size: 2.5rem;
            margin-bottom: 15px;
            color: var(--primary-red);
        }}
        
        .stat-card.green .stat-icon {{
            color: var(--primary-green);
        }}
        
        .stat-card.yellow .stat-icon {{
            color: var(--primary-yellow);
        }}
        
        .stat-number {{
            font-size: 2.8rem;
            font-weight: 800;
            margin-bottom: 5px;
            color: var(--dark-gray);
        }}
        
        .stat-label {{
            font-size: 1rem;
            color: var(--medium-gray);
            font-weight: 600;
        }}
        
        .btn {{
            background: linear-gradient(135deg, var(--primary-red) 0%, var(--dark-red) 100%);
            color: var(--white);
            border: none;
            padding: 14px 28px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: var(--transition);
            display: inline-flex;
            align-items: center;
            gap: 8px;
            box-shadow: 0 4px 8px rgba(209, 61, 57, 0.3);
            text-decoration: none;
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(209, 61, 57, 0.4);
        }}
        
        .btn-secondary {{
            background: linear-gradient(135deg, var(--primary-green) 0%, #1e7e34 100%);
            box-shadow: 0 4px 8px rgba(44, 138, 69, 0.3);
        }}
        
        .btn-secondary:hover {{
            box-shadow: 0 6px 12px rgba(44, 138, 69, 0.4);
        }}
        
        .btn-outline {{
            background: transparent;
            border: 2px solid var(--primary-red);
            color: var(--primary-red);
            box-shadow: none;
        }}
        
        .btn-outline:hover {{
            background: var(--primary-red);
            color: var(--white);
        }}
        
        .btn-warning {{
            background: linear-gradient(135deg, var(--primary-yellow) 0%, #b38f00 100%);
            box-shadow: 0 4px 8px rgba(235, 191, 0, 0.3);
        }}
        
        .results-grid {{
            display: grid;
            gap: 25px;
            margin-top: 25px;
        }}
        
        .position-card {{
            background: var(--white);
            border-radius: var(--radius);
            padding: 25px;
            box-shadow: var(--shadow);
            border: 1px solid var(--light-gray);
            transition: var(--transition);
        }}
        
        .position-card:hover {{
            box-shadow: 0 6px 16px rgba(0,0,0,0.1);
        }}
        
        .position-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid var(--light-yellow);
        }}
        
        .position-title {{
            color: var(--primary-red);
            font-size: 1.5rem;
            font-weight: 700;
        }}
        
        .position-votes {{
            color: var(--medium-gray);
            font-weight: 600;
            background: var(--light-yellow);
            padding: 6px 12px;
            border-radius: 20px;
        }}
        
        .candidates-list {{
            display: grid;
            gap: 15px;
        }}
        
        .candidate-card {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 18px;
            border-radius: 10px;
            background: var(--light-gray);
            transition: var(--transition);
        }}
        
        .candidate-card.winner {{
            background: linear-gradient(135deg, var(--primary-green) 0%, #4CAF50 100%);
            color: var(--white);
            box-shadow: 0 4px 12px rgba(44, 138, 69, 0.3);
        }}
        
        .candidate-card:hover {{
            transform: translateX(5px);
        }}
        
        .candidate-info {{
            flex: 1;
        }}
        
        .candidate-name {{
            font-weight: 700;
            font-size: 1.2rem;
            margin-bottom: 5px;
        }}
        
        .candidate-department {{
            font-size: 0.9rem;
            opacity: 0.8;
        }}
        
        .candidate-stats {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .vote-count {{
            font-weight: 700;
            font-size: 1.4rem;
        }}
        
        .vote-percentage {{
            background: rgba(255, 255, 255, 0.2);
            padding: 6px 12px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9rem;
        }}
        
        .winner-badge {{
            background: var(--primary-yellow);
            color: var(--dark-gray);
            padding: 6px 12px;
            border-radius: 20px;
            font-weight: 700;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        
        .voters-container {{
            max-height: 500px;
            overflow-y: auto;
            margin-top: 20px;
            border-radius: var(--radius);
            border: 1px solid var(--light-gray);
        }}
        
        .voter-card {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 18px 25px;
            border-bottom: 1px solid var(--light-gray);
            transition: var(--transition);
        }}
        
        .voter-card:hover {{
            background: var(--light-yellow);
        }}
        
        .voter-info {{
            flex: 1;
        }}
        
        .voter-name {{
            font-weight: 700;
            margin-bottom: 5px;
        }}
        
        .voter-details {{
            font-size: 0.9rem;
            color: var(--medium-gray);
        }}
        
        .voter-status {{
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }}
        
        .status-verified {{
            background: var(--light-green);
            color: var(--primary-green);
        }}
        
        .status-pending {{
            background: var(--light-yellow);
            color: #b38f00;
        }}
        
        .alert {{
            padding: 18px 25px;
            border-radius: var(--radius);
            margin-bottom: 25px;
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .alert-success {{
            background: var(--light-green);
            border-left: 5px solid var(--primary-green);
            color: var(--primary-green);
        }}
        
        .alert-error {{
            background: var(--light-red);
            border-left: 5px solid var(--primary-red);
            color: var(--primary-red);
        }}
        
        .alert-warning {{
            background: var(--light-yellow);
            border-left: 5px solid var(--primary-yellow);
            color: #b38f00;
        }}
        
        .system-status {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}
        
        .status-card {{
            background: var(--white);
            border-radius: var(--radius);
            padding: 20px;
            box-shadow: var(--shadow);
            text-align: center;
            border-top: 4px solid var(--primary-green);
        }}
        
        .status-card.offline {{
            border-top-color: var(--primary-red);
        }}
        
        .status-icon {{
            font-size: 2.5rem;
            margin-bottom: 15px;
        }}
        
        .status-card.online .status-icon {{
            color: var(--primary-green);
        }}
        
        .status-card.offline .status-icon {{
            color: var(--primary-red);
        }}
        
        .status-title {{
            font-weight: 700;
            margin-bottom: 10px;
        }}
        
        .status-description {{
            font-size: 0.9rem;
            color: var(--medium-gray);
        }}
        
        .last-update {{
            text-align: center;
            margin-top: 25px;
            color: var(--medium-gray);
            font-size: 0.9rem;
        }}
        
        .footer {{
            text-align: center;
            color: var(--medium-gray);
            margin-top: 40px;
            padding: 25px;
            font-size: 0.9rem;
        }}
        
        .loading {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 60px 20px;
            color: var(--medium-gray);
        }}
        
        .loading-spinner {{
            width: 50px;
            height: 50px;
            border: 5px solid var(--light-gray);
            border-top: 5px solid var(--primary-red);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 20px;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        .empty-state {{
            text-align: center;
            padding: 60px 20px;
            color: var(--medium-gray);
        }}
        
        .empty-icon {{
            font-size: 4rem;
            margin-bottom: 20px;
            opacity: 0.5;
        }}
        
        /* Responsive Design */
        @media (max-width: 1024px) {{
            .main-content {{
                grid-template-columns: 1fr;
            }}
            
            .sidebar {{
                position: static;
                margin-bottom: 0;
            }}
            
            .nav-items {{
                display: flex;
                overflow-x: auto;
                gap: 10px;
                padding-bottom: 10px;
            }}
            
            .nav-item {{
                white-space: nowrap;
                margin-bottom: 0;
            }}
        }}
        
        @media (max-width: 768px) {{
            .header {{
                flex-direction: column;
                text-align: center;
                gap: 20px;
            }}
            
            .admin-section {{
                flex-direction: column;
                gap: 15px;
            }}
            
            .page-header {{
                flex-direction: column;
                align-items: flex-start;
                gap: 15px;
            }}
            
            .candidate-card {{
                flex-direction: column;
                align-items: flex-start;
                gap: 15px;
            }}
            
            .candidate-stats {{
                width: 100%;
                justify-content: space-between;
            }}
            
            .voter-card {{
                flex-direction: column;
                align-items: flex-start;
                gap: 15px;
            }}
            
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
        }}
        
        @media (max-width: 480px) {{
            .container {{
                padding: 10px;
            }}
            
            .header {{
                padding: 20px;
            }}
            
            .university-info h1 {{
                font-size: 1.8rem;
            }}
            
            .content-area {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="university-info">
                <h1>OBONG UNIVERSITY</h1>
                <div class="subtitle">Admin Dashboard - SRC Elections 2025</div>
            </div>
            <div class="admin-section">
                <div class="election-status">
                    <i class="fas fa-circle"></i>
                    {election_settings.get('election_status', 'not_started').replace('_', ' ').title()}
                </div>
                <div class="admin-badge">
                    <i class="fas fa-shield-alt"></i>
                    ADMIN ACCESS
                </div>
                <a href="/admin/logout" class="logout-btn">
                    <i class="fas fa-sign-out-alt"></i>
                    Logout
                </a>
            </div>
        </div>
        
        <div class="main-content">
            <div class="sidebar">
                <div class="nav-items">
                    <div class="nav-item active" data-tab="results">
                        <i class="fas fa-chart-bar"></i>
                        Live Results
                    </div>
                    <div class="nav-item" data-tab="dashboard">
                        <i class="fas fa-tachometer-alt"></i>
                        Election Dashboard
                    </div>
                    <div class="nav-item" data-tab="voters">
                        <i class="fas fa-users"></i>
                        Registered Voters
                    </div>
                    <div class="nav-item" data-tab="settings">
                        <i class="fas fa-cog"></i>
                        System Settings
                    </div>
                </div>
            </div>
            
            <div class="content-area">
                <!-- Results Tab -->
                <div id="results-tab" class="tab-content active">
                    <div class="page-header">
                        <div>
                            <h2 class="page-title">Live Election Results</h2>
                            <p class="page-description">Real-time election results as votes are being cast and counted.</p>
                        </div>
                        <button class="btn" id="refresh-results">
                            <i class="fas fa-sync-alt"></i>
                            Refresh Results
                        </button>
                    </div>
                    
                    <div id="results-container">
                        <div class="loading">
                            <div class="loading-spinner"></div>
                            <h3>Loading Election Results</h3>
                            <p>Please wait while we fetch the latest data...</p>
                        </div>
                    </div>
                </div>
                
                <!-- Dashboard Tab -->
                <div id="dashboard-tab" class="tab-content">
                    <div class="page-header">
                        <div>
                            <h2 class="page-title">Election Dashboard</h2>
                            <p class="page-description">Overview of election statistics and system status.</p>
                        </div>
                        <button class="btn" id="refresh-stats">
                            <i class="fas fa-sync-alt"></i>
                            Refresh Stats
                        </button>
                    </div>
                    
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-icon">
                                <i class="fas fa-users"></i>
                            </div>
                            <div class="stat-number" id="total-voters">0</div>
                            <div class="stat-label">Registered Voters</div>
                        </div>
                        <div class="stat-card green">
                            <div class="stat-icon">
                                <i class="fas fa-vote-yea"></i>
                            </div>
                            <div class="stat-number" id="total-votes">0</div>
                            <div class="stat-label">Votes Cast</div>
                        </div>
                        <div class="stat-card yellow">
                            <div class="stat-icon">
                                <i class="fas fa-chart-line"></i>
                            </div>
                            <div class="stat-number" id="turnout-rate">0%</div>
                            <div class="stat-label">Voter Turnout</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-icon">
                                <i class="fas fa-check-circle"></i>
                            </div>
                            <div class="stat-number" id="verified-voters">0</div>
                            <div class="stat-label">Verified Voters</div>
                        </div>
                    </div>
                    
                    <div class="system-status">
                        <div class="status-card online">
                            <div class="status-icon">
                                <i class="fas fa-server"></i>
                            </div>
                            <div class="status-title">Server Status</div>
                            <div class="status-description">All systems operational</div>
                        </div>
                        <div class="status-card online">
                            <div class="status-icon">
                                <i class="fas fa-database"></i>
                            </div>
                            <div class="status-title">Database</div>
                            <div class="status-description">Connected and responsive</div>
                        </div>
                        <div class="status-card online">
                            <div class="status-icon">
                                <i class="fas fa-shield-alt"></i>
                            </div>
                            <div class="status-title">Security</div>
                            <div class="status-description">All checks passed</div>
                        </div>
                    </div>
                    
                    <div class="last-update">
                        <i class="fas fa-clock"></i>
                        Last updated: <span id="last-update">Just now</span>
                    </div>
                </div>
                
                <!-- Voters Tab -->
                <div id="voters-tab" class="tab-content">
                    <div class="page-header">
                        <div>
                            <h2 class="page-title">Registered Voters</h2>
                            <p class="page-description">List of all registered voters and their verification status.</p>
                        </div>
                        <button class="btn" id="refresh-voters">
                            <i class="fas fa-sync-alt"></i>
                            Refresh Voters
                        </button>
                    </div>
                    
                    <div id="voters-container">
                        <div class="loading">
                            <div class="loading-spinner"></div>
                            <h3>Loading Voter Information</h3>
                            <p>Please wait while we fetch the latest data...</p>
                        </div>
                    </div>
                </div>
                
                <!-- Settings Tab -->
                <div id="settings-tab" class="tab-content">
                    <div class="page-header">
                        <h2 class="page-title">System Settings</h2>
                        <p class="page-description">Manage election settings and system configuration.</p>
                    </div>
                    
                    <div class="alert alert-warning">
                        <i class="fas fa-exclamation-triangle"></i>
                        <div>
                            <strong>Administrator Access Required</strong>
                            <p>Some settings require elevated permissions to modify.</p>
                        </div>
                    </div>
                    
                    <div class="position-card">
                        <h3 class="position-title">Election Controls</h3>
                        <div class="candidates-list">
                            <div class="candidate-card">
                                <div class="candidate-info">
                                    <div class="candidate-name">Start Election</div>
                                    <div class="candidate-department">Begin accepting votes from registered voters</div>
                                </div>
                                <button class="btn btn-secondary" onclick="controlElection('start')">
                                    <i class="fas fa-play"></i>
                                    Start
                                </button>
                            </div>
                            <div class="candidate-card">
                                <div class="candidate-info">
                                    <div class="candidate-name">Pause Election</div>
                                    <div class="candidate-department">Temporarily stop accepting votes</div>
                                </div>
                                <button class="btn btn-warning" onclick="controlElection('pause')">
                                    <i class="fas fa-pause"></i>
                                    Pause
                                </button>
                            </div>
                            <div class="candidate-card">
                                <div class="candidate-info">
                                    <div class="candidate-name">End Election</div>
                                    <div class="candidate-department">Stop accepting votes and calculate final results</div>
                                </div>
                                <button class="btn btn-outline" onclick="controlElection('end')">
                                    <i class="fas fa-stop"></i>
                                    End
                                </button>
                            </div>
                            <div class="candidate-card">
                                <div class="candidate-info">
                                    <div class="candidate-name">Reset Election</div>
                                    <div class="candidate-department">Reset all votes and start fresh (Dangerous!)</div>
                                </div>
                                <button class="btn btn-outline" style="border-color: var(--primary-red); color: var(--primary-red);" onclick="controlElection('reset')">
                                    <i class="fas fa-undo"></i>
                                    Reset
                                </button>
                            </div>
                        </div>
                    </div>
                    
                    <div class="position-card" style="margin-top: 25px;">
                        <h3 class="position-title">System Configuration</h3>
                        <div class="candidates-list">
                            <div class="candidate-card">
                                <div class="candidate-info">
                                    <div class="candidate-name">Export Election Data</div>
                                    <div class="candidate-department">Download complete election results and logs</div>
                                </div>
                                <button class="btn" onclick="exportData()">
                                    <i class="fas fa-download"></i>
                                    Export
                                </button>
                            </div>
                            <div class="candidate-card">
                                <div class="candidate-info">
                                    <div class="candidate-name">System Logs</div>
                                    <div class="candidate-department">View system activity and error logs</div>
                                </div>
                                <button class="btn">
                                    <i class="fas fa-file-alt"></i>
                                    View Logs
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Obong University SRC Election System &copy; 2025 | Secure Admin Dashboard</p>
            <p>For technical support, contact ICT Department</p>
        </div>
    </div>

    <script>
        const API_BASE = '/api';
        
        // Tab navigation
        document.querySelectorAll('.nav-item').forEach(item => {{
            item.addEventListener('click', function() {{
                // Remove active class from all items
                document.querySelectorAll('.nav-item').forEach(nav => {{
                    nav.classList.remove('active');
                }});
                
                // Add active class to clicked item
                this.classList.add('active');
                
                // Hide all tab content
                document.querySelectorAll('.tab-content').forEach(tab => {{
                    tab.classList.remove('active');
                }});
                
                // Show selected tab content
                const tabId = this.getAttribute('data-tab') + '-tab';
                document.getElementById(tabId).classList.add('active');
                
                // Load data for specific tabs
                if (this.getAttribute('data-tab') === 'results') {{
                    loadResults();
                }} else if (this.getAttribute('data-tab') === 'dashboard') {{
                    loadStats();
                }} else if (this.getAttribute('data-tab') === 'voters') {{
                    loadVoters();
                }}
            }});
        }});
        
        // Button event listeners
        document.getElementById('refresh-results').addEventListener('click', loadResults);
        document.getElementById('refresh-stats').addEventListener('click', loadStats);
        document.getElementById('refresh-voters').addEventListener('click', loadVoters);
        
        // Error handling function
        function handleError(context, error) {{
            console.error(`Error in ${{context}}:`, error);
            
            let errorMessage = 'An unexpected error occurred. Please try again.';
            if (error.message) {{
                errorMessage = error.message;
            }}
            
            // Create error alert
            const alert = document.createElement('div');
            alert.className = 'alert alert-error';
            alert.innerHTML = `
                <i class="fas fa-exclamation-circle"></i>
                <div>
                    <strong>Error in ${{context}}</strong>
                    <p>${{errorMessage}}</p>
                </div>
            `;
            
            // Insert at the top of the current tab content
            const currentTab = document.querySelector('.tab-content.active');
            currentTab.insertBefore(alert, currentTab.firstChild);
            
            // Remove alert after 5 seconds
            setTimeout(() => {{
                alert.remove();
            }}, 5000);
        }}
        
        // Load results
        async function loadResults() {{
            const container = document.getElementById('results-container');
            
            try {{
                // Show loading state
                container.innerHTML = `
                    <div class="loading">
                        <div class="loading-spinner"></div>
                        <h3>Loading Election Results</h3>
                        <p>Please wait while we fetch the latest data...</p>
                    </div>
                `;
                
                const response = await fetch(API_BASE + '/results');
                
                if (!response.ok) {{
                    throw new Error(`Server returned ${{response.status}}: ${{response.statusText}}`);
                }}
                
                const result = await response.json();
                
                if (result.success) {{
                    container.innerHTML = '';
                    
                    if (result.results && result.results.length > 0) {{
                        // Group by position
                        const positions = {{}};
                        result.results.forEach(candidate => {{
                            if (!positions[candidate.position]) {{
                                positions[candidate.position] = [];
                            }}
                            positions[candidate.position].push(candidate);
                        }});
                        
                        // Find winners and create results
                        for (const [position, candidates] of Object.entries(positions)) {{
                            const positionCard = document.createElement('div');
                            positionCard.className = 'position-card';
                            
                            // Calculate total votes for this position
                            const totalVotes = candidates.reduce((sum, candidate) => sum + candidate.votes, 0);
                            
                            // Find winner (most votes)
                            const winner = candidates.reduce((prev, current) => 
                                (prev.votes > current.votes) ? prev : current
                            );
                            
                            let positionHTML = `
                                <div class="position-header">
                                    <div class="position-title">${{position}}</div>
                                    <div class="position-votes">${{totalVotes}} Total Votes</div>
                                </div>
                                <div class="candidates-list">
                            `;
                            
                            candidates.sort((a, b) => b.votes - a.votes).forEach(candidate => {{
                                const isWinner = candidate.votes === winner.votes && candidate.votes > 0;
                                const percentage = totalVotes > 0 ? Math.round((candidate.votes / totalVotes) * 100) : 0;
                                
                                positionHTML += `
                                    <div class="candidate-card ${{isWinner ? 'winner' : ''}}">
                                        <div class="candidate-info">
                                            <div class="candidate-name">${{candidate.name}}</div>
                                            <div class="candidate-department">${{candidate.department || 'No department specified'}}</div>
                                        </div>
                                        <div class="candidate-stats">
                                            <div class="vote-count">${{candidate.votes}}</div>
                                            <div class="vote-percentage">${{percentage}}%</div>
                                            ${{isWinner ? '<div class="winner-badge"><i class="fas fa-trophy"></i> LEADING</div>' : ''}}
                                        </div>
                                    </div>
                                `;
                            }});
                            
                            positionHTML += `</div>`;
                            positionCard.innerHTML = positionHTML;
                            container.appendChild(positionCard);
                        }}
                        
                        // Show success message
                        const alert = document.createElement('div');
                        alert.className = 'alert alert-success';
                        alert.innerHTML = `
                            <i class="fas fa-check-circle"></i>
                            <div>
                                <strong>Results Updated</strong>
                                <p>Election results have been successfully refreshed.</p>
                            </div>
                        `;
                        container.insertBefore(alert, container.firstChild);
                        
                        // Remove alert after 3 seconds
                        setTimeout(() => {{
                            alert.remove();
                        }}, 3000);
                    }} else {{
                        container.innerHTML = `
                            <div class="empty-state">
                                <div class="empty-icon">
                                    <i class="fas fa-chart-bar"></i>
                                </div>
                                <h3>No Results Available</h3>
                                <p>Election results will appear here once voting begins.</p>
                            </div>
                        `;
                    }}
                    
                    document.getElementById('last-update').textContent = new Date().toLocaleString();
                }} else {{
                    throw new Error(result.message || 'Failed to load results');
                }}
            }} catch (error) {{
                handleError('loadResults', error);
                
                // Show error state
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">
                            <i class="fas fa-exclamation-triangle"></i>
                        </div>
                        <h3>Unable to Load Results</h3>
                        <p>There was a problem fetching the election results. Please try again.</p>
                        <button class="btn" style="margin-top: 20px;" onclick="loadResults()">
                            <i class="fas fa-redo"></i>
                            Try Again
                        </button>
                    </div>
                `;
            }}
        }}
        
        // Load statistics
        async function loadStats() {{
            try {{
                const response = await fetch(API_BASE + '/stats');
                
                if (!response.ok) {{
                    throw new Error(`Server returned ${{response.status}}: ${{response.statusText}}`);
                }}
                
                const result = await response.json();
                
                if (result.success) {{
                    document.getElementById('total-voters').textContent = result.stats.total_registered_voters;
                    document.getElementById('total-votes').textContent = result.stats.votes_cast;
                    
                    // Calculate turnout percentage
                    const turnout = result.stats.total_registered_voters > 0 
                        ? Math.round((result.stats.votes_cast / result.stats.total_registered_voters) * 100)
                        : 0;
                    document.getElementById('turnout-rate').textContent = turnout + '%';
                    
                    document.getElementById('verified-voters').textContent = result.stats.verified_voters || result.stats.total_registered_voters;
                    document.getElementById('last-update').textContent = new Date().toLocaleString();
                    
                    // Show success message
                    const currentTab = document.getElementById('dashboard-tab');
                    const alert = document.createElement('div');
                    alert.className = 'alert alert-success';
                    alert.innerHTML = `
                        <i class="fas fa-check-circle"></i>
                        <div>
                            <strong>Statistics Updated</strong>
                            <p>Election statistics have been successfully refreshed.</p>
                        </div>
                    `;
                    currentTab.insertBefore(alert, currentTab.querySelector('.stats-grid'));
                    
                    // Remove alert after 3 seconds
                    setTimeout(() => {{
                        alert.remove();
                    }}, 3000);
                }} else {{
                    throw new Error(result.message || 'Failed to load statistics');
                }}
            }} catch (error) {{
                handleError('loadStats', error);
            }}
        }}
        
        // Load voters list
        async function loadVoters() {{
            const container = document.getElementById('voters-container');
            
            try {{
                // Show loading state
                container.innerHTML = `
                    <div class="loading">
                        <div class="loading-spinner"></div>
                        <h3>Loading Voter Information</h3>
                        <p>Please wait while we fetch the latest data...</p>
                    </div>
                `;
                
                const response = await fetch(API_BASE + '/voters');
                
                if (!response.ok) {{
                    throw new Error(`Server returned ${{response.status}}: ${{response.statusText}}`);
                }}
                
                const result = await response.json();
                
                if (result.success) {{
                    container.innerHTML = '';
                    
                    if (result.voters.length === 0) {{
                        container.innerHTML = `
                            <div class="empty-state">
                                <div class="empty-icon">
                                    <i class="fas fa-users"></i>
                                </div>
                                <h3>No Voters Registered</h3>
                                <p>Voter registration data will appear here once voters are registered.</p>
                            </div>
                        `;
                        return;
                    }}
                    
                    const votersList = document.createElement('div');
                    votersList.className = 'voters-container';
                    
                    result.voters.forEach(voter => {{
                        const voterCard = document.createElement('div');
                        voterCard.className = 'voter-card';
                        voterCard.innerHTML = `
                            <div class="voter-info">
                                <div class="voter-name">${{voter.name}}</div>
                                <div class="voter-details">
                                    ID: ${{voter.student_id}} | Email: ${{voter.email}} | Department: ${{voter.department || 'Not specified'}}
                                </div>
                            </div>
                            <div class="voter-status ${{voter.location_verified ? 'status-verified' : 'status-pending'}}">
                                ${{voter.location_verified ? '<i class="fas fa-check-circle"></i> Verified' : '<i class="fas fa-clock"></i> Pending'}}
                            </div>
                        `;
                        votersList.appendChild(voterCard);
                    }});
                    
                    container.appendChild(votersList);
                    
                    // Show success message
                    const alert = document.createElement('div');
                    alert.className = 'alert alert-success';
                    alert.innerHTML = `
                        <i class="fas fa-check-circle"></i>
                        <div>
                            <strong>Voter List Updated</strong>
                            <p>Voter information has been successfully refreshed.</p>
                        </div>
                    `;
                    container.insertBefore(alert, container.firstChild);
                    
                    // Remove alert after 3 seconds
                    setTimeout(() => {{
                        alert.remove();
                    }}, 3000);
                }} else {{
                    throw new Error(result.message || 'Failed to load voters');
                }}
            }} catch (error) {{
                handleError('loadVoters', error);
                
                // Show error state
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">
                            <i class="fas fa-exclamation-triangle"></i>
                        </div>
                        <h3>Unable to Load Voters</h3>
                        <p>There was a problem fetching the voter list. Please try again.</p>
                        <button class="btn" style="margin-top: 20px;" onclick="loadVoters()">
                            <i class="fas fa-redo"></i>
                            Try Again
                        </button>
                    </div>
                `;
            }}
        }}
        
        // Control election status
        async function controlElection(action) {{
            try {{
                const response = await fetch(API_BASE + '/election/control', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{ action: action }})
                }});
                
                const result = await response.json();
                
                if (result.success) {{
                    // Show success message
                    const alert = document.createElement('div');
                    alert.className = 'alert alert-success';
                    alert.innerHTML = `
                        <i class="fas fa-check-circle"></i>
                        <div>
                            <strong>Election ${{action.charAt(0).toUpperCase() + action.slice(1)}}ed</strong>
                            <p>${{result.message}}</p>
                        </div>
                    `;
                    
                    const currentTab = document.querySelector('.tab-content.active');
                    currentTab.insertBefore(alert, currentTab.firstChild);
                    
                    // Remove alert after 5 seconds
                    setTimeout(() => {{
                        alert.remove();
                    }}, 5000);
                    
                    // Reload page to update status
                    setTimeout(() => {{
                        window.location.reload();
                    }}, 2000);
                }} else {{
                    throw new Error(result.message || 'Failed to control election');
                }}
            }} catch (error) {{
                handleError('controlElection', error);
            }}
        }}
        
        // Export data
        async function exportData() {{
            try {{
                const response = await fetch(API_BASE + '/export');
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = 'election-data-' + new Date().toISOString().split('T')[0] + '.json';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                
                // Show success message
                const alert = document.createElement('div');
                alert.className = 'alert alert-success';
                alert.innerHTML = `
                    <i class="fas fa-check-circle"></i>
                    <div>
                        <strong>Export Successful</strong>
                        <p>Election data has been downloaded.</p>
                    </div>
                `;
                
                const currentTab = document.querySelector('.tab-content.active');
                currentTab.insertBefore(alert, currentTab.firstChild);
                
                // Remove alert after 5 seconds
                setTimeout(() => {{
                    alert.remove();
                }}, 5000);
            }} catch (error) {{
                handleError('exportData', error);
            }}
        }}
        
        // Initialize the page
        document.addEventListener('DOMContentLoaded', () => {{
            loadResults();
            loadStats();
            
            // Auto-refresh results every 30 seconds if on results tab
            setInterval(() => {{
                if (document.querySelector('.nav-item.active').getAttribute('data-tab') === 'results') {{
                    loadResults();
                }}
            }}, 30000);
        }});
    </script>
</body>
</html>
    '''

# Admin API Routes
@app.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    """Get election statistics"""
    try:
        # Total registered voters
        total_voters = db.voters.count_documents({'location_verified': True})
        
        # Total votes cast
        votes_cast = db.votes.count_documents({})
        
        return jsonify({
            'success': True,
            'stats': {
                'total_registered_voters': total_voters,
                'votes_cast': votes_cast,
                'verified_voters': total_voters
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching stats: {str(e)}'
        }), 500

@app.route('/api/results', methods=['GET'])
@login_required
def get_results():
    """Get election results"""
    try:
        # Aggregate votes by candidate using MongoDB aggregation
        pipeline = [
            {
                '$group': {
                    '_id': '$candidate_id',
                    'votes': {'$sum': 1}
                }
            }
        ]
        
        votes_by_candidate = list(db.votes.aggregate(pipeline))
        
        # Convert to dictionary for easy lookup
        votes_dict = {vote['_id']: vote['votes'] for vote in votes_by_candidate}
        
        # Get all candidates
        candidates = list(db.candidates.find({}))
        
        results_list = []
        for candidate in candidates:
            candidate_id = str(candidate['_id'])
            votes = votes_dict.get(candidate_id, 0)
            
            candidate_data = {
                'id': candidate_id,
                'name': candidate['name'],
                'position': candidate['position'],
                'department': candidate.get('department', ''),
                'votes': votes
            }
            results_list.append(candidate_data)
        
        return jsonify({
            'success': True,
            'results': results_list
        })
        
    except Exception as e:
        print(f"❌ ERROR in get_results: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error fetching results: {str(e)}'
        }), 500

@app.route('/api/voters', methods=['GET'])
@login_required
def get_voters():
    """Get list of all registered voters"""
    try:
        voters = list(db.voters.find({}).sort('registration_date', -1))
        
        voters_list = []
        for voter in voters:
            voters_list.append({
                'student_id': voter.get('student_id', ''),
                'name': voter.get('name', ''),
                'email': voter.get('email', ''),
                'department': voter.get('department', ''),
                'location_verified': voter.get('location_verified', False)
            })
        
        return jsonify({
            'success': True,
            'voters': voters_list
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching voters: {str(e)}'
        }), 500

@app.route('/api/election/control', methods=['POST'])
@login_required
def control_election():
    """Control election status (start, pause, end, reset)"""
    try:
        data = request.get_json()
        action = data.get('action')
        
        election_settings = db.election_settings.find_one({})
        
        if action == 'start':
            db.election_settings.update_one({}, {
                '$set': {
                    'election_status': 'ongoing',
                    'start_time': datetime.utcnow(),
                    'end_time': None
                }
            })
            message = 'Election has been started. Voting is now open.'
            
        elif action == 'pause':
            db.election_settings.update_one({}, {
                '$set': {
                    'election_status': 'paused'
                }
            })
            message = 'Election has been paused. Voting is temporarily suspended.'
            
        elif action == 'end':
            db.election_settings.update_one({}, {
                '$set': {
                    'election_status': 'ended',
                    'end_time': datetime.utcnow()
                }
            })
            message = 'Election has been ended. Voting is now closed.'
            
        elif action == 'reset':
            # Clear all votes (be careful with this!)
            db.votes.delete_many({})
            db.election_settings.update_one({}, {
                '$set': {
                    'election_status': 'not_started',
                    'start_time': None,
                    'end_time': None
                }
            })
            message = 'Election has been reset. All votes have been cleared.'
            
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid action'
            }), 400
        
        return jsonify({
            'success': True,
            'message': message
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error controlling election: {str(e)}'
        }), 500

@app.route('/api/export', methods=['GET'])
@login_required
def export_data():
    """Export all election data"""
    try:
        # Get all data
        voters = list(db.voters.find({}))
        candidates = list(db.candidates.find({}))
        votes = list(db.votes.find({}))
        election_settings = db.election_settings.find_one({})
        
        # Convert ObjectId to string for JSON serialization
        for voter in voters:
            voter['_id'] = str(voter['_id'])
        
        for candidate in candidates:
            candidate['_id'] = str(candidate['_id'])
            
        for vote in votes:
            vote['_id'] = str(vote['_id'])
            vote['candidate_id'] = str(vote['candidate_id'])
            vote['voter_id'] = str(vote['voter_id'])
        
        if election_settings:
            election_settings['_id'] = str(election_settings['_id'])
        
        export_data = {
            'exported_at': datetime.utcnow().isoformat(),
            'voters': voters,
            'candidates': candidates,
            'votes': votes,
            'election_settings': election_settings
        }
        
        return jsonify(export_data)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error exporting data: {str(e)}'
        }), 500

@app.route('/api/debug/info')
@login_required
def debug_info():
    """Debug endpoint to show database info"""
    return jsonify({
        'database_name': DATABASE_NAME,
        'collections': db.list_collection_names(),
        'voters_count': db.voters.count_documents({}),
        'candidates_count': db.candidates.count_documents({}),
        'votes_count': db.votes.count_documents({})
    })

if __name__ == '__main__':
    print("🚀 Starting Admin Dashboard - Obong University SRC Elections")
    print(f"📊 Database: MongoDB - {DATABASE_NAME}")
    print("🔐 Admin Login required at: http://localhost:5002/admin/login")
    print("👤 Default credentials: admin / admin123")
    print("✅ Database initialized successfully!")
    print("🌐 Admin Dashboard running at: http://localhost:5002")
    print("⚙️  Admins can control election status and monitor results")
    print("\n⏹️  Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=5002)