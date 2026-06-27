import pygame
import sys
import os
import random
import time

pygame.init()

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Speed Typing Game")
clock = pygame.time.Clock()
FULLSCREEN = False

FONT_SMALL = pygame.font.SysFont("consolas", 22)
FONT_MED = pygame.font.SysFont("consolas", 32)
FONT_LARGE = pygame.font.SysFont("consolas", 64, bold=True)
FONT_TITLE = pygame.font.SysFont("consolas", 80, bold=True)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
GREEN = (80, 220, 120)
RED = (220, 80, 80)

EASY_WORDS = "cat dog bat mat hat bag fan bed sun moon tree bird cow pig fish ant top hop mop dad mom big fig sit hit the and can man ran a to in is you that it he was for on are as with his they I at be this have from or one had by but not what all were we when your said there use an which she do how their if will up other about out many then them these so some her make like him into time has look two more write go see number way".split()

MEDIUM_WORDS = "around before sister brother mother father friend school teacher yellow orange purple green winter summer spring autumn pencil marker eraser crayon pocket jacket blanket pillow window accent acting adding modern choice fabric factor failed fairy family famous farmer memory motion museum narrow native nature nearby nearly needle ninety notice number object obtain occupy occurs oceans offers office officer official offset online opened opening opinion optics orange orbit orders organ origin outcome outline outside overall oxygen packed packet paddle page palace papers parade parent parish partly target border banner active safety sudden volume simple gentle valley member marker public velvet pocket cosmic dynamic plastic picnic helmet fabric victim metric magnet dragon backup custom market napkin bucket jacket packet rocket socket".split()

HARD_WORDS = "accommodate aggressive allegiance ambiguous anxiety bankruptcy bureaucracy camouflage carburetor cemetery chauffeur colleague conscious curiosity definite desperate dictionary environment exaggerate exercise familiar foreign guarantee hardware hygiene immediate independent irresistible jewelry judgment leisure liaison maintenance maneuver mischievous necessary occurrence parallel personnel physical physician possession privilege pronunciation questionnaire receipt recommend rhythm schedule separate sequence sergeant temporary continuous thirteenth vacuum vehicle vicious Wednesday yacht absolute accessory accurate dynamic achievement alignment analysis apparatus architecture asynchronous authority auxiliary beneficial boundary brilliant breath calculation chronological circuit classification column commitment comparative competitive component consensus controversial crystal cylinder definitely dependent description deteriorate dialogue disappear disastrous discipline discrimination efficient elementary embarrassed endeavor enthusiasm equivalent evidence exaggeration exceptional existence extraordinary fascinated favorite fluorescent fortunately foundation fulfillment fundamental gauge generally genuinely glorious government governor grammar grateful guidance hierarchy hilarious humorous horizontal hyperbole hypothesis identical illegible imaginary immigrant incidentally indispensable inevitable initiative innovative insurance intelligence intensity intercede interference intermittent interrupt intersection interpretation intuition invaluable invasion investigation invitation iridescent irrelevant irritable isolate itinerary jealousy judicial juvenile kernel laboratory labyrinth language laundry leadership legacy legitimate length lenient liability library license lieutenant lightning likelihood literal literature livelihood logical longevity luxury machinery magnificent majesty malicious management manufacture manuscript masterpiece mathematics mechanism mediocre medieval melancholy melodrama memorable memorandum mercenary merchandise meticulous metropolis microprocessor migration milestone miniature minuscule miscellaneous monotonous municipal mythology".split()

LEVELS = {
    "easy": (EASY_WORDS, 1.0),
    "medium": (MEDIUM_WORDS, 1.5),
    "hard": (HARD_WORDS, 2.2),
}

def gen_sentence(level):
    words, _ = LEVELS[level]
    return " ".join(random.choice(words) for _ in range(10))

COLOR_POOL = [
    (60, 60, 60),
    (245, 245, 245),
    (120, 100, 80),
    (90, 90, 100),
    (160, 150, 140),
    (80, 80, 70),
    (180, 170, 160),
    (100, 95, 90),
    (140, 130, 110),
    (70, 75, 80),
    (70, 130, 220),
    (90, 200, 110),
    (255, 140, 60),
    (180, 100, 240),
    (255, 60, 160),
    (255, 215, 80),
    (60, 255, 100),
    (100, 255, 220),
    (255, 255, 255),
    (240, 60, 60),
    (255, 105, 180),
    (0, 191, 255),
    (255, 99, 71),
    (50, 205, 50),
    (218, 112, 214),
    (255, 165, 0),
    (123, 104, 238),
    (32, 178, 170),
    (220, 20, 60),
    (0, 250, 154),
]

# Lava colors - each is a glowing pair that cycles between two vibrant colors, unlocked last
LAVA_COLOR_PAIRS = [
    ((255, 60, 160), (255, 215, 80)),
    ((255, 140, 60), (180, 100, 240)),
    ((60, 255, 100), (240, 60, 60)),
    ((0, 191, 255), (255, 105, 180)),
    ((123, 104, 238), (255, 165, 0)),
    ((50, 205, 50), (220, 20, 60)),
    ((255, 215, 80), (32, 178, 170)),
    ((100, 255, 220), (255, 60, 160)),
    ((218, 112, 214), (60, 255, 100)),
    ((0, 250, 154), (255, 99, 71)),
]
# Add their midpoint to COLOR_POOL so indices line up with tiers; actual rendering
# of a selected lava color glows between the pair (see get_dynamic_accent)
LAVA_START_INDEX = len(COLOR_POOL)
for _a, _b in LAVA_COLOR_PAIRS:
    COLOR_POOL.append(tuple((_a[i] + _b[i]) // 2 for i in range(3)))

# Rainbow accent - special color, purchasable separately for a flat point cost
RAINBOW_COST = 10000
RAINBOW_HUES = [
    (255, 0, 0),
    (255, 127, 0),
    (255, 255, 0),
    (0, 255, 0),
    (0, 255, 255),
    (0, 0, 255),
    (139, 0, 255),
]

ANIMATION_POOL = [
    "Hover Glow",
    "Button Scale",
    "Background Particles",
    "Gradient Background",
    "Pulse Effects",
    "Smooth Transitions",
    "Screen Shake on Type Error",
    "Confetti on Win",
    "Button Border Pulse",
    "Title Glow Pulse",
    "Slow Particle Drift",
    "Fast Particle Drift",
    "Large Particles",
    "Tiny Sparkle Particles",
    "Diagonal Gradient Background",
    "Vertical Gradient Pulse",
    "Button Ripple on Click",
    "Floating Title Animation",
    "Wavy Text Effect",
    "Color Cycle Background Tint",
    "Button Shadow Glow",
    "Typed Text Glow",
    "Pulsing Points Display",
    "Star Field Particles",
    "Snow Particles",
    "Bubble Particles",
    "Button Spin on Hover",
    "Screen Border Glow",
    "Double Confetti Burst",
    "Rainbow Text on Win",
    "Shake on Win",
    "Particle Color Cycle",
    "Button Gradient Fill",
    "Title Shadow Pulse",
    "Background Vignette",
    "Extra Smooth Easing",
]

SHOP_TIERS = [{"cost": 0}]
_tier_costs = [
    8, 15, 25, 40, 60, 85, 115, 150, 190, 235,
    285, 340, 400, 465, 535, 610, 690, 775, 865, 960,
    1060, 1165, 1275, 1390, 1510, 1635, 1765, 1900, 2040, 2185,
    2335, 2490, 2650, 2815, 2985, 3160, 3340, 3525, 3715, 3910,
]
for _c in _tier_costs:
    SHOP_TIERS.append({"cost": _c})


AUTO_TYPE_MODES = ["Off", "Very Slow", "Slow", "Normal", "Aggressive", "Insane", "Most Insane", "Instant"]
AUTO_TYPE_SPEEDS = {
    "Off": None,
    "Very Slow": 0.5,
    "Slow": 0.25,
    "Normal": 0.12,
    "Aggressive": 0.05,
    "Insane": 0.015,
    "Most Insane": 0.005,
    "Instant": 0.0,
}


import json
import base64
import zlib

try:
    CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "save_config.json")
except NameError:
    CONFIG_PATH = os.path.join(os.getcwd(), "save_config.json")


class GameState:
    def __init__(self):
        self.points = 0
        self.tier = 0
        self.selected_color_idx = 0
        self.active_animations = set()
        self.auto_type_mode = "Off"
        self.used_promo_codes = set()
        self.rainbow_unlocked = False
        self.high_scores = {"easy": 0, "medium": 0, "hard": 0}

state = GameState()


def reset_game():
    state.points = 0
    state.tier = 0
    state.selected_color_idx = 0
    state.active_animations = set()
    state.auto_type_mode = "Off"
    state.used_promo_codes = set()
    state.rainbow_unlocked = False
    state.high_scores = {"easy": 0, "medium": 0, "hard": 0}
    clear_all_particles()
    save_config()


def save_config():
    data = {
        "points": state.points,
        "tier": state.tier,
        "selected_color_idx": state.selected_color_idx,
        "active_animations": list(state.active_animations),
        "auto_type_mode": state.auto_type_mode,
        "used_promo_codes": list(state.used_promo_codes),
        "rainbow_unlocked": state.rainbow_unlocked,
        "high_scores": state.high_scores,
    }
    try:
        raw = json.dumps(data).encode("utf-8")
        compressed = zlib.compress(raw, level=9)
        encoded = base64.b85encode(compressed).decode("ascii")
        with open(CONFIG_PATH, "w") as f:
            f.write(encoded)
    except OSError:
        pass


def load_config():
    if not os.path.exists(CONFIG_PATH):
        return
    try:
        with open(CONFIG_PATH, "r") as f:
            encoded = f.read().strip()
        compressed = base64.b85decode(encoded)
        raw = zlib.decompress(compressed)
        data = json.loads(raw.decode("utf-8"))
    except Exception:
        return

    state.points = data.get("points", 0)
    state.tier = data.get("tier", 0)
    state.selected_color_idx = data.get("selected_color_idx", 0)
    state.active_animations = set(data.get("active_animations", []))
    state.auto_type_mode = data.get("auto_type_mode", "Off")
    if state.auto_type_mode not in AUTO_TYPE_MODES:
        state.auto_type_mode = "Off"
    state.used_promo_codes = set(data.get("used_promo_codes", []))
    state.rainbow_unlocked = data.get("rainbow_unlocked", False)
    hs = data.get("high_scores", {})
    state.high_scores = {
        "easy": hs.get("easy", 0),
        "medium": hs.get("medium", 0),
        "hard": hs.get("hard", 0),
    }
    state.active_animations &= set(ANIMATION_POOL)


def get_unlocked_colors():
    count = state.tier + 1
    return COLOR_POOL[:count]


def get_unlocked_animations():
    return ANIMATION_POOL[:state.tier]


def get_accent():
    if state.selected_color_idx == -1 and state.rainbow_unlocked:
        return RAINBOW_HUES[0]
    colors = get_unlocked_colors()
    idx = min(state.selected_color_idx, len(colors) - 1)
    idx = max(0, idx)
    return colors[idx]


def anim_enabled(name):
    return name in state.active_animations and name in get_unlocked_animations()


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_color(c1, c2, t):
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))


