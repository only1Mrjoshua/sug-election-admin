from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import bcrypt
import os
import urllib.parse
import logging
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'iauweiyvbiueyckuahsfdyrstvdKYWRIURIVTABSDFHCDVJQWT2648hfjbs'

# Enhanced CORS configuration
CORS(app, 
     origins=[
         "https://obong-university-src-election-admin-9x5w.onrender.com",
         "https://obong-university-src-election-admin.onrender.com",
         "http://localhost:5000", 
         "http://127.0.0.1:5000",
         "http://localhost:3000",
         "http://127.0.0.1:3000"
     ],
     supports_credentials=True,
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"])

# MongoDB configuration with proper password encoding
username = "only1MrJoshua"
password = "LovuLord2025"
encoded_password = urllib.parse.quote_plus(password)

MONGO_URI = f"mongodb+srv://{username}:{encoded_password}@cluster0.9jqnavg.mongodb.net/election_db?retryWrites=true&w=majority&socketTimeoutMS=30000&connectTimeoutMS=30000&serverSelectionTimeoutMS=30000"
DATABASE_NAME = "election_db"

# Initialize MongoDB with connection pooling
try:
    client = MongoClient(
        MONGO_URI,
        maxPoolSize=50,
        retryWrites=True,
        retryReads=True
    )
    # Test connection with timeout
    client.admin.command('ping', maxTimeMS=30000)
    db = client[DATABASE_NAME]
    logger.info("✅ MongoDB connection successful!")
except Exception as e:
    logger.error(f"❌ MongoDB connection failed: {e}")
    db = None

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'serve_login'

# Custom JSON login required decorator for APIs
def api_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({
                'success': False,
                'message': 'Authentication required. Please log in.',
                'login_required': True
            }), 401
        return f(*args, **kwargs)
    return decorated_function

# Override Flask-Login's unauthorized handler to return JSON instead of redirect
@login_manager.unauthorized_handler
def unauthorized():
    # If it's an API request, return JSON error
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'message': 'Authentication required',
            'login_required': True
        }), 401
    # For regular pages, redirect to login
    return redirect(url_for('serve_login'))

# Admin credentials - FIXED: Store the hash properly
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "obonguni2025"
# Generate hash once and store it
ADMIN_PASSWORD_HASH = bcrypt.hashpw(ADMIN_PASSWORD.encode('utf-8'), bcrypt.gensalt())

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(username):
    if username == ADMIN_USERNAME:
        return User(username)
    return None

# Initialize collections safely
def get_collection(collection_name):
    """Safely get collection reference"""
    if db is None:
        raise Exception("Database not connected")
    return db[collection_name]

# Valid matric numbers database
VALID_MATRIC_NUMBERS = {
    "U20241001", "U20241002", "U20241003", "U20241004", "U20241005",
    "U20241006", "U20241007", "U20241008", "U20241009", "U20241010",
    "U20241011", "U20241012", "U20241013", "U20241014", "U20241015",
    "U20241016", "U20241017", "U20241018", "U20241019", "U20241020",
    "U20241021", "U20241022", "U20241023", "U20241024", "U20241025",
    "U20242001", "U20242002", "U20242003", "U20242004", "U20242005",
    "U20242006", "U20242007", "U20242008", "U20242009", "U20242010",
    "U20242011", "U20242012", "U20242013", "U20242014", "U20242015",
    "U20242016", "U20242017", "U20242018", "U20242019", "U20242020",
    "U20242021", "U20242022", "U20242023", "U20242024", "U20242025",
    "U20243001", "U20243002", "U20243003", "U20243004", "U20243005",
    "U20243006", "U20243007", "U20243008", "U20243009", "U20243010",
    "U20243011", "U20243012", "U20243013", "U20243014", "U20243015",
    "U20243016", "U20243017", "U20243018", "U20243019", "U20243020",
    "U20243021", "U20243022", "U20243023", "U20243024", "U20243025",
    "U20244001", "U20244002", "U20244003", "U20244004", "U20244005",
    "U20244006", "U20244007", "U20244008", "U20244009", "U20244010",
    "U20244011", "U20244012", "U20244013", "U20244014", "U20244015",
    "U20244016", "U20244017", "U20244018", "U20244019", "U20244020",
    "U20244021", "U20244022", "U20244023", "U20244024", "U20244025"
}

