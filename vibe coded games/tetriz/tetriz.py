import pygame
import random
import json
import os
import math
import sys

pygame.init()
pygame.mixer.init()
pygame.joystick.init()

SCREEN_W, SCREEN_H = 900, 700
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
canvas = pygame.Surface((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Tetriz")
clock = pygame.time.Clock()
FPS = 60
is_fullscreen = False


def toggle_fullscreen():
    global screen, is_fullscreen
    is_fullscreen = not is_fullscreen
    if is_fullscreen:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)


def present():
    sw, sh = screen.get_size()
    scale = min(sw / SCREEN_W, sh / SCREEN_H)
    new_w, new_h = int(SCREEN_W * scale), int(SCREEN_H * scale)
    scaled = pygame.transform.smoothscale(canvas, (new_w, new_h))
    screen.fill(BLACK)
    screen.blit(scaled, ((sw - new_w) // 2, (sh - new_h) // 2))
    pygame.display.flip()

SCARLET = (255, 36, 36)
SCARLET_DIM = (140, 18, 18)
SCARLET_DARK = (60, 8, 8)
BG_DARK = (12, 4, 4)
WHITE = (240, 240, 240)
BLACK = (0, 0, 0)
GREY = (90, 90, 90)

CFG_FILE = "cfg.json"

DEFAULT_CFG = {
    "music_on": True,
    "controls": {
        "move_left": pygame.K_LEFT,
        "move_right": pygame.K_RIGHT,
        "soft_drop": pygame.K_DOWN,
        "hard_drop": pygame.K_SPACE,
        "rotate_left": pygame.K_LCTRL,
        "rotate_right": pygame.K_UP,
        "hold": pygame.K_LSHIFT
    },
    "controller_controls": {
        "move_left": "hat_left",
        "move_right": "hat_right",
        "soft_drop": "hat_down",
        "hard_drop": 0,
        "rotate_left": 2,
        "rotate_right": 3,
        "hold": 1
    },
    "controller_enabled": True,
    "high_score": 0
}


def load_cfg():
    if os.path.exists(CFG_FILE):
        try:
            with open(CFG_FILE, "r") as f:
                data = json.load(f)
            for k, v in DEFAULT_CFG.items():
                if k not in data:
                    data[k] = v
            for k, v in DEFAULT_CFG["controls"].items():
                if k not in data["controls"]:
                    data["controls"][k] = v
            for k, v in DEFAULT_CFG["controller_controls"].items():
                if k not in data["controller_controls"]:
                    data["controller_controls"][k] = v
            return data
        except Exception:
            return json.loads(json.dumps(DEFAULT_CFG))
    return json.loads(json.dumps(DEFAULT_CFG))


def save_cfg(cfg):
    with open(CFG_FILE, "w") as f:
        json.dump(cfg, f, indent=4)


cfg = load_cfg()

FONT_BIG = pygame.font.SysFont("consolas", 90, bold=True)
FONT_BTN = pygame.font.SysFont("consolas", 36, bold=True)
FONT_MED = pygame.font.SysFont("consolas", 28, bold=True)
FONT_SMALL = pygame.font.SysFont("consolas", 22, bold=True)
FONT_TINY = pygame.font.SysFont("consolas", 18)


# ---------------------------------------------------------------------------
# Particle systems for menu background
# ---------------------------------------------------------------------------
class Particle:
    def __init__(self, large=True):
        self.large = large
        self.reset(initial=True)

    def reset(self, initial=False):
        self.x = random.uniform(0, SCREEN_W)
        if initial:
            self.y = random.uniform(0, SCREEN_H)
        else:
            self.y = SCREEN_H + random.uniform(0, 50)
        if self.large:
            self.size = random.uniform(40, 110)
            self.speed = random.uniform(8, 20)
            self.alpha = random.randint(15, 35)
        else:
            self.size = random.uniform(3, 9)
            self.speed = random.uniform(60, 140)
            self.alpha = random.randint(60, 140)
        self.drift = random.uniform(-15, 15)

    def update(self, dt):
        self.y -= self.speed * dt
        self.x += self.drift * dt
        if self.y < -self.size:
            self.reset()

    def draw(self, surf):
        s = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        pygame.draw.circle(s, (*SCARLET, self.alpha), (int(self.size), int(self.size)), int(self.size))
        surf.blit(s, (self.x - self.size, self.y - self.size))


def make_particles():
    large = [Particle(large=True) for _ in range(14)]
    small = [Particle(large=False) for _ in range(45)]
    return large, small


large_particles, small_particles = make_particles()


def update_particles(dt):
    for p in large_particles:
        p.update(dt)
    for p in small_particles:
        p.update(dt)


def draw_particles(surf):
    for p in large_particles:
        p.draw(surf)
    for p in small_particles:
        p.draw(surf)


def draw_background():
    canvas.fill(BG_DARK)
    draw_particles(canvas)
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((SCARLET[0], SCARLET[1], SCARLET[2], 40))
    canvas.blit(overlay, (0, 0))


# ---------------------------------------------------------------------------
# Button with hover scale + pulse
# ---------------------------------------------------------------------------
class Button:
    def __init__(self, x, y, w, h, text, font=FONT_BTN):
        self.base_rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font
        self.hover = False
        self.scale = 1.0
        self.pulse_t = random.uniform(0, 10)

    def update(self, dt, mouse_pos):
        self.hover = self.base_rect.collidepoint(mouse_pos)
        target = 1.08 if self.hover else 1.0
        self.scale += (target - self.scale) * min(1, dt * 12)
        self.pulse_t += dt

    def get_rect(self):
        w = int(self.base_rect.w * self.scale)
        h = int(self.base_rect.h * self.scale)
        cx, cy = self.base_rect.center
        return pygame.Rect(cx - w // 2, cy - h // 2, w, h)

    def draw(self, surf):
        rect = self.get_rect()
        pulse = (math.sin(self.pulse_t * 3) + 1) / 2
        glow_alpha = int(40 + pulse * 70)
        glow_pad = int(6 + pulse * 6)

        glow_surf = pygame.Surface((rect.w + glow_pad * 2, rect.h + glow_pad * 2), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (*SCARLET, glow_alpha), glow_surf.get_rect(), border_radius=14)
        surf.blit(glow_surf, (rect.x - glow_pad, rect.y - glow_pad))

        border_col = (255, min(255, 80 + int(pulse * 80)), min(255, 80 + int(pulse * 80)))
        fill_col = SCARLET_DARK if not self.hover else (90, 14, 14)
        pygame.draw.rect(surf, fill_col, rect, border_radius=10)
        pygame.draw.rect(surf, SCARLET, rect, width=3, border_radius=10)

        txt_col = WHITE if not self.hover else (255, 220, 220)
        txt = self.font.render(self.text, True, txt_col)
        surf.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

    def clicked(self, mouse_pos, mouse_click):
        return self.base_rect.collidepoint(mouse_pos) and mouse_click


# ---------------------------------------------------------------------------
# Music
# ---------------------------------------------------------------------------
MUSIC_LOADED = False
if os.path.exists("music.ogg"):
    try:
        pygame.mixer.music.load("music.ogg")
        pygame.mixer.music.set_volume(0.5)
        MUSIC_LOADED = True
    except Exception:
        MUSIC_LOADED = False


def apply_music_state():
    if not MUSIC_LOADED:
        return
    if cfg["music_on"]:
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)
    else:
        pygame.mixer.music.stop()


apply_music_state()


# ---------------------------------------------------------------------------
# Tetris game logic
# ---------------------------------------------------------------------------
COLS, ROWS = 10, 20
CELL = 28
BOARD_X = (SCREEN_W - COLS * CELL) // 2 - 100
BOARD_Y = 40

SHAPES = {
    'I': [[(0, 1), (1, 1), (2, 1), (3, 1)]],
    'O': [[(1, 0), (2, 0), (1, 1), (2, 1)]],
    'T': [[(1, 0), (0, 1), (1, 1), (2, 1)]],
    'S': [[(1, 0), (2, 0), (0, 1), (1, 1)]],
    'Z': [[(0, 0), (1, 0), (1, 1), (2, 1)]],
    'J': [[(0, 0), (0, 1), (1, 1), (2, 1)]],
    'L': [[(2, 0), (0, 1), (1, 1), (2, 1)]],
}

SHAPE_COLORS = {
    'I': (60, 220, 230),
    'O': (255, 215, 60),
    'T': (190, 70, 230),
    'S': (80, 230, 110),
    'Z': SCARLET,
    'J': (80, 110, 240),
    'L': (255, 150, 50),
}


def rotate_cells(cells, times):
    result = cells
    for _ in range(times % 4):
        new_result = []
        for (x, y) in result:
            nx = 3 - y
            ny = x
            new_result.append((nx, ny))
        result = new_result
    return result


class Piece:
    def __init__(self, kind):
        self.kind = kind
        self.rotation = 0
        self.cells = rotate_cells(SHAPES[kind][0], 0)
        self.x = 3
        self.y = -1 if kind != 'I' and kind != 'O' else -1

    def get_cells(self, rotation=None, x=None, y=None):
        rotation = self.rotation if rotation is None else rotation
        x = self.x if x is None else x
        y = self.y if y is None else y
        cells = rotate_cells(SHAPES[self.kind][0], rotation)
        return [(cx + x, cy + y) for (cx, cy) in cells]


def new_bag():
    bag = list(SHAPES.keys())
    random.shuffle(bag)
    return bag


class Board:
    def __init__(self):
        self.grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.bag = new_bag()
        self.next_bag = new_bag()
        self.current = Piece(self.bag.pop(0))
        self.hold_piece = None
        self.can_hold = True
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.game_over = False
        self.fall_time = 0
        self.fall_speed = 0.8
        self.lock_delay = 0.5
        self.lock_timer = 0
        self.is_locking = False
        self.combo = 0
        self.clear_anim = []  # rows being cleared, with timer
        self.clear_timer = 0
        self.shake = 0

    def next_piece_kind(self):
        if not self.bag:
            self.bag = self.next_bag
            self.next_bag = new_bag()
        return self.bag[0]

    def spawn_next(self):
        if not self.bag:
            self.bag = self.next_bag
            self.next_bag = new_bag()
        kind = self.bag.pop(0)
        self.current = Piece(kind)
        self.can_hold = True
        if self.collides(self.current.get_cells()):
            self.game_over = True

    def collides(self, cells):
        for (x, y) in cells:
            if x < 0 or x >= COLS or y >= ROWS:
                return True
            if y >= 0 and self.grid[y][x] is not None:
                return True
        return False

    def lock_piece(self):
        for (x, y) in self.current.get_cells():
            if 0 <= y < ROWS and 0 <= x < COLS:
                self.grid[y][x] = SHAPE_COLORS[self.current.kind]
        self.check_lines()
        self.spawn_next()
        self.is_locking = False
        self.lock_timer = 0

    def check_lines(self):
        full_rows = []
        for y in range(ROWS):
            if all(self.grid[y][x] is not None for x in range(COLS)):
                full_rows.append(y)
        if full_rows:
            self.clear_anim = full_rows
            self.clear_timer = 0.18
            points = {1: 100, 2: 300, 3: 500, 4: 800}
            n = len(full_rows)
            self.score += points.get(n, 800) * self.level
            self.lines_cleared += n
            self.combo += 1
            self.score += max(0, (self.combo - 1)) * 50
            self.level = 1 + self.lines_cleared // 10
            self.fall_speed = max(0.08, 0.8 - (self.level - 1) * 0.07)
            self.shake = 6
        else:
            self.combo = 0

    def finish_clear(self):
        for y in sorted(self.clear_anim, reverse=True):
            del self.grid[y]
            self.grid.insert(0, [None for _ in range(COLS)])
        self.clear_anim = []

    def hold(self):
        if not self.can_hold:
            return
        if self.hold_piece is None:
            self.hold_piece = self.current.kind
            self.spawn_next()
        else:
            cur = self.current.kind
            self.current = Piece(self.hold_piece)
            self.hold_piece = cur
        self.can_hold = False
        self.lock_timer = 0
        self.is_locking = False

    def try_move(self, dx, dy):
        new_cells = self.current.get_cells(x=self.current.x + dx, y=self.current.y + dy)
        if not self.collides(new_cells):
            self.current.x += dx
            self.current.y += dy
            if dy == 0:
                self.is_locking = False
                self.lock_timer = 0
            return True
        return False

    def try_rotate(self, direction):
        old_rotation = self.current.rotation
        new_rotation = (old_rotation + direction) % 4
        kicks = [(0, 0), (-1, 0), (1, 0), (0, -1), (-1, -1), (1, -1), (-2, 0), (2, 0)]
        for (kx, ky) in kicks:
            new_cells = self.current.get_cells(rotation=new_rotation, x=self.current.x + kx, y=self.current.y + ky)
            if not self.collides(new_cells):
                self.current.rotation = new_rotation
                self.current.x += kx
                self.current.y += ky
                self.is_locking = False
                self.lock_timer = 0
                return True
        return False

    def hard_drop(self):
        dist = 0
        while self.try_move(0, 1):
            dist += 1
        self.score += dist * 2
        self.lock_piece()

    def get_ghost_y(self):
        ghost_y = self.current.y
        while not self.collides(self.current.get_cells(y=ghost_y + 1)):
            ghost_y += 1
        return ghost_y

    def update(self, dt, soft_drop):
        if self.clear_anim:
            self.clear_timer -= dt
            if self.clear_timer <= 0:
                self.finish_clear()
            return
        if self.game_over:
            return

        if self.shake > 0:
            self.shake -= dt * 30

        speed = self.fall_speed * (0.12 if soft_drop else 1.0)
        self.fall_time += dt
        if self.fall_time >= speed:
            self.fall_time = 0
            if not self.try_move(0, 1):
                self.is_locking = True

        if self.is_locking:
            self.lock_timer += dt
            if self.lock_timer >= self.lock_delay:
                self.lock_piece()


def draw_board(board, controls_map):
    # board border / panel
    panel_rect = pygame.Rect(BOARD_X - 4, BOARD_Y - 4, COLS * CELL + 8, ROWS * CELL + 8)
    shake_off = (random.uniform(-board.shake, board.shake), random.uniform(-board.shake, board.shake)) if board.shake > 0 else (0, 0)

    glow = pygame.Surface((panel_rect.w + 20, panel_rect.h + 20), pygame.SRCALPHA)
    pygame.draw.rect(glow, (*SCARLET, 40), glow.get_rect(), border_radius=10)
    canvas.blit(glow, (panel_rect.x - 10 + shake_off[0], panel_rect.y - 10 + shake_off[1]))

    pygame.draw.rect(canvas, (20, 6, 6), panel_rect.move(shake_off), border_radius=4)
    pygame.draw.rect(canvas, SCARLET, panel_rect.move(shake_off), width=2, border_radius=4)

    # grid cells
    for y in range(ROWS):
        for x in range(COLS):
            cx = BOARD_X + x * CELL + shake_off[0]
            cy = BOARD_Y + y * CELL + shake_off[1]
            cell_rect = pygame.Rect(cx, cy, CELL - 1, CELL - 1)
            if board.clear_anim and y in board.clear_anim:
                flash = int(255 * (board.clear_timer / 0.18))
                pygame.draw.rect(canvas, (255, min(255, flash + 80), min(255, flash + 80)), cell_rect)
            elif board.grid[y][x] is not None:
                col = board.grid[y][x]
                pygame.draw.rect(canvas, col, cell_rect, border_radius=3)
                pygame.draw.rect(canvas, tuple(min(255, c + 50) for c in col), cell_rect, width=1, border_radius=3)
            else:
                pygame.draw.rect(canvas, (28, 10, 10), cell_rect, border_radius=2)

    if not board.clear_anim and not board.game_over:
        # ghost piece
        ghost_y = board.get_ghost_y()
        for (x, y) in board.current.get_cells(y=ghost_y):
            if 0 <= y < ROWS and 0 <= x < COLS:
                cx = BOARD_X + x * CELL + shake_off[0]
                cy = BOARD_Y + y * CELL + shake_off[1]
                rect = pygame.Rect(cx, cy, CELL - 1, CELL - 1)
                ghost_surf = pygame.Surface((CELL - 1, CELL - 1), pygame.SRCALPHA)
                pygame.draw.rect(ghost_surf, (*SCARLET, 60), ghost_surf.get_rect(), width=2, border_radius=3)
                canvas.blit(ghost_surf, rect.topleft)

        # current piece
        col = SHAPE_COLORS[board.current.kind]
        for (x, y) in board.current.get_cells():
            if 0 <= y < ROWS and 0 <= x < COLS:
                cx = BOARD_X + x * CELL + shake_off[0]
                cy = BOARD_Y + y * CELL + shake_off[1]
                rect = pygame.Rect(cx, cy, CELL - 1, CELL - 1)
                pygame.draw.rect(canvas, col, rect, border_radius=3)
                pygame.draw.rect(canvas, tuple(min(255, c + 60) for c in col), rect, width=1, border_radius=3)

    # side panel
    side_x = BOARD_X + COLS * CELL + 40

    # Score, pulsing
    pulse = (math.sin(pygame.time.get_ticks() / 300) + 1) / 2
    score_scale = 1.0 + pulse * 0.06
    score_txt = FONT_MED.render(f"Points: {board.score}", True, (255, int(180 + pulse * 75), int(180 + pulse * 75)))
    scaled = pygame.transform.smoothscale(
        score_txt, (int(score_txt.get_width() * score_scale), int(score_txt.get_height() * score_scale))
    )
    canvas.blit(scaled, (side_x, BOARD_Y))

    level_txt = FONT_SMALL.render(f"Level: {board.level}", True, WHITE)
    canvas.blit(level_txt, (side_x, BOARD_Y + 50))

    lines_txt = FONT_SMALL.render(f"Lines: {board.lines_cleared}", True, WHITE)
    canvas.blit(lines_txt, (side_x, BOARD_Y + 80))

    hs = max(cfg.get("high_score", 0), board.score)
    hs_txt = FONT_SMALL.render(f"High: {hs}", True, (255, 150, 150))
    canvas.blit(hs_txt, (side_x, BOARD_Y + 110))

    # Next piece
    next_label = FONT_SMALL.render("NEXT", True, SCARLET)
    canvas.blit(next_label, (side_x, BOARD_Y + 160))
    draw_mini_piece(board.next_piece_kind(), side_x, BOARD_Y + 195)

    # Hold piece
    hold_label = FONT_SMALL.render("HOLD", True, SCARLET)
    canvas.blit(hold_label, (side_x, BOARD_Y + 290))
    if board.hold_piece:
        draw_mini_piece(board.hold_piece, side_x, BOARD_Y + 325)

    # controls reminder
    cy = BOARD_Y + 430
    canvas.blit(FONT_TINY.render("Controls:", True, SCARLET_DIM), (side_x, cy))
    labels = [
        ("Move L/R", f"{key_name(controls_map['move_left'])}/{key_name(controls_map['move_right'])}"),
        ("Soft drop", key_name(controls_map['soft_drop'])),
        ("Hard drop", key_name(controls_map['hard_drop'])),
        ("Rotate L/R", f"{key_name(controls_map['rotate_left'])}/{key_name(controls_map['rotate_right'])}"),
        ("Hold", key_name(controls_map['hold'])),
    ]
    for i, (label, key) in enumerate(labels):
        t = FONT_TINY.render(f"{label}: {key}", True, GREY)
        canvas.blit(t, (side_x, cy + 25 + i * 22))

    if board.game_over:
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        canvas.blit(overlay, (0, 0))
        go_txt = FONT_BIG.render("GAME OVER", True, SCARLET)
        canvas.blit(go_txt, (SCREEN_W // 2 - go_txt.get_width() // 2, SCREEN_H // 2 - 100))
        sub = FONT_MED.render(f"Final Score: {board.score}", True, WHITE)
        canvas.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, SCREEN_H // 2 - 10))
        sub2 = FONT_SMALL.render("Press ESC for menu or R to restart", True, GREY)
        canvas.blit(sub2, (SCREEN_W // 2 - sub2.get_width() // 2, SCREEN_H // 2 + 40))


def draw_mini_piece(kind, x, y):
    cells = SHAPES[kind][0]
    color = SHAPE_COLORS[kind]
    minicell = 18
    for (cx, cyy) in cells:
        rect = pygame.Rect(x + cx * minicell, y + cyy * minicell, minicell - 1, minicell - 1)
        pygame.draw.rect(canvas, color, rect, border_radius=2)


def key_name(key_code):
    name = pygame.key.name(key_code)
    return name.upper().replace("LEFT ", "L-").replace("RIGHT ", "R-")


# ---------------------------------------------------------------------------
# Title with floating shadows
# ---------------------------------------------------------------------------
class TitleEffect:
    def __init__(self):
        self.t = 0
        self.shadows = []

    def update(self, dt):
        self.t += dt
        offset = math.sin(self.t * 1.2) * 14
        self.shadows.append([offset, 255])
        for s in self.shadows:
            s[1] -= dt * 220
        self.shadows = [s for s in self.shadows if s[1] > 0]
        if len(self.shadows) > 40:
            self.shadows = self.shadows[-40:]
        return offset

    def draw(self, surf, base_y):
        cx = SCREEN_W // 2
        for offset, alpha in self.shadows:
            txt = FONT_BIG.render("Tetriz", True, SCARLET)
            txt.set_alpha(int(alpha * 0.35))
            surf.blit(txt, (cx - txt.get_width() // 2, base_y + offset))
        offset = math.sin(self.t * 1.2) * 14
        txt = FONT_BIG.render("Tetriz", True, WHITE)
        surf.blit(txt, (cx - txt.get_width() // 2, base_y + offset))


# ---------------------------------------------------------------------------
# Settings canvas state
# ---------------------------------------------------------------------------
REBIND_KEYS = ["move_left", "move_right", "soft_drop", "hard_drop", "rotate_left", "rotate_right", "hold"]
REBIND_LABELS = {
    "move_left": "Move Left",
    "move_right": "Move Right",
    "soft_drop": "Soft Drop",
    "hard_drop": "Hard Drop",
    "rotate_left": "Rotate Left",
    "rotate_right": "Rotate Right",
    "hold": "Hold Piece",
}


def get_canvas_mouse_pos():
    sw, sh = screen.get_size()
    scale = min(sw / SCREEN_W, sh / SCREEN_H)
    new_w, new_h = int(SCREEN_W * scale), int(SCREEN_H * scale)
    off_x, off_y = (sw - new_w) // 2, (sh - new_h) // 2
    mx, my = pygame.mouse.get_pos()
    cx = (mx - off_x) / scale if scale > 0 else 0
    cy = (my - off_y) / scale if scale > 0 else 0
    return (cx, cy)


def controller_button_action(button):
    """Return the action name bound to this controller button, or None."""
    for action, val in cfg["controller_controls"].items():
        if val == button:
            return action
    return None


def controller_name_for(action):
    val = cfg["controller_controls"].get(action)
    if val is None:
        return "-"
    if isinstance(val, str):
        return val.replace("hat_", "D-Pad ").title()
    return f"Button {val}"


def main():
    global cfg, screen
    state = "menu"
    title_fx = TitleEffect()

    btn_play = Button(SCREEN_W // 2 - 130, 360, 260, 60, "PLAY")
    btn_settings = Button(SCREEN_W // 2 - 130, 440, 260, 60, "SETTINGS")
    btn_fullscreen = Button(SCREEN_W // 2 - 130, 520, 260, 60, "FULLSCREEN")
    btn_back = Button(40, 600, 160, 50, "BACK", font=FONT_SMALL)
    btn_reset = Button(220, 600, 220, 50, "RESET DEFAULTS", font=FONT_TINY)
    btn_music = Button(SCREEN_W // 2 - 150, 100, 300, 44, "", font=FONT_SMALL)
    btn_controller_toggle = Button(SCREEN_W // 2 - 150, 152, 300, 44, "", font=FONT_SMALL)
    btn_tab = Button(SCREEN_W - 220, 25, 180, 44, "", font=FONT_TINY)

    rebind_buttons = {}
    for i, k in enumerate(REBIND_KEYS):
        rebind_buttons[k] = Button(SCREEN_W // 2 - 150, 248 + i * 46, 300, 38, "", font=FONT_TINY)

    awaiting_rebind = None
    settings_tab = "keyboard"
    board = None
    countdown_timer = 0
    joysticks = {}
    for i in range(pygame.joystick.get_count()):
        joy = pygame.joystick.Joystick(i)
        joysticks[joy.get_instance_id()] = joy
    hat_state = (0, 0)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        mouse_pos = get_canvas_mouse_pos()
        mouse_click = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                if not is_fullscreen:
                    screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            elif event.type == pygame.JOYDEVICEADDED:
                joy = pygame.joystick.Joystick(event.device_index)
                joysticks[joy.get_instance_id()] = joy
            elif event.type == pygame.JOYDEVICEREMOVED:
                joysticks.pop(event.instance_id, None)
                hat_state = (0, 0)
            elif event.type == pygame.JOYHATMOTION:
                hat_state = event.value
            elif event.type == pygame.JOYBUTTONDOWN and cfg.get("controller_enabled", True):
                action = controller_button_action(event.button)
                if state == "settings" and awaiting_rebind and settings_tab == "controller":
                    cfg["controller_controls"][awaiting_rebind] = event.button
                    save_cfg(cfg)
                    awaiting_rebind = None
                elif state == "menu":
                    if action == "hard_drop":
                        board = Board()
                        countdown_timer = 1.5
                        state = "countdown"
                elif state == "play":
                    controls = cfg["controls"]
                    if board.game_over:
                        if action == "hard_drop":
                            board = Board()
                    else:
                        if action == "rotate_left":
                            board.try_rotate(-1)
                        elif action == "rotate_right":
                            board.try_rotate(1)
                        elif action == "hard_drop":
                            board.hard_drop()
                        elif action == "hold":
                            board.hold()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_click = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    toggle_fullscreen()
                elif state == "settings" and awaiting_rebind and settings_tab == "keyboard":
                    cfg["controls"][awaiting_rebind] = event.key
                    save_cfg(cfg)
                    awaiting_rebind = None
                elif state == "play":
                    controls = cfg["controls"]
                    if board.game_over:
                        if event.key == pygame.K_ESCAPE:
                            state = "menu"
                        elif event.key == pygame.K_r:
                            board = Board()
                    else:
                        if event.key == controls["rotate_left"]:
                            board.try_rotate(-1)
                        elif event.key == controls["rotate_right"]:
                            board.try_rotate(1)
                        elif event.key == controls["hard_drop"]:
                            board.hard_drop()
                        elif event.key == controls["hold"]:
                            board.hold()
                        elif event.key == pygame.K_ESCAPE:
                            state = "menu"
                elif state == "settings":
                    if event.key == pygame.K_ESCAPE:
                        state = "menu"
                elif state == "menu":
                    if event.key == pygame.K_ESCAPE:
                        running = False

        update_particles(dt)

        # ---------------- MENU ----------------
        if state == "menu":
            draw_background()
            esc_txt = FONT_TINY.render("ESC to leave", True, GREY)
            canvas.blit(esc_txt, (15, 15))
            offset = title_fx.update(dt)
            title_fx.draw(canvas, 60)

            btn_play.update(dt, mouse_pos)
            btn_settings.update(dt, mouse_pos)
            btn_fullscreen.update(dt, mouse_pos)
            btn_play.draw(canvas)
            btn_settings.draw(canvas)
            btn_fullscreen.draw(canvas)

            hs = cfg.get("high_score", 0)
            hs_txt = FONT_MED.render(f"High Score: {hs}", True, (255, 160, 160))
            canvas.blit(hs_txt, (SCREEN_W // 2 - hs_txt.get_width() // 2, 290))

            if btn_play.clicked(mouse_pos, mouse_click):
                board = Board()
                countdown_timer = 1.5
                state = "countdown"
            if btn_settings.clicked(mouse_pos, mouse_click):
                state = "settings"
            if btn_fullscreen.clicked(mouse_pos, mouse_click):
                toggle_fullscreen()

        # ---------------- SETTINGS ----------------
        elif state == "settings":
            draw_background()
            esc_txt = FONT_TINY.render("ESC to leave", True, GREY)
            canvas.blit(esc_txt, (15, 15))
            header = FONT_BIG.render("Settings", True, WHITE)
            header = pygame.transform.smoothscale(header, (int(header.get_width() * 0.5), int(header.get_height() * 0.5)))
            canvas.blit(header, (SCREEN_W // 2 - header.get_width() // 2, 25))

            btn_tab.text = "Controller Binds" if settings_tab == "keyboard" else "Keyboard Binds"
            btn_tab.update(dt, mouse_pos)
            btn_tab.draw(canvas)
            if btn_tab.clicked(mouse_pos, mouse_click):
                settings_tab = "controller" if settings_tab == "keyboard" else "keyboard"
                awaiting_rebind = None

            if settings_tab == "keyboard":
                ctrl_label = FONT_SMALL.render("Rotation / Movement Controls (Keyboard):", True, SCARLET)
                canvas.blit(ctrl_label, (SCREEN_W // 2 - 150, 205))

                btn_music.text = f"Music: {'ON' if cfg['music_on'] else 'OFF'}"
                btn_music.update(dt, mouse_pos)
                btn_music.draw(canvas)
                if btn_music.clicked(mouse_pos, mouse_click):
                    cfg["music_on"] = not cfg["music_on"]
                    save_cfg(cfg)
                    apply_music_state()

                for k in REBIND_KEYS:
                    b = rebind_buttons[k]
                    if awaiting_rebind == k:
                        b.text = "Press a key..."
                    else:
                        b.text = f"{REBIND_LABELS[k]}: {key_name(cfg['controls'][k])}"
                    b.update(dt, mouse_pos)
                    b.draw(canvas)
                    if b.clicked(mouse_pos, mouse_click):
                        awaiting_rebind = k

            else:
                ctrl_label = FONT_SMALL.render("Rotation / Movement Controls (Controller):", True, SCARLET)
                canvas.blit(ctrl_label, (SCREEN_W // 2 - 150, 205))

                btn_controller_toggle.text = f"Controller: {'ON' if cfg.get('controller_enabled', True) else 'OFF'}"
                btn_controller_toggle.update(dt, mouse_pos)
                btn_controller_toggle.draw(canvas)
                if btn_controller_toggle.clicked(mouse_pos, mouse_click):
                    cfg["controller_enabled"] = not cfg.get("controller_enabled", True)
                    save_cfg(cfg)

                for k in REBIND_KEYS:
                    b = rebind_buttons[k]
                    if k in ("move_left", "move_right", "soft_drop"):
                        b.text = f"{REBIND_LABELS[k]}: D-Pad (fixed)"
                    elif awaiting_rebind == k:
                        b.text = "Press a controller button..."
                    else:
                        b.text = f"{REBIND_LABELS[k]}: {controller_name_for(k)}"
                    b.update(dt, mouse_pos)
                    b.draw(canvas)
                    if k not in ("move_left", "move_right", "soft_drop") and b.clicked(mouse_pos, mouse_click):
                        awaiting_rebind = k

            btn_back.update(dt, mouse_pos)
            btn_back.draw(canvas)
            if btn_back.clicked(mouse_pos, mouse_click):
                state = "menu"
                awaiting_rebind = None

            btn_reset.update(dt, mouse_pos)
            btn_reset.draw(canvas)
            if btn_reset.clicked(mouse_pos, mouse_click):
                if settings_tab == "keyboard":
                    cfg["controls"] = json.loads(json.dumps(DEFAULT_CFG["controls"]))
                    cfg["music_on"] = DEFAULT_CFG["music_on"]
                    apply_music_state()
                else:
                    cfg["controller_controls"] = json.loads(json.dumps(DEFAULT_CFG["controller_controls"]))
                    cfg["controller_enabled"] = DEFAULT_CFG["controller_enabled"]
                save_cfg(cfg)
                awaiting_rebind = None

        # ---------------- COUNTDOWN ----------------
        elif state == "countdown":
            canvas.fill(BG_DARK)
            draw_particles(canvas)
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((SCARLET[0], SCARLET[1], SCARLET[2], 25))
            canvas.blit(overlay, (0, 0))

            draw_board(board, cfg["controls"])

            countdown_timer -= dt
            display_number = max(1, min(3, math.ceil(countdown_timer / 0.5)))

            dark_overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            dark_overlay.fill((0, 0, 0, 140))
            canvas.blit(dark_overlay, (0, 0))

            num_txt = FONT_BIG.render(str(display_number), True, SCARLET)
            pulse = (math.sin(pygame.time.get_ticks() / 120) + 1) / 2
            scale = 1.0 + pulse * 0.15
            num_txt = pygame.transform.smoothscale(
                num_txt, (int(num_txt.get_width() * scale), int(num_txt.get_height() * scale))
            )
            canvas.blit(num_txt, (SCREEN_W // 2 - num_txt.get_width() // 2, SCREEN_H // 2 - num_txt.get_height() // 2))

            if countdown_timer <= 0:
                state = "play"

        # ---------------- PLAY ----------------
        elif state == "play":
            canvas.fill(BG_DARK)
            draw_particles(canvas)
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((SCARLET[0], SCARLET[1], SCARLET[2], 25))
            canvas.blit(overlay, (0, 0))

            controls = cfg["controls"]
            keys = pygame.key.get_pressed()
            controller_on = cfg.get("controller_enabled", True)
            hat_left = controller_on and hat_state[0] == -1
            hat_right = controller_on and hat_state[0] == 1
            hat_down = controller_on and hat_state[1] == -1

            soft_drop = (keys[controls["soft_drop"]] or hat_down) if not board.game_over else False

            if not board.game_over:
                # continuous left/right movement with simple repeat handling
                if not hasattr(board, "_move_timer"):
                    board._move_timer = {"left": 0, "right": 0}
                for direction, key_held, dx in (("left", keys[controls["move_left"]] or hat_left, -1), ("right", keys[controls["move_right"]] or hat_right, 1)):
                    if key_held:
                        board._move_timer[direction] += dt
                        if board._move_timer[direction] == dt or board._move_timer[direction] > 0.18:
                            if board._move_timer[direction] > 0.18:
                                board._move_timer[direction] = 0.18 - 0.04
                            board.try_move(dx, 0)
                    else:
                        board._move_timer[direction] = 0

            board.update(dt, soft_drop)

            if board.game_over and board.score > cfg.get("high_score", 0):
                cfg["high_score"] = board.score
                save_cfg(cfg)

            draw_board(board, controls)

        present()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()