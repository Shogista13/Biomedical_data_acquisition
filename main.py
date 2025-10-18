import game
import data_acquisition
import pygame
import pandas as pd
import serial
import os

period = 300
speed = 5

path = "C:/Users/Łuki/GSR/GSR_game/Data_project/"
port_name = 'COM7'
phase = 'control'

run = True

game_instance = game.Game(period,speed)
#database = data_acquisition.Data(path,port_name,phase)

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        #data_acquisition.save_data()
        run = False
    game_instance.spawn_enemies()
    game_instance.move_objects(keys)
    game_instance.draw_objects()
    #game_instance.change_difficulty(5,0.01) #!!!!!!!!!!!!!!!!!!! jest 5,0.01 teraz, jak odkomentujecie i zmienicie to bedzie hardcore
    pygame.display.update()
    #if game.instance.time % 100 == 0:
        #data_acquisition.get_data()
    pygame.time.delay(10)