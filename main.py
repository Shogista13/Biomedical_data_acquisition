import game
from data_acquisition import Data
import pygame
import pandas as pd
import serial
import os
import threading


period = 50
speed = 10
HP = 10
bullet_relative_speed = 0.6
bullet_targeting = 0.005

path = "Data_project"
port_name = 'COM7'
phase = 'control'

run = True

game_instance = game.Game(period,speed,HP,bullet_relative_speed,bullet_targeting)
database = Data(path,phase)

port = serial.Serial(port_name, 115200, timeout=None)
data_splitted = ""
def acquire_data():
    global port,data_splitted
    data = port.readline().decode('utf-8').strip()
    data_splitted = [int(i) for i in data.split(",")]

data_acquisition_thread = threading.Thread(target=acquire_data)
data_acquisition_thread.start()

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        data_acquisition_thread.join()
        database.save_data()
        run = False
    game_instance.spawn_enemies()
    game_instance.move_objects()
    game_instance.draw_objects()
    if game_instance.time % 100 == 0 and game_instance.time > 500:
        database.get_data(data_splitted,game_instance.player,game_instance.enemies,game_instance.enemy_bullets,game_instance.player_bullets,game_instance.HP,game_instance.power_up.exists)
    pygame.display.update()
    pygame.time.delay(10)

