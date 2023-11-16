import math
from random import choice, randint
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
GAME_COLORS = [RED, BLUE, YELLOW, GREEN, MAGENTA, CYAN]

g = 0  # Ускорение свободного падения
G = 0  # Кэффициент, пропорциональный силе взаимодействия частиц
k = 1  # Коэффицент потери скорости при ударе о стену

WIDTH = 800
HEIGHT = 600


class Ball:
    def __init__(self, screen, x=40, y=450):
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
        self.color = choice(GAME_COLORS)
        self.live = 30

    def move(self):
        """Переместить мяч по прошествии единицы времени.

        Метод описывает перемещение мяча за один кадр перерисовки. То есть, обновляет значения
        self.x и self.y с учетом скоростей self.vx и self.vy, силы гравитации, действующей на мяч,
        и стен по краям окна (размер окна 800х600).
        """
        self.hitedges()
        self.movementevolution()

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
            self.vx = - self.vx * k
        if (self.x <= self.r) and (self.vx < 0):
            self.x = self.r
            self.vx = -self.vx * k

        if (self.y + self.r >= HEIGHT) and (self.vy >= 0):
            self.y = HEIGHT - self.r
            self.vy = - self.vy * k
        if (self.y <= self.r) and (self.vy < 0):
            self.y = self.r
            self.vy = -self.vy * k

    def draw(self):
        pygame.draw.circle(
            self.screen,
            self.color,
            (self.x, self.y),
            self.r
        )


class Gun:
    def __init__(self, screen):
        self.screen = screen
        self.f2_power = 2
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
        self.f2_power = 2

    def targetting(self, event):
        """Прицеливание. Зависит от положения мыши."""
        if event:
            self.an = math.atan((event.pos[1]-450) / (event.pos[0]-20))
            self.color = RED
        else:
            self.color = GREY

    def draw(self):
        pygame.draw.rect(self.screen, self.color, pygame.Rect(15, 435, 30, 30))

    def power_up(self):
        if self.f2_on:
            if self.f2_power < 7:
                self.f2_power += 1
            self.color = RED
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
        x = self.x = randint(600, 780)
        y = self.y = randint(300, 550)
        r = self.r = randint(2, 50)
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


def balls_interactions():
    for ballpair in ballspairs:
        ball1 = ballpair[0]
        ball2 = ballpair[1]

        l = np.array([ball2.x - ball1.x, ball2.y - ball1.y])
        absl = np.linalg.norm(l)

        a2 = - (G/absl**3) * l
        a1 = -a2

        ball1.ax = a1[0]
        ball1.ay = a1[1]
        ball2.ax = a2[0]
        ball2.ay = a2[1]


def balls_collision():
    for ballpair in ballspairs:
        ball1 = ballpair[0]
        ball2 = ballpair[1]

        if ball1.hittest(ball2):
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

            ball1.vx = v1_col[0]
            ball1.vy = v1_col[1]

            ball2.vx = v2_col[0]
            ball2.vy = v2_col[1]

            l1_col = - l * (ball1.r/(2 * absl) + ball2.r/(2 * absl) + 1/2)
            l2_col = l * (ball1.r/(2 * absl) + ball2.r/(2 * absl) + 1/2)

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

while not finished:
    screen.fill(WHITE)
    gun.draw()
    #target.draw()
    for b in balls:
        b.draw()

    font1 = pygame.font.Font(None, 36)
    font2 = pygame.font.Font(None, 28)

    bullets_count = font1.render('Bullets on screen: ' + str(bullet), True, BLACK, WHITE)
    bullets_radius = font2.render('Bullet radius: ' + str(gun.bullet_radius), True, BLACK, WHITE)
    bullets_mass = font2.render('Bullet mass: ' + str(gun.bullet_mass), True, BLACK, WHITE)

    screen.blit(bullets_radius, (WIDTH - 180, 10))
    screen.blit(bullets_mass, (WIDTH - 180, 30))
    screen.blit(bullets_count, (10, 10))

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
            if event.key == pygame.K_UP:
                if gun.bullet_radius < 59:
                    gun.bullet_radius += 1
            elif event.key == pygame.K_DOWN:
                if gun.bullet_radius > 5:
                    gun.bullet_radius -= 1
            if event.key == pygame.K_RIGHT:
                if gun.bullet_mass < 250:
                    gun.bullet_mass += 5
            elif event.key == pygame.K_LEFT:
                if gun.bullet_mass > 10:
                    gun.bullet_mass -= 5



    #balls_interactions()

    balls_collision()

    #print(sum([ball.vx**2 + ball.vy**2 for ball in balls]))
    for b in balls:
        b.move()
        #if b.hittest(target) and target.live:
            #target.live = 0
            #target.hit()
            #target.new_target()
    gun.power_up()

pygame.quit()
