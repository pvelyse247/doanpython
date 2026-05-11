# ============================================================
#   SNAKE GAME - Phiên bản hoàn chỉnh
#   Có: Menu, Gameplay, Game Over, Option, Icon
# ============================================================
#   pip install pygame
#   python snake_game_final.py
# ============================================================

import pygame
import random
import sys
import math
import os

# ──────────────────────────────────────────────
# CẤU HÌNH
# ──────────────────────────────────────────────
WIN_W, WIN_H = 700, 600
GRID_SIZE    = 25
COLS         = WIN_W  // GRID_SIZE   # 28
ROWS         = WIN_H  // GRID_SIZE   # 24
FPS          = 10
BONUS_EVERY  = 15     # Giây để mồi phình to

# ──────────────────────────────────────────────
# MÀU SẮC
# ──────────────────────────────────────────────
BG          = ( 15,  20,  35)
CELL_ALT    = ( 22,  28,  45)
GREEN       = ( 34, 197,  94)
DARK_GREEN  = ( 22, 101,  52)
HEAD_GREEN  = ( 74, 222, 128)
ORANGE      = (249, 115,  22)
ORANGE_DARK = (194,  65,   0)
WHITE       = (255, 255, 255)
BLACK       = (  0,   0,   0)
YELLOW      = (250, 204,  21)
GRAY        = (100, 110, 130)
GRAY_LIGHT  = (160, 170, 190)
RED         = (220,  50,  50)
ACCENT      = ( 99, 102, 241)   # Tím nhạt — màu nhấn
ACCENT2     = ( 56, 189, 248)   # Xanh dương nhạt

# Màu menu
MENU_BG     = ( 10,  14,  26)
MENU_CARD   = ( 22,  28,  48)
MENU_BORDER = ( 45,  55,  90)

# ──────────────────────────────────────────────
# TIỆN ÍCH VẼ CHỮ
# ──────────────────────────────────────────────
def draw_text(surface, text, font, color, cx, cy, shadow=False):
    if shadow:
        s = font.render(text, True, (0, 0, 0))
        surface.blit(s, s.get_rect(center=(cx+2, cy+2)))
    txt = font.render(text, True, color)
    surface.blit(txt, txt.get_rect(center=(cx, cy)))

def draw_text_left(surface, text, font, color, x, y):
    txt = font.render(text, True, color)
    surface.blit(txt, (x, y))


# ──────────────────────────────────────────────
# NÚT BẤM
# ──────────────────────────────────────────────
class Button:
    def __init__(self, cx, cy, w, h, text, font,
                 color=ACCENT, hover_color=ACCENT2, text_color=WHITE):
        self.rect       = pygame.Rect(0, 0, w, h)
        self.rect.center = (cx, cy)
        self.text       = text
        self.font       = font
        self.color      = color
        self.hover_color= hover_color
        self.text_color = text_color
        self.hovered    = False
        self.alpha      = 0   # Cho hiệu ứng fade-in

    def update(self, mx, my):
        self.hovered = self.rect.collidepoint(mx, my)

    def draw(self, surface):
        color = self.hover_color if self.hovered else self.color
        # Vẽ nền nút với bo góc
        pygame.draw.rect(surface, color, self.rect, border_radius=12)
        # Viền sáng khi hover
        if self.hovered:
            pygame.draw.rect(surface, WHITE, self.rect, width=2, border_radius=12)
        # Chữ
        txt = self.font.render(self.text, True, self.text_color)
        surface.blit(txt, txt.get_rect(center=self.rect.center))

    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and self.rect.collidepoint(event.pos))


