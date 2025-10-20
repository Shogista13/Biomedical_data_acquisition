import game
import data_acquisition
import pygame
import pandas as pd
import serial
import os

period = 200
speed = 10
HP = 10
bullet_relative_speed = 1.2
bullet_targeting = 0.05

path = "C:/Users/Łuki/GSR/GSR_game/Data_project/"
port_name = 'COM7'
phase = 'control'

run = True

game_instance = game.Game(period,speed,HP,bullet_relative_speed,bullet_targeting)
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
    game_instance.move_objects()
    game_instance.draw_objects()
    #game_instance.change_difficulty(5,0.01) #!!!!!!!!!!!!!!!!!!! jest 5,0.01 teraz, jak odkomentujecie i zmienicie to bedzie hardcore
    pygame.display.update()
    #if game.instance.time % 100 == 0:
        #data_acquisition.get_data(game_instance.player,game_instance.enemies,game_instance.enemy_bullets,game_instance.player_bullets,game_instance.HP,game_instance.power_up.exists)
    pygame.time.delay(10)