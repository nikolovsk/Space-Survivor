import pygame
import random

pygame.init()

width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Space Survivor")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

player_width = 50
player_height = 50
player_speed = 9
player = pygame.Rect(width // 2 - player_width // 2, height - player_height - 10, player_width, player_height)

fall_speed = 5  # Почетна брзина на паѓање
lives = 3
score = 0
game_over = False
level = 1
shield = False  # Дали играчот има штит
shield_used = False  # Дали штитот е веќе искористен
game_state = "menu"  # "menu", "playing", "game_over"
highest_score = 0

start_time = None  # Времето кога играта започнува
elapsed_time = 0   # Поминато време


# Вчитување на слики за објекти
rock_img = pygame.image.load('rock.png')  # Камен
rock_img = pygame.transform.scale(rock_img, (50, 50))

star_img = pygame.image.load('star.png')  # Ѕвезда
star_img = pygame.transform.scale(star_img, (50, 50))

moon_img = pygame.image.load('moon.png')  # Месечина
moon_img = pygame.transform.scale(moon_img, (50, 50))

planet_img = pygame.image.load('planet.png')  # Планета
planet_img = pygame.transform.scale(planet_img, (70, 50))

bonus_star_img = pygame.image.load('bonus_star.png')  # Бонус ѕвезда
bonus_star_img = pygame.transform.scale(bonus_star_img, (50, 50))

shield_img = pygame.image.load('shield.png')  # Штит
shield_img = pygame.transform.scale(shield_img, (50, 50))

spaceship_img = pygame.image.load('spaceship.png')  # Вселенски брод за играчот
spaceship_img = pygame.transform.scale(spaceship_img, (80, 60))


# Звучни ефекти
background_music = pygame.mixer.Sound("game-level-music.wav")
background_music.play(-1)  # Бесконечна позадинска музика

level_up_sound = pygame.mixer.Sound("level-increased.wav")  # Достигнување на нов левел
life_recharge_sound = pygame.mixer.Sound("winning-a-life.wav")  # Зголемување на бројот на животите
rock_collision_sound = pygame.mixer.Sound("rock-collision.wav")  # Судир со камен
shield_recharge_sound = pygame.mixer.Sound("shield-recharge.wav")  # Добивање на штит
game_over_sound = pygame.mixer.Sound("game-over.wav")  # Game over


# Фонт
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 36)


