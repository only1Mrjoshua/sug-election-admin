from flask import Flask, request, jsonify, render_template, redirect, url_for, make_response
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
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'iauweiyvbiueyckuahsfdyrstvdKYWRIURIVTABSDFHCDVJQWT2648hfjbs'
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

# MongoDB configuration
username = "only1MrJoshua"
password = "LovuLord2025"
encoded_password = urllib.parse.quote_plus(password)

MONGO_URI = f"mongodb+srv://{username}:{encoded_password}@cluster0.9jqnavg.mongodb.net/election_db?retryWrites=true&w=majority&socketTimeoutMS=30000&connectTimeoutMS=30000&serverSelectionTimeoutMS=30000"
DATABASE_NAME = "election_db"

# Initialize MongoDB
try:
    client = MongoClient(
        MONGO_URI,
        maxPoolSize=50,
        retryWrites=True,
        retryReads=True
    )
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

@login_manager.unauthorized_handler
def unauthorized():
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'message': 'Authentication required',
            'login_required': True
        }), 401
    return redirect(url_for('serve_login'))

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "obonguni2025"
ADMIN_PASSWORD_HASH = bcrypt.hashpw(ADMIN_PASSWORD.encode('utf-8'), bcrypt.gensalt())

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(username):
    if username == ADMIN_USERNAME:
        return User(username)
    return None

