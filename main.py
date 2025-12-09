import game
from data_acquisition import Data
import pygame
from get_subject_data import Form
import time

run = True
discrete_time = 0
form = Form()
path = form.path

phase = 'power up in installments with sound effect'#"control"#'busy music'#
#period,speed,HP,bullet_relative_speed,bullet_targeting,power_up_strenght,power_up_gradually,power_up_risky_time,
#power_up_animated,subdued_color
phases = {'control':[40,10,10,0.7,0.005,3,False,500,False,False,0],
'reward in installments':[40,10,10,0.7,0.005,3,True,500,False,False,0],
'power up in installments with sound effect':[40,10,10,0.7,0.005,4,True,500,True,False,0],
'subdued colors':[40,10,10,0.7,0.005,3,False,500,False,True,0],
'busy music':[40,10,10,0.7,0.005,3,False,500,False,False,1],
'soft music':[40,10,10,0.7,0.005,3,False,500,False,False,2]
}

game_instance = game.Game(*phases[phase])
database = Data(path,phase)
start_time = time.time()

while run and discrete_time < 18000:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        run = False
    game_instance.play()
    if game_instance.time % 20 == 0 and game_instance.time > 500 and game_instance.HP > 0:
        database.get_data(game_instance.player,game_instance.enemies,game_instance.enemy_bullets,game_instance.player_bullets,game_instance.HP,game_instance.power_up.exists,round(time.time() - start_time, 2))
    if game_instance.HP == 0:
        pygame.mixer.stop()
        game_instance = game.Game(*phases[phase])
    discrete_time += 1

database.save_data()