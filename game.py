import pygame
import random
import math

class Game:
    def __init__(self,period,speed):
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.Font(None, 80)
        self.time = 0
        self.enemies = []
        self.bullets = []
        self.HP = 3
        info = pygame.display.Info()
        self.width = info.current_w
        self.height = info.current_h
        self.surface = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
        self.max_enemies = 5
        self.player_starting_y = self.height//4
        self.time = 0
        self.period = period
        self.speed = speed
        self.player = Game.Player(self)
        self.enemies_boundary = self.height // 2

    def display_HP(self):
        text = self.font.render(f'HP: {self.HP}', True,(0,0,0))
        textRect = text.get_rect()
        textRect.center = (self.width - textRect.width//2-50, textRect.height//2 + 50)
        self.surface.blit(text,textRect)

    def spawn_enemies(self):
        if self.time % self.period == 0 and len(self.enemies) < self.max_enemies:
            self.enemies.append(Game.Enemy(self,random.randint(50, self.width - 50), random.randint(self.enemies_boundary, self.enemies_boundary + self.height//2)))

    def move_objects(self,keys):
        self.player.move(keys)
        for enemy in self.enemies:
            enemy.move(self.time)
            enemy.shoot()
        for bullet in self.bullets:
            bullet.move()
        self.bullets = [bullet for bullet in self.bullets if not bullet.to_delete]
        self.time += 1

    def draw_objects(self):
        self.surface.fill((128, 128, 128))
        pygame.draw.rect(self.surface, (255, 0, 0), self.player.hitbox)
        for enemy in self.enemies:
            pygame.draw.rect(self.surface, (0, 255, 0), enemy.hitbox)
        for bullet in self.bullets:
            pygame.draw.rect(self.surface, (0, 0, 255), bullet.hitbox)
        self.display_HP()

    class Enemy:
        def __init__(self,game_instance, x, y):
            self.game_instance = game_instance
            size_x = 50
            size_y = 50
            self.hitbox = pygame.Rect(x, y, size_x, size_y)
            self.speed_x = 0
            self.speed_y = 0

        def shoot(self):
            if self.game_instance.time % self.game_instance.period == 0 and self.game_instance.time > 500:
                bullet_x = self.hitbox.x + (self.hitbox.width - 25) // 2
                bullet_y = self.hitbox.y + (self.hitbox.height - 25) // 2
                self.game_instance.bullets.append(Game.EnemyBullet(self.game_instance,bullet_x, bullet_y))

        def move(self, time):
            basic_component = (2 * (int(((time+50) / 100)) % 2) - 1) * self.game_instance.speed // 10
            chaotic_component_x = int(4*math.sin(2 * math.pi * self.hitbox.x))
            chaotic_component_y = int(4*math.sin(2 * math.pi * self.hitbox.y))
            centalizing_component_x = (self.game_instance.width//2 - self.hitbox.x)//100
            centalizing_component_y = (self.game_instance.enemies_boundary + self.game_instance.height//4 - self.hitbox.y)//100
            self.speed_x += (basic_component +  chaotic_component_x + centalizing_component_x)
            self.speed_y += (basic_component + chaotic_component_y + centalizing_component_y)
            self.hitbox.move_ip(self.speed_x//50, self.speed_y//50)
            self.bound()

        def bound(self):
            self.hitbox.x = min(max(0, self.hitbox.x), self.game_instance.width - self.hitbox.width)
            self.hitbox.y = min(max(self.game_instance.height // 2,self.hitbox.y), self.game_instance.height)

    class EnemyBullet:
        def __init__(self,game_instance,x, y):
            self.game_instance = game_instance
            size_x = 25
            size_y = 25
            self.hitbox = pygame.Rect(x, y, size_x, size_y)
            self.speed_x = self.game_instance.player.hitbox.x - self.hitbox.x + random.randint(-300, 300)
            self.speed_y = self.game_instance.player.hitbox.y - self.hitbox.y + random.randint(-300, 300)
            self.normalizer = 3*self.game_instance.speed / (math.sqrt(self.speed_x ** 2 + self.speed_y ** 2) + 1)
            self.direction = (int(self.normalizer * self.speed_x), int(self.normalizer * self.speed_y))
            self.to_delete = False

        def move(self):
            self.speed_x = 0.985 * self.speed_x + 0.015*(self.game_instance.player.hitbox.x - self.hitbox.x)
            self.speed_y = 0.985 * self.speed_y + 0.015*(self.game_instance.player.hitbox.y - self.hitbox.y)
            self.normalizer = 2*self.game_instance.speed / (math.sqrt(self.speed_x ** 2 + self.speed_y ** 2) + 1)
            self.direction = (int(self.normalizer * self.speed_x), int(self.normalizer * self.speed_y))

            self.hitbox.move_ip(*self.direction)
            self.bound()
            self.checK_for_collisions()

        def bound(self):
            if not (0 < self.hitbox.x < self.game_instance.width and 0 < self.hitbox.y < self.game_instance.height):
                self.to_delete = True

        def checK_for_collisions(self):
            if self.hitbox.colliderect(self.game_instance.player.hitbox):
                self.game_instance.HP -= 1
                self.to_delete = True

    class Player:
        def __init__(self,game_instance):
            self.game_instance = game_instance
            size_x = 50
            size_y = 50
            self.hitbox = pygame.Rect(self.game_instance.width // 2, self.game_instance.player_starting_y, size_x, size_y)
            self.speed = 0
            self.speed_x = 0
            self.speed_y = 0
            self.direction = (0, 0)

        def calculate_speed(self, keys):
            speed_limit = 30
            if keys[pygame.K_LEFT]:
                self.speed_x -= 1
                self.speed_x = max(self.speed_x, -speed_limit)
            elif keys[pygame.K_RIGHT]:
                self.speed_x += 1
                self.speed_x = min(self.speed_x, speed_limit)
            if keys[pygame.K_UP]:
                self.speed_y -= 1
                self.speed_y = max(self.speed_y, -speed_limit)
            elif keys[pygame.K_DOWN]:
                self.speed_y += 1
                self.speed_y = min(self.speed_y, speed_limit)

        def move(self, keys):
            self.calculate_speed(keys)
            normalizer = self.game_instance.speed/(self.speed_x ** 2 + self.speed_y ** 2 + 1)**(2/5)
            self.direction = (int(normalizer * self.speed_x), int(normalizer * self.speed_y))
            self.hitbox.move_ip(*self.direction)
            self.bound()

        def bound(self):
            self.hitbox.x = min(max(0, self.hitbox.x), self.game_instance.width - self.hitbox.width)
            self.hitbox.y = min(max(0,self.hitbox.y), self.game_instance.height // 2)