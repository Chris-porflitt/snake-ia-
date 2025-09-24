# snake_agent.py
import sys, time, random, heapq, collections
import pygame
from time import perf_counter

# ================== Parámetros del juego ==================
GRID_W = 10
GRID_H = 10
CELL   = 40
WINDOW_W, WINDOW_H = GRID_W * CELL, GRID_H * CELL

SNAKE_SPEED = 12          # FPS
MAX_APPLES  = 35
SEED        = int(time.time())   # fija a 1234 p/ reproducibilidad
random.seed(SEED)

# Colores
BLACK = pygame.Color(0,0,0)
WHITE = pygame.Color(255,255,255)
RED   = pygame.Color(255,0,0)
GREEN = pygame.Color(0,255,0)

# Movimientos en grilla (U, R, D, L)
DIRS = [(0,-1),(1,0),(0,1),(-1,0)]

# ================== Utilidades de render ==================
def to_rect(cell_pos):
    x, y = cell_pos
    return pygame.Rect(x*CELL, y*CELL, CELL, CELL)

def valid(p):
    x, y = p
    return 0 <= x < GRID_W and 0 <= y < GRID_H

def draw_text(surface, text, x, y, color=WHITE, size=20, center=False):
    font = pygame.font.SysFont('times new roman', size)
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(surf, rect)

# ================== Búsqueda: UCS ==================
def ucs(start, goal, blocked):
    """Uniform Cost Search (costo unitario).
       Devuelve ruta SIN incluir start, SÍ incluyendo goal. [] si no hay."""
    if start == goal:
        return []

    frontier = []
    heapq.heappush(frontier, (0, start))
    came = {start: None}
    g    = {start: 0}

    while frontier:
        cost, u = heapq.heappop(frontier)
        if u == goal:
            # reconstruir
            path = []
            cur = u
            while came[cur] is not None:
                path.append(cur)
                cur = came[cur]
            path.reverse()
            return path

        for dx, dy in DIRS:
            v = (u[0]+dx, u[1]+dy)
            if not valid(v) or v in blocked:
                continue
            new_g = g[u] + 1
            if v not in g or new_g < g[v]:
                g[v] = new_g
                came[v] = u
                heapq.heappush(frontier, (new_g, v))
    return []

# ================== Heurísticas de seguridad ==================
def flood_reachable(start, blocked):
    """Cuenta cuántas celdas libres son alcanzables desde start (BFS)."""
    if start in blocked or not valid(start):
        return 0
    q = collections.deque([start])
    seen = {start}
    while q:
        u = q.popleft()
        for dx, dy in DIRS:
            v = (u[0]+dx, u[1]+dy)
            if valid(v) and v not in blocked and v not in seen:
                seen.add(v); q.append(v)
    return len(seen)

def simulate_until_eat_and_check_escape(snake, path_to_fruit):
    """
    Simula recorrer path_to_fruit:
      - si el paso es fruta: crece (no se mueve la cola) y se detiene la simulación
      - si no: mueve cabeza y cola.
    Luego verifica que exista camino cabeza -> cola con UCS (bloqueando el cuerpo intermedio).
    Retorna True si hay escape; False si no.
    """
    if not path_to_fruit:
        return False

    sim = list(snake)  # copia
    fruit = path_to_fruit[-1]
    ate = False
    for step in path_to_fruit:
        sim.insert(0, step)     # mover cabeza
        if step == fruit:
            ate = True
            break               # al comer, no se mueve la cola
        else:
            sim.pop()           # mover cola

    if not ate:
        return False

    head_sim, tail_sim = sim[0], sim[-1]
    blocked = set(sim[1:-1])     # bloquea cuerpo salvo cabeza y cola
    escape_path = ucs(head_sim, tail_sim, blocked)
    return bool(escape_path)

def best_safe_neighbor(head, snake, fruit):
    """
    Elige el vecino que maximiza espacio alcanzable en el SIGUIENTE estado:
      - si el vecino es la fruta: no mover cola en ese paso
      - si no: mover cola normal
    """
    best_v, best_score = None, -1
    for dx, dy in DIRS:
        v = (head[0]+dx, head[1]+dy)
        if not valid(v):
            continue
        if v in snake[1:]:   # chocar con el cuerpo (excepto la cabeza actual)
            continue

        # Simular siguiente estado mínimo
        sim = list(snake)
        sim.insert(0, v)
        if v != fruit:       # si no comes, se mueve la cola
            sim.pop()

        blocked = set(sim[1:])  # bloquea cuerpo salvo cabeza
        score = flood_reachable(sim[0], blocked)
        if score > best_score:
            best_score = score
            best_v = v
    return best_v

