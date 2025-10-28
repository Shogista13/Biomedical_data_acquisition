import pandas as pd
import os
#from data_preprocessing import process_data

class Data:
    def __init__(self,path,phase):
        self.phase = phase
        self.path = path
        column_titles = ["HP", "Power up","Player x", "Player y", "Player speed_x", "Player speed_y", "Player bullet x", "Player bullet y", "Player bullet speed_x",
                         "Player bullet speed_y",'Enemy x', "Enemy y","Enemy speed_x", "Enemy speed_y", "Enemy bullet x", "Enemy bullet y",
                         "Enemy bullet speed_x", "Enemy bullet speed_y", "Humidity", "Temperature", "Skin conductance", "Relative blood volume"]
        self.number = len(os.listdir(path+'/'+phase+'/unprocessed'))
        self.df = pd.DataFrame(columns=column_titles)

    def get_data(self,sensor_data,player,enemies,enemy_bullets, player_bullets,HP,power_up):
        player_x = player.hitbox.x
        player_y = player.hitbox.y
        player_speed_x = player.direction[0]
        player_speed_y = player.direction[1]
        player_bullet_x = [bullet.hitbox.x for bullet in player_bullets]
        player_bullet_y = [bullet.hitbox.y for bullet in player_bullets]
        player_bullet_speed_x = [bullet.direction[0] for bullet in player_bullets]
        player_bullet_speed_y = [bullet.direction[1] for bullet in player_bullets]
        enemy_x = [enemy.hitbox.x for enemy in enemies]
        enemy_y = [enemy.hitbox.x for enemy in enemies]
        enemy_speed_x = [enemy.speed_x for enemy in enemies]
        enemy_speed_y = [enemy.speed_y for enemy in enemies]
        enemy_bullet_x = [bullet.hitbox.x for bullet in enemy_bullets]
        enemy_bullet_y = [bullet.hitbox.y for bullet in enemy_bullets]
        enemy_bullet_speed_x = [bullet.direction[0] for bullet in enemy_bullets]
        enemy_bullet_speed_y = [bullet.direction[1] for bullet in enemy_bullets]
        humidity = sensor_data[0]
        temperature = sensor_data[1]
        skin_conductance = sensor_data[2]
        relative_blood_volume = sensor_data[3:]
        self.df.loc[len(self.df)] = [HP,power_up, player_x, player_y, player_speed_x, player_speed_y,player_bullet_x,player_bullet_y,
                                     player_bullet_speed_x,player_bullet_speed_y,enemy_x, enemy_y, enemy_speed_x,
                           enemy_speed_y, enemy_bullet_x, enemy_bullet_y, enemy_bullet_speed_x, enemy_bullet_speed_y, humidity, temperature,
                           skin_conductance,relative_blood_volume]

    def save_data(self):
        pd.DataFrame.to_csv(self.df, self.path +"/" + self.phase + '/unprocessed/subject' + str(self.number))
        #process_data(self.df,self.path,self.phase,str(self.number))