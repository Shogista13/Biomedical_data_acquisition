#import pandas as pd
#import os
#from data_preprocessing import process_data

class Data:
    def __init__(self,path,phase):
        self.phase = phase
        self.path = path
        column_titles = ["HP","Power up","Player x", "Player y", "Player speed_x", "Player speed_y", "Player bullet x", "Player bullet y", "Player bullet speed_x",
                         "Player bullet speed_y",'Enemy x', "Enemy y","Enemy speed_x", "Enemy speed_y", "Enemy bullet x", "Enemy bullet y",
                         "Enemy bullet speed_x", "Enemy bullet speed_y"]
        self.df = pd.DataFrame(columns=column_titles)

    def get_data(self,player,enemies,enemy_bullets, player_bullets,HP,power_up):
        player_x = player.rect.x
        player_y = player.rect.y
        player_speed_x = player.direction[0]
        player_speed_y = player.direction[1]
        player_bullet_x = [bullet.rect.x for bullet in player_bullets]
        player_bullet_y = [bullet.rect.y for bullet in player_bullets]
        player_bullet_speed_x = [bullet.direction[0] for bullet in player_bullets]
        player_bullet_speed_y = [bullet.direction[1] for bullet in player_bullets]
        enemy_x = [enemy.rect.x for enemy in enemies]
        enemy_y = [enemy.rect.x for enemy in enemies]
        enemy_speed_x = [enemy.speed_x for enemy in enemies]
        enemy_speed_y = [enemy.speed_y for enemy in enemies]
        enemy_bullet_x = [bullet.rect.x for bullet in enemy_bullets]
        enemy_bullet_y = [bullet.rect.y for bullet in enemy_bullets]
        enemy_bullet_speed_x = [bullet.direction[0] for bullet in enemy_bullets]
        enemy_bullet_speed_y = [bullet.direction[1] for bullet in enemy_bullets]
        self.df.loc[len(self.df)] = [HP,power_up, player_x, player_y, player_speed_x, player_speed_y,player_bullet_x,player_bullet_y,
                                     player_bullet_speed_x,player_bullet_speed_y,enemy_x, enemy_y, enemy_speed_x,
                           enemy_speed_y, enemy_bullet_x, enemy_bullet_y, enemy_bullet_speed_x, enemy_bullet_speed_y]

    def save_data(self):
        pd.DataFrame.to_csv(self.df, self.path +'/unprocessed/' + self.phase)