def init_db():
    """Initialize database with sample data"""
    try:
        if db is None:
            logger.error("Database not connected - cannot initialize")
            return
            
        voters_collection = get_collection('voters')
        candidates_collection = get_collection('candidates')
        votes_collection = get_collection('votes')
        election_settings_collection = get_collection('election_settings')

        # Clean up existing indexes
        try:
            current_voter_indexes = list(voters_collection.list_indexes())
            for index in current_voter_indexes:
                index_name = index['name']
                if index_name == 'email_1':
                    voters_collection.drop_index('email_1')
        except Exception as e:
            logger.info(f"Index cleanup: {e}")

        # Create indexes
        indexes_to_create = [
            (voters_collection, "matric_number", True),
            (votes_collection, "candidate_id", False),
            (votes_collection, [("voter_id", 1), ("candidate_position", 1)], True),
        ]
        
        for collection, field, unique in indexes_to_create:
            try:
                if isinstance(field, list):
                    collection.create_index(field, unique=unique, name="unique_vote_per_position")
                else:
                    if unique:
                        collection.create_index(field, unique=True)
                    else:
                        collection.create_index(field)
                logger.info(f"✅ Created index for {field}")
            except Exception as e:
                logger.warning(f"⚠️  Index warning for {field}: {e}")

        # Initialize election settings
        if election_settings_collection.count_documents({}) == 0:
            election_settings_collection.insert_one({
                'election_status': 'not_started',
                'start_time': None,
                'end_time': None,
                'updated_at': datetime.utcnow()
            })
            logger.info("✅ Election settings initialized")

        # Initialize candidates
        if candidates_collection.count_documents({}) == 0:
            real_candidates = [
                {
                    "name": "Olukunle Tomiwa Covenant",
                    "position": "President",
                    "faculty": "Natural and Applied Science",
                    "created_at": datetime.utcnow()
                },
                {
                    "name": "Kennedy Solomon", 
                    "position": "President",
                    "faculty": "Natural and Applied Science",
                    "created_at": datetime.utcnow()
                },
                {
                    "name": "Jeremiah Gideon Emmanuel",
                    "position": "President",
                    "faculty": "Natural and Applied Science",
                    "created_at": datetime.utcnow()
                },
                {
                    "name": "Onwuoha Confidence Daberechi",
                    "position": "Vice President",
                    "faculty": "Natural and Applied Science",
                    "created_at": datetime.utcnow()
                },
                {
                    "name": "Babade Beatrice Jonathan",
                    "position": "Vice President",
                    "faculty": "Arts and Communications",
                    "created_at": datetime.utcnow()
                },
                {
                    "name": "Dimkpa Raymond Baribeebi",
                    "position": "Financial Secretary",
                    "faculty": "Natural and Applied Science",
                    "created_at": datetime.utcnow()
                },
                {
                    "name": "Mbang Donnoble Godwin",
                    "position": "Director of Transport",
                    "faculty": "Natural and Applied Science",
                    "created_at": datetime.utcnow()
                },
                {
                    "name": "Olukunle Titilola Oyindamola",
                    "position": "Director of Socials",
                    "faculty": "Management Science",
                    "created_at": datetime.utcnow()
                },
                {
                    "name": "Alasy Clinton Ebubechukwu",
                    "position": "Director of Socials",
                    "faculty": "Management Science",
                    "created_at": datetime.utcnow()
                },
                {
                    "name": "Collins Jacob",
                    "position": "Director of Sports",
                    "faculty": "Natural and Applied Science",
                    "created_at": datetime.utcnow()
                },
                {
                    "name": "Chisom Ejims",
                    "position": "Director of Sports",
                    "faculty": "Management Science",
                    "created_at": datetime.utcnow()
                },
                {
                    "name": "Davidson Lawrence",
                    "position": "Director of Sports",
                    "faculty": "Natural and Applied Science",
                    "created_at": datetime.utcnow()
                },
                {
                    "name": "Meshach Efioke",
                    "position": "Director of Information",
                    "faculty": "Natural and Applied Science",
                    "created_at": datetime.utcnow()
                },
                {
                    "name": "Abraham Raymond",
                    "position": "Student Chaplain",
                    "faculty": "Natural and Applied Science",
                    "created_at": datetime.utcnow()
                }
            ]
            candidates_collection.insert_many(real_candidates)
            logger.info("✅ REAL candidates added to MongoDB")
        else:
            logger.info("✅ Candidates already exist in database")
            
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")

