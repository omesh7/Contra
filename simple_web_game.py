#!/usr/bin/env python3
"""
Simple web-playable Contra-style game using Flask and HTML5 Canvas
This creates an actual playable game in the browser
"""

from flask import Flask, render_template_string, jsonify
import json

app = Flask(__name__)

def get_game_template():
    """Return the HTML5 Canvas game template"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contra Web Game</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            font-family: Arial, sans-serif;
        }
        .game-container {
            text-align: center;
            background: rgba(0,0,0,0.8);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 0 30px rgba(0,0,0,0.5);
        }
        canvas {
            border: 3px solid #ffd700;
            border-radius: 10px;
            background: #000;
        }
        .controls {
            margin-top: 20px;
            color: #fff;
        }
        .controls h3 {
            color: #ffd700;
            margin-bottom: 10px;
        }
        .score {
            color: #ffd700;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .game-over {
            color: #ff4444;
            font-size: 32px;
            font-weight: bold;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="game-container">
        <h1 style="color: #ffd700; margin-bottom: 20px;">🎮 CONTRA WEB</h1>
        <div class="score">Score: <span id="score">0</span></div>
        <canvas id="gameCanvas" width="800" height="600"></canvas>
        <div id="gameOver" class="game-over" style="display: none;">GAME OVER</div>
        <div class="controls">
            <h3>🎮 Controls</h3>
            <p><strong>WASD / Arrow Keys:</strong> Move</p>
            <p><strong>Space:</strong> Shoot</p>
            <p><strong>R:</strong> Restart Game</p>
        </div>
    </div>
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        let game = {
            player: { x: 50, y: 500, width: 30, height: 40, speed: 5, health: 3 },
            bullets: [],
            enemies: [],
            score: 0,
            gameOver: false,
            keys: {},
            lastEnemySpawn: 0
        };
        document.addEventListener('keydown', (e) => {
            game.keys[e.key.toLowerCase()] = true;
            if (e.key === ' ') {
                e.preventDefault();
                shoot();
            }
            if (e.key.toLowerCase() === 'r' && game.gameOver) {
                restartGame();
            }
        });
        document.addEventListener('keyup', (e) => {
            game.keys[e.key.toLowerCase()] = false;
        });
        function shoot() {
            if (!game.gameOver) {
                game.bullets.push({
                    x: game.player.x + game.player.width,
                    y: game.player.y + game.player.height / 2,
                    width: 10,
                    height: 4,
                    speed: 8
                });
            }
        }
        function spawnEnemy() {
            const now = Date.now();
            if (now - game.lastEnemySpawn > 2000) {
                game.enemies.push({
                    x: canvas.width,
                    y: Math.random() * (canvas.height - 100) + 50,
                    width: 25,
                    height: 30,
                    speed: 2 + Math.random() * 2,
                    health: 1
                });
                game.lastEnemySpawn = now;
            }
        }
        function updatePlayer() {
            if (game.gameOver) return;
            if (game.keys['a'] || game.keys['arrowleft']) {
                game.player.x = Math.max(0, game.player.x - game.player.speed);
            }
            if (game.keys['d'] || game.keys['arrowright']) {
                game.player.x = Math.min(canvas.width - game.player.width, game.player.x + game.player.speed);
            }
            if (game.keys['w'] || game.keys['arrowup']) {
                game.player.y = Math.max(0, game.player.y - game.player.speed);
            }
            if (game.keys['s'] || game.keys['arrowdown']) {
                game.player.y = Math.min(canvas.height - game.player.height, game.player.y + game.player.speed);
            }
        }
        function updateBullets() {
            game.bullets = game.bullets.filter(bullet => {
                bullet.x += bullet.speed;
                return bullet.x < canvas.width;
            });
        }
        function updateEnemies() {
            game.enemies = game.enemies.filter(enemy => {
                enemy.x -= enemy.speed;
                return enemy.x + enemy.width > 0 && enemy.health > 0;
            });
        }
        function checkCollisions() {
            game.bullets.forEach((bullet, bulletIndex) => {
                game.enemies.forEach((enemy, enemyIndex) => {
                    if (bullet.x < enemy.x + enemy.width &&
                        bullet.x + bullet.width > enemy.x &&
                        bullet.y < enemy.y + enemy.height &&
                        bullet.y + bullet.height > enemy.y) {
                        game.bullets.splice(bulletIndex, 1);
                        game.enemies.splice(enemyIndex, 1);
                        game.score += 10;
                        document.getElementById('score').textContent = game.score;
                    }
                });
            });
            game.enemies.forEach((enemy, enemyIndex) => {
                if (game.player.x < enemy.x + enemy.width &&
                    game.player.x + game.player.width > enemy.x &&
                    game.player.y < enemy.y + enemy.height &&
                    game.player.y + game.player.height > enemy.y) {
                    game.enemies.splice(enemyIndex, 1);
                    game.player.health--;
                    if (game.player.health <= 0) {
                        game.gameOver = true;
                        document.getElementById('gameOver').style.display = 'block';
                    }
                }
            });
        }
        function draw() {
            ctx.fillStyle = '#001122';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.strokeStyle = '#003344';
            ctx.lineWidth = 1;
            for (let i = 0; i < canvas.width; i += 50) {
                ctx.beginPath();
                ctx.moveTo(i, 0);
                ctx.lineTo(i, canvas.height);
                ctx.stroke();
            }
            for (let i = 0; i < canvas.height; i += 50) {
                ctx.beginPath();
                ctx.moveTo(0, i);
                ctx.lineTo(canvas.width, i);
                ctx.stroke();
            }
            ctx.fillStyle = '#00ff00';
            ctx.fillRect(game.player.x, game.player.y, game.player.width, game.player.height);
            ctx.fillStyle = '#ffff00';
            ctx.fillRect(game.player.x + 5, game.player.y + 5, 20, 10);
            ctx.fillRect(game.player.x + 25, game.player.y + 15, 10, 5);
            ctx.fillStyle = '#ffff00';
            game.bullets.forEach(bullet => {
                ctx.fillRect(bullet.x, bullet.y, bullet.width, bullet.height);
            });
            ctx.fillStyle = '#ff0000';
            game.enemies.forEach(enemy => {
                ctx.fillRect(enemy.x, enemy.y, enemy.width, enemy.height);
                ctx.fillStyle = '#ff4444';
                ctx.fillRect(enemy.x + 5, enemy.y + 5, 15, 8);
                ctx.fillStyle = '#ff0000';
            });
            ctx.fillStyle = '#ff0000';
            ctx.font = '20px Arial';
            ctx.fillText('Health: ' + '❤️'.repeat(game.player.health), 10, 30);
        }
        function gameLoop() {
            if (!game.gameOver) {
                spawnEnemy();
                updatePlayer();
                updateBullets();
                updateEnemies();
                checkCollisions();
            }
            draw();
            requestAnimationFrame(gameLoop);
        }
        function restartGame() {
            game = {
                player: { x: 50, y: 500, width: 30, height: 40, speed: 5, health: 3 },
                bullets: [],
                enemies: [],
                score: 0,
                gameOver: false,
                keys: {},
                lastEnemySpawn: 0
            };
            document.getElementById('score').textContent = '0';
            document.getElementById('gameOver').style.display = 'none';
        }
        gameLoop();
    </script>
</body>
</html>"""

@app.route('/')
def game():
    """Serve the playable web game"""
    return get_game_template()

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'contra-web-game',
        'game': 'playable'
    })

if __name__ == '__main__':
    print("🎮 Starting Contra Web Game Server...")
    print("🌐 Game available at http://0.0.0.0:8080")
    print("🎯 Fully playable in browser!")
    
    app.run(host='0.0.0.0', port=8080, debug=False)