def get_screen_size():
    return screen.get_size()


def toggle_fullscreen():
    global FULLSCREEN, screen
    FULLSCREEN = not FULLSCREEN
    if FULLSCREEN:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))


def draw_gradient_bg(surf, color1, color2):
    w, h = surf.get_size()
    for y in range(0, h, 4):
        t = y / h
        c = lerp_color(color1, color2, t)
        pygame.draw.rect(surf, c, (0, y, w, 4))


def draw_text_glow(surf, text, font, color, pos, glow_color, glow_amount=3):
    for dx in range(-glow_amount, glow_amount + 1, 2):
        for dy in range(-glow_amount, glow_amount + 1, 2):
            if dx == 0 and dy == 0:
                continue
            glow_surf = font.render(text, True, glow_color)
            surf.blit(glow_surf, (pos[0] + dx, pos[1] + dy))
    main_surf = font.render(text, True, color)
    surf.blit(main_surf, pos)


class Particle:
    def __init__(self, color, w, h, style="dot"):
        self.style = style
        self.x = random.uniform(0, w)
        self.y = random.uniform(0, h)
        self.color = color

        if style == "dot":
            self.vx = random.uniform(-0.5, 0.5)
            self.vy = random.uniform(-0.8, -0.2)
            self.size = random.uniform(1, 3)
            self.alpha = random.randint(50, 150)
        elif style == "slow_drift":
            self.vx = random.uniform(-0.15, 0.15)
            self.vy = random.uniform(-0.25, -0.05)
            self.size = random.uniform(1, 3)
            self.alpha = random.randint(40, 120)
        elif style == "fast_drift":
            self.vx = random.uniform(-1.5, 1.5)
            self.vy = random.uniform(-2.5, -0.8)
            self.size = random.uniform(1, 2.5)
            self.alpha = random.randint(60, 160)
        elif style == "large":
            self.vx = random.uniform(-0.3, 0.3)
            self.vy = random.uniform(-0.5, -0.1)
            self.size = random.uniform(6, 12)
            self.alpha = random.randint(30, 80)
        elif style == "sparkle":
            self.vx = random.uniform(-0.2, 0.2)
            self.vy = random.uniform(-0.2, 0.2)
            self.size = random.uniform(0.5, 1.5)
            self.alpha = random.randint(100, 220)
            self.twinkle = random.uniform(0, 6.28)
        elif style == "star":
            self.vx = 0
            self.vy = random.uniform(0.05, 0.3)
            self.size = random.uniform(1, 2.5)
            self.alpha = random.randint(120, 255)
        elif style == "snow":
            self.vx = random.uniform(-0.3, 0.3)
            self.vy = random.uniform(0.5, 1.5)
            self.size = random.uniform(2, 4)
            self.alpha = random.randint(150, 255)
        elif style == "bubble":
            self.vx = random.uniform(-0.2, 0.2)
            self.vy = random.uniform(-0.6, -0.2)
            self.size = random.uniform(4, 10)
            self.alpha = random.randint(40, 100)
        else:
            self.vx = random.uniform(-0.5, 0.5)
            self.vy = random.uniform(-0.8, -0.2)
            self.size = random.uniform(1, 3)
            self.alpha = random.randint(50, 150)

    def update(self, w, h):
        self.x += self.vx
        self.y += self.vy

        if self.style in ("snow", "star"):
            if self.y > h:
                self.y = 0
                self.x = random.uniform(0, w)
            if self.x < 0:
                self.x = w
            elif self.x > w:
                self.x = 0
        elif self.style == "sparkle":
            self.twinkle += 0.1
        else:
            if self.y < -10:
                self.y = h
                self.x = random.uniform(0, w)
            if self.y > h + 10:
                self.y = 0
                self.x = random.uniform(0, w)
            if self.x < -10:
                self.x = w
            elif self.x > w + 10:
                self.x = 0

    def draw(self, surf):
        if self.style == "sparkle":
            import math
            alpha = int(self.alpha * (0.4 + 0.6 * abs(math.sin(self.twinkle))))
        else:
            alpha = self.alpha

        alpha = max(0, min(255, alpha))
        size = max(1, int(self.size))
        s = pygame.Surface((size * 2 + 2, size * 2 + 2), pygame.SRCALPHA)

        if self.style == "bubble":
            pygame.draw.circle(s, (*self.color, alpha), (size + 1, size + 1), size, width=2)
        else:
            pygame.draw.circle(s, (*self.color, alpha), (size + 1, size + 1), size)

        surf.blit(s, (self.x - size, self.y - size))


# Each independent particle-style animation: name -> (style, count, color_source)
PARTICLE_LAYERS = {
    "Background Particles": ("dot", 40),
    "Slow Particle Drift": ("slow_drift", 35),
    "Fast Particle Drift": ("fast_drift", 35),
    "Large Particles": ("large", 18),
    "Tiny Sparkle Particles": ("sparkle", 50),
    "Star Field Particles": ("star", 60),
    "Snow Particles": ("snow", 45),
    "Bubble Particles": ("bubble", 20),
}

particle_layers = {name: [] for name in PARTICLE_LAYERS}


