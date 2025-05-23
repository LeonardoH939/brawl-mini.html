# brawl-mini.html

<!DOCTYPE html>
<html lang="pt">
<head>
  <meta charset="UTF-8" />
  <title>Mini Brawl Stars</title>
  <style>
    canvas { background: #222; display: block; margin: auto; }
  </style>
</head>
<body>
<canvas id="gameCanvas" width="800" height="600"></canvas>
<script>
  const canvas = document.getElementById("gameCanvas");
  const ctx = canvas.getContext("2d");

  const player = {
    x: 400,
    y: 300,
    size: 30,
    speed: 4,
    bullets: []
  };

  const keys = {};
  const enemies = [];

  for (let i = 0; i < 5; i++) {
    enemies.push({
      x: Math.random() * 700 + 50,
      y: Math.random() * 500 + 50,
      size: 30,
      speed: 1.5
    });
  }

  document.addEventListener("keydown", e => keys[e.key] = true);
  document.addEventListener("keyup", e => keys[e.key] = false);
  canvas.addEventListener("click", e => {
    const rect = canvas.getBoundingClientRect();
    const angle = Math.atan2(e.clientY - rect.top - player.y, e.clientX - rect.left - player.x);
    player.bullets.push({
      x: player.x,
      y: player.y,
      dx: Math.cos(angle) * 6,
      dy: Math.sin(angle) * 6,
      size: 6
    });
  });

  function update() {
    if (keys["w"]) player.y -= player.speed;
    if (keys["s"]) player.y += player.speed;
    if (keys["a"]) player.x -= player.speed;
    if (keys["d"]) player.x += player.speed;

    // Atualizar balas
    player.bullets.forEach((b, i) => {
      b.x += b.dx;
      b.y += b.dy;

      // Remover se sair da tela
      if (b.x < 0 || b.x > 800 || b.y < 0 || b.y > 600) {
        player.bullets.splice(i, 1);
      }
    });

    // Atualizar inimigos
    enemies.forEach((enemy, i) => {
      const angle = Math.atan2(player.y - enemy.y, player.x - enemy.x);
      enemy.x += Math.cos(angle) * enemy.speed;
      enemy.y += Math.sin(angle) * enemy.speed;

      // Colisão com bala
      player.bullets.forEach((b, j) => {
        const dx = b.x - enemy.x;
        const dy = b.y - enemy.y;
        const dist = Math.sqrt(dx*dx + dy*dy);
        if (dist < enemy.size/2 + b.size/2) {
          enemies.splice(i, 1);
          player.bullets.splice(j, 1);
        }
      });
    });
  }

  function draw() {
    ctx.clearRect(0, 0, 800, 600);

    // Jogador
    ctx.fillStyle = "cyan";
    ctx.beginPath();
    ctx.arc(player.x, player.y, player.size/2, 0, Math.PI * 2);
    ctx.fill();

    // Balas
    ctx.fillStyle = "yellow";
    player.bullets.forEach(b => {
      ctx.beginPath();
      ctx.arc(b.x, b.y, b.size/2, 0, Math.PI * 2);
      ctx.fill();
    });

    // Inimigos
    ctx.fillStyle = "red";
    enemies.forEach(e => {
      ctx.beginPath();
      ctx.arc(e.x, e.y, e.size/2, 0, Math.PI * 2);
      ctx.fill();
    });
  }

  function gameLoop() {
    update();
    draw();
    requestAnimationFrame(gameLoop);
  }

  gameLoop();
</script>
</body>
</html>
