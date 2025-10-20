import pandas as pd
import os
import serial

def get_skin_conductance(signal):
    voltage = 5 / 1023 * signal
    return (5 - voltage) / (10 * voltage)

class Data:
    def __init__(self,path,port_name,phase):
        self.phase = phase
        self.path = path
        column_titles = ["HP", "Power up","Player x", "Player y", "Player speed_x", "Player speed_y", "Player bullet x", "Player bullet y", "Player bullet speed_x",
                         "Player bullet speed_y",'Enemy x', "Enemy y","Enemy speed_x", "Enemy speed_y", "Enemy bullet x", "Enemy bullet y",
                         "Enemy bullet speed_x", "Enemy bullet speed_y", "Humidity", "Temperature", "Skin conductance", "Relative_blood_volume"]
        self.number = len(os.listdir(path))
        self.df = pd.DataFrame(columns=column_titles)
        self.port = serial.Serial(port_name, 9600)

    def get_data(self,player,enemies,enemy_bullets, player_bullets,HP,power_up):
        data = self.port.readline().decode('utf-8').strip()
        data_splitted = data.split(",")
        player_x = player.hitbox.x
        player_y = player.hitbox.y
        player_speed_x = player.direction[0]
        player_speed_y = player.direction[1]
        player_bullet_x = [bullet.hitbox.x for bullet in player_bullets]
        player_bullet_y = [bullet.hitbox.y for bullet in player_bullets]
        player_bullet_speed_x = [bullet.direction[0] for bullet in player_bullets]
        player_bullet_speed_y = [bullet.direction[1] for bullet in player_bullets]
        enemy_x = [enemy.hitbox.x for enemy in enemies]
        enemy_y = [enemy.hitbox.xy for enemy in enemies]
        enemy_speed_x = [enemy.speed_x for enemy in enemies]
        enemy_speed_y = [enemy.speed_y for enemy in enemies]
        enemy_bullet_x = [bullet.hitbox.x for bullet in enemy_bullets]
        enemy_bullet_y = [bullet.hitbox.y for bullet in enemy_bullets]
        enemy_bullet_speed_x = [bullet.direction[0] for bullet in enemy_bullets]
        enemy_bullet_speed_y = [bullet.direction[1] for bullet in enemy_bullets]
        humidity = data_splitted[0]
        temperature = data_splitted[1]
        skin_conductance = get_skin_conductance(data_splitted[2])
        relative_blood_volume = data_splitted[3]
        self.df.loc[len(self.df)] = [HP,power_up, player_x, player_y, player_speed_x, player_speed_y,player_bullet_x,player_bullet_y,
                                     player_bullet_speed_x,player_bullet_speed_y,enemy_x, enemy_y, enemy_speed_x,
                           enemy_speed_y, enemy_bullet_x, enemy_bullet_y, enemy_bullet_speed_x, enemy_bullet_speed_y, humidity, temperature,
                           skin_conductance, relative_blood_volume]

    def save_data(self):
        global df, path, number
        pd.DataFrame.to_csv(self.df, self.path + self.phase + '/subject' + str(self.number))
