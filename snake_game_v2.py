# ============================================================
#   GAME RẮN SĂN MỒI v2 - Pygame
#   Đồ án Python - Sinh viên năm nhất
#
#   TÍNH NĂNG MỚI:
#     - Mỗi 15 giây, cục mồi tự phình to gấp đôi (+10 điểm)
#     - Ăn mồi to xong → mồi trở về bình thường, đếm ngược lại
#     - Hiển thị đếm ngược bên dưới sân
# ============================================================
#
#   CÀI ĐẶT:
#     pip install pygame
#
#   CHẠY:
#     python snake_game_v2.py
#
#   ĐIỀU KHIỂN:
#     Mũi tên / WASD  → Di chuyển
#     SPACE           → Bắt đầu / Chơi lại
#     P               → Tạm dừng
#     ESC             → Thoát
# ============================================================

import pygame
import random
import sys

# ──────────────────────────────────────────────
# 1. CẤU HÌNH GAME
# ──────────────────────────────────────────────
WINDOW_WIDTH  = 600
WINDOW_HEIGHT = 650       # 50px cho thanh HUD
GRID_SIZE     = 25
GRID_COLS     = WINDOW_WIDTH  // GRID_SIZE        # 24 cột
GRID_ROWS     = (WINDOW_HEIGHT - 50) // GRID_SIZE  # 24 hàng
FPS           = 10        # Tốc độ vừa phải
BONUS_EVERY   = 15        # Giây để mồi phình to

# ──────────────────────────────────────────────
# 2. BẢNG MÀU
# ──────────────────────────────────────────────
BLACK       = (  0,   0,   0)
WHITE       = (255, 255, 255)
GREEN       = ( 34, 197,  94)
DARK_GREEN  = ( 22, 101,  52)
HEAD_GREEN  = ( 74, 222, 128)
ORANGE      = (249, 115,  22)
ORANGE_LITE = (254, 215, 170)
ORANGE_BIG  = (234,  88,  12)
YELLOW      = (250, 204,  21)
BG_DARK     = ( 17,  24,  39)
BG_CELL     = ( 24,  24,  24)
GRAY        = (107, 114, 128)
RED_GLOW    = (252, 165,  86)

# ──────────────────────────────────────────────
# 3. LỚP CON RẮN
# ──────────────────────────────────────────────
class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        cx, cy = GRID_COLS // 2, GRID_ROWS // 2
        self.body = [
            {"x": cx,     "y": cy},
            {"x": cx - 1, "y": cy},
            {"x": cx - 2, "y": cy},
        ]
        self.dir      = {"x": 1, "y": 0}
        self.next_dir = {"x": 1, "y": 0}
        self.alive    = True
        self.grew     = False

    def change_direction(self, new_dir):
        if (self.dir["x"] + new_dir["x"] != 0 or
            self.dir["y"] + new_dir["y"] != 0):
            self.next_dir = new_dir

    def move(self):
        self.dir = self.next_dir
        new_head = {
            "x": self.body[0]["x"] + self.dir["x"],
            "y": self.body[0]["y"] + self.dir["y"],
        }
        # Va chạm tường
        if (new_head["x"] < 0 or new_head["x"] >= GRID_COLS or
            new_head["y"] < 0 or new_head["y"] >= GRID_ROWS):
            self.alive = False
            return
        # Va chạm thân
        if new_head in self.body:
            self.alive = False
            return

        self.body.insert(0, new_head)
        if self.grew:
            self.grew = False
        else:
            self.body.pop()

    def draw(self, surface, offset_y):
        for i, seg in enumerate(self.body):
            x = seg["x"] * GRID_SIZE
            y = seg["y"] * GRID_SIZE + offset_y
            rect = pygame.Rect(x + 1, y + 1, GRID_SIZE - 2, GRID_SIZE - 2)

            if i == 0:
                pygame.draw.rect(surface, HEAD_GREEN, rect, border_radius=6)
                pygame.draw.rect(surface, DARK_GREEN, rect, width=1, border_radius=6)
                # Mắt rắn
                ex, ey = self.dir["x"], self.dir["y"]
                nx, ny = -ey, ex
                cx_ = x + GRID_SIZE // 2
                cy_ = y + GRID_SIZE // 2
                e1 = (cx_ + nx*4 + ex*3, cy_ + ny*4 + ey*3)
                e2 = (cx_ - nx*4 + ex*3, cy_ - ny*4 + ey*3)
                pygame.draw.circle(surface, BLACK, e1, 2)
                pygame.draw.circle(surface, BLACK, e2, 2)
            else:
                t = i / len(self.body)
                g = int(197 - t * 80)
                color = (34, g, 94)
                pygame.draw.rect(surface, color, rect, border_radius=4)
                pygame.draw.rect(surface, DARK_GREEN, rect, width=1, border_radius=4)


