import pygame
import sys
import random
import time

# Khởi tạo pygame
pygame.init()

# Màn hình game
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird and Typing Game")

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Tốc độ game
FPS = 60
clock = pygame.time.Clock()

# Các giá trị cho game
GRAVITY = 0
PIPE_WIDTH = 70
PIPE_GAP = 200
PIPE_VELOCITY = 3

# Tải hình ảnh
bird_image = pygame.image.load("yellowbird-upflap.png")
bird_image = pygame.transform.scale(bird_image, (40, 40))
bird_rect = bird_image.get_rect(center=(100, SCREEN_HEIGHT // 2))

pipe_image = pygame.image.load("pipe-green.png")
pipe_image = pygame.transform.scale(pipe_image, (PIPE_WIDTH, SCREEN_HEIGHT))

background_image = pygame.image.load("BG.png")
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))


# Biến trạng thái game
bird_velocity = 0

game_over = False
game_started = False
pipes = []
score = 0
passed_pipes = -1


# Tạo danh sách chữ cái ngẫu nhiên
letters = [chr(i) for i in range(65, 91)]  # Từ 'A' đến 'Z'
pipe_letters = [] 

# Từ ngẫu nhiên cho trò chơi gõ phím
words = ["TINHOC", "BANPHIM", "CHUOT", "MANHINH", "GAME", "MAYTINH","ROM","LAPTOP", "PHANMEM","SAVE","GYGABYTE","BYTE","DATA","TV"]
current_word = ""
typed_word = ""

# Thời gian cho trò gõ phím
typing_time_limit = 30
time_left = typing_time_limit

