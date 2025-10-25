import pygame
import random
import math

class Game:
    def __init__(self,period,speed,HP,bullet_relative_speed,bullet_targeting,power_up_strenght):
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.Font(None, 80)
        self.time = 0
        self.enemies = []
        self.enemy_bullets = []
        self.player_bullets = []
        self.bullet_targeting = bullet_targeting
        self.bullet_relative_speed = bullet_relative_speed
        self.HP = HP
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
        self.power_up = Game.PowerUp(self)
        self.power_up_strenght = power_up_strenght
        self.enemies_boundary = self.height // 2

    def display_HP(self):
        text = self.font.render(f'HP: {self.HP}', True,(0,0,0))
        textRect = text.get_rect()
        textRect.center = (self.width - textRect.width//2-50, textRect.height//2 + 50)
        self.surface.blit(text,textRect)

    def display_time(self):
        text = self.font.render(f'Time: {self.time // 100}', True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (self.width - textRect.width // 2 - 50, textRect.height // 2 + 140)
        self.surface.blit(text, textRect)

    def spawn_enemies(self):
        if self.time % self.period == 0 and len(self.enemies) < self.max_enemies:
            self.enemies.append(Game.Enemy(self,random.randint(50, self.width - 50), random.randint(self.enemies_boundary, self.enemies_boundary + self.height//2)))

    def move_objects(self):
        self.player.move()
        self.power_up.spawn_or_collect()
        for enemy in self.enemies:
            enemy.move(self.time)
            enemy.shoot()
        for bullet in self.enemy_bullets:
            bullet.move()
        for bullet in self.player_bullets:
            bullet.move()
        self.enemy_bullets = [bullet for bullet in self.enemy_bullets if not bullet.to_delete]
        self.player_bullets = [bullet for bullet in self.player_bullets if not bullet.to_delete]
        self.time += 1

    def draw_objects(self):
        self.surface.fill((128, 128, 128))
        if self.power_up.exists:
            pygame.draw.rect(self.surface,(255,255,255),self.power_up.hitbox)
        for enemy in self.enemies:
            pygame.draw.rect(self.surface, (0, 255, 0), enemy.hitbox)
        for bullet in self.enemy_bullets:
            pygame.draw.rect(self.surface, (0, 0, 255), bullet.hitbox)
        for bullet in self.player_bullets:
            pygame.draw.rect(self.surface, (0, 102, 0), bullet.hitbox)
        pygame.draw.rect(self.surface, (212, 175, 55), self.player.hitbox)
        self.display_HP()
        self.display_time()

    def change_difficulty(self,speed,bullet_targeting,bullet_relative_speed):
        self.speed = speed
        self.bullet_targeting = bullet_targeting
        self.bullet_relative_speed = bullet_relative_speed

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
                self.game_instance.enemy_bullets.append(Game.EnemyBullet(self.game_instance,bullet_x, bullet_y))

        def move(self, time):
            basic_component = (2 * (int(((time+50) / 100)) % 2) - 1) * self.game_instance.speed // 10
            chaotic_component_x = int(4*math.sin(2 * math.pi * self.hitbox.x)) + random.randint(-4,4)
            chaotic_component_y = int(4*math.sin(2 * math.pi * self.hitbox.y)) + random.randint(-4,4)
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
            self.spawn_time = self.game_instance.time
            size_x = 25
            size_y = 25
            self.hitbox = pygame.Rect(x, y, size_x, size_y)
            self.speed_x = self.game_instance.player.hitbox.x - self.hitbox.x + random.randint(-300, 300)
            self.speed_y = self.game_instance.player.hitbox.y - self.hitbox.y + random.randint(-300, 300)
            self.normalizer = self.game_instance.bullet_relative_speed*self.game_instance.speed / (math.sqrt(self.speed_x ** 2 + self.speed_y ** 2) + 1)
            self.direction = (int(self.normalizer * self.speed_x), int(self.normalizer * self.speed_y))
            self.to_delete = False

        def move(self):
            self.speed_x = (1-self.game_instance.bullet_targeting) * self.speed_x + self.game_instance.bullet_targeting*(self.game_instance.player.hitbox.x - self.hitbox.x)
            self.speed_y = (1-self.game_instance.bullet_targeting) * self.speed_y + self.game_instance.bullet_targeting*(self.game_instance.player.hitbox.y - self.hitbox.y)
            self.normalizer = self.game_instance.bullet_relative_speed*self.game_instance.speed / (math.sqrt(self.speed_x ** 2 + self.speed_y ** 2) + 1)
            self.direction = (int(self.normalizer * self.speed_x), int(self.normalizer * self.speed_y))
            self.hitbox.move_ip(*self.direction)
            self.delete()
            self.check_for_collisions()

        def delete(self):
            #if self.game_instance.time-self.spawn_time == 500:
                #self.to_delete = True
            if not (0 < self.hitbox.x <= self.game_instance.width) :
                self.to_delete = True
            if not (0 < self.hitbox.y <= self.game_instance.height) :
                self.to_delete = True

        def check_for_collisions(self):
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
            self.last_shot = 0

        def calculate_speed(self):
            mouse_position = pygame.mouse.get_pos()
            delta_x = mouse_position[0] - self.hitbox.x
            delta_y = mouse_position[1] - self.hitbox.y
            self.speed_x = delta_x / math.sqrt(delta_x**2+delta_y**2+1)
            self.speed_y = delta_y / math.sqrt(delta_x**2+delta_y**2+1)

        def move(self):
            self.calculate_speed()
            self.direction = (int(self.game_instance.speed * self.speed_x), int(self.game_instance.speed * self.speed_y))
            self.hitbox.move_ip(*self.direction)
            self.bound()
            if pygame.mouse.get_pressed()[0]:
                self.shoot()

        def bound(self):
            self.hitbox.x = min(max(0, self.hitbox.x), self.game_instance.width - self.hitbox.width)
            self.hitbox.y = min(max(0,self.hitbox.y), self.game_instance.height // 2)

        def shoot(self):
            if self.game_instance.time - self.last_shot > 300:
                self.last_shot = self.game_instance.time
                bullet_x = self.hitbox.x + (self.hitbox.width - 25) // 2
                bullet_y = self.hitbox.y + (self.hitbox.height - 25) // 2
                self.game_instance.player_bullets.append(Game.PlayerBullet(self.game_instance,bullet_x, bullet_y))


    class PowerUp:
        def __init__(self,game_instance):
            self.game_instance = game_instance
            self.hitbox = pygame.Rect(game_instance.width//2,game_instance.height//4,50,50)
            self.exists = False
            self.time_since_last_collection = 0

        def spawn_or_collect(self):
            if self.hitbox.colliderect(self.game_instance.player.hitbox) and self.exists:
                self.exists = False
                self.game_instance.HP += self.game_instance.power_up_strenght
                self.time_since_last_collection = self.game_instance.time
                self.game_instance.bullet_targeting += 0.0025
                self.game_instance.bullet_relative_speed += 0.05
                self.game_instance.period -= 10
            elif not self.exists and self.game_instance.time - self.time_since_last_collection == 300:
                self.game_instance.bullet_targeting -= 0.0025
                self.game_instance.bullet_relative_speed -= 0.1
                self.game_instance.period += 10
            elif not self.exists and self.game_instance.time - self.time_since_last_collection == 1000:
                self.exists = True

    class PlayerBullet:
        def __init__(self,game_instance,x, y):
            self.game_instance = game_instance
            size_x = 25
            size_y = 25
            self.hitbox = pygame.Rect(x, y, size_x, size_y)
            self.spawn_time = 0
            self.speed_x = game_instance.player.speed_x
            self.speed_y = game_instance.player.speed_y
            self.normalizer = self.game_instance.bullet_relative_speed*self.game_instance.speed / (math.sqrt(self.speed_x ** 2 + self.speed_y ** 2) + 1)
            self.direction = (int(self.normalizer * self.speed_x), int(self.normalizer * self.speed_y))
            self.to_delete = False

        def find_closest_enemy(self):
            enemies = [(enemy.hitbox.x,enemy.hitbox.y) for enemy in self.game_instance.enemies]
            enemies.sort(key = lambda enemy:(enemy[0]-self.hitbox.x)**2+(enemy[1]-self.hitbox.y)**2)
            if enemies:
                return enemies[0]
            else:
                return (self.game_instance.width//2,self.game_instance.height//2)

        def move(self):
            closest_enemy = self.find_closest_enemy()
            self.speed_x = (1-self.game_instance.bullet_targeting/2) * self.speed_x + self.game_instance.bullet_targeting/2*(closest_enemy[0]- self.hitbox.x)
            self.speed_y = (1-self.game_instance.bullet_targeting/2) * self.speed_y + self.game_instance.bullet_targeting/2*(closest_enemy[1] - self.hitbox.y)
            self.normalizer = self.game_instance.bullet_relative_speed*self.game_instance.speed / (math.sqrt(self.speed_x ** 2 + self.speed_y ** 2) + 1)
            self.direction = (int(self.normalizer * self.speed_x), int(self.normalizer * self.speed_y))
            self.hitbox.move_ip(*self.direction)
            self.delete()
            self.checK_for_collisions()

        def delete(self):
            if self.game_instance.time-self.spawn_time == 500:
                self.to_delete = True
            if not (0 < self.hitbox.x <= self.game_instance.width) :
                self.to_delete = True
            if not (0 < self.hitbox.y <= self.game_instance.height) :
                self.to_delete = True

        def checK_for_collisions(self):
            collisions = self.hitbox.collidelistall([enemy.hitbox for enemy in self.game_instance.enemies])
            if collisions:
                self.to_delete = True
                self.game_instance.enemies.pop(collisions[0])