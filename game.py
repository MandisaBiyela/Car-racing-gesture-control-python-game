import pygame
import cv2
import mediapipe as mp
import sys
import math
import random
import time

# -------------------- INIT ------------------------
pygame.init()
WIDTH, HEIGHT = 800, 750
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gesture Racing with Power-ups & Day-Night Cycle")
clock = pygame.time.Clock()

# Load assets
car_img = pygame.transform.scale(pygame.image.load("car.png"), (60, 120))
coin_img = pygame.transform.scale(pygame.image.load("coin.png"), (30, 30))
engine_sound = pygame.mixer.Sound("engine.mp3")
crash_sound = pygame.mixer.Sound("crash.mp3")
boost_sound = pygame.mixer.Sound("boost.mp3")

# Fonts
font = pygame.font.SysFont("Arial", 30)

# -------------------- MediaPipe ------------------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1,
                       min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# -------------------- Game Variables ------------------------
player_name = ""
level = "Easy"
score = 0
base_speed = 8
speed = base_speed
car_x = WIDTH//2 - 30
car_y = HEIGHT - 150
smoothed_x = 0.5
open_palm = False
thumbs_up = False
obstacles = []
coins = []
shield = False
shield_timer = 0
boost_timer = 0
start_time = time.time()

def detect_gestures():
    global smoothed_x, open_palm, thumbs_up
    ret, frame = cap.read()
    if not ret:
        return smoothed_x
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    res = hands.process(rgb)
    open_palm = False
    thumbs_up = False
    if res.multi_hand_landmarks:
        lm = res.multi_hand_landmarks[0].landmark
        mp_draw.draw_landmarks(frame, res.multi_hand_landmarks[0], mp_hands.HAND_CONNECTIONS)
        x = lm[mp_hands.HandLandmark.WRIST].x
        smoothed_x = 0.6 * smoothed_x + 0.4 * x
        # open palm: all finger tips above wrist
        if all(lm[tip].y < lm[mp_hands.HandLandmark.WRIST].y for tip in [8,12,16,20]):
            open_palm = True
        # thumbs up: thumb tip above IP joint and other fingers folded
        if lm[4].y < lm[3].y and all(lm[tip].y > lm[tip-2].y for tip in [8,12,16,20]):
            thumbs_up = True
    return smoothed_x

# Game progression: day-night cycle based on elapsed time
def get_background_color():
    elapsed = time.time() - start_time
    # cycle every 30 seconds
    phase = (elapsed % 30) / 30
    # day = light blue, night = dark blue
    day = pygame.Color(135,206,235)
    night = pygame.Color(25,25,112)
    return day.lerp(night, abs(math.sin(math.pi * phase)))

# Power-ups: coin collection and shield

def spawn_coin():
    if random.random() < 0.01:
        x = random.choice([160,260,360,460,560])
        coins.append(pygame.Rect(x, -30, 30, 30))

def move_coins():
    global score, shield, shield_timer
    for coin in coins[:]:
        coin.y += speed
        if coin.y > HEIGHT:
            coins.remove(coin)
        elif car_rect.colliderect(coin):
            coins.remove(coin)
            score += 5
            shield = True
            shield_timer = pygame.time.get_ticks()

def draw_coins():
    for coin in coins:
        win.blit(coin_img, (coin.x, coin.y))

# Obstacles

def spawn_obstacle():
    if random.random() < 0.02:
        x = random.choice([160,260,360,460,560])
        obstacles.append(pygame.Rect(x, -100, 60, 100))

def move_obstacles():
    global score
    for obs in obstacles[:]:
        obs.y += speed
        if obs.y > HEIGHT:
            obstacles.remove(obs)
            score += 1

# Collision
def detect_collision():
    if shield: return False
    for obs in obstacles:
        if car_rect.colliderect(obs): return True
    return False

# Level progression: increase base_speed every score threshold

def progression():
    global base_speed
    if score > 50: base_speed = 12
    elif score > 30: base_speed = 10
    else: base_speed = 8

# Input screens
def input_name():
    global player_name
    name = ""
    while True:
        win.fill((0,0,0))
        txt = font.render("Enter Name: " + name + "|", True, (255,255,255))
        win.blit(txt,(200,300))
        pygame.display.update()
        for e in pygame.event.get():
            if e.type==pygame.QUIT: sys.exit()
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_RETURN and name:
                    player_name = name; return
                elif e.key==pygame.K_BACKSPACE:
                    name = name[:-1]
                else: name += e.unicode