# Tên người chơi
player_name = ""
# Thêm biến cho Flappy Bird trong màn gõ phím
typing_bird_rect = bird_image.get_rect(center=(100, SCREEN_HEIGHT // 2))
typing_bird_velocity = 0

# Thêm biến cho boss
boss_image = pygame.image.load("boss.png")  # Thay bằng file ảnh boss
boss_image = pygame.transform.scale(boss_image, (450, 450))
boss_rect = boss_image.get_rect(center=(SCREEN_WIDTH - 0, SCREEN_HEIGHT // 1.5))
boss_health = 15
boss_max_health = 15

# Tải các hình ảnh nút lệnh
start_button_image = pygame.image.load("start_button.png")
start_button_rect = start_button_image.get_rect(center=(SCREEN_WIDTH // 2+200, SCREEN_HEIGHT // 2 + 100))

leaderboard_button_image = pygame.image.load("leaderboard_button.png")
leaderboard_button_rect = leaderboard_button_image.get_rect(center=(SCREEN_WIDTH // 2-200, SCREEN_HEIGHT // 2 + 100))

# Lớp Pipe để quản lý các ống
class Pipe:
    def __init__(self, top_pipe, bottom_pipe, letter):
        self.top_pipe = top_pipe
        self.bottom_pipe = bottom_pipe
        self.letter = letter  # Chữ cái trên chướng ngại vật
        self.passed = False
# Biến mới cho đạn
bullets = []
bullet_image = pygame.image.load("bullet.png")  # Thay bằng ảnh đạn của bạn
bullet_image = pygame.transform.scale(bullet_image, (200, 80))  # Kích thước đạn
BULLET_VELOCITY = 10  # Tốc độ của đạn

# Tạo đạn khi gõ đúng từ
def shoot_bullet():
    bullet_rect = bullet_image.get_rect(center=(typing_bird_rect.centerx + 40, typing_bird_rect.centery))
    bullets.append(bullet_rect)

# Di chuyển các đạn
def move_bullets():
    global boss_health
    for bullet in bullets[:]:
        bullet.x += BULLET_VELOCITY  # Đạn di chuyển sang phải
        if bullet.colliderect(boss_rect):  # Kiểm tra va chạm với boss
            boss_health -= 1  # Giảm máu boss
            bullets.remove(bullet)  # Xóa đạn sau khi va chạm
        elif bullet.x > SCREEN_WIDTH:  # Nếu đạn ra khỏi màn hình, xóa nó
            bullets.remove(bullet)
    
# Vẽ các đạn lên màn hình
def draw_bullets():
    for bullet in bullets:
        screen.blit(bullet_image, bullet)

def create_pipe():
    height = random.randint(150, SCREEN_HEIGHT - PIPE_GAP)
    top_pipe = pipe_image.get_rect(midbottom=(SCREEN_WIDTH + PIPE_WIDTH, height - PIPE_GAP // 2))
    bottom_pipe = pipe_image.get_rect(midtop=(SCREEN_WIDTH + PIPE_WIDTH, height + PIPE_GAP // 2))
    letter = random.choice(letters)
    return Pipe(top_pipe, bottom_pipe, letter)

def move_pipes(pipes):
    global passed_pipes
    for pipe in pipes:
        pipe.top_pipe.centerx -= PIPE_VELOCITY
        pipe.bottom_pipe.centerx -= PIPE_VELOCITY
    pipes = [pipe for pipe in pipes if pipe.top_pipe.right > 0]
    for pipe in pipes:
        if pipe.top_pipe.right < bird_rect.left and not pipe.passed:
            pipe.passed = True
            passed_pipes += 1
    return pipes

def draw_pipes(pipes):
    font = pygame.font.SysFont("Arial", 30)
    for pipe in pipes:
        screen.blit(pygame.transform.flip(pipe_image, False, True), pipe.top_pipe)
        screen.blit(pipe_image, pipe.bottom_pipe)
        # Vẽ chữ cái trên chướng ngại vật
        letter_pos = (pipe.top_pipe.centerx - 10, pipe.top_pipe.bottom + 10)
        draw_text(pipe.letter, font, BLACK, *letter_pos)


def check_collision(bird, pipes):
    if bird.top <= 0 or bird.bottom >= SCREEN_HEIGHT:
        return True
    for pipe in pipes:
        if bird.colliderect(pipe.top_pipe) or bird.colliderect(pipe.bottom_pipe):
            return True
    return False

def draw_text(text, font, color, x, y):
    label = font.render(text, True, color)
    screen.blit(label, (x, y))

def save_score(player_name, score):
    scores = load_leaderboard()

    # Thêm điểm mới vào danh sách
    scores.append(f"{player_name}: {score}")
    scores = sorted(scores, key=lambda x: int(x.split(": ")[1]), reverse=True)

    # Chỉ lưu top 5 điểm cao nhất
    with open("leaderboard.txt", "w") as file:
        for score_entry in scores[:5]:
            file.write(score_entry + "\n")

def load_leaderboard():
    try:
        with open("leaderboard.txt", "r") as file:
            scores = file.readlines()
            scores = [s.strip() for s in scores]
            scores = sorted(scores, key=lambda x: int(x.split(": ")[1]), reverse=True)
            return scores[:5]
    except FileNotFoundError:
        return []

def display_leaderboard():
    font = pygame.font.SysFont("Arial", 30)
    scores = load_leaderboard()
    y_offset = SCREEN_HEIGHT // 2 - 150
    draw_text("Top 5 Scores:", font, BLACK, SCREEN_WIDTH // 2 - 100, y_offset)
    for i, score in enumerate(scores, start=1):
        draw_text(f"{i}. {score}", font, BLACK, SCREEN_WIDTH // 2 - 100, y_offset + i * 40)
    
    # Hiển thị bảng xếp hạng trong 10 giây
    start_time = time.time()
    while True:
        screen.fill(WHITE)
        screen.blit(background_image, (0, 0))
        # Hiển thị bảng xếp hạng
        draw_text("Top 5 Scores:", font, BLACK, SCREEN_WIDTH // 2 - 100, y_offset)
        for i, score in enumerate(scores, start=1):
            draw_text(f"{i}. {score}", font, BLACK, SCREEN_WIDTH // 2 - 100, y_offset + i * 40)

        # Kiểm tra nếu đã 10 giây
        if time.time() - start_time >= 10:
            break

        pygame.display.update()
        clock.tick(FPS)

def typing_game():
    global typed_word, current_word, score, time_left, boss_health, game_over, boss_rect

    # Kiểm tra nếu từ gõ đúng
    if typed_word == current_word:
        score += 1
        typed_word = ""
        current_word = random.choice(words)

        # Giảm máu boss nếu còn máu và bắn đạn
        if boss_health > 0:
            shoot_bullet()

    # Tính khoảng cách và tốc độ di chuyển của boss
    def calculate_boss_movement():
    # Khoảng cách giữa boss và Flappy Bird trên cả 2 trục
        dx = typing_bird_rect.centerx - boss_rect.centerx
        dy = typing_bird_rect.centery - boss_rect.centery

    # Tính toán tốc độ di chuyển mỗi khung hình
        total_frames = 30 * FPS  # Tổng số khung hình trong 30 giây
        speed_x = dx / total_frames  # Tốc độ di chuyển theo trục x
        speed_y = dy / total_frames  # Tốc độ di chuyển theo trục y

        return speed_x, speed_y


    # Di chuyển boss từ vị trí hiện tại đến vị trí Flappy Bird
    speed_x, speed_y = calculate_boss_movement()
    boss_rect.centerx += speed_x
    boss_rect.centery += speed_y

    # Kiểm tra nếu boss đã chạm vào Flappy Bird
    if boss_rect.colliderect(typing_bird_rect):
        game_over = True
        save_score(player_name, score)
        reset_flappy_bird_game()
        draw_text("Game Over! Boss caught you!", pygame.font.SysFont("Arial", 30), BLACK, SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 3)
        pygame.time.wait(2000)
        name_input_screen()

    # Vẽ các đối tượng trong màn chơi
    font = pygame.font.SysFont("Arial", 50)
    draw_text(f"Word: {current_word}", font, BLACK, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 4)
    draw_text(f">: {typed_word}", font, BLACK, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 3)
    draw_text(f"Score: {score}", font, BLACK, 10, 10)
    draw_text(f"Time left: {time_left}", font, BLACK, SCREEN_WIDTH - 200, 10)

    # Hiển thị Flappy Bird
    screen.blit(bird_image, typing_bird_rect)

    # Hiển thị Boss và thanh máu
    screen.blit(boss_image, boss_rect)
    draw_boss_health()

    # Cập nhật thời gian
    if time_left <= 0:
        save_score(player_name, score)
        reset_flappy_bird_game()
        display_leaderboard()
        pygame.time.wait(2000)
        name_input_screen()

    # Di chuyển và vẽ đạn
    move_bullets()
    draw_bullets()


    # Hiển thị Flappy Bird
    screen.blit(bird_image, typing_bird_rect)

    # Hiển thị Boss và thanh máu
    screen.blit(boss_image, boss_rect)
    draw_boss_health()

    # Cập nhật thời gian
    if time_left <= 0:
        save_score(player_name, score)
        reset_flappy_bird_game()
        display_leaderboard()
        pygame.time.wait(2000)
        name_input_screen()


def draw_boss_health():
    health_bar_width = 200
    health_bar_height = 20
    health_bar_x = boss_rect.centerx - health_bar_width // 2
    health_bar_y = boss_rect.top - 30

    # Vẽ viền thanh máu
    pygame.draw.rect(screen, BLACK, (health_bar_x, health_bar_y, health_bar_width, health_bar_height), 2)
    # Vẽ thanh máu
    current_health_width = int((boss_health / boss_max_health) * health_bar_width)
    pygame.draw.rect(screen, (255, 0, 0), (health_bar_x, health_bar_y, current_health_width, health_bar_height))
def reset_flappy_bird_game():
    global game_started, score, pipes, time_left, player_name, typed_word, current_word, passed_pipes, pipe_letters, bird_rect
    global boss_health, typing_bird_rect, typing_bird_velocity

    game_started = False
    score = 0
    passed_pipes = -1
    pipes.clear()
    pipe_letters.clear()
    bird_rect.center = (100, SCREEN_HEIGHT // 2)
    player_name = ""
    time_left = typing_time_limit
    typed_word = ""
    current_word = random.choice(words)

    # Reset trạng thái boss và Flappy Bird
    boss_health = boss_max_health
    typing_bird_rect = bird_image.get_rect(center=(100, SCREEN_HEIGHT // 2))
    typing_bird_velocity = 0

def name_input_screen():
    global player_name
    name_input = True
    font = pygame.font.SysFont("Arial", 30)
    while name_input:
        screen.fill(WHITE)
        screen.blit(background_image, (0, 0))
        draw_text("Player Name", font, BLACK, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 4)
        draw_text(f"> {player_name}", font, BLACK, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 3)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    player_name += event.unicode

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if start_button_rect.collidepoint(mouse_x, mouse_y) and player_name != "":
                    name_input = False
                elif leaderboard_button_rect.collidepoint(mouse_x, mouse_y):
                    display_leaderboard()  # Chuyển đến màn hình bảng xếp hạng

        # Hiển thị các nút Start và Leaderboard cùng lúc
        screen.blit(start_button_image, start_button_rect)
        screen.blit(leaderboard_button_image, leaderboard_button_rect)
        pygame.display.update()
        clock.tick(FPS)


def main():
    global bird_velocity, game_over, pipes, score, game_started, passed_pipes, typed_word, current_word, time_left, player_name, pipe_letters

    font = pygame.font.SysFont("Arial", 30)
    name_input_screen()
    
    last_time = time.time()

    while True:
        screen.fill(WHITE)
        screen.blit(background_image, (0, 0))

        # Kiểm tra các sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                if start_button_rect.collidepoint(mouse_x, mouse_y) and not game_started:
                    game_started = True

                elif leaderboard_button_rect.collidepoint(mouse_x, mouse_y):
                    display_leaderboard()  # Hiển thị bảng xếp hạng

            if event.type == pygame.KEYDOWN:
                
                typed_letter = event.unicode.upper()
                if pipes and pipes[0].letter == typed_letter:
                        # Di chuyển chim đến tâm khoảng trống giữa chướng ngại vật
                    bird_rect.centery = (pipes[0].top_pipe.bottom + pipes[0].bottom_pipe.top) // 2
                    pipes[0].passed = False
                
                if event.key == pygame.K_SPACE and game_over:
                    game_over = False
                    pipes.clear()
                    bird_rect.center = (100, SCREEN_HEIGHT // 2)
                    bird_velocity = 0
                    score = 0
                    passed_pipes = 0
                    time_left = typing_time_limit
                    game_started = False
                
                if game_started and not game_over:
                    if event.key == pygame.K_BACKSPACE: 
                        typed_word = typed_word[:-1]
                    else:
                        typed_word += event.unicode

        # Nếu trò chơi chưa bắt đầu hoặc đã kết thúc, hiển thị nút Start và Leaderboard
        if game_started and not game_over and passed_pipes == -1:
            passed_pipes = 0
            screen.blit(start_button_image, start_button_rect)
            screen.blit(leaderboard_button_image, leaderboard_button_rect)

        if not game_started:
            # Chạy trò chơi Flappy Bird
            if passed_pipes >= 20:
                passed_pipes = 0
                game_started = True
                screen.blit(background_image, (0, 0))
                pipes.clear()
                current_word = random.choice(words)
                typed_word = ""
                draw_text("Switching to Typing Game!", font, BLACK, SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 3)
            else:
                bird_velocity += GRAVITY
                bird_rect.centery += bird_velocity

                if len(pipes) == 0 or pipes[-1].top_pipe.centerx < SCREEN_WIDTH - 200:
                    new_pipe = create_pipe()
                    pipes.append(new_pipe)
                    pipe_letters.append(new_pipe.letter)

                pipes = move_pipes(pipes)

                draw_pipes(pipes)
                screen.blit(bird_image, bird_rect)

                if check_collision(bird_rect, pipes):
                    game_over = True

                draw_text(f"Score: {passed_pipes}", font, BLACK, 10, 10)

        else:
            # Cập nhật thời gian còn lại
            current_time = time.time()
            if current_time - last_time >= 1:
                time_left -= 1
                last_time = current_time
            if time_left <= 0:
                game_started = False

            # Chuyển sang trò chơi gõ chữ
            typing_game()

        if game_over:
            draw_text("Game Over! Press SPACE to Restart", font, BLACK, SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 3)

        pygame.display.update()
        clock.tick(FPS)

if __name__ == "__main__":
    main()