import game
from data_acquisition import Data
import pygame
import pandas as pd
import serial
import os
import threading
from get_subject_data import Form

run = True

form = Form()
path = form.path
port_name = 'COM7'
phase = 'control'
#period,speed,HP,bullet_relative_speed,bullet_targeting,power_up_strenght,power_up_gradually,power_up_risky_time,
#power_up_animated
phases = {'control':[40,10,10,0.7,0.005,3,False,500,False],
#'more reward, more risky time':[40,10,10,0.7,0.005,4,False,600,False],
'reward in installments':[40,10,10,0.7,0.005,3,True,500,False],
'power up animated with sound effect':[40,10,10,0.7,0.005,2,False,500,True]
}

game_instance = game.Game(*phases[phase])
database = Data(path,phase)

port = serial.Serial(port_name, 115200, timeout=None)
data_splitted = ""

def acquire_data():
    global run,port,data_splitted
    while run:
        data = port.readline().decode('utf-8').strip()
        data_splitted = [float(i.strip('[]')) for i in data.split(",")]

data_acquisition_thread = threading.Thread(target=acquire_data)
data_acquisition_thread.start()

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        run = False
        data_acquisition_thread.join()
        database.save_data()
    game_instance.spawn_enemies()
    game_instance.move_objects()
    game_instance.draw_objects()
    if game_instance.time % 20 == 0 and game_instance.time > 500:
        database.get_data(data_splitted,game_instance.player,game_instance.enemies,game_instance.enemy_bullets,game_instance.player_bullets,game_instance.HP,game_instance.power_up.exists)
    pygame.display.update()
    pygame.time.delay(10)