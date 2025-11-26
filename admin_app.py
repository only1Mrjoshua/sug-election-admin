from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import bcrypt
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'iauweiyvbiueyckuahsfdyrstvdKYWRIURIVTABSDFHCDVJQWT2648hfjbs'  # Change this in production!

# MongoDB configuration - FIXED URI
MONGO_URI = "mongodb+srv://only1MrJoshua:LovuLord2025@cluster0.9jqnavg.mongodb.net/election_db?retryWrites=true&w=majority"
DATABASE_NAME = "election_db"

# Initialize MongoDB
try:
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    # Test connection
    client.admin.command('ping')
    print("✅ MongoDB connection successful!")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    # Fallback to local database or exit
    exit(1)

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

# Collections
voters_collection = db['voters']
candidates_collection = db['candidates']
votes_collection = db['votes']
election_settings_collection = db['election_settings']

# Valid matric numbers database (100 mock matric numbers) - MATCHING STUDENT PORTAL
VALID_MATRIC_NUMBERS = {
    # Natural and Applied Science (25 students)
    "U20241001", "U20241002", "U20241003", "U20241004", "U20241005",
    "U20241006", "U20241007", "U20241008", "U20241009", "U20241010",
    "U20241011", "U20241012", "U20241013", "U20241014", "U20241015",
    "U20241016", "U20241017", "U20241018", "U20241019", "U20241020",
    "U20241021", "U20241022", "U20241023", "U20241024", "U20241025",
    
    # Arts and Communications (25 students)
    "U20242001", "U20242002", "U20242003", "U20242004", "U20242005",
    "U20242006", "U20242007", "U20242008", "U20242009", "U20242010",
    "U20242011", "U20242012", "U20242013", "U20242014", "U20242015",
    "U20242016", "U20242017", "U20242018", "U20242019", "U20242020",
    "U20242021", "U20242022", "U20242023", "U20242024", "U20242025",
    
    # Social Science (25 students)
    "U20243001", "U20243002", "U20243003", "U20243004", "U20243005",
    "U20243006", "U20243007", "U20243008", "U20243009", "U20243010",
    "U20243011", "U20243012", "U20243013", "U20243014", "U20243015",
    "U20243016", "U20243017", "U20243018", "U20243019", "U20243020",
    "U20243021", "U20243022", "U20243023", "U20243024", "U20243025",
    
    # Management Science (25 students)
    "U20244001", "U20244002", "U20244003", "U20244004", "U20244005",
    "U20244006", "U20244007", "U20244008", "U20244009", "U20244010",
    "U20244011", "U20244012", "U20244013", "U20244014", "U20244015",
    "U20244016", "U20244017", "U20244018", "U20244019", "U20244020",
    "U20244021", "U20244022", "U20244023", "U20244024", "U20244025"
}

