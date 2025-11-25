from flask import Flask, request, jsonify
from shared_database import init_db
import sqlite3

app = Flask(__name__)
DATABASE = 'election.db'

# Initialize database
init_db()

@app.route('/')
def admin_home():
    """Admin dashboard home page"""
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Admin Dashboard - Obong University SRC Elections</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #D13D39 0%, #b32b2b 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            
            .header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                background: white;
                padding: 20px;
                border-radius: 15px 15px 0 0;
                margin-bottom: 0;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }
            
            .university-info h1 {
                color: #D13D39;
                font-size: 1.8rem;
                margin-bottom: 5px;
                font-weight: 700;
            }
            
            .university-info .subtitle {
                color: #2C8A45;
                font-size: 1.1rem;
                font-weight: 600;
            }
            
            .admin-badge {
                background: #D13D39;
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: 600;
                font-size: 0.9rem;
            }
            
            .card {
                background: white;
                border-radius: 0 0 15px 15px;
                padding: 30px;
                margin-bottom: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            
            .tabs {
                display: flex;
                margin-bottom: 20px;
                background: #f8f9fa;
                border-radius: 10px;
                padding: 5px;
                border: 2px solid #D13D39;
            }
            
            .tab {
                flex: 1;
                padding: 15px;
                text-align: center;
                cursor: pointer;
                border-radius: 8px;
                transition: all 0.3s ease;
                font-weight: 600;
                color: #D13D39;
            }
            
            .tab.active {
                background: #D13D39;
                color: white;
            }
            
            .tab:hover:not(.active) {
                background: #EBBF00;
                color: black;
            }
            
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }
            
            .stat-card {
                background: linear-gradient(135deg, #D13D39 0%, #2C8A45 100%);
                color: white;
                padding: 25px;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }
            
            .stat-number {
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 5px;
            }
            
            .stat-label {
                font-size: 1rem;
                opacity: 0.9;
            }
            
            .btn {
                background: linear-gradient(135deg, #D13D39 0%, #E74C3C 100%);
                color: white;
                border: none;
                padding: 16px 30px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin: 10px 5px;
            }
            
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(209, 61, 57, 0.4);
            }
            
            .hidden {
                display: none;
            }
            
            .results-grid {
                display: grid;
                gap: 20px;
                margin-top: 20px;
            }
            
            .position-group {
                background: #f8f9fa;
                border: 2px solid #EBBF00;
                border-radius: 10px;
                padding: 20px;
            }
            
            .position-title {
                color: #D13D39;
                font-size: 1.3rem;
                font-weight: 700;
                margin-bottom: 15px;
                border-bottom: 2px solid #EBBF00;
                padding-bottom: 10px;
            }
            
            .candidate-item {
                background: white;
                border: 2px solid #2C8A45;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 10px;
                transition: all 0.3s ease;
            }
            
            .candidate-item.winner {
                background: linear-gradient(135deg, #2C8A45 0%, #4CAF50 100%);
                color: white;
                border-color: #2C8A45;
            }
            
            .candidate-name {
                font-weight: 600;
                font-size: 1.1rem;
            }
            
            .candidate-votes {
                color: #D13D39;
                font-weight: 600;
                margin-top: 5px;
            }
            
            .candidate-item.winner .candidate-votes {
                color: #EBBF00;
            }
            
            .voters-list {
                max-height: 400px;
                overflow-y: auto;
                margin-top: 20px;
            }
            
            .voter-item {
                background: #f8f9fa;
                border: 1px solid #EBBF00;
                border-radius: 6px;
                padding: 12px;
                margin-bottom: 8px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .voter-info {
                flex: 1;
            }
            
            .voter-status {
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 0.8rem;
                font-weight: 600;
            }
            
            .status-verified {
                background: #2C8A45;
                color: white;
            }
            
            .status-pending {
                background: #EBBF00;
                color: black;
            }
            
            .footer {
                text-align: center;
                color: white;
                margin-top: 30px;
                padding: 20px;
                font-size: 0.9rem;
                opacity: 0.8;
            }
            
            @media (max-width: 768px) {
                .container {
                    padding: 10px;
                }
                
                .header {
                    flex-direction: column;
                    text-align: center;
                    gap: 15px;
                }
                
                .tabs {
                    flex-direction: column;
                }
                
                .tab {
                    margin-bottom: 5px;
                }
                
                .stats {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="university-info">
                    <h1>OBONG UNIVERSITY</h1>
                    <div class="subtitle">Admin Dashboard - SRC Elections 2024</div>
                </div>
                <div class="admin-badge">🔐 ADMIN ACCESS</div>
            </div>
            
            <div class="card">
                <div class="tabs">
                    <div class="tab active" onclick="showTab('results')">📊 Live Results</div>
                    <div class="tab" onclick="showTab('dashboard')">📈 Election Dashboard</div>
                    <div class="tab" onclick="showTab('voters')">👥 Registered Voters</div>
                </div>
                
                <!-- Results Tab -->
                <div id="results-tab" class="tab-content">
                    <h2 style="color: #D13D39; margin-bottom: 20px;">Live Election Results</h2>
                    <p style="margin-bottom: 20px; color: #666;">
                        Real-time election results as votes are being cast.
                    </p>
                    
                    <button class="btn" onclick="loadResults()">🔄 Refresh Results</button>
                    
                    <div id="results-container" class="results-grid">
                        <div style="text-align: center; padding: 40px; color: #666;">
                            <div style="font-size: 3rem; margin-bottom: 20px;">📈</div>
                            <h3 style="color: #2C8A45;">Loading Results...</h3>
                            <p>Election results will be displayed here.</p>
                        </div>
                    </div>
                </div>
                
                <!-- Dashboard Tab -->
                <div id="dashboard-tab" class="tab-content hidden">
                    <h2 style="color: #D13D39; margin-bottom: 20px;">Election Dashboard</h2>
                    <p style="margin-bottom: 20px; color: #666;">
                        Overview of election statistics and system status.
                    </p>
                    
                    <div class="stats">
                        <div class="stat-card">
                            <div class="stat-number" id="total-voters">0</div>
                            <div class="stat-label">Registered Voters</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number" id="total-votes">0</div>
                            <div class="stat-label">Votes Cast</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number" id="turnout-rate">0%</div>
                            <div class="stat-label">Voter Turnout</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number" id="verified-voters">0</div>
                            <div class="stat-label">Location Verified</div>
                        </div>
                    </div>
                    
                    <button class="btn" onclick="loadStats()">🔄 Refresh Statistics</button>
                    
                    <div style="margin-top: 30px;">
                        <h3 style="color: #2C8A45; margin-bottom: 15px;">System Information</h3>
                        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; border: 2px solid #EBBF00;">
                            <p><strong>Server Status:</strong> <span style="color: #2C8A45;">● Online</span></p>
                            <p><strong>Database:</strong> <span style="color: #2C8A45;">● Connected</span></p>
                            <p><strong>Last Update:</strong> <span id="last-update">Just now</span></p>
                        </div>
                    </div>
                </div>
                
                <!-- Voters Tab -->
                <div id="voters-tab" class="tab-content hidden">
                    <h2 style="color: #D13D39; margin-bottom: 20px;">Registered Voters</h2>
                    <p style="margin-bottom: 20px; color: #666;">
                        List of all registered voters and their verification status.
                    </p>
                    
                    <button class="btn" onclick="loadVoters()">🔄 Refresh Voter List</button>
                    
                    <div id="voters-container" class="voters-list">
                        <!-- Voters will be loaded here -->
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <p>Obong University SRC Election System 2024 • Admin Dashboard</p>
                <p>Restricted Access - Authorized Personnel Only</p>
            </div>
        </div>

        <script>
            const API_BASE = '/api';
            
            function showTab(tabName) {
                // Hide all tabs
                document.querySelectorAll('.tab-content').forEach(tab => {
                    tab.classList.add('hidden');
                });
                
                // Remove active class from all tabs
                document.querySelectorAll('.tab').forEach(tab => {
                    tab.classList.remove('active');
                });
                
                // Show selected tab
                document.getElementById(`${tabName}-tab`).classList.remove('hidden');
                
                // Add active class to clicked tab
                event.target.classList.add('active');
                
                // Load data for specific tabs
                if (tabName === 'results') {
                    loadResults();
                } else if (tabName === 'dashboard') {
                    loadStats();
                } else if (tabName === 'voters') {
                    loadVoters();
                }
            }
            
            // Load results
            async function loadResults() {
                try {
                    const response = await fetch(API_BASE + '/results');
                    const result = await response.json();
                    
                    if (result.success) {
                        const container = document.getElementById('results-container');
                        container.innerHTML = '';
                        
                        // Group by position
                        const positions = {};
                        result.results.forEach(candidate => {
                            if (!positions[candidate.position]) {
                                positions[candidate.position] = [];
                            }
                            positions[candidate.position].push(candidate);
                        });
                        
                        // Find winners and create results
                        for (const [position, candidates] of Object.entries(positions)) {
                            const positionGroup = document.createElement('div');
                            positionGroup.className = 'position-group';
                            
                            // Find winner (most votes)
                            const winner = candidates.reduce((prev, current) => 
                                (prev.votes > current.votes) ? prev : current
                            );
                            
                            let positionHTML = `<div class="position-title">${position}</div>`;
                            
                            candidates.sort((a, b) => b.votes - a.votes).forEach(candidate => {
                                const isWinner = candidate.votes === winner.votes && candidate.votes > 0;
                                positionHTML += `
                                    <div class="candidate-item ${isWinner ? 'winner' : ''}">
                                        <div class="candidate-name">${candidate.name}</div>
                                        <div class="candidate-department">${candidate.department || ''}</div>
                                        <div class="candidate-votes">Votes: ${candidate.votes}</div>
                                        ${isWinner ? '<div style="color: #EBBF00; font-weight: 600;">🏆 LEADING</div>' : ''}
                                    </div>
                                `;
                            });
                            
                            positionGroup.innerHTML = positionHTML;
                            container.appendChild(positionGroup);
                        }
                        
                        document.getElementById('last-update').textContent = new Date().toLocaleString();
                    }
                } catch (error) {
                    console.error('Error loading results:', error);
                }
            }
            
            // Load statistics
            async function loadStats() {
                try {
                    const response = await fetch(API_BASE + '/stats');
                    const result = await response.json();
                    
                    if (result.success) {
                        document.getElementById('total-voters').textContent = result.stats.total_registered_voters;
                        document.getElementById('total-votes').textContent = result.stats.votes_cast;
                        
                        // Calculate turnout percentage
                        const turnout = result.stats.total_registered_voters > 0 
                            ? Math.round((result.stats.votes_cast / result.stats.total_registered_voters) * 100)
                            : 0;
                        document.getElementById('turnout-rate').textContent = turnout + '%';
                        
                        document.getElementById('verified-voters').textContent = result.stats.total_registered_voters;
                        document.getElementById('last-update').textContent = new Date().toLocaleString();
                    }
                } catch (error) {
                    console.error('Error loading stats:', error);
                }
            }
            
            // Load voters list
            async function loadVoters() {
                try {
                    const response = await fetch(API_BASE + '/voters');
                    const result = await response.json();
                    
                    if (result.success) {
                        const container = document.getElementById('voters-container');
                        container.innerHTML = '';
                        
                        if (result.voters.length === 0) {
                            container.innerHTML = '<p style="text-align: center; color: #666; padding: 40px;">No voters registered yet.</p>';
                            return;
                        }
                        
                        result.voters.forEach(voter => {
                            const voterItem = document.createElement('div');
                            voterItem.className = 'voter-item';
                            voterItem.innerHTML = `
                                <div class="voter-info">
                                    <strong>${voter.name}</strong><br>
                                    <small>ID: ${voter.student_id} | Email: ${voter.email}</small>
                                </div>
                                <div class="voter-status ${voter.location_verified ? 'status-verified' : 'status-pending'}">
                                    ${voter.location_verified ? '✓ Verified' : 'Pending'}
                                </div>
                            `;
                            container.appendChild(voterItem);
                        });
                    }
                } catch (error) {
                    console.error('Error loading voters:', error);
                }
            }
            
            // Initialize the page
            document.addEventListener('DOMContentLoaded', () => {
                loadResults();
                loadStats();
            });
            
            // Auto-refresh results every 30 seconds
            setInterval(loadResults, 30000);
        </script>
    </body>
    </html>
    '''

# Admin API Routes
@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get election statistics"""
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Total registered voters
        c.execute('SELECT COUNT(*) FROM voters WHERE location_verified = 1')
        total_voters = c.fetchone()[0]
        
        # Total votes cast
        c.execute('SELECT COUNT(*) FROM votes')
        votes_cast = c.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_registered_voters': total_voters,
                'votes_cast': votes_cast
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching stats: {str(e)}'
        }), 500

@app.route('/api/results', methods=['GET'])
def get_results():
    """Get election results"""
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        c.execute('''
            SELECT c.id, c.name, c.position, c.department, COUNT(v.id) as vote_count
            FROM candidates c
            LEFT JOIN votes v ON c.id = v.candidate_id
            GROUP BY c.id, c.name, c.position, c.department
            ORDER BY c.position, vote_count DESC
        ''')
        
        results = c.fetchall()
        conn.close()
        
        results_list = []
        for result in results:
            results_list.append({
                'id': result[0],
                'name': result[1],
                'position': result[2],
                'department': result[3],
                'votes': result[4]
            })
        
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
def get_voters():
    """Get list of all registered voters"""
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('SELECT student_id, name, email, location_verified FROM voters ORDER BY registration_date DESC')
        voters = c.fetchall()
        conn.close()
        
        voters_list = []
        for voter in voters:
            voters_list.append({
                'student_id': voter[0],
                'name': voter[1],
                'email': voter[2],
                'location_verified': bool(voter[3])
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

if __name__ == '__main__':
    print("🚀 Starting Admin Dashboard - Obong University SRC Elections")
    print("✅ Database initialized successfully!")
    print("🌐 Admin Dashboard running at: http://localhost:5002")
    print("⚙️  Admins can monitor results and statistics at this portal")
    print("\n⏹️  Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=5002)