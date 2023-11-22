import math
from random import choice
import numpy as np

import pygame


FPS = 60

RED = 0xFF0000
BLUE = 0x0000FF
YELLOW = 0xFFC91F
GREEN = 0x00FF00
MAGENTA = 0xFF03B8
CYAN = 0x00FFCC
BLACK = (0, 0, 0)
WHITE = 0xFFFFFF
GREY = 0x7D7D7D
BLUE_RED_GRADIENT = []
for i in range(256):
    red = str(hex(i))
    green = str(hex(50))
    blue = str(hex(230 - (i*3)//4))
    if len(red) == 3:
        red = red[0:2] + '0' + red[2:]
    if len(green) == 3:
        green = green[0:2] + '0' + green[2:]
    if len(blue) == 3:
        blue = blue[0:2] + '0' + blue[2:]
    BLUE_RED_GRADIENT.append(red[0:2] + red[2:].upper() + green[2:].upper() + blue[2:].upper())

GAME_COLORS = [RED, BLUE, YELLOW, GREEN, MAGENTA, CYAN]

g = 10000  # Ускорение свободного падения
k_walls = 1.0  # Коэффицент потери скорости при ударе о стену
k_balls = 1.0  # Коэффицент потери скорости при ударе шариков друг с другом
k_dry_friction = 0.0  # Коэффицент сухой силы трения
k_viscous_friction = 0.0  # Коэффицент вязкой силы трения

WIDTH = 800
HEIGHT = 600


class Ball:
    def __init__(self, screen, x=40, y=HEIGHT/2):
        """ Конструктор класса ball

        Args:
        x - начальное положение мяча по горизонтали
        y - начальное положение мяча по вертикали
        r - радиус шара
        """
        self.screen = screen
        self.x = x
        self.y = y
        self.r = 15
        self.vx = 0
        self.vy = 0
        self.ax = 0
        self.ay = 0
        self.mass = 30
        self.color = choice(BLUE_RED_GRADIENT)
        self.live = 30

    def move(self):
        """Переместить мяч по прошествии единицы времени.

        Метод описывает перемещение мяча за один кадр перерисовки. То есть, обновляет значения
        self.x и self.y с учетом скоростей self.vx и self.vy, силы гравитации, действующей на мяч,
        и стен по краям окна (размер окна 800х600).
        """
        self.hitedges()
        self.movementevolution()

        self.ax = 0
        self.ay = 0

    def movementevolution(self):
        if self.vx >= 0:
            self.x += min(self.vx, abs(self.x + self.r - WIDTH))
        elif self.vx < 0:
            self.x += max(self.vx, -abs(self.x - self.r))

        if self.vy >= 0:
            self.y += min(self.vy, abs(self.y + self.r - HEIGHT))
        elif self.vy < 0:
            self.y += max(self.vy, -abs(self.y - self.r))

        self.vy += self.ay
        self.vx += self.ax

    def hittest(self, obj):
        if (self.x - obj.x)**2 + (self.y - obj.y)**2 <= (self.r + obj.r)**2:
            return True
        else:
            return False

    def hitedges(self):
        if (self.x + self.r >= WIDTH) and (self.vx >= 0):
            self.x = WIDTH - self.r
            self.vx = - self.vx * k_walls
        if (self.x <= self.r) and (self.vx < 0):
            self.x = self.r
            self.vx = -self.vx * k_walls

        if (self.y + self.r >= HEIGHT) and (self.vy >= 0):
            self.y = HEIGHT - self.r
            self.vy = - self.vy * k_walls
        if (self.y <= self.r) and (self.vy < 0):
            self.y = self.r
            self.vy = -self.vy * k_walls

    def draw(self):
        velocity = int(2 * (self.vx**2 + self.vy**2))
        if velocity > 255:
            self.color = BLUE_RED_GRADIENT[255]
        else:
            self.color = BLUE_RED_GRADIENT[velocity]

        pygame.draw.circle(
            self.screen,
            self.color,
            (self.x, self.y),
            self.r
        )


class Gun:
    def __init__(self, screen):
        self.screen = screen
        self.f2_power = 1
        self.f2_on = 0
        self.an = 1
        self.bullet_radius = 15
        self.bullet_mass = 30
        self.color = GREY

    def fire2_start(self, event):
        self.f2_on = 1

    def fire2_end(self, event):
        """Выстрел мячом.

        Происходит при отпускании кнопки мыши.
        Начальные значения компонент скорости мяча vx и vy зависят от положения мыши.
        """
        global balls, bullet, ballspairs
        bullet += 1
        new_ball = Ball(self.screen)
        new_ball.r = self.bullet_radius
        new_ball.mass = self.bullet_mass
        self.an = math.atan2((event.pos[1]-new_ball.y), (event.pos[0]-new_ball.x))
        new_ball.vx = self.f2_power * math.cos(self.an)
        new_ball.vy = self.f2_power * math.sin(self.an)
        balls.append(new_ball)
        for i in range(len(balls) - 1):
            ballspairs.append((balls[i], new_ball))
        self.f2_on = 0
        self.f2_power = 1

    def targetting(self, event):
        """Прицеливание. Зависит от положения мыши."""
        if event:
            self.an = math.atan2((event.pos[1]-450), (event.pos[0]-20))
        else:
            self.color = GREY

    def draw(self):
        if self.f2_on:
            power = int(2 * self.f2_power ** 2)
            if power >= 255:
                self.color = BLUE_RED_GRADIENT[255]
            else:
                self.color = BLUE_RED_GRADIENT[power]
        if not hide_interface:
            pygame.draw.rect(self.screen, self.color, pygame.Rect(25, HEIGHT/2 - 15, 30, 30))

    def power_up(self):
        if self.f2_on:
            if self.f2_power < 10:
                self.f2_power += 0.05
        else:
            self.color = GREY


class Target:
    def __init__(self, screen):
        self.screen = screen
        self.points = 0
        self.live = 1
        self.new_target()
        self.vx = 0
        self.vy = 0

    def new_target(self):
        """ Инициализация новой цели. """
        x = self.x = np.random.randint(600, 780)
        y = self.y = np.random.randint(300, 550)
        r = self.r = np.random.randint(2, 50)
        color = self.color = RED

    def hit(self, points=1):
        """Попадание шарика в цель."""
        self.points += points

    def draw(self):
        pygame.draw.circle(
            self.screen,
            self.color,
            (self.x, self.y),
            self.r
        )


def gravity_force(center_x, center_y):
    for ball in balls:
        l = np.array([center_x - ball.x, center_y - ball.y])
        absl = np.linalg.norm(l)

        if absl >= 70:
            a = (g/absl**3) * l
        else:
            a = np.array([0, 0])

        ball.ax += a[0]
        ball.ay += a[1]


def dry_friction_force():
    for ball in balls:
        v = np.array([ball.vx, ball.vy])
        absv = np.linalg.norm(v)

        ball.ax += (- v/absv * k_dry_friction)[0]
        ball.ay += (- v/absv * k_dry_friction)[1]


def viscous_friction_force():
    for ball in balls:
        v = np.array([ball.vx, ball.vy])

        ball.ax += (- v * k_viscous_friction)[0]
        ball.ay += (- v * k_viscous_friction)[1]


def balls_collision(check_for_collisions_in_frame):
    for ballpair in ballspairs:
        ball1 = ballpair[0]
        ball2 = ballpair[1]

        if ((ball1.mass > 100 or ball2.mass > 100) or check_for_collisions_in_frame) and ball1.hittest(ball2):
            v1 = np.array([ball1.vx, ball1.vy])
            v2 = np.array([ball2.vx, ball2.vy])
            v1rel2 = v1 - v2
            l = np.array([ball2.x - ball1.x, ball2.y - ball1.y])
            absl = np.linalg.norm(l)

            v1rel2_l = l * (np.dot(v1rel2, l))/(absl ** 2)
            v2rel2_col = v1rel2_l * (2 * ball1.mass / (ball1.mass + ball2.mass))
            v1rel2_col = v1rel2 - v1rel2_l + v1rel2_l * ((ball1.mass - ball2.mass)/(ball1.mass + ball2.mass))

            v1_col = v1rel2_col + v2
            v2_col = v2rel2_col + v2

            ball1.vx = k_balls * v1_col[0]
            ball1.vy = k_balls * v1_col[1]

            ball2.vx = k_balls * v2_col[0]
            ball2.vy = k_balls * v2_col[1]

            if (absl >= ball1.r) and (absl >= ball2.r):
                l1_col = - (l + l * (ball1.r/(2 * absl) + ball2.r/(2 * absl) - 1/2) *((ball2.mass * ball2.r)/(ball1.mass * ball1.r + ball2.mass * ball2.r)))
                l2_col = l + l * (ball1.r/(2 * absl) + ball2.r/(2 * absl) - 1/2) * ((ball1.mass * ball1.r)/(ball1.mass * ball1.r + ball2.mass * ball2.r))
            else:
                l1_col = - (l + l * (ball1.r / absl + ball2.r / absl - 1) * (
                            (ball2.mass * ball2.r) / (ball1.mass * ball1.r + ball2.mass * ball2.r)))
                l2_col = l + l * (ball1.r / absl + ball2.r / absl - 1) * (
                            (ball1.mass * ball1.r) / (ball1.mass * ball1.r + ball2.mass * ball2.r))

            ball1.x = ball2.x + l1_col[0]
            ball1.y = ball2.y + l1_col[1]
            ball2.x = ball1.x + l2_col[0]
            ball2.y = ball1.y + l2_col[1]


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
bullet = 0
balls = []
ballspairs = []

clock = pygame.time.Clock()
gun = Gun(screen)
#target = Target(screen)

finished = False
counter = 0
hide_interface = False
check_for_collision_in_frame = False
keys_pressed = {'SPACE': False, 'LSHIFT': False}

while not finished:
    screen.fill(WHITE)
    gun.draw()
    #target.draw()
    for b in balls:
        b.draw()

    font1 = pygame.font.Font(None, 36)
    font2 = pygame.font.Font(None, 28)

    if not hide_interface:
        bullets_count = font1.render('Balls on screen: ' + str(bullet), True, BLACK, WHITE)
        bullets_radius = font2.render('Bullet radius: ' + str(gun.bullet_radius), True, BLACK, WHITE)
        bullets_mass = font2.render('Bullet mass: ' + str(int(gun.bullet_mass)), True, BLACK, WHITE)
        damping_factor_walls = font2.render('Dumping factor(walls): ' + str(round(k_walls, 2)), True, BLACK, WHITE)
        damping_factor_balls = font2.render('Dumping factor(balls): ' + str(round(k_balls, 2)), True, BLACK, WHITE)
        dry_friction_coefficient = font2.render('Dry friction coefficient: ' + str(round(k_dry_friction, 2)), True, BLACK, WHITE)
        viscous_friction_coefficient = font2.render('Viscous friction coefficient: ' + str(round(k_viscous_friction, 3)), True, BLACK, WHITE)

        screen.blit(bullets_count, (10, 10))
        screen.blit(bullets_mass, (WIDTH - 180, 10))
        screen.blit(bullets_radius, (WIDTH - 180, 33))
        screen.blit(damping_factor_balls, (10, HEIGHT - 80))
        screen.blit(damping_factor_walls, (10, HEIGHT - 105))
        screen.blit(dry_friction_coefficient, (10, HEIGHT - 55))
        screen.blit(viscous_friction_coefficient, (10, HEIGHT - 30))

    pygame.display.update()

    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finished = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            gun.fire2_start(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            gun.fire2_end(event)
        elif event.type == pygame.MOUSEMOTION:
            gun.targetting(event)
        elif event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()
            '''
            ESC -- завершить приложение
            Стрелки вверх-вниз -- изменение радиуса шаров
            Стрелки вправо-влево -- изменение масс шаров
            R -- сбросить значения к исходным. gun.bullet_radius = 5 gun.bullet_mass = 10
            k_walls = 1, k_balls = 1
            B -- установить значение gun.bullet_radius = 60, gun.bullet_mass = 1000
            1 и LSHIFT + 1 -- увеличить и уменьшить кооффициент k_walls соответственно
            2 и LSHIFT + 2 -- увеличить и уменьшить кооффициент k_balls соответственно
            3 и LSHIFT + 3 -- увеличить и уменьшить кооффициент k_dry_coefficient соответственно
            4 и LSHIFT + 4 -- увеличить и уменьшить кооффициент k_viscous_coefficient соответственно
            SPACE -- создает большое количества шариков с теми же параметрами, что и пушка, но в центре экрана
            H -- спрятать интерфейс
            '''
            if event.key == pygame.K_ESCAPE:
                finished = True
            elif event.key == pygame.K_SPACE:
                keys_pressed['SPACE'] = True
            elif event.key == pygame.K_LSHIFT:
                keys_pressed['LSHIFT'] = True
            elif event.key == pygame.K_UP:
                if gun.bullet_radius < 60:
                    gun.bullet_radius += 1
            elif event.key == pygame.K_DOWN:
                if gun.bullet_radius > 5:
                    gun.bullet_radius -= 1
            if event.key == pygame.K_RIGHT:
                if 10 <= gun.bullet_mass < 200:
                    gun.bullet_mass += 10
                elif 200 <= gun.bullet_mass < 500:
                    gun.bullet_mass += 20
                elif 500 <= gun.bullet_mass < 1000:
                    gun.bullet_mass += 50
                elif 4 <= gun.bullet_mass < 10:
                    gun.bullet_mass += 1
            elif event.key == pygame.K_LEFT:
                if 10 < gun.bullet_mass <= 200:
                    gun.bullet_mass -= 10
                elif 200 < gun.bullet_mass <= 500:
                    gun.bullet_mass -= 20
                elif 500 < gun.bullet_mass <= 1000:
                    gun.bullet_mass -= 50
                elif 4 < gun.bullet_mass <= 10:
                    gun.bullet_mass -= 1
            elif event.key == pygame.K_r:
                gun.bullet_radius = 10
                gun.bullet_mass = 10
                k_walls = 1.0
                k_balls = 1.0
                k_dry_friction = 0.0
                k_viscous_friction = 0.0
            elif event.key == pygame.K_b:
                gun.bullet_radius = 60
                gun.bullet_mass = 1000
            elif keys_pressed['LSHIFT'] and event.key == pygame.K_1:
                k_walls -= 0.01
            elif event.key == pygame.K_1:
                k_walls += 0.01
            elif keys_pressed['LSHIFT'] and event.key == pygame.K_2:
                k_balls -= 0.01
            elif event.key == pygame.K_2:
                k_balls += 0.01
            elif keys_pressed['LSHIFT'] and event.key == pygame.K_3:
                k_dry_friction -= 0.01
            elif event.key == pygame.K_3:
                k_dry_friction += 0.01
            elif keys_pressed['LSHIFT'] and event.key == pygame.K_4:
                k_viscous_friction -= 0.005
            elif event.key == pygame.K_4:
                k_viscous_friction += 0.005
            elif event.key == pygame.K_h:
                if not hide_interface:
                    hide_interface = True
                else:
                    hide_interface = False
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                keys_pressed['SPACE'] = False
            elif event.key == pygame.K_LSHIFT:
                keys_pressed['LSHIFT'] = False

    if keys_pressed['SPACE']:
        bullet += 1
        new_ball = Ball(screen, WIDTH / 2, HEIGHT / 2)
        new_ball.r = gun.bullet_radius
        new_ball.mass = gun.bullet_mass
        new_ball.vx = np.random.randint(-40, 40) / 10
        new_ball.vy = np.random.randint(-40, 40) / 10
        balls.append(new_ball)
        for i in range(len(balls) - 1):
            ballspairs.append((balls[i], new_ball))

    # gravity_force(WIDTH / 2, HEIGHT / 2)

    viscous_friction_force()
    dry_friction_force()

    if counter > 0:
        counter = 0
        check_for_collision_in_frame = True

    balls_collision(check_for_collision_in_frame)

    check_for_collision_in_frame = False
    counter += 1

    print(sum([ball.mass * (ball.vx**2 + ball.vy**2) for ball in balls]))
    for b in balls:
        b.move()
        #if b.hittest(target) and target.live:
            #target.live = 0
            #target.hit()
            #target.new_target()
    gun.power_up()

pygame.quit()