def update_particles():
    w, h = get_screen_size()
    accent = get_accent()

    for name, (style, count) in PARTICLE_LAYERS.items():
        layer = particle_layers[name]
        target_count = count if anim_enabled(name) else 0

        if name == "Star Field Particles":
            color = (255, 255, 255)
        elif name == "Snow Particles":
            color = (255, 255, 255)
        elif anim_enabled("Particle Color Cycle"):
            import math
            t = (math.sin(rainbow_time + hash(name) % 10) + 1) / 2
            other = COLOR_POOL[(state.selected_color_idx + 3) % len(COLOR_POOL)]
            color = lerp_color(accent, other, t)
        else:
            color = accent

        while len(layer) < target_count:
            layer.append(Particle(color, w, h, style))
        while len(layer) > target_count:
            layer.pop()

        for p in layer:
            if name not in ("Star Field Particles", "Snow Particles"):
                p.color = color
            p.update(w, h)


def draw_particles(surf):
    for name in PARTICLE_LAYERS:
        if anim_enabled(name):
            for p in particle_layers[name]:
                p.draw(surf)


def clear_all_particles():
    for layer in particle_layers.values():
        layer.clear()


BG_BASE = (30, 30, 35)


def draw_diagonal_gradient(surf, color1, color2):
    w, h = surf.get_size()
    surf.fill(color2)
    steps = 40
    band_w = (w + h) / steps
    for i in range(steps):
        t = i / steps
        c = lerp_color(color1, color2, t)
        x = -h + i * band_w
        points = [(x, 0), (x + band_w + 1, 0), (x + band_w + 1 - h, h), (x - h, h)]
        pygame.draw.polygon(surf, c, points)