# Initialize database
init_db()

# Serve the login page
@app.route('/')
def serve_login():
    return render_template('index.html')

# Serve the admin dashboard
@app.route('/admin_dashboard')
@login_required
def serve_admin_dashboard():
    return render_template('admin_dashboard.html')

# API Routes
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Admin login API"""
    try:
        # Check if database is connected
        if db is None:
            logger.error("Database connection is None in admin_login")
            return jsonify({
                'success': False,
                'message': 'Database connection failed. Please check server logs.'
            }), 500

        # Check if request has JSON data
        if not request.is_json:
            logger.error("Request is not JSON")
            return jsonify({
                'success': False,
                'message': 'Request must be JSON'
            }), 400

        data = request.get_json()
        if not data:
            logger.error("No JSON data received")
            return jsonify({
                'success': False,
                'message': 'No data received'
            }), 400
            
        username = data.get('username')
        password = data.get('password')
        
        logger.info(f"Login attempt for username: {username}")
        
        if not username or not password:
            logger.error("Missing username or password")
            return jsonify({
                'success': False,
                'message': 'Username and password are required'
            }), 400
        
        # Verify credentials
        logger.info(f"Verifying credentials for: {username}")
        if username == ADMIN_USERNAME and bcrypt.checkpw(password.encode('utf-8'), ADMIN_PASSWORD_HASH):
            user = User(username)
            login_user(user)
            logger.info(f"✅ Successful login for: {username}")
            response_data = {
                'success': True,
                'message': 'Login successful',
                'redirect': '/admin_dashboard'
            }
            logger.info(f"Returning response: {response_data}")
            return jsonify(response_data)
        else:
            logger.warning(f"❌ Failed login attempt for: {username}")
            return jsonify({
                'success': False,
                'message': 'Invalid credentials. Please try again.'
            }), 401
            
    except Exception as e:
        logger.error(f"💥 Login error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Server error during login: {str(e)}'
        }), 500

@app.route('/api/admin/logout', methods=['POST'])
@api_login_required
def admin_logout():
    """Admin logout API"""
    try:
        logout_user()
        return jsonify({
            'success': True,
            'message': 'You have been logged out successfully.',
            'redirect': '/'
        })
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error during logout'
        }), 500

@app.route('/api/stats', methods=['GET'])
@api_login_required
def get_stats():
    """Get election statistics"""
    try:
        voters_collection = get_collection('voters')
        votes_collection = get_collection('votes')
        
        total_voters = voters_collection.count_documents({})
        votes_cast = votes_collection.count_documents({})
        voted_count = voters_collection.count_documents({'has_voted': True})
        
        return jsonify({
            'success': True,
            'stats': {
                'total_registered_voters': total_voters,
                'votes_cast': votes_cast,
                'voted_count': voted_count,
                'remaining_voters': total_voters - voted_count
            }
        })
        
    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error fetching stats: {str(e)}'
        }), 500

@app.route('/api/results', methods=['GET'])
@api_login_required
def get_results():
    """Get election results"""
    try:
        votes_collection = get_collection('votes')
        candidates_collection = get_collection('candidates')
        
        pipeline = [
            {
                '$group': {
                    '_id': '$candidate_id',
                    'votes': {'$sum': 1}
                }
            }
        ]
        
        votes_by_candidate = list(votes_collection.aggregate(pipeline))
        votes_dict = {vote['_id']: vote['votes'] for vote in votes_by_candidate}
        
        candidates = list(candidates_collection.find({}))
        
        results_list = []
        for candidate in candidates:
            candidate_id = str(candidate['_id'])
            votes = votes_dict.get(candidate_id, 0)
            
            candidate_data = {
                'id': candidate_id,
                'name': candidate['name'],
                'position': candidate['position'],
                'department': candidate.get('faculty', ''),
                'votes': votes
            }
            results_list.append(candidate_data)
        
        return jsonify({
            'success': True,
            'results': results_list
        })
        
    except Exception as e:
        logger.error(f"Results error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error fetching results: {str(e)}'
        }), 500

@app.route('/api/voters', methods=['GET'])
@api_login_required
def get_voters():
    """Get list of all registered voters"""
    try:
        voters_collection = get_collection('voters')
        
        voters = list(voters_collection.find({}).sort('registration_date', -1))
        
        voters_list = []
        for voter in voters:
            voters_list.append({
                'matric_number': voter.get('matric_number', ''),
                'has_voted': voter.get('has_voted', False),
                'registration_date': voter.get('registration_date', '').isoformat() if voter.get('registration_date') else ''
            })
        
        return jsonify({
            'success': True,
            'voters': voters_list
        })
        
    except Exception as e:
        logger.error(f"Voters error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error fetching voters: {str(e)}'
        }), 500

@app.route('/api/election/control', methods=['POST'])
@api_login_required
def control_election():
    """Control election status (start, pause, end, reset)"""
    try:
        election_settings_collection = get_collection('election_settings')
        votes_collection = get_collection('votes')
        voters_collection = get_collection('voters')
        
        data = request.get_json()
        action = data.get('action')
        
        if action == 'start':
            election_settings_collection.update_one({}, {
                '$set': {
                    'election_status': 'ongoing',
                    'start_time': datetime.utcnow(),
                    'end_time': None,
                    'updated_at': datetime.utcnow()
                }
            }, upsert=True)
            message = 'Election has been started. Voting is now open.'
            
        elif action == 'pause':
            election_settings_collection.update_one({}, {
                '$set': {
                    'election_status': 'paused',
                    'updated_at': datetime.utcnow()
                }
            }, upsert=True)
            message = 'Election has been paused. Voting is temporarily suspended.'
            
        elif action == 'end':
            election_settings_collection.update_one({}, {
                '$set': {
                    'election_status': 'ended',
                    'end_time': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }
            }, upsert=True)
            message = 'Election has been ended. Voting is now closed.'
            
        elif action == 'reset':
            votes_collection.delete_many({})
            voters_collection.update_many({}, {'$set': {'has_voted': False}})
            election_settings_collection.update_one({}, {
                '$set': {
                    'election_status': 'not_started',
                    'start_time': None,
                    'end_time': None,
                    'updated_at': datetime.utcnow()
                }
            }, upsert=True)
            message = 'Election has been reset. All votes have been cleared and voters can vote again.'
            
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid action'
            }), 400
        
        logger.info(f"Election control action: {action}")
        return jsonify({
            'success': True,
            'message': message
        })
        
    except Exception as e:
        logger.error(f"Election control error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error controlling election: {str(e)}'
        }), 500

@app.route('/api/election/status', methods=['GET'])
@api_login_required
def get_election_status():
    """Get current election status"""
    try:
        election_settings_collection = get_collection('election_settings')
        
        election_settings = election_settings_collection.find_one({})
        election_status = 'not_started'
        if election_settings:
            election_status = election_settings.get('election_status', 'not_started')
        
        status_colors = {
            'not_started': '#666',
            'ongoing': '#2C8A45',
            'paused': '#EBBF00',
            'ended': '#D13D39'
        }
        status_color = status_colors.get(election_status, '#666')
        
        return jsonify({
            'success': True,
            'status': election_status,
            'color': status_color
        })
        
    except Exception as e:
        logger.error(f"Election status error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error fetching election status: {str(e)}'
        }), 500

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Server is running',
        'database_connected': db is not None,
        'timestamp': datetime.utcnow().isoformat()
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'message': 'API endpoint not found'
        }), 404
    return render_template('index.html')

@app.errorhandler(500)
def internal_error(error):
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    print("🚀 Starting Admin Dashboard API - Obong University SRC Elections")
    print(f"📊 MongoDB Connected: {db is not None}")
    print(f"🔐 Admin Username: {ADMIN_USERNAME}")
    print(f"🔑 Admin Password Hash: {ADMIN_PASSWORD_HASH}")
    print(f"🌐 Server running on port: {port}")
    app.run(debug=False, host='0.0.0.0', port=port)