def select_level():
    global level, speed
    opts=["Easy","Medium","Hard"]
    idx=0
    while True:
        win.fill((0,0,0))
        for i,o in enumerate(opts):
            color=(255,255,0) if i==idx else (255,255,255)
            txt=font.render(o,True,color)
            win.blit(txt,(350,300+i*40))
        pygame.display.update()
        for e in pygame.event.get():
            if e.type==pygame.QUIT: sys.exit()
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_UP: idx=(idx-1)%3
                if e.key==pygame.K_DOWN: idx=(idx+1)%3
                if e.key==pygame.K_RETURN:
                    level=opts[idx]
                    speed = {"Easy":8,"Medium":10,"Hard":13}[level]
                    return

# Main loop
# Main loop (wrapped to avoid recursion on restart)
def main_loop():
    while True:
        game_running = main()
        if not game_running:
            break

# Modified main function to return when quitting
def main():
    global speed, car_x, car_rect, shield, boost_timer
    input_name()
    select_level()
    engine_sound.play(-1)
    running = True
    tick = 0
    boost_timer = pygame.time.get_ticks()  # ✅ INIT boost_timer properly
    while running:
        clock.tick(60)
        tick += 1
        bg = get_background_color()
        win.fill(bg)

        # Road drawing
        pygame.draw.rect(win, (50, 50, 50), (140, 0, 520, HEIGHT))
        for y in range(0, HEIGHT, 40):
            pygame.draw.rect(win, (255, 255, 255), (WIDTH//2 - 5, y + (tick % 40), 10, 20))

        # Gesture detection
        hand_x = detect_gestures()

        # Speed control
        if open_palm:
            speed = min(base_speed + score * 0.02, 25)
        else:
            speed = max(speed - 0.2, base_speed)

        # Boost with gradual decay
        if thumbs_up and pygame.time.get_ticks() - boost_timer > 5000:
            boost_sound.play()
            speed += 5  # boost
            boost_timer = pygame.time.get_ticks()
        if pygame.time.get_ticks() - boost_timer > 2000:
            speed = max(speed - 0.5, base_speed)

        # Spawning and movement
        spawn_obstacle()
        move_obstacles()
        spawn_coin()
        move_coins()
        progression()

        # Draw obstacles and coins
        for obs in obstacles:
            pygame.draw.rect(win, (200, 0, 0), obs)
        draw_coins()

        # Car positioning
        draw_y = car_y + int(5 * math.sin(tick * 0.15))
        draw_x = int(140 + hand_x * 520 - 30)
        car_x = max(140, min(draw_x, 580))
        car_rect = pygame.Rect(car_x, draw_y, 60, 120)
        win.blit(car_img, (car_x, draw_y))

        # Shield drawing
        if shield and pygame.time.get_ticks() - shield_timer < 5000:
            pygame.draw.circle(win, (0, 255, 255), (car_x + 30, draw_y + 60), 40, 4)
        else:
            shield = False

        # UI
        txt = font.render(f"{player_name} Score:{score}", True, (255, 255, 255))
        win.blit(txt, (20, 20))
        txt2 = font.render(f"Level:{level}", True, (255, 255, 255))
        win.blit(txt2, (650, 20))
        pygame.display.update()

        # Collision
        if detect_collision():
            crash_sound.play()
            engine_sound.stop()
            for i in range(3):
                win.fill((255, 0, 0))
                pygame.display.update()
                pygame.time.wait(100)
                win.fill((0, 0, 0))
                pygame.display.update()
                pygame.time.wait(100)
            return game_over()

        # Events
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                cap.release()
                pygame.quit()
                return False
    cap.release()
    pygame.quit()
    return False

# Game over screen, return True if restarting, False if quitting
def game_over():
    while True:
        win.fill((0, 0, 0))
        txt = font.render(f"Game Over! Score: {score}", True, (255, 255, 255))
        win.blit(txt, (250, 300))
        txt2 = font.render("R: Restart  Q: Quit", True, (255, 255, 255))
        win.blit(txt2, (270, 350))
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    reset_game()
                    return True
                if e.key == pygame.K_q:
                    return False

# Reset game state
def reset_game():
    global score, base_speed, speed, car_x, smoothed_x, open_palm, thumbs_up
    global obstacles, coins, shield, shield_timer, boost_timer, start_time
    score = 0
    base_speed = 8
    speed = base_speed
    car_x = WIDTH // 2 - 30
    smoothed_x = 0.5
    open_palm = False
    thumbs_up = False
    obstacles = []
    coins = []
    shield = False
    shield_timer = 0
    boost_timer = 0
    start_time = time.time()

if __name__ == '__main__':
    main_loop()