def draw_background(surf):
    accent = get_accent()
    w, h = surf.get_size()

    bg_base = BG_BASE
    if anim_enabled("Color Cycle Background Tint"):
        import math
        t = (math.sin(rainbow_time * 0.5) + 1) / 2
        tint = tuple(int(lerp(BG_BASE[i], accent[i] * 0.15, t)) for i in range(3))
        bg_base = tint

    if anim_enabled("Diagonal Gradient Background"):
        bg2 = tuple(min(255, c + 35) for c in bg_base)
        draw_diagonal_gradient(surf, bg_base, bg2)
    elif anim_enabled("Vertical Gradient Pulse"):
        import math
        pulse = (math.sin(pulse_time * 2) + 1) / 2
        bg2 = tuple(min(255, int(c + 15 + 25 * pulse)) for c in bg_base)
        draw_gradient_bg(surf, bg_base, bg2)
    elif anim_enabled("Gradient Background"):
        bg2 = tuple(min(255, c + 25) for c in bg_base)
        draw_gradient_bg(surf, bg_base, bg2)
    else:
        surf.fill(bg_base)

    draw_particles(surf)

    if anim_enabled("Background Vignette"):
        vignette = pygame.Surface((w, h), pygame.SRCALPHA)
        vignette.fill((0, 0, 0, 0))
        # Draw concentric dark rings from the edge inward, fading to transparent at center
        steps = 20
        for i in range(steps):
            t = i / steps  # 0 = edge, 1 = center
            alpha = int(160 * (1 - t))
            margin_x = int(w * 0.5 * t)
            margin_y = int(h * 0.5 * t)
            r = pygame.Rect(margin_x, margin_y, w - 2 * margin_x, h - 2 * margin_y)
            if r.width > 0 and r.height > 0:
                pygame.draw.rect(vignette, (0, 0, 0, alpha), r, width=max(1, w // (steps * 2)))
        surf.blit(vignette, (0, 0))

    if anim_enabled("Screen Border Glow"):
        glow_color = get_dynamic_accent()
        border_thickness = 6
        glow_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        for i in range(border_thickness):
            alpha = int(120 * (1 - i / border_thickness))
            pygame.draw.rect(glow_surf, (*glow_color, alpha), (i, i, w - 2 * i, h - 2 * i), width=1)
        surf.blit(glow_surf, (0, 0))


pulse_time = 0.0


def get_pulse_scale():
    if not anim_enabled("Pulse Effects"):
        return 1.0
    import math
    return 1.0 + 0.03 * math.sin(pulse_time * 3)


rainbow_time = 0.0


def get_dynamic_accent():
    import math

    if state.selected_color_idx == -1 and state.rainbow_unlocked:
        # Fast cycle through true rainbow hues
        n = len(RAINBOW_HUES)
        pos = (rainbow_time * 2.5) % n
        i = int(pos)
        t = pos - i
        c1 = RAINBOW_HUES[i]
        c2 = RAINBOW_HUES[(i + 1) % n]
        return lerp_color(c1, c2, t)

    if state.selected_color_idx >= LAVA_START_INDEX:
        lava_idx = state.selected_color_idx - LAVA_START_INDEX
        if 0 <= lava_idx < len(LAVA_COLOR_PAIRS):
            c1, c2 = LAVA_COLOR_PAIRS[lava_idx]
            t = (math.sin(rainbow_time * 2) + 1) / 2
            return lerp_color(c1, c2, t)

    return get_accent()


class Button:
    def __init__(self, rect_func, text, font=FONT_MED):
        self.rect_func = rect_func
        self.text = text
        self.font = font
        self.hover_t = 0.0
        self.ripples = []
        self.was_hovering = False

    def get_rect(self):
        return pygame.Rect(self.rect_func())

    def update(self, mouse_pos):
        rect = self.get_rect()
        hovering = rect.collidepoint(mouse_pos)
        target = 1.0 if hovering else 0.0

        if anim_enabled("Extra Smooth Easing"):
            speed = 0.05
        elif anim_enabled("Smooth Transitions"):
            speed = 0.15
        else:
            speed = 0.5

        self.hover_t = lerp(self.hover_t, target, speed)
        self.was_hovering = hovering

        for ripple in self.ripples:
            ripple["radius"] += 4
            ripple["alpha"] -= 8
        self.ripples = [r for r in self.ripples if r["alpha"] > 0]

    def trigger_ripple(self, pos):
        if anim_enabled("Button Ripple on Click"):
            self.ripples.append({"pos": pos, "radius": 0, "alpha": 180})

    def draw(self, surf):
        rect = self.get_rect()
        base_color = get_dynamic_accent()

        if anim_enabled("Hover Glow"):
            hover_color = tuple(min(255, int(c * 1.4) + 20) for c in base_color)
            color = lerp_color(base_color, hover_color, self.hover_t)
        else:
            color = base_color

        scale = 1.0
        if anim_enabled("Button Scale"):
            scale += 0.05 * self.hover_t
        scale *= get_pulse_scale()

        w = int(rect.width * scale)
        h = int(rect.height * scale)
        r = pygame.Rect(0, 0, w, h)
        r.center = rect.center

        angle = 0.0
        if anim_enabled("Button Spin on Hover"):
            angle = self.hover_t * 8  # degrees, subtle wobble

        if anim_enabled("Hover Glow") and self.hover_t > 0.01:
            glow_surf = pygame.Surface((w + 30, h + 30), pygame.SRCALPHA)
            glow_alpha = int(80 * self.hover_t)
            pygame.draw.rect(glow_surf, (*color, glow_alpha), (0, 0, w + 30, h + 30), border_radius=18)
            surf.blit(glow_surf, (r.x - 15, r.y - 15))

        if anim_enabled("Button Shadow Glow"):
            shadow_surf = pygame.Surface((w + 12, h + 12), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surf, (*color, 60), (0, 0, w + 12, h + 12), border_radius=14)
            surf.blit(shadow_surf, (r.x - 6, r.y - 2))

        if anim_enabled("Button Border Pulse"):
            import math
            pulse_alpha = int(150 + 105 * math.sin(pulse_time * 4))
            border_surf = pygame.Surface((w + 8, h + 8), pygame.SRCALPHA)
            pygame.draw.rect(border_surf, (*color, pulse_alpha), (0, 0, w + 8, h + 8), width=3, border_radius=14)
            surf.blit(border_surf, (r.x - 4, r.y - 4))

        if anim_enabled("Button Gradient Fill"):
            grad_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            top_color = color
            bottom_color = tuple(max(0, c - 60) for c in color)
            for yy in range(h):
                t = yy / h if h else 0
                line_color = lerp_color(top_color, bottom_color, t)
                pygame.draw.line(grad_surf, line_color, (0, yy), (w, yy))
            mask = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=12)
            grad_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            surf.blit(grad_surf, r.topleft)
        else:
            if angle != 0:
                temp = pygame.Surface((w, h), pygame.SRCALPHA)
                pygame.draw.rect(temp, color, (0, 0, w, h), border_radius=12)
                rotated = pygame.transform.rotate(temp, angle)
                rr = rotated.get_rect(center=r.center)
                surf.blit(rotated, rr.topleft)
            else:
                pygame.draw.rect(surf, color, r, border_radius=12)

        pygame.draw.rect(surf, WHITE, r, 2, border_radius=12)

        for ripple in self.ripples:
            ripple_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            local_pos = (ripple["pos"][0] - r.x, ripple["pos"][1] - r.y)
            pygame.draw.circle(ripple_surf, (255, 255, 255, max(0, ripple["alpha"])), local_pos, ripple["radius"], width=2)
            surf.blit(ripple_surf, r.topleft)

        txt_surf = self.font.render(self.text, True, WHITE)
        txt_rect = txt_surf.get_rect(center=r.center)
        surf.blit(txt_surf, txt_rect)

    def clicked(self, mouse_pos, event):
        is_click = event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.get_rect().collidepoint(mouse_pos)
        if is_click:
            self.trigger_ripple(mouse_pos)
        return is_click


class AdminPanel:
    def __init__(self):
        self.visible = False
        self.x = 100
        self.y = 100
        self.w = 400
        self.h = 580
        self.dragging = False
        self.drag_offset = (0, 0)
        self.points_input = ""
        self.input_active = False

    def toggle(self):
        self.visible = not self.visible

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def get_titlebar_rect(self):
        return pygame.Rect(self.x, self.y, self.w, 36)

    def handle_event(self, event, mouse_pos):
        if not self.visible:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            close_rect = pygame.Rect(self.x + self.w - 30, self.y + 4, 26, 26)
            if close_rect.collidepoint(mouse_pos):
                self.visible = False
                self.dragging = False
                return True

            titlebar = self.get_titlebar_rect()
            if titlebar.collidepoint(mouse_pos):
                self.dragging = True
                self.drag_offset = (mouse_pos[0] - self.x, mouse_pos[1] - self.y)
                return True

            input_rect = pygame.Rect(self.x + 20, self.y + 70, 200, 36)
            self.input_active = input_rect.collidepoint(mouse_pos)

            add_rect = pygame.Rect(self.x + 250, self.y + 70, 130, 36)
            if add_rect.collidepoint(mouse_pos):
                try:
                    val = int(self.points_input)
                except ValueError:
                    val = 0
                state.points += val
                self.points_input = ""
                return True

            unlock_rect = pygame.Rect(self.x + 20, self.y + 130, 360, 40)
            if unlock_rect.collidepoint(mouse_pos):
                state.tier = len(SHOP_TIERS) - 1
                return True

            delete_rect = pygame.Rect(self.x + 20, self.y + 185, 360, 40)
            if delete_rect.collidepoint(mouse_pos):
                state.points = 0
                return True

            for i, mode in enumerate(AUTO_TYPE_MODES):
                mode_rect = pygame.Rect(self.x + 20 + (i % 2) * 185, self.y + 280 + (i // 2) * 46, 175, 40)
                if mode_rect.collidepoint(mouse_pos):
                    state.auto_type_mode = mode
                    return True

            if self.get_rect().collidepoint(mouse_pos):
                return True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False

        if event.type == pygame.MOUSEMOTION and self.dragging:
            self.x = mouse_pos[0] - self.drag_offset[0]
            self.y = mouse_pos[1] - self.drag_offset[1]

        if event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_BACKSPACE:
                self.points_input = self.points_input[:-1]
            elif event.key == pygame.K_RETURN:
                try:
                    val = int(self.points_input)
                except ValueError:
                    val = 0
                state.points += val
                self.points_input = ""
            elif event.unicode.isdigit() or (event.unicode == "-" and not self.points_input):
                self.points_input += event.unicode
            return True

        return False

    def draw(self, surf):
        if not self.visible:
            return

        rect = self.get_rect()
        pygame.draw.rect(surf, (25, 25, 30), rect, border_radius=10)
        pygame.draw.rect(surf, (255, 80, 80), rect, 2, border_radius=10)

        titlebar = self.get_titlebar_rect()
        pygame.draw.rect(surf, (50, 20, 20), titlebar, border_top_left_radius=10, border_top_right_radius=10)
        title_surf = FONT_SMALL.render("Admin Panel (drag to move)", True, WHITE)
        surf.blit(title_surf, (rect.x + 10, rect.y + 6))

        close_rect = pygame.Rect(rect.x + rect.w - 30, rect.y + 4, 26, 26)
        pygame.draw.rect(surf, (180, 50, 50), close_rect, border_radius=6)
        x_surf = FONT_SMALL.render("X", True, WHITE)
        surf.blit(x_surf, x_surf.get_rect(center=close_rect.center))

        label = FONT_SMALL.render("Add/Remove Points:", True, WHITE)
        surf.blit(label, (rect.x + 20, rect.y + 48))

        input_rect = pygame.Rect(rect.x + 20, rect.y + 70, 200, 36)
        input_color = (60, 60, 70) if self.input_active else (40, 40, 48)
        pygame.draw.rect(surf, input_color, input_rect, border_radius=6)
        pygame.draw.rect(surf, WHITE, input_rect, 1, border_radius=6)
        disp = self.points_input if self.points_input else "Type amount..."
        disp_color = WHITE if self.points_input else GRAY
        input_text = FONT_SMALL.render(disp, True, disp_color)
        surf.blit(input_text, (input_rect.x + 8, input_rect.y + 6))

        add_rect = pygame.Rect(rect.x + 250, rect.y + 70, 130, 36)
        pygame.draw.rect(surf, (80, 180, 120), add_rect, border_radius=6)
        add_text = FONT_SMALL.render("Apply", True, WHITE)
        surf.blit(add_text, add_text.get_rect(center=add_rect.center))

        unlock_rect = pygame.Rect(rect.x + 20, rect.y + 130, 360, 40)
        pygame.draw.rect(surf, (80, 120, 220), unlock_rect, border_radius=6)
        unlock_text = FONT_SMALL.render("Unlock Everything", True, WHITE)
        surf.blit(unlock_text, unlock_text.get_rect(center=unlock_rect.center))

        delete_rect = pygame.Rect(rect.x + 20, rect.y + 185, 360, 40)
        pygame.draw.rect(surf, (200, 70, 70), delete_rect, border_radius=6)
        delete_text = FONT_SMALL.render("Delete All Points", True, WHITE)
        surf.blit(delete_text, delete_text.get_rect(center=delete_rect.center))

        autotype_label = FONT_SMALL.render(f"Auto-Type Mode: {state.auto_type_mode}", True, WHITE)
        surf.blit(autotype_label, (rect.x + 20, rect.y + 240))

        for i, mode in enumerate(AUTO_TYPE_MODES):
            mode_rect = pygame.Rect(rect.x + 20 + (i % 2) * 185, rect.y + 280 + (i // 2) * 46, 175, 40)
            active = state.auto_type_mode == mode
            color = (90, 200, 110) if active else (50, 50, 58)
            pygame.draw.rect(surf, color, mode_rect, border_radius=6)
            pygame.draw.rect(surf, WHITE, mode_rect, 1, border_radius=6)
            mode_text = FONT_SMALL.render(mode, True, WHITE)
            surf.blit(mode_text, mode_text.get_rect(center=mode_rect.center))

        pts_text = FONT_SMALL.render(f"Current Points: {state.points}", True, (255, 215, 80))
        surf.blit(pts_text, (rect.x + 20, rect.y + 540))


admin_panel = AdminPanel()


notifications = []

def push_notification(text, color=None):
    if color is None:
        color = get_dynamic_accent()
    notifications.append({"text": text, "timer": 180, "alpha": 255, "color": color})

def draw_notifications(surf):
    w, h = surf.get_size()
    to_remove = []
    y = h - 50
    for n in reversed(notifications):
        n["timer"] -= 1
        if n["timer"] <= 0:
            to_remove.append(n)
            continue
        if n["timer"] < 40:
            n["alpha"] = int(255 * (n["timer"] / 40))
        bg = pygame.Surface((400, 36), pygame.SRCALPHA)
        pygame.draw.rect(bg, (20, 20, 28, min(220, n["alpha"])), (0, 0, 400, 36), border_radius=8)
        pygame.draw.rect(bg, (*n["color"], min(200, n["alpha"])), (0, 0, 400, 36), width=2, border_radius=8)
        surf.blit(bg, (w - 420, y - 36))
        txt = FONT_SMALL.render(n["text"], True, (*WHITE, n["alpha"]))
        surf.blit(txt, (w - 415, y - 30))
        y -= 44
    for n in to_remove:
        notifications.remove(n)


def fade_transition(direction="out", speed=8):
    """Fade screen to black (out) or from black (in)."""
    w, h = get_screen_size()
    overlay = pygame.Surface((w, h))
    overlay.fill(BLACK)
    steps = 255 // speed
    rng = range(0, 256, speed) if direction == "out" else range(255, -1, -speed)
    for alpha in rng:
        overlay.set_alpha(alpha)
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


def intro_screen():
    start = pygame.time.get_ticks()
    running = True
    while running:
        w, h = get_screen_size()
        title_text = "Speed Typing Game"
        title_surf = FONT_TITLE.render(title_text, True, WHITE)
        title_rect = title_surf.get_rect(center=(w // 2, h // 2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                running = False

        elapsed = pygame.time.get_ticks() - start
        screen.fill(BLACK)

        if elapsed < 1000:
            alpha = int(255 * (elapsed / 1000))
        elif elapsed < 1800:
            alpha = 255
        else:
            running = False
            alpha = 255

        title_alpha_surf = title_surf.copy()
        title_alpha_surf.set_alpha(alpha)
        screen.blit(title_alpha_surf, title_rect)

        hint = FONT_SMALL.render("Press any key to continue...", True, (alpha, alpha, alpha))
        hint_rect = hint.get_rect(center=(w // 2, h // 2 + 100))
        screen.blit(hint, hint_rect)

        pygame.display.flip()
        clock.tick(60)


def main_menu():
    global pulse_time, rainbow_time

    def r_easy():
        w, h = get_screen_size()
        return (w // 2 - 150, h // 2 - 230, 300, 60)

    def r_medium():
        w, h = get_screen_size()
        return (w // 2 - 150, h // 2 - 150, 300, 60)

    def r_hard():
        w, h = get_screen_size()
        return (w // 2 - 150, h // 2 - 70, 300, 60)

    def r_shop():
        w, h = get_screen_size()
        return (w // 2 - 150, h // 2 + 10, 300, 60)

    def r_fullscreen():
        w, h = get_screen_size()
        return (w // 2 - 150, h // 2 + 90, 300, 60)

    def r_quit():
        w, h = get_screen_size()
        return (w // 2 - 150, h // 2 + 170, 300, 60)

    def r_reset():
        w, h = get_screen_size()
        return (w - 200, h - 65, 180, 48)

    btn_easy = Button(r_easy, "Easy")
    btn_medium = Button(r_medium, "Medium")
    btn_hard = Button(r_hard, "Hard")
    btn_shop = Button(r_shop, "Shop")
    btn_fullscreen = Button(r_fullscreen, "Toggle Fullscreen")
    btn_quit = Button(r_quit, "Quit")
    btn_reset = Button(r_reset, "Reset Progress", FONT_SMALL)

    buttons = [btn_easy, btn_medium, btn_hard, btn_shop, btn_fullscreen, btn_quit]

    promo_input = ""
    promo_active = False
    promo_message = ""
    promo_message_timer = 0

    show_reset_confirm = False

    while True:
        mouse_pos = pygame.mouse.get_pos()
        w, h = get_screen_size()
        pulse_time += 1 / 60
        rainbow_time += 1 / 60
        update_particles()
        draw_background(screen)
        accent = get_dynamic_accent()

        title_text = "Speed Typing Game"
        title_y = h // 2 - 330

        if anim_enabled("Floating Title Animation"):
            import math
            title_y += int(8 * math.sin(pulse_time * 1.5))

        if anim_enabled("Wavy Text Effect"):
            import math
            x_cursor = w // 2 - FONT_LARGE.size(title_text)[0] // 2
            for i, ch in enumerate(title_text):
                ch_surf = FONT_LARGE.render(ch, True, WHITE)
                offset_y = int(10 * math.sin(pulse_time * 3 + i * 0.4))
                screen.blit(ch_surf, (x_cursor, title_y + offset_y))
                x_cursor += ch_surf.get_width()
        else:
            title = FONT_LARGE.render(title_text, True, WHITE)
            title_rect = title.get_rect(center=(w // 2, title_y))

            if anim_enabled("Title Shadow Pulse"):
                import math
                shadow_alpha = int(80 + 60 * math.sin(pulse_time * 2))
                shadow_surf = FONT_LARGE.render(title_text, True, (0, 0, 0))
                shadow_surf.set_alpha(shadow_alpha)
                screen.blit(shadow_surf, (title_rect.x + 4, title_rect.y + 4))

            if anim_enabled("Title Glow Pulse"):
                import math
                glow_amount = int(2 + 2 * abs(math.sin(pulse_time * 2)))
                draw_text_glow(screen, title_text, FONT_LARGE, WHITE, title_rect.topleft, accent, glow_amount)
            elif anim_enabled("Hover Glow"):
                draw_text_glow(screen, title_text, FONT_LARGE, WHITE, title_rect.topleft, accent, 2)
            else:
                screen.blit(title, title_rect)

        points_text_str = f"Points: {state.points}"
        points_color = accent
        points_scale = 1.0
        if anim_enabled("Pulsing Points Display"):
            import math
            points_scale = 1.0 + 0.08 * abs(math.sin(pulse_time * 2))
        points_font = FONT_MED
        if points_scale != 1.0:
            base_surf = points_font.render(points_text_str, True, points_color)
            new_w = int(base_surf.get_width() * points_scale)
            new_h = int(base_surf.get_height() * points_scale)
            points_text = pygame.transform.smoothscale(base_surf, (max(1, new_w), max(1, new_h)))
        else:
            points_text = points_font.render(points_text_str, True, points_color)
        screen.blit(points_text, (20, 20))

        tier_text = FONT_SMALL.render(f"Upgrade Tier: {state.tier}/{len(SHOP_TIERS)-1}", True, WHITE)
        screen.blit(tier_text, (20, 60))

        # High scores
        hs_y = 95
        hs_label = FONT_SMALL.render("Best Scores:", True, GRAY)
        screen.blit(hs_label, (20, hs_y))
        for lvl, label in [("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")]:
            hs_y += 26
            hs_val = state.high_scores.get(lvl, 0)
            hs_surf = FONT_SMALL.render(f"  {label}: {hs_val}", True, accent)
            screen.blit(hs_surf, (20, hs_y))

        fs_text = FONT_SMALL.render("Press F11 fullscreen  |  ESC quit", True, GRAY)
        screen.blit(fs_text, (20, h - 30))

        for b in buttons:
            b.update(mouse_pos)
            b.draw(screen)

        btn_reset.update(mouse_pos)
        btn_reset.draw(screen)

        # Promo code input box
        promo_rect = pygame.Rect(20, h - 70, 260, 36)
        pygame.draw.rect(screen, (40, 40, 48), promo_rect, border_radius=6)
        pygame.draw.rect(screen, (100, 100, 110), promo_rect, 1, border_radius=6)
        promo_disp = promo_input if promo_input else "Enter promo code..."
        promo_disp_color = WHITE if promo_input else GRAY
        promo_text = FONT_SMALL.render(promo_disp, True, promo_disp_color)
        screen.blit(promo_text, (promo_rect.x + 8, promo_rect.y + 6))

        if promo_message_timer > 0:
            promo_message_timer -= 1
            msg_surf = FONT_SMALL.render(promo_message, True, GREEN)
            screen.blit(msg_surf, (promo_rect.x, promo_rect.y - 28))

        admin_panel.draw(screen)
        draw_notifications(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_config()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                toggle_fullscreen()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                save_config()
                pygame.quit()
                sys.exit()

            if admin_panel.handle_event(event, mouse_pos):
                continue

            if show_reset_confirm:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    yes_rect = pygame.Rect(w // 2 - 130, h // 2 + 40, 110, 44)
                    no_rect = pygame.Rect(w // 2 + 20, h // 2 + 40, 110, 44)
                    if yes_rect.collidepoint(mouse_pos):
                        reset_game()
                        show_reset_confirm = False
                        push_notification("Progress reset!", RED)
                    elif no_rect.collidepoint(mouse_pos):
                        show_reset_confirm = False
                continue

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                promo_active = promo_rect.collidepoint(mouse_pos)

            if event.type == pygame.KEYDOWN and promo_active:
                if event.key == pygame.K_BACKSPACE:
                    promo_input = promo_input[:-1]
                elif event.key == pygame.K_RETURN:
                    code = promo_input.strip().lower()
                    if code == "admin":
                        admin_panel.visible = True
                        promo_message = "Admin panel opened!"
                    elif code in ("free", "summer"):
                        if code in state.used_promo_codes:
                            promo_message = "Code already used"
                        else:
                            if code == "free":
                                state.points += 100
                                promo_message = "+100 points!"
                                push_notification("Promo 'free': +100 points!", GREEN)
                            else:
                                state.points += 50
                                promo_message = "+50 points!"
                                push_notification("Promo 'summer': +50 points!", GREEN)
                            state.used_promo_codes.add(code)
                            save_config()
                    elif code:
                        promo_message = "Invalid code"
                    promo_message_timer = 120
                    promo_input = ""
                elif event.unicode.isprintable() and len(promo_input) < 24:
                    promo_input += event.unicode

            if btn_easy.clicked(mouse_pos, event):
                fade_transition("out")
                play_game("easy")
                fade_transition("in")
            if btn_medium.clicked(mouse_pos, event):
                fade_transition("out")
                play_game("medium")
                fade_transition("in")
            if btn_hard.clicked(mouse_pos, event):
                fade_transition("out")
                play_game("hard")
                fade_transition("in")
            if btn_shop.clicked(mouse_pos, event):
                fade_transition("out")
                shop_screen()
                fade_transition("in")
            if btn_fullscreen.clicked(mouse_pos, event):
                toggle_fullscreen()
            if btn_quit.clicked(mouse_pos, event):
                save_config()
                pygame.quit()
                sys.exit()
            if btn_reset.clicked(mouse_pos, event):
                show_reset_confirm = True

        if show_reset_confirm:
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            box_rect = pygame.Rect(w // 2 - 220, h // 2 - 80, 440, 200)
            pygame.draw.rect(screen, (35, 35, 42), box_rect, border_radius=12)
            pygame.draw.rect(screen, RED, box_rect, 2, border_radius=12)

            msg1 = FONT_MED.render("Reset all progress?", True, WHITE)
            screen.blit(msg1, (box_rect.centerx - msg1.get_width() // 2, box_rect.y + 30))
            msg2 = FONT_SMALL.render("This cannot be undone.", True, GRAY)
            screen.blit(msg2, (box_rect.centerx - msg2.get_width() // 2, box_rect.y + 75))

            yes_rect = pygame.Rect(w // 2 - 130, h // 2 + 40, 110, 44)
            no_rect = pygame.Rect(w // 2 + 20, h // 2 + 40, 110, 44)
            pygame.draw.rect(screen, RED, yes_rect, border_radius=8)
            pygame.draw.rect(screen, (80, 120, 220), no_rect, border_radius=8)
            yes_text = FONT_SMALL.render("Yes, Reset", True, WHITE)
            no_text = FONT_SMALL.render("Cancel", True, WHITE)
            screen.blit(yes_text, yes_text.get_rect(center=yes_rect.center))
            screen.blit(no_text, no_text.get_rect(center=no_rect.center))

        pygame.display.flip()
        clock.tick(60)


def shop_screen():
    global pulse_time, rainbow_time

    def r_back():
        return (20, 20, 150, 50)

    btn_back = Button(r_back, "Back", FONT_SMALL)
    shop_scroll = 0

    while True:
        mouse_pos = pygame.mouse.get_pos()
        w, h = get_screen_size()
        pulse_time += 1 / 60
        rainbow_time += 1 / 60
        update_particles()
        draw_background(screen)
        accent = get_dynamic_accent()

        title = FONT_MED.render("Shop - Upgrades", True, WHITE)
        screen.blit(title, (w // 2 - title.get_width() // 2, 30))

        points_text = FONT_SMALL.render(f"Points: {state.points}", True, accent)
        screen.blit(points_text, (w - 220, 30))

        btn_back.update(mouse_pos)
        btn_back.draw(screen)

        next_tier = state.tier + 1
        upgrade_rect = pygame.Rect(w // 2 - 280, 100, 560, 100)
        pygame.draw.rect(screen, (45, 45, 55), upgrade_rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, upgrade_rect, 2, border_radius=10)

        buy_rect = None
        if next_tier < len(SHOP_TIERS):
            cost = SHOP_TIERS[next_tier]["cost"]
            if next_tier - 1 < len(ANIMATION_POOL):
                anim_name = f"+ '{ANIMATION_POOL[next_tier-1]}'"
            else:
                anim_name = "(color only)"
            info = FONT_SMALL.render(
                f"Upgrade {next_tier}: Unlocks {next_tier+1} colors {anim_name}",
                True, WHITE
            )
            screen.blit(info, (upgrade_rect.x + 15, upgrade_rect.y + 12))
            cost_text = FONT_SMALL.render(f"Cost: {cost} pts", True, accent)
            screen.blit(cost_text, (upgrade_rect.x + 15, upgrade_rect.y + 42))

            buy_rect = pygame.Rect(upgrade_rect.right - 150, upgrade_rect.y + 45, 130, 44)
            can_afford = state.points >= cost
            buy_color = accent if can_afford else GRAY
            pygame.draw.rect(screen, buy_color, buy_rect, border_radius=8)
            pygame.draw.rect(screen, WHITE, buy_rect, 2, border_radius=8)
            buy_text = FONT_SMALL.render("Upgrade", True, WHITE)
            screen.blit(buy_text, buy_text.get_rect(center=buy_rect.center))
        else:
            max_rect = pygame.Rect(upgrade_rect.x + 15, upgrade_rect.y + 15, upgrade_rect.width - 30, upgrade_rect.height - 30)
            pygame.draw.rect(screen, (30, 60, 40), max_rect, border_radius=8)
            line1 = FONT_SMALL.render("Max tier reached!", True, GREEN)
            line2 = FONT_SMALL.render("All colors & animations unlocked.", True, GREEN)
            screen.blit(line1, (max_rect.centerx - line1.get_width() // 2, max_rect.centery - line1.get_height()))
            screen.blit(line2, (max_rect.centerx - line2.get_width() // 2, max_rect.centery + 2))

        color_label = FONT_SMALL.render("Choose Accent Color:", True, WHITE)
        screen.blit(color_label, (w // 2 - 280, 220))

        colors = get_unlocked_colors()
        color_rects = []
        rainbow_swatch_rect = None
        panel_left = w // 2 - 280
        panel_width = 560
        cols_per_row = max(1, panel_width // 42)
        for i, c in enumerate(colors):
            # Lava colors: animate the swatch between their pair
            if i >= LAVA_START_INDEX:
                lava_idx = i - LAVA_START_INDEX
                c1, c2 = LAVA_COLOR_PAIRS[lava_idx]
                import math
                t = (math.sin(rainbow_time * 2 + lava_idx * 0.8) + 1) / 2
                draw_c = lerp_color(c1, c2, t)
            else:
                draw_c = c
            cx = panel_left + (i % cols_per_row) * 42
            cy = 248 + (i // cols_per_row) * 42
            crect = pygame.Rect(cx, cy, 32, 32)
            pygame.draw.rect(screen, draw_c, crect, border_radius=6)
            if i == state.selected_color_idx:
                pygame.draw.rect(screen, WHITE, crect, 3, border_radius=6)
            else:
                pygame.draw.rect(screen, (80, 80, 80), crect, 1, border_radius=6)
            color_rects.append(crect)

        # Rainbow special color swatch
        rb_buy_rect = None
        color_rows = (len(colors) + cols_per_row - 1) // cols_per_row
        rainbow_y = 248 + color_rows * 42 + 8
        rbow_x = panel_left
        if state.rainbow_unlocked:
            import math
            n = len(RAINBOW_HUES)
            pos = (rainbow_time * 2.5) % n
            ri = int(pos)
            rbow_c = lerp_color(RAINBOW_HUES[ri], RAINBOW_HUES[(ri + 1) % n], pos - ri)
            rainbow_swatch_rect = pygame.Rect(rbow_x, rainbow_y, 80, 32)
            pygame.draw.rect(screen, rbow_c, rainbow_swatch_rect, border_radius=6)
            label = FONT_SMALL.render("Rainbow", True, WHITE)
            screen.blit(label, (rbow_x + 88, rainbow_y + 6))
            if state.selected_color_idx == -1:
                pygame.draw.rect(screen, WHITE, rainbow_swatch_rect, 3, border_radius=6)
            else:
                pygame.draw.rect(screen, (80, 80, 80), rainbow_swatch_rect, 1, border_radius=6)
            anim_section_y = rainbow_y + 46
        else:
            # Show rainbow locked with buy button
            rainbow_swatch_rect = pygame.Rect(rbow_x, rainbow_y, 80, 32)
            # Draw rainbow gradient preview
            rbow_preview = pygame.Surface((80, 32))
            for rx in range(80):
                t = rx / 80 * (len(RAINBOW_HUES) - 1)
                ri = int(t)
                rc = lerp_color(RAINBOW_HUES[ri], RAINBOW_HUES[min(ri + 1, len(RAINBOW_HUES)-1)], t - ri)
                pygame.draw.line(rbow_preview, rc, (rx, 0), (rx, 32))
            screen.blit(rbow_preview, (rbow_x, rainbow_y))
            pygame.draw.rect(screen, GRAY, rainbow_swatch_rect, 1, border_radius=6)
            lock_label = FONT_SMALL.render(f"Rainbow — {RAINBOW_COST} pts", True, GRAY)
            screen.blit(lock_label, (rbow_x + 88, rainbow_y + 2))
            can_afford_rb = state.points >= RAINBOW_COST
            rb_buy_rect = pygame.Rect(rbow_x + 88 + lock_label.get_width() + 12, rainbow_y, 70, 32)
            rb_color = accent if can_afford_rb else GRAY
            pygame.draw.rect(screen, rb_color, rb_buy_rect, border_radius=6)
            rb_text = FONT_SMALL.render("Buy", True, WHITE)
            screen.blit(rb_text, rb_text.get_rect(center=rb_buy_rect.center))
            anim_section_y = rainbow_y + 46

        esc_hint = FONT_SMALL.render("Press ESC to exit", True, GRAY)
        screen.blit(esc_hint, (w // 2 - esc_hint.get_width() // 2, h - 24))

        anim_label = FONT_SMALL.render("Animations (click to toggle, scroll for more):", True, WHITE)
        screen.blit(anim_label, (w // 2 - 280, anim_section_y))

        # Scrollable animation list area
        list_top = anim_section_y + 32
        list_bottom = h - 32
        clip_rect = pygame.Rect(w // 2 - 280, list_top, 560, list_bottom - list_top)
        old_clip = screen.get_clip()
        screen.set_clip(clip_rect)

        unlocked_anims = get_unlocked_animations()
        anim_rects = []
        anim_cols = 2
        col_width = 280
        row_height = 32
        for i, name in enumerate(ANIMATION_POOL):
            col = i % anim_cols
            row = i // anim_cols
            ax = w // 2 - 280 + col * col_width
            ay = list_top + row * row_height - shop_scroll
            unlocked = name in unlocked_anims
            active = name in state.active_animations and unlocked
            box_rect = pygame.Rect(ax, ay, 22, 22)
            if unlocked:
                box_color = accent if active else (60, 60, 60)
            else:
                box_color = (30, 30, 30)
            pygame.draw.rect(screen, box_color, box_rect, border_radius=4)
            pygame.draw.rect(screen, WHITE if unlocked else GRAY, box_rect, 2, border_radius=4)
            text_color = WHITE if unlocked else GRAY
            name_text = FONT_SMALL.render(name, True, text_color)
            screen.blit(name_text, (ax + 30, ay - 2))
            anim_rects.append((box_rect, name, unlocked))

        screen.set_clip(old_clip)
        max_scroll = max(0, ((len(ANIMATION_POOL) + anim_cols - 1) // anim_cols) * row_height - clip_rect.height)

        admin_panel.draw(screen)
        draw_notifications(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_config()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                toggle_fullscreen()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                save_config()
                return

            if admin_panel.handle_event(event, mouse_pos):
                continue

            if btn_back.clicked(mouse_pos, event):
                save_config()
                return

            if event.type == pygame.MOUSEWHEEL:
                shop_scroll -= event.y * 25
                shop_scroll = max(0, min(shop_scroll, max_scroll))

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if next_tier < len(SHOP_TIERS) and buy_rect and buy_rect.collidepoint(mouse_pos):
                    cost = SHOP_TIERS[next_tier]["cost"]
                    if state.points >= cost:
                        state.points -= cost
                        state.tier = next_tier
                        clear_all_particles()
                        anim_unlocked = ANIMATION_POOL[next_tier - 1] if next_tier - 1 < len(ANIMATION_POOL) else None
                        msg = f"Tier {next_tier} unlocked!"
                        if anim_unlocked:
                            msg += f" '{anim_unlocked}' available"
                        push_notification(msg, accent)
                        save_config()

                if not state.rainbow_unlocked and rb_buy_rect and rb_buy_rect.collidepoint(mouse_pos):
                    if state.points >= RAINBOW_COST:
                        state.points -= RAINBOW_COST
                        state.rainbow_unlocked = True
                        state.selected_color_idx = -1
                        push_notification("Rainbow color unlocked!", (255, 127, 0))
                        save_config()

                if state.rainbow_unlocked and rainbow_swatch_rect and rainbow_swatch_rect.collidepoint(mouse_pos):
                    state.selected_color_idx = -1
                    save_config()

                for i, crect in enumerate(color_rects):
                    if crect.collidepoint(mouse_pos):
                        state.selected_color_idx = i
                        save_config()

                if clip_rect.collidepoint(mouse_pos):
                    for box_rect, name, unlocked in anim_rects:
                        if unlocked and box_rect.collidepoint(mouse_pos):
                            if name in state.active_animations:
                                state.active_animations.discard(name)
                                push_notification(f"'{name}' off", GRAY)
                            else:
                                state.active_animations.add(name)
                                push_notification(f"'{name}' on", accent)
                            clear_all_particles()
                            save_config()

        pygame.display.flip()
        clock.tick(60)


def render_wrapped_sentence(surf, sentence, typed, font, center_x, start_y, max_width, shake_x=0):
    words = sentence.split(" ")
    lines = []
    current_line = ""
    for word in words:
        candidate = (current_line + " " + word).strip()
        if font.size(candidate)[0] > max_width and current_line:
            lines.append(current_line)
            current_line = word
        else:
            current_line = candidate
    if current_line:
        lines.append(current_line)

    char_index = 0
    line_height = font.get_linesize() + 6
    y = start_y
    for line in lines:
        line_width = font.size(line)[0]
        x = center_x - line_width // 2 + shake_x
        for ch in line:
            if char_index < len(typed):
                color = GREEN if typed[char_index] == ch else RED
            else:
                color = WHITE
            ch_surf = font.render(ch, True, color)
            surf.blit(ch_surf, (x, y))
            x += ch_surf.get_width()
            char_index += 1
        char_index += 1  # account for space between words
        y += line_height
    return y


def play_game(level):
    global pulse_time, rainbow_time

    sentence = gen_sentence(level)
    typed = ""
    start_time = None
    finished = False
    result_message = ""
    shake_offset = 0
    confetti_particles = []
    auto_type_timer = 0.0
    win_shake_timer = 0

    sentence_font = FONT_MED if level != "hard" else FONT_SMALL

    def r_back():
        return (20, 20, 150, 50)

    btn_back = Button(r_back, "Back", FONT_SMALL)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        w, h = get_screen_size()
        pulse_time += 1 / 60
        rainbow_time += 1 / 60
        update_particles()
        draw_background(screen)
        accent = get_dynamic_accent()

        btn_back.update(mouse_pos)
        btn_back.draw(screen)

        level_text = FONT_SMALL.render(f"Level: {level.capitalize()}", True, accent)
        screen.blit(level_text, (w - 220, 30))

        points_text = FONT_SMALL.render(f"Points: {state.points}", True, accent)
        screen.blit(points_text, (w - 220, 60))

        instruction = FONT_SMALL.render("Type the sentence below exactly, then press Enter:", True, WHITE)
        screen.blit(instruction, (w // 2 - instruction.get_width() // 2, 130))

        if shake_offset > 0:
            shake_x = random.randint(-shake_offset, shake_offset)
            shake_offset = max(0, shake_offset - 1)
        else:
            shake_x = 0

        sentence_y = 200
        max_text_width = min(w - 80, 760)

        win_shake_x = 0
        if win_shake_timer > 0:
            win_shake_x = random.randint(-6, 6)
            win_shake_timer -= 1

        bottom_y = render_wrapped_sentence(screen, sentence, typed, sentence_font, w // 2, sentence_y, max_text_width, shake_x + win_shake_x)

        typed_x_center = w // 2 + shake_x + win_shake_x
        typed_surf = FONT_MED.render(typed, True, accent)
        typed_x = typed_x_center - typed_surf.get_width() // 2
        typed_y = bottom_y + 20

        if anim_enabled("Typed Text Glow") and typed:
            draw_text_glow(screen, typed, FONT_MED, accent, (typed_x, typed_y), accent, 2)
        else:
            screen.blit(typed_surf, (typed_x, typed_y))

        if not finished:
            if start_time:
                elapsed = time.time() - start_time
                timer_surf = FONT_SMALL.render(f"Time: {elapsed:.2f}s", True, WHITE)
                screen.blit(timer_surf, (20, 60))

            if state.auto_type_mode != "Off":
                if state.auto_type_mode == "Instant":
                    if start_time is None:
                        start_time = time.time()
                    typed = sentence
                else:
                    auto_type_timer -= 1 / 60
                    if auto_type_timer <= 0 and len(typed) < len(sentence):
                        if start_time is None:
                            start_time = time.time()
                        typed += sentence[len(typed)]
                        auto_type_timer = AUTO_TYPE_SPEEDS[state.auto_type_mode]
                if len(typed) >= len(sentence) and typed == sentence:
                    elapsed = time.time() - start_time if start_time else 1.0
                    _, multiplier = LEVELS[level]
                    base_points = len(sentence.split()) * 1.5 * multiplier
                    speed_bonus = max(0, (20 - elapsed)) * 0.75 * multiplier
                    result_points = base_points + speed_bonus
                    if elapsed < 15:
                        result_points *= 1.25
                    result_points = max(1, int(result_points))
                    state.points += result_points
                    # High score
                    new_best = result_points > state.high_scores.get(level, 0)
                    if new_best:
                        state.high_scores[level] = result_points
                        push_notification(f"New {level.capitalize()} best: {result_points} pts!", (255, 215, 80))
                    result_message = f"Correct! +{result_points} pts (Time: {elapsed:.2f}s)"
                    if new_best:
                        result_message += "  NEW BEST!"
                    finished = True
                    if anim_enabled("Shake on Win"):
                        win_shake_timer = 15
                    save_config()
        else:
            if anim_enabled("Rainbow Text on Win"):
                import math
                x_cursor = w // 2 - FONT_MED.size(result_message)[0] // 2
                for i, ch in enumerate(result_message):
                    t = (math.sin(rainbow_time * 2 + i * 0.3) + 1) / 2
                    ch_color = lerp_color(accent, COLOR_POOL[(state.selected_color_idx + 2) % len(COLOR_POOL)] if state.selected_color_idx >= 0 else (255, 100, 100), t)
                    ch_surf = FONT_MED.render(ch, True, ch_color)
                    screen.blit(ch_surf, (x_cursor, typed_y + 60))
                    x_cursor += ch_surf.get_width()
            else:
                res_surf = FONT_MED.render(result_message, True, GREEN)
                screen.blit(res_surf, (w // 2 - res_surf.get_width() // 2, typed_y + 60))

            cont_surf = FONT_SMALL.render("Press Enter to continue", True, WHITE)
            screen.blit(cont_surf, (w // 2 - cont_surf.get_width() // 2, typed_y + 110))

            if anim_enabled("Confetti on Win"):
                target_confetti = 120 if anim_enabled("Double Confetti Burst") else 60
                if not confetti_particles:
                    for _ in range(target_confetti):
                        confetti_particles.append({
                            "x": random.uniform(0, w),
                            "y": random.uniform(-h, 0),
                            "vy": random.uniform(2, 6),
                            "color": random.choice(get_unlocked_colors()),
                            "size": random.randint(3, 7),
                        })
                for cp in confetti_particles:
                    cp["y"] += cp["vy"]
                    if cp["y"] > h:
                        cp["y"] = random.uniform(-50, 0)
                        cp["x"] = random.uniform(0, w)
                    pygame.draw.rect(screen, cp["color"], (cp["x"], cp["y"], cp["size"], cp["size"]))

        # Bottom hints
        esc_text = FONT_SMALL.render("Press ESC to exit", True, GRAY)
        screen.blit(esc_text, (w // 2 - esc_text.get_width() // 2, h - 24))
        ctrl_text = FONT_SMALL.render("Press CTRL to reset level", True, GRAY)
        screen.blit(ctrl_text, (w // 2 - ctrl_text.get_width() // 2, h - 48))

        admin_panel.draw(screen)
        draw_notifications(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_config()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                toggle_fullscreen()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_LCTRL, pygame.K_RCTRL):
                # Reset level
                sentence = gen_sentence(level)
                typed = ""
                start_time = None
                finished = False
                result_message = ""
                shake_offset = 0
                confetti_particles = []
                auto_type_timer = 0.0
                win_shake_timer = 0
                cursor_trail = []

            if admin_panel.handle_event(event, mouse_pos):
                continue

            if btn_back.clicked(mouse_pos, event):
                return
            if event.type == pygame.KEYDOWN:
                if not finished:
                    if state.auto_type_mode != "Off":
                        continue
                    if event.key == pygame.K_BACKSPACE:
                        typed = typed[:-1]
                    elif event.key == pygame.K_RETURN:
                        if typed == sentence:
                            elapsed = time.time() - start_time if start_time else 1.0
                            _, multiplier = LEVELS[level]
                            base_points = len(sentence.split()) * 1.5 * multiplier
                            speed_bonus = max(0, (20 - elapsed)) * 0.75 * multiplier
                            result_points = base_points + speed_bonus
                            if elapsed < 15:
                                result_points *= 1.25
                            result_points = max(1, int(result_points))
                            state.points += result_points
                            new_best = result_points > state.high_scores.get(level, 0)
                            if new_best:
                                state.high_scores[level] = result_points
                                push_notification(f"New {level.capitalize()} best: {result_points} pts!", (255, 215, 80))
                            result_message = f"Correct! +{result_points} pts (Time: {elapsed:.2f}s)"
                            if new_best:
                                result_message += "  NEW BEST!"
                            finished = True
                            if anim_enabled("Shake on Win"):
                                win_shake_timer = 15
                            save_config()
                        else:
                            result_message = "Not accurate yet, keep typing..."
                            if anim_enabled("Screen Shake on Type Error"):
                                shake_offset = 8
                    elif event.key not in (pygame.K_ESCAPE, pygame.K_LCTRL, pygame.K_RCTRL):
                        if event.unicode and event.unicode.isprintable():
                            if start_time is None:
                                start_time = time.time()
                            new_typed = typed + event.unicode
                            if len(new_typed) <= len(sentence):
                                if anim_enabled("Screen Shake on Type Error"):
                                    idx = len(typed)
                                    if idx < len(sentence) and event.unicode != sentence[idx]:
                                        shake_offset = 6
                                typed = new_typed
                else:
                    if event.key == pygame.K_RETURN:
                        return

        pygame.display.flip()
        clock.tick(60)


def main():
    load_config()
    intro_screen()
    main_menu()
    save_config()


if __name__ == "__main__":
    main()