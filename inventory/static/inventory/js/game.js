/**
 * NetDevFlow Easter Egg Game
 * Flappy Server game implementation
 */

window.addEventListener('DOMContentLoaded', () => {
    // Easter Egg Logic
    const trigger = document.getElementById('egg-trigger');
    const eggContainer = document.getElementById('easter-egg-container');
    const canvas = document.getElementById('game-canvas');
    
    if (!trigger || !eggContainer || !canvas) {
        return; // Elements don't exist on this page
    }

    const ctx = canvas.getContext('2d');
    const startBtn = document.getElementById('start-game');
    const gameUI = document.getElementById('game-ui');

    if (trigger) {
        trigger.onclick = () => {
            eggContainer.style.display = 'block';
            eggContainer.scrollIntoView({ behavior: 'smooth' });
        };
    }

    // Flappy Server Game
    let gameRunning = false;
    let score = 0;
    let server = { x: 50, y: 250, velocity: 0, gravity: 0.25, jump: -5, size: 30 };
    let pipes = [];
    let frame = 0;

    function initGame() {
        score = 0;
        server.y = 250;
        server.velocity = 0;
        pipes = [];
        frame = 0;
        gameRunning = true;
        gameUI.style.display = 'none';
        loop();
    }

    function drawServer() {
        ctx.font = '30px serif';
        ctx.fillText('🖥️', server.x, server.y + 10);
    }

    function drawPipes() {
        pipes.forEach(pipe => {
            ctx.fillStyle = '#adb5bd';
            // Draw Upper Rack
            ctx.fillRect(pipe.x, 0, 50, pipe.top);
            ctx.fillStyle = '#6c757d';
            ctx.fillRect(pipe.x + 5, 0, 40, pipe.top);
            
            // Draw Lower Rack
            ctx.fillStyle = '#adb5bd';
            ctx.fillRect(pipe.x, pipe.bottom, 50, canvas.height - pipe.bottom);
            ctx.fillStyle = '#6c757d';
            ctx.fillRect(pipe.x + 5, pipe.bottom, 40, canvas.height - pipe.bottom);

            // Add some "cloud" aesthetics
            ctx.font = '20px serif';
            ctx.fillText('☁️', pipe.x - 20, pipe.top - 20);
            ctx.fillText('☁️', pipe.x + 30, pipe.bottom + 40);
        });
    }

    function update() {
        server.velocity += server.gravity;
        server.y += server.velocity;

        if (frame % 100 === 0) {
            const gap = 150;
            const top = Math.random() * (canvas.height - gap - 100) + 50;
            pipes.push({ x: canvas.width, top: top, bottom: top + gap });
        }

        pipes.forEach(pipe => {
            pipe.x -= 2;
            // Collision
            if (server.x + 20 > pipe.x && server.x < pipe.x + 50) {
                if (server.y < pipe.top || server.y + 20 > pipe.bottom) {
                    gameOver();
                }
            }
            if (pipe.x === 50) score++;
        });

        pipes = pipes.filter(p => p.x > -50);

        if (server.y > canvas.height || server.y < 0) {
            gameOver();
        }
    }

    function gameOver() {
        gameRunning = false;
        gameUI.innerHTML = `<h3 class="fw-bold">Connection Lost!</h3><p>Score: ${score}</p><button class="btn btn-light btn-sm mt-2 rounded-pill px-4" id="restart-game">Reboot</button>`;
        gameUI.style.display = 'block';
        document.getElementById('restart-game').onclick = initGame;
    }

    function loop() {
        if (!gameRunning) return;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Draw background pattern (grid)
        ctx.strokeStyle = 'rgba(255,255,255,0.05)';
        for(let i=0; i<canvas.width; i+=20) {
            ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, canvas.height); ctx.stroke();
        }
        for(let i=0; i<canvas.height; i+=20) {
            ctx.beginPath(); ctx.moveTo(0, i); ctx.lineTo(canvas.width, i); ctx.stroke();
        }

        update();
        drawPipes();
        drawServer();
        
        ctx.fillStyle = 'white';
        ctx.font = 'bold 20px sans-serif';
        ctx.fillText(`Uptime: ${score}s`, 20, 40);
        
        frame++;
        requestAnimationFrame(loop);
    }

    function jump() {
        if (gameRunning) server.velocity = server.jump;
    }

    if (startBtn) startBtn.onclick = initGame;
    if (canvas) canvas.onclick = jump;
    window.onkeydown = (e) => { if (e.code === 'Space') jump(); };
});