# ──────────────────────────────────────────────
# 4. LỚP THỨC ĂN
# ──────────────────────────────────────────────
class Food:
    def __init__(self):
        self.pos     = {"x": 0, "y": 0}
        self.is_big  = False       # True = mồi to (+10 điểm)
        self.pulse   = 0.0        # Dùng để tạo hiệu ứng nhấp nháy
        self.spawn([])

    def spawn(self, snake_body):
        """Tạo thức ăn ở vị trí ngẫu nhiên, không trùng thân rắn."""
        while True:
            pos = {
                "x": random.randint(0, GRID_COLS - 1),
                "y": random.randint(0, GRID_ROWS - 1),
            }
            if pos not in snake_body:
                self.pos    = pos
                self.is_big = False   # Luôn bắt đầu bình thường
                break

    def make_big(self):
        """Phình mồi to lên."""
        self.is_big = True

    def update(self, dt):
        """Cập nhật hiệu ứng nhấp nháy (pulse)."""
        self.pulse += dt * 5   # Tốc độ nhấp nháy

    def draw(self, surface, offset_y):
        cx = self.pos["x"] * GRID_SIZE + GRID_SIZE // 2
        cy = self.pos["y"] * GRID_SIZE + GRID_SIZE // 2 + offset_y

        if self.is_big:
            # Mồi to: bán kính lớn hơn + nhấp nháy
            import math
            pulse_scale = 0.85 + 0.15 * math.sin(self.pulse)
            r = int((GRID_SIZE // 2 + 5) * pulse_scale)
            pygame.draw.circle(surface, ORANGE_BIG, (cx, cy), r)
            pygame.draw.circle(surface, RED_GLOW,   (cx, cy), r, width=2)
            # Chữ +10
            font = pygame.font.SysFont("segoeui", 11, bold=True)
            txt  = font.render("+10", True, WHITE)
            surface.blit(txt, (cx - txt.get_width() // 2, cy - txt.get_height() // 2))
        else:
            # Mồi bình thường
            r = GRID_SIZE // 2 - 2
            pygame.draw.circle(surface, ORANGE, (cx, cy), r)
            pygame.draw.circle(surface, (251, 191, 36), (cx - 2, cy - 2), 3)


# ──────────────────────────────────────────────
# 5. VẼ NỀN LƯỚI
# ──────────────────────────────────────────────
def draw_background(surface, offset_y):
    surface.fill(BG_DARK)
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            if (row + col) % 2 == 0:
                rect = pygame.Rect(
                    col * GRID_SIZE,
                    row * GRID_SIZE + offset_y,
                    GRID_SIZE, GRID_SIZE
                )
                pygame.draw.rect(surface, BG_CELL, rect)


# ──────────────────────────────────────────────
# 6. VẼ HUD (thanh điểm + đếm ngược)
# ──────────────────────────────────────────────
def draw_hud(surface, font_hud, score, high_score, paused):
    pygame.draw.rect(surface, (10, 15, 30), (0, 0, WINDOW_WIDTH, 50))
    pygame.draw.line(surface, (50, 60, 80), (0, 50), (WINDOW_WIDTH, 50), 1)

    # Điểm
    score_text = font_hud.render(f"Điểm: {score}", True, WHITE)
    surface.blit(score_text, (15, 13))

    # Điểm cao nhất
    high_text = font_hud.render(f"Cao nhất: {high_score}", True, YELLOW)
    surface.blit(high_text, (WINDOW_WIDTH // 2 - high_text.get_width() // 2, 13))

    # Tạm dừng
    if paused:
        p_text = font_hud.render("TẠM DỪNG", True, GRAY)
        surface.blit(p_text, (WINDOW_WIDTH - p_text.get_width() - 15, 13))


# ──────────────────────────────────────────────
# 7. VẼ OVERLAY (bắt đầu / game over / tạm dừng)
# ──────────────────────────────────────────────
def draw_overlay(surface, big_font, small_font, title, subtitle, score=None):
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))

    title_surf = big_font.render(title, True, HEAD_GREEN)
    surface.blit(title_surf, (
        WINDOW_WIDTH  // 2 - title_surf.get_width()  // 2,
        WINDOW_HEIGHT // 2 - 60
    ))

    if score is not None:
        sc_surf = small_font.render(f"Điểm của bạn: {score}", True, WHITE)
        surface.blit(sc_surf, (
            WINDOW_WIDTH  // 2 - sc_surf.get_width()  // 2,
            WINDOW_HEIGHT // 2
        ))

    sub_surf = small_font.render(subtitle, True, GRAY)
    surface.blit(sub_surf, (
        WINDOW_WIDTH  // 2 - sub_surf.get_width()  // 2,
        WINDOW_HEIGHT // 2 + 45
    ))


# ──────────────────────────────────────────────
# 8. HÀM CHÍNH
# ──────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Rắn Săn Mồi 🐍 v2")
    clock = pygame.time.Clock()

    try:
        font_big   = pygame.font.SysFont("segoeui", 42, bold=True)
        font_small = pygame.font.SysFont("segoeui", 18)
        font_hud   = pygame.font.SysFont("segoeui", 20)
    except:
        font_big   = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 24)
        font_hud   = pygame.font.Font(None, 26)

    OFFSET_Y = 50   # Khu vực game bắt đầu từ y=50

    snake      = Snake()
    food       = Food()
    score      = 0
    high_score = 0
    state      = "start"

    # Biến đếm thời gian mồi to — chạy liên tục, không reset khi ăn mồi bé
    elapsed_bonus = 0.0

    while True:
        dt = clock.tick(FPS) / 1000.0   # Delta time (giây)

        # ── Xử lý sự kiện ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

                if event.key == pygame.K_SPACE:
                    if state in ("start", "gameover"):
                        snake.reset()
                        food.spawn(snake.body)
                        score         = 0
                        elapsed_bonus = 0.0
                        state         = "playing"
                    elif state == "playing":
                        state = "paused"
                    elif state == "paused":
                        state = "playing"

                if event.key == pygame.K_p:
                    if state == "playing":  state = "paused"
                    elif state == "paused": state = "playing"

                if state == "playing":
                    if event.key in (pygame.K_UP,    pygame.K_w):
                        snake.change_direction({"x": 0, "y": -1})
                    if event.key in (pygame.K_DOWN,  pygame.K_s):
                        snake.change_direction({"x": 0, "y":  1})
                    if event.key in (pygame.K_LEFT,  pygame.K_a):
                        snake.change_direction({"x": -1, "y": 0})
                    if event.key in (pygame.K_RIGHT, pygame.K_d):
                        snake.change_direction({"x":  1, "y": 0})

        # ── Cập nhật logic ──
        if state == "playing":
            # Đếm thời gian liên tục — không phụ thuộc việc ăn mồi
            elapsed_bonus += dt

            # Cứ đủ 15 giây → mồi phình to, reset đồng hồ
            if elapsed_bonus >= BONUS_EVERY and not food.is_big:
                food.make_big()
                elapsed_bonus = 0.0

            # Cập nhật hiệu ứng nhấp nháy
            food.update(dt)

            # Di chuyển rắn
            snake.move()

            if not snake.alive:
                if score > high_score:
                    high_score = score
                state = "gameover"

            elif snake.body[0] == food.pos:
                pts = 10 if food.is_big else 1
                score += pts
                snake.grew = True
                if food.is_big:
                    elapsed_bonus = 0.0   # Chỉ reset khi ăn mồi TO
                food.spawn(snake.body)

        # ── Vẽ ──
        draw_background(screen, OFFSET_Y)
        draw_hud(screen, font_hud, score, high_score, state == "paused")
        food.draw(screen, OFFSET_Y)
        snake.draw(screen, OFFSET_Y)

        if state == "start":
            draw_overlay(screen, font_big, font_small,
                         "RẮN SĂN MỒI", "Nhấn SPACE để bắt đầu")
        if state == "paused":
            draw_overlay(screen, font_big, font_small,
                         "TẠM DỪNG", "Nhấn SPACE hoặc P để tiếp tục")
        if state == "gameover":
            draw_overlay(screen, font_big, font_small,
                         "GAME OVER", "Nhấn SPACE để chơi lại", score=score)

        pygame.display.flip()


# ──────────────────────────────────────────────
# 9. ĐIỂM VÀO
# ──────────────────────────────────────────────
if __name__ == "__main__":
    main()
