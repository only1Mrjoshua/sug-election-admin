from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import bcrypt
import os
from functools import wraps
import hashlib
import requests

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

def get_client_ip():
    """Get client IP address"""
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        ip = request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0]
    else:
        ip = request.environ.get('REMOTE_ADDR', '127.0.0.1')
    return ip

def hash_ip(ip_address):
    """Hash IP address for privacy"""
    return hashlib.sha256(ip_address.encode()).hexdigest()

def get_ip_location(ip_address):
    """Get location information for an IP address"""
    try:
        # Using ipapi.co for IP geolocation
        response = requests.get(f'http://ipapi.co/{ip_address}/json/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                'city': data.get('city', 'Unknown'),
                'region': data.get('region', 'Unknown'),
                'country': data.get('country_name', 'Unknown'),
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude'),
                'isp': data.get('org', 'Unknown')
            }
    except Exception as e:
        print(f"⚠️  IP location lookup failed: {e}")
    
    return {
        'city': 'Unknown',
        'region': 'Unknown', 
        'country': 'Unknown',
        'latitude': None,
        'longitude': None,
        'isp': 'Unknown'
    }

def init_db():
    """Initialize database with sample data if needed"""
    # First, clean up any existing problematic indexes
    try:
        # Get all current indexes on votes collection
        current_indexes = list(votes_collection.list_indexes())
        for index in current_indexes:
            index_name = index['name']
            # Remove problematic unique index on voter_id alone if it exists
            if index_name == 'voter_id_1' and index.get('unique', False):
                votes_collection.drop_index('voter_id_1')
                print("✅ Removed problematic unique index on voter_id")
    except Exception as e:
        print(f"ℹ️  Index cleanup: {e}")

    # Create correct indexes
    indexes_to_create = [
        (voters_collection, "matric_number", True),
        (voters_collection, "email", True),
        (voters_collection, "ip_hash", False),
        (voters_collection, "name", False),
        (candidates_collection, "name", False),
        (candidates_collection, "position", False),
        (votes_collection, "candidate_id", False),
        # Compound unique index - allows multiple votes per voter but only one per position
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

    # Add comprehensive sample candidates if none exist
    if candidates_collection.count_documents({}) == 0:
        sample_candidates = [
            # SRC President (3 candidates)
            {
                "name": "John Chukwuma",
                "position": "SRC President",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Maria Okon",
                "position": "SRC President", 
                "faculty": "Management Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "David Bassey",
                "position": "SRC President",
                "faculty": "Social Science",
                "created_at": datetime.utcnow()
            },
            
            # SRC Vice President (3 candidates)
            {
                "name": "Grace Emmanuel",
                "position": "SRC Vice President",
                "faculty": "Management Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Samuel Johnson",
                "position": "SRC Vice President",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Fatima Bello",
                "position": "SRC Vice President",
                "faculty": "Social Science",
                "created_at": datetime.utcnow()
            },
            
            # SRC Secretary (3 candidates)
            {
                "name": "Chinwe Okafor",
                "position": "SRC Secretary",
                "faculty": "Arts and Communications",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Michael Adebayo",
                "position": "SRC Secretary",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Jennifer Musa",
                "position": "SRC Secretary",
                "faculty": "Management Science",
                "created_at": datetime.utcnow()
            },
            
            # Senate Members - Natural and Applied Science (4 candidates for 2 positions)
            {
                "name": "Emeka Nwosu",
                "position": "Senate Member - Natural and Applied Science",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Bisi Adekunle",
                "position": "Senate Member - Natural and Applied Science",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Tunde Ogunleye",
                "position": "Senate Member - Natural and Applied Science",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Ngozi Eze",
                "position": "Senate Member - Natural and Applied Science",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            
            # Senate Members - Management Science (4 candidates for 2 positions)
            {
                "name": "Oluwatoyin Bankole",
                "position": "Senate Member - Management Science",
                "faculty": "Management Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "James Okoro",
                "position": "Senate Member - Management Science",
                "faculty": "Management Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Patience Udoh",
                "position": "Senate Member - Management Science",
                "faculty": "Management Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Sunday Moses",
                "position": "Senate Member - Management Science",
                "faculty": "Management Science",
                "created_at": datetime.utcnow()
            },
            
            # Senate Members - Social Science (4 candidates for 2 positions)
            {
                "name": "Aisha Ibrahim",
                "position": "Senate Member - Social Science",
                "faculty": "Social Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Peter Okon",
                "position": "Senate Member - Social Science",
                "faculty": "Social Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Ruth Chukwu",
                "position": "Senate Member - Social Science",
                "faculty": "Social Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Daniel Akpan",
                "position": "Senate Member - Social Science",
                "faculty": "Social Science",
                "created_at": datetime.utcnow()
            },
            
            # Senate Members - Arts and Communications (4 candidates for 2 positions)
            {
                "name": "Chioma Nwankwo",
                "position": "Senate Member - Arts and Communications",
                "faculty": "Arts and Communications",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Kolawole Adeyemi",
                "position": "Senate Member - Arts and Communications",
                "faculty": "Arts and Communications",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Mercy Thompson",
                "position": "Senate Member - Arts and Communications",
                "faculty": "Arts and Communications",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Ibrahim Sani",
                "position": "Senate Member - Arts and Communications",
                "faculty": "Arts and Communications",
                "created_at": datetime.utcnow()
            },
            
            # Representative Members - Information (3 candidates)
            {
                "name": "Tech Savvy Smart",
                "position": "Information Representative",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Media Pro Grace",
                "position": "Information Representative",
                "faculty": "Arts and Communications",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Info King David",
                "position": "Information Representative",
                "faculty": "Arts and Communications",
                "created_at": datetime.utcnow()
            },
            
            # Representative Members - Social (3 candidates)
            {
                "name": "Social Butterfly Amina",
                "position": "Social Representative",
                "faculty": "Social Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Event Master Tunde",
                "position": "Social Representative",
                "faculty": "Management Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Party Planner Joy",
                "position": "Social Representative",
                "faculty": "Arts and Communications",
                "created_at": datetime.utcnow()
            },
            
            # Representative Members - Sports (3 candidates)
            {
                "name": "Sport Star Mike",
                "position": "Sports Representative",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Team Captain Bola",
                "position": "Sports Representative",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Fitness Queen Sarah",
                "position": "Sports Representative",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            
            # Representative Members - Security (3 candidates)
            {
                "name": "Safety First James",
                "position": "Security Representative",
                "faculty": "Social Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Campus Guard Faith",
                "position": "Security Representative",
                "faculty": "Social Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Watchful Eye Ken",
                "position": "Security Representative",
                "faculty": "Social Science",
                "created_at": datetime.utcnow()
            },
            
            # Representative Members - Transport (3 candidates)
            {
                "name": "Mobility Expert John",
                "position": "Transport Representative",
                "faculty": "Management Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Ride Master Peace",
                "position": "Transport Representative",
                "faculty": "Management Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Commute King Henry",
                "position": "Transport Representative",
                "faculty": "Management Science",
                "created_at": datetime.utcnow()
            },
            
            # Representative Members - Hostel 1 (3 candidates)
            {
                "name": "Dorm Leader Tina",
                "position": "Hostel 1 Representative",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Room Rep Ahmed",
                "position": "Hostel 1 Representative",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Hostel Hero Linda",
                "position": "Hostel 1 Representative",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            
            # Representative Members - Hostel 2 (3 candidates)
            {
                "name": "Accommodation Ace Paul",
                "position": "Hostel 2 Representative",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Dorm Chief Blessing",
                "position": "Hostel 2 Representative",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Hostel Head Victor",
                "position": "Hostel 2 Representative",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            
            # Representative Members - Chapel (3 candidates)
            {
                "name": "Spiritual Guide Peter",
                "position": "Chapel Representative",
                "faculty": "Arts and Communications",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Faith Leader Deborah",
                "position": "Chapel Representative",
                "faculty": "Arts and Communications",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Morality Mentor Joseph",
                "position": "Chapel Representative",
                "faculty": "Arts and Communications",
                "created_at": datetime.utcnow()
            }
        ]
        candidates_collection.insert_many(sample_candidates)
        print("✅ Comprehensive sample candidates added to MongoDB")
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
    """Get election statistics"""
    try:
        # Total registered voters
        total_voters = voters_collection.count_documents({'location_verified': True})
        
        # Total votes cast
        votes_cast = votes_collection.count_documents({})
        
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
    """Get list of all registered voters"""
    try:
        voters = list(voters_collection.find({}).sort('registration_date', -1))
        
        voters_list = []
        for voter in voters:
            voters_list.append({
                'matric_number': voter.get('matric_number', ''),
                'name': voter.get('name', ''),
                'email': voter.get('email', ''),
                'faculty': voter.get('faculty', ''),
                'location_verified': voter.get('location_verified', False),
                'has_voted': voter.get('has_voted', False),
                'ip_address': voter.get('ip_address', ''),
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
    """Export all election data"""
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

@app.route('/api/debug/fix-indexes', methods=['POST'])
@login_required
def fix_indexes():
    """Fix the problematic indexes"""
    try:
        # Remove the problematic unique index on voter_id alone
        votes_collection.drop_index('voter_id_1')
        print("✅ Removed problematic unique index on voter_id")
        
        # Ensure the compound index exists
        votes_collection.create_index([("voter_id", 1), ("candidate_position", 1)], unique=True, name="unique_vote_per_position")
        print("✅ Ensured compound unique index exists")
        
        # Recreate other necessary indexes
        votes_collection.create_index("candidate_id")
        print("✅ Recreated candidate_id index")
        
        return jsonify({
            'success': True,
            'message': 'Indexes fixed successfully!'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fixing indexes: {str(e)}'
        }), 500

# Fix for Render deployment - use PORT environment variable
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    print("🚀 Starting Admin Dashboard - Obong University SRC Elections")
    print(f"📊 Database: MongoDB - {DATABASE_NAME}")
    print("🔐 Admin Login required at: http://localhost:5002/admin/login")
    print("👤 Default credentials: admin / obonguni2025")
    print("✅ Database initialized successfully!")
    print("🌐 Admin Dashboard running at: http://localhost:5002")
    print("⚙️  Admins can control election status and monitor results")
    print("\n⏹️  Press Ctrl+C to stop the server")
    
    app.run(debug=False, host='0.0.0.0', port=port)