from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import bcrypt
import os

app = Flask(__name__, template_folder='templates')
app.secret_key = 'iauweiyvbiueyckuahsfdyrstvdKYWRIURIVTABSDFHCDVJQWT2648hfjbs'
CORS(app)  # Enable CORS for all routes

# MongoDB configuration
MONGO_URI = "mongodb+srv://only1MrJoshua:LovuLord2025@cluster0.9jqnavg.mongodb.net/election_db?retryWrites=true&w=majority"
DATABASE_NAME = "election_db"

# Initialize MongoDB
try:
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    client.admin.command('ping')
    print("✅ MongoDB connection successful!")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    exit(1)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'serve_login'

# Admin credentials
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

# Collections
voters_collection = db['voters']
candidates_collection = db['candidates']
votes_collection = db['votes']
election_settings_collection = db['election_settings']

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
        current_voter_indexes = list(voters_collection.list_indexes())
        for index in current_voter_indexes:
            index_name = index['name']
            if index_name == 'email_1':
                voters_collection.drop_index('email_1')
        
        current_vote_indexes = list(votes_collection.list_indexes())
        for index in current_vote_indexes:
            index_name = index['name']
            if index_name == 'voter_id_1' and index.get('unique', False):
                votes_collection.drop_index('voter_id_1')
    except Exception as e:
        print(f"ℹ️  Index cleanup: {e}")

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
            print(f"✅ Created index for {field}")
        except Exception as e:
            print(f"⚠️  Index warning for {field}: {e}")

    if election_settings_collection.count_documents({}) == 0:
        election_settings_collection.insert_one({
            'election_status': 'not_started',
            'start_time': None,
            'end_time': None,
            'updated_at': datetime.utcnow()
        })
        print("✅ Election settings initialized")

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
        print("✅ REAL candidates added to MongoDB")
    else:
        print("✅ Candidates already exist in database")

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
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if username == ADMIN_USERNAME and bcrypt.checkpw(password.encode('utf-8'), ADMIN_PASSWORD_HASH):
        user = User(username)
        login_user(user)
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'redirect': '/admin_dashboard'
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Invalid credentials. Please try again.'
        }), 401

@app.route('/api/admin/logout', methods=['POST'])
@login_required
def admin_logout():
    """Admin logout API"""
    logout_user()
    return jsonify({
        'success': True,
        'message': 'You have been logged out successfully.',
        'redirect': '/'
    })

@app.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    """Get election statistics"""
    try:
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
        return jsonify({
            'success': False,
            'message': f'Error fetching stats: {str(e)}'
        }), 500

@app.route('/api/results', methods=['GET'])
@login_required
def get_results():
    """Get election results"""
    try:
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
        return jsonify({
            'success': False,
            'message': f'Error fetching results: {str(e)}'
        }), 500

@app.route('/api/voters', methods=['GET'])
@login_required
def get_voters():
    """Get list of all registered voters"""
    try:
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
        
        election_settings = election_settings_collection.find_one({})
        
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
        
        return jsonify({
            'success': True,
            'message': message
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error controlling election: {str(e)}'
        }), 500

@app.route('/api/election/status', methods=['GET'])
@login_required
def get_election_status():
    """Get current election status"""
    try:
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
        return jsonify({
            'success': False,
            'message': f'Error fetching election status: {str(e)}'
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    print("🚀 Starting Admin Dashboard API - Obong University SRC Elections")
    app.run(debug=False, host='0.0.0.0', port=port)