import game
from data_acquisition import Data
import pygame
from get_subject_data import Form

run = True
time = 0
form = Form()
path = form.path

phase = 'control'
#period,speed,HP,bullet_relative_speed,bullet_targeting,power_up_strenght,power_up_gradually,power_up_risky_time,
#power_up_animated,subdued_color
phases = {'control':[40,10,10,0.7,0.005,3,False,500,False,False],
'reward in installments':[40,10,10,0.7,0.005,3,True,500,False,False],
'power up animated with sound effect':[40,10,10,0.7,0.005,2,False,500,True,False],
'subdued colors':[40,10,10,0.7,0.005,3,False,500,False,True],
}

game_instance = game.Game(*phases[phase])
database = Data(path,phase)

while run and time < 18000:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        run = False
    game_instance.play()
    if game_instance.time % 20 == 0 and game_instance.time > 500 and game_instance.HP > 0:
        database.get_data(game_instance.player,game_instance.enemies,game_instance.enemy_bullets,game_instance.player_bullets,game_instance.HP,game_instance.power_up.exists)
    time += 1

database.save_data()