def init_db():
    """Initialize database with sample data if needed - MATCHING STUDENT PORTAL"""
    # Clean up any existing problematic indexes
    try:
        # Clean up voters collection indexes - REMOVE EMAIL INDEXES
        current_voter_indexes = list(voters_collection.list_indexes())
        for index in current_voter_indexes:
            index_name = index['name']
            # Remove any email indexes
            if index_name == 'email_1':
                voters_collection.drop_index('email_1')
                print("✅ Removed email index from voters collection")
        
        # Clean up votes collection indexes  
        current_vote_indexes = list(votes_collection.list_indexes())
        for index in current_vote_indexes:
            index_name = index['name']
            if index_name == 'voter_id_1' and index.get('unique', False):
                votes_collection.drop_index('voter_id_1')
                print("✅ Removed problematic unique index on voter_id")
    except Exception as e:
        print(f"ℹ️  Index cleanup: {e}")

    # Create correct indexes - MATRIC NUMBER ONLY (NO EMAIL)
    indexes_to_create = [
        (voters_collection, "matric_number", True),  # Only unique index we need
        (votes_collection, "candidate_id", False),
        (votes_collection, [("voter_id", 1), ("candidate_position", 1)], True),
    ]
    
    for collection, field, unique in indexes_to_create:
        try:
            if isinstance(field, list):  # Compound index
                collection.create_index(field, unique=unique, name="unique_vote_per_position")
            else:  # Single field index
                if unique:
                    collection.create_index(field, unique=True)
                else:
                    collection.create_index(field)
            print(f"✅ Created index for {field}")
        except Exception as e:
            print(f"⚠️  Index warning for {field}: {e}")

    # Initialize election settings if not exists
    if election_settings_collection.count_documents({}) == 0:
        election_settings_collection.insert_one({
            'election_status': 'not_started',
            'start_time': None,
            'end_time': None,
            'updated_at': datetime.utcnow()
        })
        print("✅ Election settings initialized")

    # Add REAL candidates if none exist
    if candidates_collection.count_documents({}) == 0:
        real_candidates = [
            # President (3 candidates)
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
            
            # Vice President (2 candidates)
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
            
            # Financial Secretary (1 candidate)
            {
                "name": "Dimkpa Raymond Baribeebi",
                "position": "Financial Secretary",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            
            # Director of Transport (1 candidate)
            {
                "name": "Mbang Donnoble Godwin",
                "position": "Director of Transport",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            
            # Director of Socials (2 candidates)
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
            
            # Director of Sports (3 candidates)
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
            
            # Director of Information (1 candidate)
            {
                "name": "Meshach Efioke",
                "position": "Director of Information",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            
            # Student Chaplain (1 candidate)
            {
                "name": "Abraham Raymond",
                "position": "Student Chaplain",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            }
        ]
        candidates_collection.insert_many(real_candidates)
        print("✅ REAL candidates added to MongoDB")
        print("📋 Candidate Positions Summary:")
        print("   - President: 3 candidates")
        print("   - Vice President: 2 candidates") 
        print("   - Financial Secretary: 1 candidate")
        print("   - Director of Transport: 1 candidate")
        print("   - Director of Socials: 2 candidates")
        print("   - Director of Sports: 3 candidates")
        print("   - Director of Information: 1 candidate")
        print("   - Student Chaplain: 1 candidate")
    else:
        print("✅ Candidates already exist in database")

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
    
    return render_template('admin_login.html')

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
    election_settings = election_settings_collection.find_one({})
    
    # Safe access to election status
    election_status = 'not_started'
    if election_settings:
        election_status = election_settings.get('election_status', 'not_started')
    
    # Determine status color
    status_colors = {
        'not_started': '#666',
        'ongoing': '#2C8A45',
        'paused': '#EBBF00',
        'ended': '#D13D39'
    }
    status_color = status_colors.get(election_status, '#666')
    
    return render_template('admin_dashboard.html', 
                         election_status=election_status,
                         status_color=status_color)

# Admin API Routes
@app.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    """Get election statistics - UPDATED FOR MATRIC-ONLY"""
    try:
        # Total registered voters (matric-only)
        total_voters = voters_collection.count_documents({})
        
        # Total votes cast
        votes_cast = votes_collection.count_documents({})
        
        # Voters who have voted
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
        # Aggregate votes by candidate using MongoDB aggregation
        pipeline = [
            {
                '$group': {
                    '_id': '$candidate_id',
                    'votes': {'$sum': 1}
                }
            }
        ]
        
        votes_by_candidate = list(votes_collection.aggregate(pipeline))
        
        # Convert to dictionary for easy lookup
        votes_dict = {vote['_id']: vote['votes'] for vote in votes_by_candidate}
        
        # Get all candidates
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
        print(f"❌ ERROR in get_results: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error fetching results: {str(e)}'
        }), 500

@app.route('/api/voters', methods=['GET'])
@login_required
def get_voters():
    """Get list of all registered voters - UPDATED FOR MATRIC-ONLY"""
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
            # Clear all votes (be careful with this!)
            votes_collection.delete_many({})
            # Reset all voters' has_voted status
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

@app.route('/api/export', methods=['GET'])
@login_required
def export_data():
    """Export all election data - UPDATED FOR MATRIC-ONLY"""
    try:
        # Get all data
        voters = list(voters_collection.find({}))
        candidates = list(candidates_collection.find({}))
        votes = list(votes_collection.find({}))
        election_settings = election_settings_collection.find_one({})
        
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
            'valid_matric_numbers': list(VALID_MATRIC_NUMBERS),
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
        'voters_count': voters_collection.count_documents({}),
        'candidates_count': candidates_collection.count_documents({}),
        'votes_count': votes_collection.count_documents({}),
        'valid_matric_count': len(VALID_MATRIC_NUMBERS),
        'election_settings': election_settings_collection.find_one({})
    })

@app.route('/api/debug/reset-votes', methods=['POST'])
@login_required
def reset_votes():
    """Debug endpoint to reset all votes and voter status (for testing only)"""
    try:
        # Delete all votes
        votes_result = votes_collection.delete_many({})
        # Reset all voters' has_voted status
        voters_result = voters_collection.update_many({}, {'$set': {'has_voted': False}})
        
        return jsonify({
            'success': True,
            'message': f'Reset complete: {votes_result.deleted_count} votes deleted, {voters_result.modified_count} voters reset',
            'votes_deleted': votes_result.deleted_count,
            'voters_reset': voters_result.modified_count
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error resetting votes: {str(e)}'
        }), 500

@app.route('/api/debug/delete-database', methods=['POST'])
@login_required
def delete_database():
    """DEBUG: Completely delete the database"""
    try:
        client.drop_database(DATABASE_NAME)
        return jsonify({
            'success': True,
            'message': 'Database deleted successfully. Restart the app to recreate it.'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error deleting database: {str(e)}'
        }), 500

@app.route('/api/debug/valid-matrics')
@login_required
def debug_valid_matrics():
    """Debug endpoint to see all valid matric numbers"""
    return jsonify({
        'success': True,
        'valid_matric_numbers': list(VALID_MATRIC_NUMBERS),
        'total_valid': len(VALID_MATRIC_NUMBERS)
    })

# Fix for Render deployment - use PORT environment variable
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    print("🚀 Starting Admin Dashboard - Obong University SRC Elections")
    print(f"📊 Database: MongoDB - {DATABASE_NAME}")
    print("🔐 Admin Login required at: http://localhost:5002/admin/login")
    print("👤 Default credentials: admin / obonguni2025")
    print("✅ Database initialized successfully!")
    print("🎓 Matric-Only System (matching student portal)")
    print(f"📋 Total Valid Matric Numbers: {len(VALID_MATRIC_NUMBERS)}")
    print("🗳️  REAL CANDIDATES LOADED:")
    print("   - President: 3 candidates")
    print("   - Vice President: 2 candidates")
    print("   - Financial Secretary: 1 candidate")
    print("   - Director of Transport: 1 candidate")
    print("   - Director of Socials: 2 candidates")
    print("   - Director of Sports: 3 candidates")
    print("   - Director of Information: 1 candidate")
    print("   - Student Chaplain: 1 candidate")
    print("🌐 Admin Dashboard running at: http://localhost:5002")
    print("⚙️  Admins can control election status and monitor results")
    print("\n⏹️  Press Ctrl+C to stop the server")
    
    app.run(debug=False, host='0.0.0.0', port=port)