# ──────────────────────────────────────────────
# THANH SLIDER (Option)
# ──────────────────────────────────────────────
class Slider:
    def __init__(self, cx, cy, w, label, font, value=0.5):
        self.rect  = pygame.Rect(cx - w//2, cy - 8, w, 16)
        self.label = label
        self.font  = font
        self.value = value   # 0.0 → 1.0
        self.dragging = False

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
        if event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        if event.type == pygame.MOUSEMOTION and self.dragging:
            x = max(self.rect.left, min(event.pos[0], self.rect.right))
            self.value = (x - self.rect.left) / self.rect.width

    def draw(self, surface, label_x, cy):
        # Label
        lbl = self.font.render(self.label, True, GRAY_LIGHT)
        surface.blit(lbl, (label_x, cy - lbl.get_height()//2))

        # Track
        pygame.draw.rect(surface, MENU_BORDER, self.rect, border_radius=8)
        # Fill
        fill_w = int(self.rect.width * self.value)
        fill_r = pygame.Rect(self.rect.left, self.rect.top, fill_w, self.rect.height)
        if fill_w > 0:
            pygame.draw.rect(surface, ACCENT, fill_r, border_radius=8)
        # Thumb
        tx = self.rect.left + fill_w
        pygame.draw.circle(surface, WHITE, (tx, cy), 12)
        pygame.draw.circle(surface, ACCENT, (tx, cy), 9)

        # Giá trị %
        pct = self.font.render(f"{int(self.value*100)}%", True, GRAY_LIGHT)
        surface.blit(pct, (self.rect.right + 16, cy - pct.get_height()//2))


# ──────────────────────────────────────────────
# CON RẮN
# ──────────────────────────────────────────────
class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        cx, cy = COLS//2, ROWS//2
        self.body     = [{"x": cx, "y": cy}, {"x": cx-1, "y": cy}, {"x": cx-2, "y": cy}]
        self.dir      = {"x": 1, "y": 0}
        self.next_dir = {"x": 1, "y": 0}
        self.alive    = True
        self.grew     = False

    def change_dir(self, nd):
        if self.dir["x"] + nd["x"] != 0 or self.dir["y"] + nd["y"] != 0:
            self.next_dir = nd

    def move(self):
        self.dir = self.next_dir
        head = {"x": self.body[0]["x"] + self.dir["x"],
                "y": self.body[0]["y"] + self.dir["y"]}
        if head["x"] < 0 or head["x"] >= COLS or head["y"] < 0 or head["y"] >= ROWS:
            self.alive = False; return
        if head in self.body:
            self.alive = False; return
        self.body.insert(0, head)
        if self.grew: self.grew = False
        else: self.body.pop()

    def draw(self, surface):
        for i, s in enumerate(self.body):
            x, y = s["x"]*GRID_SIZE, s["y"]*GRID_SIZE
            r = pygame.Rect(x+1, y+1, GRID_SIZE-2, GRID_SIZE-2)
            if i == 0:
                pygame.draw.rect(surface, HEAD_GREEN, r, border_radius=7)
                pygame.draw.rect(surface, DARK_GREEN, r, width=1, border_radius=7)
                # Mắt
                ex, ey = self.dir["x"], self.dir["y"]
                nx, ny = -ey, ex
                cx_, cy_ = x+GRID_SIZE//2, y+GRID_SIZE//2
                e1 = (cx_+nx*5+ex*4, cy_+ny*5+ey*4)
                e2 = (cx_-nx*5+ex*4, cy_-ny*5+ey*4)
                pygame.draw.circle(surface, WHITE, e1, 4)
                pygame.draw.circle(surface, BLACK, e1, 2)
                pygame.draw.circle(surface, WHITE, e2, 4)
                pygame.draw.circle(surface, BLACK, e2, 2)
            else:
                t = i / len(self.body)
                g = int(197 - t*80)
                pygame.draw.rect(surface, (34, g, 94), r, border_radius=4)
                pygame.draw.rect(surface, DARK_GREEN, r, width=1, border_radius=4)


# ──────────────────────────────────────────────
# THỨC ĂN
# ──────────────────────────────────────────────
class Food:
    def __init__(self):
        self.pos    = {"x": 5, "y": 5}
        self.is_big = False
        self.pulse  = 0.0
        self.spawn([])

    def spawn(self, snake_body):
        self.is_big = False
        while True:
            pos = {"x": random.randint(0, COLS-1), "y": random.randint(0, ROWS-1)}
            if pos not in snake_body:
                self.pos = pos; break

    def make_big(self):
        self.is_big = True

    def update(self, dt):
        self.pulse += dt * 4

    def draw(self, surface):
        cx = self.pos["x"]*GRID_SIZE + GRID_SIZE//2
        cy = self.pos["y"]*GRID_SIZE + GRID_SIZE//2
        if self.is_big:
            p  = 0.85 + 0.15*math.sin(self.pulse)
            r  = int((GRID_SIZE//2 + 7)*p)
            pygame.draw.circle(surface, ORANGE_DARK, (cx, cy), r+2)
            pygame.draw.circle(surface, ORANGE, (cx, cy), r)
            pygame.draw.circle(surface, (255, 200, 100), (cx, cy), r, width=2)
            font = pygame.font.SysFont("segoeui", 11, bold=True)
            t = font.render("+10", True, WHITE)
            surface.blit(t, t.get_rect(center=(cx, cy)))
        else:
            r = GRID_SIZE//2 - 3
            pygame.draw.circle(surface, ORANGE, (cx, cy), r)
            pygame.draw.circle(surface, (255,180,60), (cx-2, cy-2), 4)


# ──────────────────────────────────────────────
# VẼ NỀN LƯỚI
# ──────────────────────────────────────────────
def draw_bg(surface):
    surface.fill(BG)
    for r in range(ROWS):
        for c in range(COLS):
            if (r+c) % 2 == 0:
                pygame.draw.rect(surface, CELL_ALT,
                    (c*GRID_SIZE, r*GRID_SIZE, GRID_SIZE, GRID_SIZE))


# ──────────────────────────────────────────────
# HUD GAMEPLAY
# ──────────────────────────────────────────────
def draw_gameplay_hud(surface, font, score, high, length):
    # Panel nhỏ góc trên trái
    info = [
        ("SCORE", str(score), YELLOW),
        ("BEST",  str(high),  ACCENT2),
        ("LEN",   str(length), GREEN),
    ]
    for i, (label, val, color) in enumerate(info):
        px = 10 + i*130
        pygame.draw.rect(surface, MENU_CARD,
            (px, 4, 118, 40), border_radius=8)
        pygame.draw.rect(surface, MENU_BORDER,
            (px, 4, 118, 40), width=1, border_radius=8)
        lf = pygame.font.SysFont("segoeui", 11)
        vf = pygame.font.SysFont("segoeui", 16, bold=True)
        surface.blit(lf.render(label, True, GRAY), (px+8, 8))
        surface.blit(vf.render(val, True, color), (px+8, 22))


# ──────────────────────────────────────────────
# MÀN HÌNH MENU
# ──────────────────────────────────────────────
def scene_menu(screen, fonts, clock, snake_icon_surf):
    btn_play = Button(WIN_W//2, 280, 240, 54, "PLAY", fonts["btn"],
                      color=(34,197,94), hover_color=(74,222,128), text_color=BLACK)
    btn_opt  = Button(WIN_W//2, 354, 240, 54, "OPTION", fonts["btn"],
                      color=ACCENT, hover_color=ACCENT2)
    btn_quit = Button(WIN_W//2, 428, 240, 54, "QUIT", fonts["btn"],
                      color=(80,30,30), hover_color=RED)
    buttons  = [btn_play, btn_opt, btn_quit]
    tick     = 0

    while True:
        dt = clock.tick(60) / 1000
        tick += dt
        mx, my = pygame.mouse.get_pos()
        for b in buttons: b.update(mx, my)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()
            for b in buttons:
                if b.is_clicked(event):
                    if b.text == "PLAY":   return "play"
                    if b.text == "OPTION": return "option"
                    if b.text == "QUIT":   pygame.quit(); sys.exit()

        # Nền
        screen.fill(MENU_BG)

        # Lưới mờ trang trí
        for r in range(0, WIN_H, 40):
            pygame.draw.line(screen, (25,32,55), (0,r), (WIN_W,r))
        for c in range(0, WIN_W, 40):
            pygame.draw.line(screen, (25,32,55), (c,0), (c,WIN_H))

        # Card trung tâm
        card = pygame.Rect(WIN_W//2-160, 120, 320, 360)
        pygame.draw.rect(screen, MENU_CARD, card, border_radius=20)
        pygame.draw.rect(screen, MENU_BORDER, card, width=2, border_radius=20)

        # Icon con rắn + tên game
        if snake_icon_surf:
            ic = pygame.transform.scale(snake_icon_surf, (72, 72))
            screen.blit(ic, ic.get_rect(center=(WIN_W//2, 168)))

        # Tiêu đề SNAKE với hiệu ứng shimmer
        shimmer = abs(math.sin(tick*1.5))
        title_color = (
            int(74  + shimmer*180),
            int(222 + shimmer*33),
            int(128 + shimmer*127)
        )
        draw_text(screen, "SNAKE", fonts["title"], title_color, WIN_W//2, 220, shadow=True)

        for b in buttons: b.draw(screen)

        # Hướng dẫn nhỏ phía dưới
        draw_text(screen, "Arrow Keys / WASD  •  P = Pause  •  ESC = Quit",
                  fonts["small"], GRAY, WIN_W//2, WIN_H-20)

        pygame.display.flip()


# ──────────────────────────────────────────────
# MÀN HÌNH OPTION
# ──────────────────────────────────────────────
def scene_option(screen, fonts, clock, settings):
    slider_vol = Slider(WIN_W//2+60, WIN_H//2-40, 260, "VOLUME", fonts["sub"],
                        value=settings["volume"])
    slider_bri = Slider(WIN_W//2+60, WIN_H//2+40, 260, "BRIGHTNESS", fonts["sub"],
                        value=settings["brightness"])
    btn_back   = Button(WIN_W//2, WIN_H//2+140, 200, 50, "BACK", fonts["btn"],
                        color=(60,30,80), hover_color=ACCENT)

    while True:
        clock.tick(60)
        mx, my = pygame.mouse.get_pos()
        btn_back.update(mx, my)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                settings["volume"]     = slider_vol.value
                settings["brightness"] = slider_bri.value
                return
            slider_vol.handle(event)
            slider_bri.handle(event)
            if btn_back.is_clicked(event):
                settings["volume"]     = slider_vol.value
                settings["brightness"] = slider_bri.value
                return

        screen.fill(MENU_BG)
        for r in range(0, WIN_H, 40):
            pygame.draw.line(screen, (25,32,55), (0,r), (WIN_W,r))
        for c in range(0, WIN_W, 40):
            pygame.draw.line(screen, (25,32,55), (c,0), (c,WIN_H))

        card = pygame.Rect(WIN_W//2-220, WIN_H//2-140, 440, 320)
        pygame.draw.rect(screen, MENU_CARD, card, border_radius=20)
        pygame.draw.rect(screen, MENU_BORDER, card, width=2, border_radius=20)

        draw_text(screen, "OPTION", fonts["title"], ACCENT2, WIN_W//2, WIN_H//2-100, shadow=True)

        label_x = WIN_W//2 - 200
        slider_vol.draw(screen, label_x, WIN_H//2-40)
        slider_bri.draw(screen, label_x, WIN_H//2+40)
        btn_back.draw(screen)

        pygame.display.flip()


# ──────────────────────────────────────────────
# MÀN HÌNH GAME OVER
# ──────────────────────────────────────────────
def scene_gameover(screen, fonts, clock, score, high):
    btn_cont = Button(WIN_W//2-110, WIN_H//2+90, 180, 52, "CONTINUE", fonts["btn"],
                      color=(34,197,94), hover_color=(74,222,128), text_color=BLACK)
    btn_back = Button(WIN_W//2+110, WIN_H//2+90, 180, 52, "BACK", fonts["btn"],
                      color=(60,30,80), hover_color=ACCENT)
    tick = 0

    while True:
        dt = clock.tick(60)/1000
        tick += dt
        mx, my = pygame.mouse.get_pos()
        btn_cont.update(mx, my); btn_back.update(mx, my)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: return "play"
                if event.key == pygame.K_ESCAPE: return "menu"
            if btn_cont.is_clicked(event): return "play"
            if btn_back.is_clicked(event): return "menu"

        screen.fill(MENU_BG)
        for r in range(0, WIN_H, 40):
            pygame.draw.line(screen, (25,32,55), (0,r), (WIN_W,r))
        for c in range(0, WIN_W, 40):
            pygame.draw.line(screen, (25,32,55), (c,0), (c,WIN_H))

        card = pygame.Rect(WIN_W//2-220, WIN_H//2-170, 440, 300)
        pygame.draw.rect(screen, MENU_CARD, card, border_radius=20)
        pygame.draw.rect(screen, (120,20,20), card, width=2, border_radius=20)

        # GAME OVER nhấp nháy đỏ
        pulse = abs(math.sin(tick*2))
        gc = (int(200+55*pulse), int(50*pulse), int(50*pulse))
        draw_text(screen, "GAME OVER", fonts["title"], gc, WIN_W//2, WIN_H//2-110, shadow=True)

        # Điểm
        draw_text(screen, "YOUR SCORE", fonts["sub"], GRAY_LIGHT, WIN_W//2, WIN_H//2-50)
        draw_text(screen, str(score), fonts["score"], YELLOW, WIN_W//2, WIN_H//2)

        if score >= high and score > 0:
            draw_text(screen, "🏆 NEW HIGH SCORE!", fonts["sub"], YELLOW, WIN_W//2, WIN_H//2+48)
        else:
            draw_text(screen, f"Best: {high}", fonts["sub"], GRAY, WIN_W//2, WIN_H//2+48)

        btn_cont.draw(screen); btn_back.draw(screen)

        draw_text(screen, "SPACE = Continue  •  ESC = Menu",
                  fonts["small"], GRAY, WIN_W//2, WIN_H-20)

        pygame.display.flip()


# ──────────────────────────────────────────────
# MÀN HÌNH GAMEPLAY
# ──────────────────────────────────────────────
def scene_play(screen, fonts, clock, high_score):
    snake         = Snake()
    food          = Food()
    score         = 0
    state         = "playing"   # playing | paused
    elapsed_bonus = 0.0
    tick          = 0

    while True:
        dt = clock.tick(FPS) / 1000
        tick += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:      return "menu", high_score
                if event.key in (pygame.K_p, pygame.K_SPACE):
                    state = "paused" if state=="playing" else "playing"
                if state == "playing":
                    if event.key in (pygame.K_UP,    pygame.K_w): snake.change_dir({"x":0,"y":-1})
                    if event.key in (pygame.K_DOWN,  pygame.K_s): snake.change_dir({"x":0,"y": 1})
                    if event.key in (pygame.K_LEFT,  pygame.K_a): snake.change_dir({"x":-1,"y":0})
                    if event.key in (pygame.K_RIGHT, pygame.K_d): snake.change_dir({"x": 1,"y":0})

        if state == "playing":
            elapsed_bonus += dt
            food.update(dt)
            if elapsed_bonus >= BONUS_EVERY and not food.is_big:
                food.make_big()
                elapsed_bonus = 0.0

            snake.move()

            if not snake.alive:
                if score > high_score: high_score = score
                result = scene_gameover(screen, fonts, clock, score, high_score)
                return result, high_score

            if snake.body[0] == food.pos:
                pts = 10 if food.is_big else 1
                score += pts
                snake.grew = True
                if food.is_big: elapsed_bonus = 0.0
                food.spawn(snake.body)

        # Vẽ
        draw_bg(screen)
        food.draw(screen)
        snake.draw(screen)
        draw_gameplay_hud(screen, fonts["hud"], score, high_score, len(snake.body))

        if state == "paused":
            ov = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
            ov.fill((0,0,0,140))
            screen.blit(ov, (0,0))
            draw_text(screen, "PAUSED", fonts["title"], ACCENT2, WIN_W//2, WIN_H//2-20, shadow=True)
            draw_text(screen, "Press P or SPACE to continue", fonts["sub"],
                      GRAY_LIGHT, WIN_W//2, WIN_H//2+40)

        pygame.display.flip()


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Snake")

    # ── Set icon cửa sổ ──
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(BASE_DIR, "snake_icon.png")
    snake_icon_surf = None
    if os.path.exists(icon_path):
        icon_surf = pygame.image.load(icon_path).convert_alpha()
        pygame.display.set_icon(icon_surf)
        snake_icon_surf = icon_surf
    
    clock = pygame.time.Clock()

    # ── Font ──
    try:
        fonts = {
            "title": pygame.font.SysFont("segoeui", 52, bold=True),
            "sub"  : pygame.font.SysFont("segoeui", 22),
            "btn"  : pygame.font.SysFont("segoeui", 20, bold=True),
            "hud"  : pygame.font.SysFont("segoeui", 18),
            "small": pygame.font.SysFont("segoeui", 14),
            "score": pygame.font.SysFont("segoeui", 64, bold=True),
        }
    except:
        fonts = {k: pygame.font.Font(None, s) for k, s in
                 [("title",64),("sub",28),("btn",26),("hud",24),("small",20),("score",80)]}

    settings   = {"volume": 0.7, "brightness": 0.8}
    high_score = 0
    scene      = "menu"

    while True:
        if scene == "menu":
            result = scene_menu(screen, fonts, clock, snake_icon_surf)
            scene  = result

        elif scene == "option":
            scene_option(screen, fonts, clock, settings)
            scene = "menu"

        elif scene == "play":
            result, high_score = scene_play(screen, fonts, clock, high_score)
            scene = result


if __name__ == "__main__":
    main()