# ================== Lógica del juego ==================
def generate_fruit(snake_body):
    while True:
        p = (random.randrange(0, GRID_W), random.randrange(0, GRID_H))
        if p not in snake_body:
            return p

def any_safe_step(head, blocked):
    """Vecino libre cualquiera (último recurso básico)."""
    for dx, dy in DIRS:
        v = (head[0]+dx, head[1]+dy)
        if valid(v) and v not in blocked:
            return v
    return None

def game_over(screen, apples, steps, elapsed_s, plan_time_s, seed, success):
    screen.fill(BLACK)
    title = "¡Éxito!" if success else "Game Over"
    draw_text(screen, title, WINDOW_W//2, WINDOW_H//2 - 60, RED, 40, center=True)
    draw_text(screen, f"Score (manzanas): {apples}", WINDOW_W//2, WINDOW_H//2 - 10, WHITE, 24, center=True)
    draw_text(screen, f"Movimientos: {steps}",       WINDOW_W//2, WINDOW_H//2 + 20, WHITE, 24, center=True)
    draw_text(screen, f"Tiempo total: {elapsed_s:.3f}s", WINDOW_W//2, WINDOW_H//2 + 50, WHITE, 24, center=True)
    draw_text(screen, f"Tiempo planificación (UCS): {plan_time_s*1000:.1f} ms", WINDOW_W//2, WINDOW_H//2 + 80, WHITE, 24, center=True)
    draw_text(screen, f"Seed: {seed}", WINDOW_W//2, WINDOW_H//2 + 110, WHITE, 18, center=True)
    pygame.display.flip()

    time.sleep(2.0)
    pygame.quit()
    sys.exit(0)

def main():
    pygame.init()
    pygame.display.set_caption('Snake UCS – 10x10 (Safe)')
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    clock = pygame.time.Clock()

    # Estado inicial: largo mínimo 3
    snake = [(3,5), (2,5), (1,5)]  # cabeza = snake[0]
    head  = snake[0]
    fruit = generate_fruit(snake)

    apples = 0
    steps  = 0

    run_start     = perf_counter()
    plan_time_acc = 0.0

    while True:
        # Eventos
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit(0)
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit(0)

        # ===== Plan 1: UCS a la fruta con bloqueos completos
        t0 = perf_counter()
        path = ucs(head, fruit, set(snake[1:]))
        plan_time_acc += (perf_counter() - t0)

        # ===== Plan 2: Relajar liberando la cola (se moverá si NO comes)
        if not path:
            t0 = perf_counter()
            path = ucs(head, fruit, set(snake[1:-1]))
            plan_time_acc += (perf_counter() - t0)

        # ===== Filtro de seguridad: ¿hay escape tras comer?
        if path:
            if not simulate_until_eat_and_check_escape(snake, path):
                # No comer aún: seguir cola en su lugar
                t0 = perf_counter()
                path_tail = ucs(head, snake[-1], set(snake[1:-1]))
                plan_time_acc += (perf_counter() - t0)
                if path_tail:
                    path = path_tail
                else:
                    # Elegir vecino que maximiza espacio libre
                    v = best_safe_neighbor(head, snake, fruit)
                    if v is None:
                        v = any_safe_step(head, set(snake[1:]))
                    path = [v] if v else []

        # ===== Si no hay path a nada, heurística de espacio libre
        if not path:
            v = best_safe_neighbor(head, snake, fruit)
            if v is None:
                v = any_safe_step(head, set(snake[1:]))
            if v is None:
                elapsed = perf_counter() - run_start
                game_over(screen, apples, steps, elapsed, plan_time_acc, SEED, success=False)
            next_cell = v
        else:
            next_cell = path[0]

        # ===== Mover =====
        head = next_cell
        snake.insert(0, head)
        steps += 1

        if head == fruit:
            apples += 1
            fruit = generate_fruit(snake)
        else:
            snake.pop()

        # Colisiones / límites
        if not valid(head) or head in snake[1:]:
            elapsed = perf_counter() - run_start
            game_over(screen, apples, steps, elapsed, plan_time_acc, SEED, success=False)

        # Éxito
        if apples >= MAX_APPLES:
            elapsed = perf_counter() - run_start
            game_over(screen, apples, steps, elapsed, plan_time_acc, SEED, success=True)

        # Render
        screen.fill(BLACK)
        for seg in snake:
            pygame.draw.rect(screen, GREEN, to_rect(seg))
        pygame.draw.rect(screen, WHITE, to_rect(fruit))
        draw_text(screen, f"Score: {apples}", 8, 8, WHITE, 20)
        draw_text(screen, f"10x10 | UCS+Seguridad", WINDOW_W-220, 8, WHITE, 18)

        pygame.display.flip()
        clock.tick(SNAKE_SPEED)

if __name__ == "__main__":
    main()