class FlashEffect:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 50  # Почетна големина
        self.alpha = 255  # Почетна транспарентност
        self.max_size = 100  # Максимална големина
        self.fade_speed = 1  # Брзина на избледување
        self.grow_speed = 5  # Брзина на растење

    def update(self):
        self.size += self.grow_speed
        self.alpha -= self.fade_speed

        # Кога ефектот ќе достигне максимална големина или кога ќе избледи, врати False
        if self.size >= self.max_size or self.alpha <= 0:
            return False
        return True

    def draw(self, screen):
        # Креирање на површина за ефектот и примена на fade ефектот
        flash_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)  # транспарентна површина
        pygame.draw.circle(flash_surface, (255, 255, 0, self.alpha),
                           (self.size // 2, self.size // 2), self.size // 2)
        screen.blit(flash_surface, (self.x - self.size // 2, self.y - self.size // 2))


# Генерирање на рандом паѓачки објекти
def generate_falling_object():
    object_type = random.choice(["rock", "star", "moon", "planet", "bonus_star", "shield"])
    x_pos = random.randint(0, width - 50)
    y_pos = -50  # Почетна позиција над екранот
    return {"type": object_type, "rect": pygame.Rect(x_pos, y_pos, 50, 50)}


# Функција за испишување на текст
def draw_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x - text_surface.get_width() // 2, y))


# Функција за рестартирање на играта
def reset_game():
    global lives, score, fall_speed, game_over, level, shield, shield_used, falling_objects, \
        highest_score, start_time

    lives = 3
    score = 0
    fall_speed = 5
    level = 1
    highest_score = 0
    shield = False
    shield_used = False
    game_over = False
    falling_objects = [generate_falling_object()]
    start_time = pygame.time.get_ticks()  # Почеток на тајмерот

    background_music.stop()
    background_music.play(-1)


# Екран за Game Over
def game_over_screen():
    global game_state, score, highest_score

    if score > highest_score:
        highest_score = score  # Ажурирање на највисокиот резултат

    background_music.stop()
    game_over_sound.play()  # звук за GAME OVER

    screen.fill(BLACK)
    draw_text("Game Over", font, RED, width // 2, height // 3)
    draw_text(f"High Score: {highest_score}", small_font, WHITE, width // 2, height // 2)
    draw_text(f"Time Survived: {elapsed_time // 60}m {elapsed_time % 60}s", small_font, WHITE, width // 2,
              height // 2 + 50)
    draw_text("Press R to Restart or ESC to Exit", small_font, WHITE, width // 2, height // 2 + 150)
    pygame.display.flip()

    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()
                    game_state = "playing"
                    waiting_for_input = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()


# Почетното главно мени за стартување на играта
def main_menu():
    global game_state

    while game_state == "menu":
        screen.fill(BLACK)
        draw_text("Space Survivor", font, WHITE, width // 2, height // 3)
        draw_text("Press ENTER to Play", small_font, WHITE, width // 2, height // 2)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    reset_game()
                    game_state = "playing"
                    return


# Ефект на потрес на екранот при судир со камен
def shake_screen():
    global flash_effects, clock

    shake_duration = 0.3  # во секунди
    shake_intensity = 5

    # Започни потрес
    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < shake_duration * 1000:
        # Генерирање случајни поместувања на екранот
        shake_offset_x = random.randint(-shake_intensity, shake_intensity)
        shake_offset_y = random.randint(-shake_intensity, shake_intensity)

        screen.fill(BLACK)

        for obj in falling_objects:
            obj["rect"].x += shake_offset_x
            obj["rect"].y += shake_offset_y

            if obj["type"] == "rock":
                screen.blit(rock_img, obj["rect"])
            elif obj["type"] == "star":
                screen.blit(star_img, obj["rect"])
            elif obj["type"] == "moon":
                screen.blit(moon_img, obj["rect"])
            elif obj["type"] == "planet":
                screen.blit(planet_img, obj["rect"])
            elif obj["type"] == "bonus_star":
                screen.blit(bonus_star_img, obj["rect"])
            elif obj["type"] == "shield":
                screen.blit(shield_img, obj["rect"])

        screen.blit(spaceship_img, player)

        # Прикажување на ефекти
        for flash in flash_effects[:]:
            if not flash.update():  # Ако ефектот заврши, отстрани го
                flash_effects.remove(flash)
            flash.draw(screen)

        # Прикажување на резултати
        score_text = font.render(f"Score: {score}", True, WHITE)
        lives_text = font.render(f"Lives: {lives}", True, WHITE)
        level_text = font.render(f"Level: {level}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (width - lives_text.get_width() - 10, 10))
        screen.blit(level_text, (width // 2 - level_text.get_width() // 2, 10))

        pygame.display.flip()

        # Врати ги координатите на објектите на нивните оригинални позиции
        for obj in falling_objects:
            obj["rect"].x -= shake_offset_x
            obj["rect"].y -= shake_offset_y

        clock.tick(60)


# Главна функција на играта
def game_loop():
    global lives, score, fall_speed, game_over, level, shield, shield_used, game_state, falling_objects, \
        flash_effects, clock, score, highest_score, elapsed_time, start_time

    falling_objects = [generate_falling_object()]
    game_over_played = False  # Променлива што ги следи повторувањата на звукот

    flash_effects = []

    clock = pygame.time.Clock()

    if start_time is None:
        start_time = pygame.time.get_ticks()

    while game_state == "playing":
        screen.fill(BLACK)

        if not game_over:
            elapsed_time = (pygame.time.get_ticks() - start_time) // 1000  # во секунди

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = "game_over"
                    game_over_screen()
                    return

        # Движење на играчот
        if not game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and player.left > 0:
                player.x -= player_speed
            if keys[pygame.K_RIGHT] and player.right < width:
                player.x += player_speed

            # Движење на паѓачките предмети
            for obj in falling_objects[:]:
                obj["rect"].y += fall_speed
                if obj["rect"].top > height:
                    # Ако предметот падне до дното, одземи поени
                    falling_objects.remove(obj)
                    falling_objects.append(generate_falling_object())
                    if obj["type"] == "star":
                        score -= 10
                    elif obj["type"] == "moon":
                        score -= 20
                    elif obj["type"] == "planet":
                        score -= 30

                # Проверка за судир
                if player.colliderect(obj["rect"]):
                    if obj["type"] == "rock":
                        if shield and not shield_used:
                            # Ако има штит и не е искористен, дозволи да фати камен без да изгуби живот
                            shield_used = True
                        else:
                            # Ако нема штит или штитот е искористен, одземи живот
                            lives -= 1
                            rock_collision_sound.play()  # Звук при судир со камен
                            shake_screen()  # Ефект на потрес на екранот
                    elif obj["type"] == "star":
                        score += 10
                    elif obj["type"] == "moon":
                        score += 20
                    elif obj["type"] == "planet":
                        score += 30
                    elif obj["type"] == "bonus_star":
                        flash_effects.append(FlashEffect(player.centerx, player.centery))  # Додај нов блесок
                        if lives < 3:
                            lives += 1
                            life_recharge_sound.play()  # Звук за зголемување на животите
                        else:
                            score += 50
                    elif obj["type"] == "shield":
                        shield = True
                        shield_used = False
                        shield_recharge_sound.play()  # Звук за добивање на штит
                    falling_objects.remove(obj)
                    falling_objects.append(generate_falling_object())

        if lives <= 0 or score < 0:
            game_over = True

        # Ако е game over, пушти звук
        if game_over and not game_over_played:
            background_music.stop()
            game_over_sound.play()
            game_over_played = True  # Обележи дека звукот е репродуциран
            game_state = "game_over"

        # Прикажување на фигурата која го претставува играчот
        screen.blit(spaceship_img, player)

        # Прикажување на паѓачките предмети
        for obj in falling_objects:
            if obj["type"] == "rock":
                screen.blit(rock_img, obj["rect"])
            elif obj["type"] == "star":
                screen.blit(star_img, obj["rect"])
            elif obj["type"] == "moon":
                screen.blit(moon_img, obj["rect"])
            elif obj["type"] == "planet":
                screen.blit(planet_img, obj["rect"])
            elif obj["type"] == "bonus_star":
                screen.blit(bonus_star_img, obj["rect"])
            elif obj["type"] == "shield":
                screen.blit(shield_img, obj["rect"])

        for flash in flash_effects[:]:
            if not flash.update():  # Ако ефектот заврши, отстранете го
                flash_effects.remove(flash)
            flash.draw(screen)

        if score > highest_score:
            highest_score = score

        score_text = font.render(f"Score: {score}", True, WHITE)
        lives_text = font.render(f"Lives: {lives}", True, WHITE)
        level_text = font.render(f"Level: {level}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (width - lives_text.get_width() - 10, 10))
        screen.blit(level_text, (width // 2 - level_text.get_width() // 2, 10))

        if game_over:
            game_over_screen()

        pygame.display.flip()

        # Брзина на играта и напредување на нивоата
        clock.tick(60)

        if score >= level * 100:  # Како што се зголемуваат поените, така и нивоата
            level += 1
            fall_speed += 0.25  # Зголемување на брзина на движење на паѓачките објекти
            falling_objects.append(generate_falling_object())  # Додади нов предмет
            level_up_sound.play()  # Звук за достигнување на ново ниво


while True:
    if game_state == "menu":
        main_menu()
    elif game_state == "playing":
        game_loop()
    elif game_state == "game_over":
        game_over_screen()