def get_collection(collection_name):
    """Safely get collection reference"""
    if db is None:
        raise Exception("Database not connected")
    return db[collection_name]

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

        # Create indexes
        indexes_to_create = [
            (voters_collection, "voter_id", True),
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

        # Initialize sample voters with ID and name system
        if voters_collection.count_documents({}) == 0:
            sample_voters = [
                {
                    "voter_id": "V2024001",
                    "full_name": "John Chukwuma Adebayo",
                    "has_voted": False,
                    "registration_date": datetime.utcnow()
                },
                {
                    "voter_id": "V2024002", 
                    "full_name": "Grace Ngozi Okoro",
                    "has_voted": False,
                    "registration_date": datetime.utcnow()
                },
                {
                    "voter_id": "V2024003",
                    "full_name": "Michael Oluwaseun Bello",
                    "has_voted": False,
                    "registration_date": datetime.utcnow()
                },
                {
                    "voter_id": "V2024004",
                    "full_name": "Sarah Temitope Johnson",
                    "has_voted": False,
                    "registration_date": datetime.utcnow()
                },
                {
                    "voter_id": "V2024005",
                    "full_name": "David Ifeanyi Mohammed",
                    "has_voted": False,
                    "registration_date": datetime.utcnow()
                }
            ]
            voters_collection.insert_many(sample_voters)
            logger.info("✅ Sample voters added to database")

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
@app.route('/api/admin/login', methods=['POST', 'GET'])
def admin_login():
    """Admin login API"""
    try:
        if db is None:
            return jsonify({
                'success': False,
                'message': 'Database not connected'
            }), 500

        if request.method == 'GET':
            return jsonify({
                'success': True,
                'message': 'Login endpoint is reachable',
                'database_connected': db is not None
            })

        if not request.is_json:
            return jsonify({
                'success': False,
                'message': 'Request must be JSON'
            }), 400

        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Username and password are required'
            }), 400
        
        password_matches = bcrypt.checkpw(password.encode('utf-8'), ADMIN_PASSWORD_HASH)
        
        if username == ADMIN_USERNAME and password_matches:
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
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
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
    """Get list of all registered voters with ID and name system"""
    try:
        voters_collection = get_collection('voters')
        
        voters = list(voters_collection.find({}).sort('registration_date', -1))
        
        voters_list = []
        for voter in voters:
            voters_list.append({
                'voter_id': voter.get('voter_id', ''),
                'full_name': voter.get('full_name', ''),
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

@app.route('/api/votes/detailed', methods=['GET'])
@api_login_required
def get_detailed_votes():
    """Get detailed votes with voter information"""
    try:
        votes_collection = get_collection('votes')
        candidates_collection = get_collection('candidates')
        
        # Get all votes with voter details
        votes = list(votes_collection.find({}).sort('vote_date', -1))
        
        detailed_votes = []
        for vote in votes:
            candidate = candidates_collection.find_one({'_id': ObjectId(vote['candidate_id'])})
            detailed_votes.append({
                'voter_id': vote.get('voter_id', ''),
                'voter_name': vote.get('voter_name', ''),
                'candidate_name': vote.get('candidate_name', ''),
                'candidate_position': vote.get('candidate_position', ''),
                'vote_date': vote.get('vote_date', '').isoformat() if vote.get('vote_date') else '',
                'candidate_faculty': candidate.get('faculty', '') if candidate else ''
            })
        
        return jsonify({
            'success': True,
            'votes': detailed_votes
        })
        
    except Exception as e:
        logger.error(f"Detailed votes error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error fetching detailed votes: {str(e)}'
        }), 500

@app.route('/api/reports/votes-pdf', methods=['GET'])
@api_login_required
def generate_votes_pdf():
    """Generate PDF report of all votes organized by position and candidate"""
    try:
        votes_collection = get_collection('votes')
        candidates_collection = get_collection('candidates')
        
        # Get all votes grouped by position and candidate
        pipeline = [
            {
                '$group': {
                    '_id': {
                        'position': '$candidate_position',
                        'candidate_id': '$candidate_id',
                        'candidate_name': '$candidate_name'
                    },
                    'voters': {
                        '$push': {
                            'voter_id': '$voter_id',
                            'voter_name': '$voter_name'
                        }
                    },
                    'total_votes': {'$sum': 1}
                }
            },
            {
                '$sort': {'_id.position': 1, 'total_votes': -1}
            }
        ]
        
        votes_data = list(votes_collection.aggregate(pipeline))
        
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch)
        elements = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        # Title
        title = Paragraph("OBONG UNIVERSITY SRC ELECTION 2025 - VOTE REPORT", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        # Generate date
        date_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontSize=10,
            alignment=1
        )
        date_text = Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", date_style)
        elements.append(date_text)
        elements.append(Spacer(1, 0.3*inch))
        
        # Organize data by position
        positions_data = {}
        for item in votes_data:
            position = item['_id']['position']
            if position not in positions_data:
                positions_data[position] = []
            
            positions_data[position].append({
                'candidate_name': item['_id']['candidate_name'],
                'voters': item['voters'],
                'total_votes': item['total_votes']
            })
        
        # Create content for each position
        for position, candidates in positions_data.items():
            # Position header
            position_style = ParagraphStyle(
                'PositionStyle',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12,
                spaceBefore=20,
                textColor=colors.HexColor('#2c8a45')
            )
            position_title = Paragraph(f"Position: {position}", position_style)
            elements.append(position_title)
            
            for candidate in candidates:
                # Candidate header
                candidate_style = ParagraphStyle(
                    'CandidateStyle',
                    parent=styles['Heading3'],
                    fontSize=12,
                    spaceAfter=6,
                    spaceBefore=15
                )
                candidate_title = Paragraph(f"Candidate: {candidate['candidate_name']} - Total Votes: {candidate['total_votes']}", candidate_style)
                elements.append(candidate_title)
                
                # Voters table
                if candidate['voters']:
                    # Prepare table data
                    table_data = [['Voter ID', 'Voter Name']]
                    for voter in candidate['voters']:
                        table_data.append([voter['voter_id'], voter['voter_name']])
                    
                    # Create table
                    voter_table = Table(table_data, colWidths=[2*inch, 3*inch])
                    voter_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d13d39')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -1), 9),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    elements.append(voter_table)
                    elements.append(Spacer(1, 0.1*inch))
                else:
                    no_votes = Paragraph("No votes recorded for this candidate", styles['Normal'])
                    elements.append(no_votes)
                
                elements.append(Spacer(1, 0.2*inch))
            
            # Add page break after each position
            elements.append(Spacer(1, 0.3*inch))
        
        # Build PDF
        doc.build(elements)
        
        # Prepare response
        buffer.seek(0)
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=election-vote-report-{datetime.now().strftime("%Y%m%d")}.pdf'
        
        return response
        
    except Exception as e:
        logger.error(f"PDF generation error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error generating PDF report: {str(e)}'
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
    print(f"🌐 Server running on port: {port}")
    app.run(debug=False, host='0.0.0.0', port=port)