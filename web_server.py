#!/usr/bin/env python3
"""
Simple web server for Contra game demonstration.
Serves game information and status while running the game in background.
"""

from flask import Flask, render_template_string, jsonify
import subprocess
import threading
import time
import os
import sys

app = Flask(__name__)

# Game status tracking
game_status = {
    'running': False,
    'start_time': None,
    'error': None
}

# HTML template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contra Game - Cloud Deployment</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            color: #fff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            max-width: 800px;
            padding: 20px;
            text-align: center;
        }
        .header {
            background: rgba(0,0,0,0.3);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
        }
        .game-title {
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        .subtitle {
            font-size: 1.2em;
            opacity: 0.8;
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .info-card {
            background: rgba(255,255,255,0.1);
            padding: 25px;
            border-radius: 10px;
            backdrop-filter: blur(5px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .info-card h3 {
            color: #ffd700;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        .controls {
            background: rgba(0,0,0,0.2);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        .status {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            margin: 10px 0;
        }
        .status.running { background: #4CAF50; }
        .status.error { background: #f44336; }
        .tech-stack {
            display: flex;
            justify-content: center;
            gap: 15px;
            flex-wrap: wrap;
            margin: 20px 0;
        }
        .tech-item {
            background: rgba(255,255,255,0.1);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9em;
        }
        .footer {
            margin-top: 40px;
            opacity: 0.7;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="game-title">🎮 CONTRA</h1>
            <p class="subtitle">Classic Side-Scrolling Shooter - Cloud Edition</p>
            <div class="status running">Game Engine: Active</div>
        </div>

        <div class="info-grid">
            <div class="info-card">
                <h3>🎯 Game Features</h3>
                <p>• Classic Contra gameplay</p>
                <p>• Side-scrolling action</p>
                <p>• Enemy AI system</p>
                <p>• Power-ups & weapons</p>
                <p>• Multiple levels</p>
            </div>

            <div class="info-card">
                <h3>🎮 Controls</h3>
                <p><strong>Arrow Keys / WASD:</strong> Move</p>
                <p><strong>Space:</strong> Shoot</p>
                <p><strong>Ctrl / S:</strong> Duck</p>
                <p><strong>Up / W:</strong> Jump</p>
            </div>

            <div class="info-card">
                <h3>☁️ Cloud Deployment</h3>
                <p>• Google Cloud Platform</p>
                <p>• Docker containerized</p>
                <p>• Auto-scaling enabled</p>
                <p>• Health monitoring</p>
                <p>• Terraform managed</p>
            </div>
        </div>

        <div class="controls">
            <h3>🚀 Technical Implementation</h3>
            <div class="tech-stack">
                <span class="tech-item">Python 3.11</span>
                <span class="tech-item">Pygame 2.4.0</span>
                <span class="tech-item">Flask Web Server</span>
                <span class="tech-item">Docker</span>
                <span class="tech-item">GCP Compute Engine</span>
                <span class="tech-item">Terraform IaC</span>
            </div>
        </div>

        <div class="info-card">
            <h3>📊 System Status</h3>
            <p><strong>Game Engine:</strong> <span id="gameStatus">Running</span></p>
            <p><strong>Web Server:</strong> Active</p>
            <p><strong>Health Check:</strong> <a href="/health" style="color: #4CAF50;">/health</a></p>
            <p><strong>Deployment:</strong> Production Ready</p>
        </div>

        <div class="footer">
            <p>🎮 This is a demonstration of a pygame-based game deployed to the cloud</p>
            <p>The game runs in headless mode while this web interface provides information and monitoring</p>
        </div>
    </div>

    <script>
        // Auto-refresh game status
        setInterval(() => {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('gameStatus').textContent = 
                        data.game_running ? 'Running' : 'Stopped';
                })
                .catch(() => {
                    document.getElementById('gameStatus').textContent = 'Unknown';
                });
        }, 5000);
    </script>
</body>
</html>
'''

def run_game():
    """Run the game in background thread"""
    global game_status
    try:
        game_status['running'] = True
        game_status['start_time'] = time.time()
        game_status['error'] = None
        
        print("Starting Contra game in headless mode...")
        result = subprocess.run([sys.executable, 'main.py'], 
                              capture_output=True, text=True, timeout=None)
        
        if result.returncode != 0:
            game_status['error'] = f"Game exited with code {result.returncode}"
            print(f"Game stderr: {result.stderr}")
        
    except Exception as e:
        game_status['error'] = str(e)
        print(f"Error running game: {e}")
    finally:
        game_status['running'] = False

@app.route('/')
def index():
    """Main page showing game information"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    uptime = time.time() - game_status['start_time'] if game_status['start_time'] else 0
    return jsonify({
        'status': 'healthy',
        'service': 'contra-game-web',
        'game_running': game_status['running'],
        'uptime_seconds': round(uptime, 2),
        'error': game_status['error']
    })

@app.route('/api/status')
def api_status():
    """API endpoint for game status"""
    return jsonify({
        'game_running': game_status['running'],
        'start_time': game_status['start_time'],
        'error': game_status['error']
    })

if __name__ == '__main__':
    print("🎮 Starting Contra Game Web Server...")
    
    # Start game in background thread
    game_thread = threading.Thread(target=run_game, daemon=True)
    game_thread.start()
    
    # Give game a moment to start
    time.sleep(2)
    
    print("🌐 Web server starting on http://0.0.0.0:8080")
    print("📊 Health check available at /health")
    print("🎯 Game status API at /api/status")
    
    # Start Flask web server
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)