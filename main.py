import game
from data_acquisition import Data
import pygame
from get_subject_data import Form
import time

run = True
discrete_time = 0
form = Form()
path = form.path

phase = 'subdued colors' # we just changed it manually every time

# IT CAN MORE EASILY BE READ FROM Gamemodes.png
# period,speed,HP,bullet_relative_speed,bullet_targeting,power_up_strength,power_up_gradually,power_up_risky_time,
# power_up_animated,subdued_color,music
phases = {'control':[40,10,10,0.7,0.005,3,False,500,False,False,0],
'reward in installments':[40,10,10,0.7,0.005,3,True,500,False,False,0],
'power up in installments with sound effect':[40,10,10,0.7,0.005,3,True,500,True,False,0],
'subdued colors':[40,10,10,0.7,0.005,3,False,500,False,True,0],
'busy music':[40,10,10,0.7,0.005,3,False,500,False,False,1],
'soft music':[40,10,10,0.7,0.005,3,False,500,False,False,2]
}

game_instance = game.Game(*phases[phase])# * unpacks the values into arguments
database = Data(path,phase)# for storing and saving the game data
start_time = time.time() # measuring the time of the game (in real world)

while run and time.time() - start_time < 240:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        run = False
    game_instance.play()
    if discrete_time%20 == 0:# saves the data every 20 frames
        database.get_data(game_instance.player,game_instance.enemies,game_instance.enemy_bullets,game_instance.player_bullets,game_instance.HP,game_instance.power_up.exists,round(time.time() - start_time, 2))
    if game_instance.HP == 0:
        if discrete_time % 20 != 0:# saves the data if it was not saved in this frame:
            database.get_data(game_instance.player,game_instance.enemies,game_instance.enemy_bullets,game_instance.player_bullets,game_instance.HP,game_instance.power_up.exists,round(time.time() - start_time, 2))
        pygame.mixer.stop()# stops the music
        game_instance = game.Game(*phases[phase])
    discrete_time += 1
    while time.time() - start_time < discrete_time*0.01:# does not happen because the game
        # runs too slow for 100 fps, is better than a "raw" delay, because it doesn't slow it further
        # but it caps the (average) fps at 100 fps
        pygame.time.delay(10)
database.save_data()# saves to a csv