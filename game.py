import pygame
import random
import math

class Game:
    def __init__(self,period,speed,HP,bullet_relative_speed,bullet_targeting,power_up_strength,power_up_gradually,power_up_risky_time,power_up_animated,subdued_colors):
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.Font(None, 80)

        info = pygame.display.Info()
        self.width = info.current_w
        self.height = info.current_h
        self.surface = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)

        self.subdued_colors = subdued_colors
        self.player_sprite = "Resprite_exports/Player"+str(int(subdued_colors))+".gif"
        self.enemy_sprite = "Resprite_exports/Enemy"+str(int(subdued_colors))+".gif"
        self.bullet_sprite = "Resprite_exports/Bullet"+str(int(subdued_colors))+".gif"
        self.power_up_sprite = "Resprite_exports/Medkit"+str(int(subdued_colors))+".gif"
        self.background = pygame.image.load("Resprite_exports/Background"+str(int(subdued_colors))+".jpg").convert()

        self.time = 0
        self.enemies = []
        self.enemy_bullets = []
        self.player_bullets = []
        self.player = Game.Player(self)
        self.max_HP = HP

        self.bullet_targeting = bullet_targeting
        self.bullet_relative_speed = bullet_relative_speed
        self.period = period
        self.speed = speed
        self.max_enemies = 5
        self.HP = HP

        self.power_up = Game.PowerUp(self)
        self.power_up_strength = power_up_strength
        self.power_up_gradually = power_up_gradually
        self.power_up_risky_time = power_up_risky_time
        self.power_up_animated = power_up_animated

        self.enemies_boundary = 2*self.height // 3

    def display_HP(self):
        text = self.font.render(f'HP: {self.HP}', True,(255,255,255))
        textRect = text.get_rect()
        textRect.center = (self.width - textRect.width//2-50, textRect.height//2 + 50)
        self.surface.blit(text,textRect)

    def display_time(self):
        text = self.font.render(f'Time: {self.time // 100}', True, (255, 255, 255))
        textRect = text.get_rect()
        textRect.center = (self.width - textRect.width // 2 - 50, textRect.height // 2 + 140)
        self.surface.blit(text, textRect)

    def spawn_enemies(self):
        if self.time % self.period == 0 and len(self.enemies) < self.max_enemies:
            self.enemies.append(Game.Enemy(self,random.randint(50, self.width - 50), random.randint(self.enemies_boundary, self.enemies_boundary + self.height//3)))

    def death(self):
        time_till_respawn = 10
        while time_till_respawn > 0:
            self.surface.fill((100,100,100))
            text = self.font.render(f'Time till respawning: {time_till_respawn}', True, (0, 0, 0))
            textRect = text.get_rect()
            textRect.center = (self.width // 2 ,self.height// 2)
            self.surface.blit(text, textRect)
            pygame.display.update()
            time_till_respawn -= 1
            pygame.time.delay(990)

    def move_objects(self):
        self.player.move()
        self.power_up.spawn_or_collect()
        for enemy in self.enemies:
            enemy.move()
        for bullet in self.enemy_bullets:
            bullet.move()
        for bullet in self.player_bullets:
            bullet.move()
        self.enemy_bullets = [bullet for bullet in self.enemy_bullets if not bullet.to_delete]
        self.player_bullets = [bullet for bullet in self.player_bullets if not bullet.to_delete]
        self.time += 1

    def draw_objects(self):
        self.surface.blit(self.background, (0, 0))
        if self.power_up.exists:
            self.surface.blit(self.power_up.image,self.power_up.rect)
        for enemy in self.enemies:
            self.surface.blit(enemy.image,enemy.rect)
        for bullet in self.enemy_bullets:
            self.surface.blit(bullet.image,bullet.rect)
        for bullet in self.player_bullets:
            self.surface.blit(bullet.image, bullet.rect)
        self.surface.blit(self.player.image, self.player.rect)
        self.display_HP()
        self.display_time()

    def change_difficulty(self, speed, bullet_targeting, bullet_relative_speed):
        self.speed = speed
        self.bullet_targeting = bullet_targeting
        self.bullet_relative_speed = bullet_relative_speed

    def play(self):
        self.spawn_enemies()
        self.move_objects()
        self.draw_objects()
        if self.HP < 1:
            self.death()
        pygame.display.update()
        pygame.time.delay(10)

    class GameObject:
        def __init__(self, game_instance, x, y,sprite_path):
            self.sprite_path = sprite_path
            self.image = pygame.image.load(self.sprite_path).convert()
            self.game_instance = game_instance
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.speed_x = 0
            self.speed_y = 0

        def rotate(self):
            self.image = pygame.image.load(self.sprite_path).convert()
            x = self.rect.x
            y = self.rect.y
            if self.direction[1] != 0:
                angle = int(math.atan(self.direction[0] / self.direction[1]) * 180 / math.pi)
            else:
                angle = 90
            if self.direction[1] > 0:
                angle += 180
            self.image = pygame.transform.rotate(self.image, angle)
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y

    class PowerUp:
        def __init__(self,game_instance):
            self.game_instance = game_instance
            self.image = pygame.image.load(game_instance.power_up_sprite).convert()
            self.rect = self.image.get_rect()
            self.rect.x = game_instance.width//2
            self.rect.y = game_instance.height//3
            self.exists = False
            self.time_since_last_collection = 0

        def spawn_or_collect(self):
            if self.rect.colliderect(self.game_instance.player.rect) and self.exists:
                self.collected()
            elif not self.exists and self.game_instance.time - self.time_since_last_collection == self.game_instance.power_up_risky_time: #300
                self.restore_difficulty()
            elif not self.exists and self.game_instance.time - self.time_since_last_collection == 3000:
                self.exists = True

        def collected(self):
            if self.game_instance.power_up_animated:
                self.play_animation()
            self.exists = False
            self.time_since_last_collection = self.game_instance.time
            self.game_instance.bullet_targeting += 0.0025
            self.game_instance.bullet_relative_speed += 0.05
            self.game_instance.period -= 10
            if not self.game_instance.power_up_gradually:
                self.game_instance.HP += self.game_instance.power_up_strength
            else:
                self.heal_gradually()

        def heal_gradually(self):
            if (self.game_instance.time - self.time_since_last_collection)%1000 == 0 and 0<(self.game_instance.time - self.time_since_last_collection)<= self.game_instance.power_up_strength * 1000:
                self.game_instance.HP += 1

        def restore_difficulty(self):
            self.game_instance.bullet_targeting -= 0.0025
            self.game_instance.bullet_relative_speed -= 0.1
            self.game_instance.period += 10

        def play_animation(self):
            pass

    class Sprite(GameObject):
        def __init__(self, game_instance, x, y, sprite_path):
            super().__init__(game_instance, x, y, sprite_path)
            self.direction = (0, 0)

        def calculate_speed(self):
            if isinstance(self, Game.Enemy):
                basic_component = (2 * (
                            int(((self.game_instance.time + 50) / 100)) % 2) - 1) * self.game_instance.speed // 10
                chaotic_component_x = int(4 * math.sin(2 * math.pi * self.rect.x))
                chaotic_component_y = int(4 * math.sin(2 * math.pi * self.rect.y))
                centralizing_component_x = (self.game_instance.width // 2 - self.rect.x) // 100
                centralizing_component_y = (
                                                       self.game_instance.enemies_boundary + self.game_instance.height // 6 - self.rect.y) // 100
                self.speed_x += (basic_component + chaotic_component_x + centralizing_component_x)
                self.speed_y += (basic_component + chaotic_component_y + centralizing_component_y)
                self.direction = (self.speed_x // 50, self.speed_y // 50)
            elif isinstance(self, Game.Player):
                mouse_position = pygame.mouse.get_pos()
                delta_x = mouse_position[0] - self.rect.centerx
                delta_y = mouse_position[1] - self.rect.centery
                speed_magnitude = math.sqrt(delta_x ** 2 + delta_y ** 2 + 1)
                if speed_magnitude > 40:
                    self.speed_x = delta_x / math.sqrt(delta_x ** 2 + delta_y ** 2 + 1)
                    self.speed_y = delta_y / math.sqrt(delta_x ** 2 + delta_y ** 2 + 1)
                else:
                    self.speed_x = 0
                    self.speed_y = 0
                self.direction = (int(self.game_instance.speed * self.speed_x), int(self.game_instance.speed * self.speed_y))

        def move(self):
            self.calculate_speed()
            self.rect.move_ip(*self.direction)
            self.bound()
            self.rotate()
            if isinstance(self,Game.Enemy) and self.game_instance.time % self.game_instance.period == 0 and self.game_instance.time > 500:
                self.shoot()
            elif isinstance(self, Game.Player) and self.game_instance.time - self.last_shot > 100 and pygame.mouse.get_pressed()[0]:
                self.shoot()

        def shoot(self):
            bullet_x = self.rect.centerx
            bullet_y = self.rect.centery
            if isinstance(self, Game.Enemy):
                self.game_instance.enemy_bullets.append(Game.EnemyBullet(self.game_instance, bullet_x, bullet_y))
            elif isinstance(self, Game.Player):
                self.game_instance.player_bullets.append(Game.PlayerBullet(self.game_instance, bullet_x, bullet_y))
                self.last_shot = self.game_instance.time

        def bound(self):
            self.rect.x = min(max(0, self.rect.x), self.game_instance.width - self.rect.width)
            if isinstance(self, Game.Enemy):
                self.rect.y = min(max(self.game_instance.enemies_boundary, self.rect.y),
                                  self.game_instance.height - self.rect.height)
            elif isinstance(self, Game.Player):
                self.rect.y = min(max(0, self.rect.y), 2 * self.game_instance.height // 3)

    class Enemy(Sprite):
        def __init__(self, game_instance, x, y):
            super().__init__(game_instance, x, y, game_instance.enemy_sprite)

    class Player(Sprite, pygame.sprite.Sprite):
        def __init__(self, game_instance):
            super().__init__(game_instance, game_instance.width // 2, game_instance.height // 3,
                             game_instance.player_sprite)
            self.last_shot = 0

    class Bullet(GameObject):
        def __init__(self, game_instance, x, y):
            super().__init__(game_instance,x,y,game_instance.bullet_sprite)
            self.spawn_time = game_instance.time
            self.to_delete = False

        def delete(self):
            if self.game_instance.time-self.spawn_time == 800:
                self.to_delete = True
            if not (0 < self.rect.x <= self.game_instance.width) :
                self.to_delete = True
            if not (0 < self.rect.y <= self.game_instance.height) :
                self.to_delete = True

        def move(self):
            closest_enemy = self.find_closest_enemy()
            self.speed_x = ( 1 - self.game_instance.bullet_targeting) * self.speed_x + self.game_instance.bullet_targeting * (closest_enemy[0] - self.rect.centerx)
            self.speed_y = (1 - self.game_instance.bullet_targeting) * self.speed_y + self.game_instance.bullet_targeting * (closest_enemy[1] - self.rect.centery)
            self.normalizer = self.game_instance.bullet_relative_speed * self.game_instance.speed / (math.sqrt(self.speed_x ** 2 + self.speed_y ** 2) + 1)
            self.direction = (int(self.normalizer * self.speed_x), int(self.normalizer * self.speed_y))
            self.rect.move_ip(*self.direction)
            self.delete()
            self.check_for_collisions()
            self.rotate()

        def find_closest_enemy(self):
            if isinstance(self, Game.PlayerBullet):
                enemies = [(enemy.rect.centerx,enemy.rect.centery) for enemy in self.game_instance.enemies]
                enemies.sort(key = lambda enemy:(enemy[0]-self.rect.centerx)**2+(enemy[1]-self.rect.centery)**2)
                if enemies:
                    return enemies[0]
                else:
                    return (self.game_instance.width//2,self.game_instance.height//2)
            elif isinstance(self, Game.EnemyBullet):
                return (self.game_instance.player.rect.centerx, self.game_instance.player.rect.centery)

        def check_for_collisions(self):
            if isinstance(self, Game.PlayerBullet):
                collisions = self.rect.collidelistall([enemy.rect for enemy in self.game_instance.enemies])
                if collisions:
                    self.to_delete = True
                    self.game_instance.enemies.pop(collisions[0])
            elif isinstance(self, Game.EnemyBullet):
                if self.rect.colliderect(self.game_instance.player.rect):
                    self.game_instance.HP -= 1
                    self.to_delete = True

    class PlayerBullet(Bullet):
        def __init__(self,game_instance,x,y):
            super().__init__(game_instance,x,y)
            mouse_position = pygame.mouse.get_pos()
            self.speed_x = mouse_position[0] - self.rect.x
            self.speed_y = mouse_position[1] - self.rect.y
            self.normalizer = self.game_instance.bullet_relative_speed*self.game_instance.speed / (math.sqrt(self.speed_x ** 2 + self.speed_y ** 2) + 1)
            self.direction = (int(self.normalizer * self.speed_x), int(self.normalizer * self.speed_y))
            self.to_delete = False

    class EnemyBullet(Bullet):
        def __init__(self,game_instance,x, y):
            super().__init__(game_instance,x,y)
            self.speed_x = self.game_instance.player.rect.centerx - self.rect.centerx + random.randint(-300, 300)
            self.speed_y = self.game_instance.player.rect.centery - self.rect.centery + random.randint(-300, 300)
            self.normalizer = self.game_instance.bullet_relative_speed*self.game_instance.speed / (math.sqrt(self.speed_x ** 2 + self.speed_y ** 2) + 1)
            self.direction = (int(self.normalizer * self.speed_x), int(self.normalizer * self.speed_y))
