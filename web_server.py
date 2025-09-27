#!/usr/bin/env python3
"""
Web server for Contra game - now with playable web version!
Serves the actual game using pygame-web (pygbag) for browser play.
"""

from flask import Flask, render_template_string, jsonify, send_from_directory
import subprocess
import threading
import time
import os
import sys
import shutil

app = Flask(__name__)

# Game status tracking
game_status = {
    'running': False,
    'start_time': None,
    'error': None,
    'web_build_ready': False
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
            <p class="subtitle">Classic Side-Scrolling Shooter - Playable Web Edition</p>
            <div class="status running">🕹️ Click to Play Below!</div>
        </div>

        <!-- Game Canvas Container -->
        <div class="game-container" style="background: #000; border-radius: 10px; padding: 20px; margin: 20px 0;">
            <div id="gameframe" style="text-align: center;">
                <h3 style="color: #ffd700;">🎮 Loading Contra Game...</h3>
                <p>The game is being prepared for web play. This may take a moment.</p>
                <div style="margin: 20px 0;">
                    <div style="display: inline-block; width: 200px; height: 4px; background: #333; border-radius: 2px;">
                        <div id="loadingBar" style="width: 0%; height: 100%; background: #4CAF50; border-radius: 2px; transition: width 0.3s;"></div>
                    </div>
                </div>
                <iframe id="gameIframe" src="/game" width="800" height="600" style="border: none; display: none; border-radius: 5px;"></iframe>
            </div>
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

def build_web_game():
    """Build the game for web using pygbag"""
    global game_status
    try:
        print("🔨 Building Contra game for web...")
        game_status['running'] = True
        game_status['start_time'] = time.time()
        game_status['error'] = None
        
        # Create dist directory if it doesn't exist
        os.makedirs('dist', exist_ok=True)
        
        # Build the game using pygbag with minimal arguments
        result = subprocess.run([
            sys.executable, '-m', 'pygbag',
            '--width', '800',
            '--height', '600',
            'main_web.py'
        ], capture_output=True, text=True, timeout=300)  # 5 minute timeout
        
        if result.returncode == 0:
            game_status['web_build_ready'] = True
            print("✅ Web game build completed successfully!")
        else:
            game_status['error'] = f"Build failed: {result.stderr}"
            print(f"❌ Build error: {result.stderr}")
        
    except subprocess.TimeoutExpired:
        game_status['error'] = "Build timeout - taking too long"
        print("⏰ Build timed out")
    except Exception as e:
        game_status['error'] = str(e)
        print(f"❌ Build error: {e}")
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
        'web_build_ready': game_status['web_build_ready'],
        'start_time': game_status['start_time'],
        'error': game_status['error']
    })

@app.route('/game')
def serve_game():
    """Serve the web game"""
    if game_status['web_build_ready'] and os.path.exists('dist/contra.html'):
        return send_from_directory('dist', 'contra.html')
    else:
        return '''
        <html>
        <body style="background: #000; color: #fff; font-family: Arial; text-align: center; padding: 50px;">
            <h2>🎮 Game is Building...</h2>
            <p>The web version is being prepared. Please wait a moment and refresh.</p>
            <script>setTimeout(() => location.reload(), 5000);</script>
        </body>
        </html>
        '''

@app.route('/dist/<path:filename>')
def serve_game_assets(filename):
    """Serve game assets"""
    return send_from_directory('dist', filename)

if __name__ == '__main__':
    print("🎮 Starting Contra Web Game Server...")
    
    # Start web game build in background thread
    build_thread = threading.Thread(target=build_web_game, daemon=True)
    build_thread.start()
    
    print("🌐 Web server starting on http://0.0.0.0:8080")
    print("🎮 Game will be available at /game once build completes")
    print("📊 Health check available at /health")
    print("🎯 Game status API at /api/status")
    
    # Start Flask web server
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)