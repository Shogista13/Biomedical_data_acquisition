import math
import statistics
import numpy as np
import pandas as pd

def process_spatial_parameters_in_single_frame(player_x,player_y,other_objects_x,other_objects_y):
    number_of_objects = len(other_objects_x)
    distances = [math.sqrt((player_x-other_objects_x[i])**2+(player_y-other_objects_y[i])**2) for i in range(number_of_objects)]
    if distances:
        collapsed = statistics.harmonic_mean(distances)
        #bierzemy średnią harmoniczną, bo bardzo na nią wpływają małe wartości (blisko coś),
        #dalsze obiekty mniej
    else:
        collapsed = None
        #nie wiemy co z tym zrobić, żeby nie psuło analizy,
        #pewnie damy po prostu jakąś dużą liczbę do środka, ale chyba sie nie zdarzy i tak
    return number_of_objects,collapsed

def process_spatial_parameters(player_x_list,player_y_list,other_objects_x_list,other_objects_y_list):
    numbers_of_objects = []
    collapsed_distances = []
    for frame in range(len(player_x_list)):
        number_of_objects,collapsed = process_spatial_parameters_in_single_frame(player_x_list[frame],player_y_list[frame],other_objects_x_list[frame],other_objects_y_list[frame])
        numbers_of_objects.append(number_of_objects)
        collapsed_distances.append(collapsed)
        #bierzemy liczbę przeciwników/pocisków i średnią harmoniczną odległości
    return numbers_of_objects,collapsed_distances

def process_data(dataframe,path,phase):
    eda,era = get_gsr(dataframe['Skin conductance'].tolist())
    heart_rate = get_pulse([sample for samples in dataframe['Relative blood volume'].tolist() for sample in samples])
    #humidity = calculate_derivative(dataframe['Humidity'].tolist())
    number_of_enemies,collapsed_distances_to_enemies = process_spatial_parameters(dataframe['Player x'].tolist(),dataframe['Player y'].tolist(),dataframe['Enemy x'].tolist(),dataframe['Enemy y'].tolist())
    #collapsed_distances_to_enemies_derivative = calculate_derivative(collapsed_distances_to_enemies)
    number_of_enemy_bullets, collapsed_distances_to_enemy_bullets = process_spatial_parameters(dataframe['Player x'].tolist(),dataframe['Player y'].tolist(),dataframe['Enemy bullet x'].tolist(),dataframe['Enemy bullet y'].tolist())
    #collapsed_distances_to_enemy_bullets_derivative = calculate_derivative(collapsed_distances_to_enemy_bullets)
    collection_time = calculate_collection_time(dataframe)
    data = dict({"eda":eda,
                 "era":era,
                 "heart rate":heart_rate,
                 #"humidity derivative":humidity,
                 "number_of_enemies":number_of_enemies,
                 "collapsed_distances_to_enemies":collapsed_distances_to_enemies,
                 #"collapsed_distances_to_enemies_derivative":collapsed_distances_to_enemies_derivative,
                 "number_of_enemy_bullets": number_of_enemy_bullets,
                 "collapsed_distances_to_enemy_bullets": collapsed_distances_to_enemy_bullets,
                 #"collapsed_distances_to_enemy_bullets_derivative": collapsed_distances_to_enemy_bullets_derivative,
                 "HP":dataframe['HP'].tolist(),
                 "Power up":collection_time
                 })
    print(len(eda))
    print(len(heart_rate))
    #print(len(humidity))
    print(len(number_of_enemies))
    print(len(collapsed_distances_to_enemies))
    #print(len(collapsed_distances_to_enemies_derivative))
    print(len(number_of_enemy_bullets))
    print(len(collapsed_distances_to_enemy_bullets))
    #print(len(collapsed_distances_to_enemy_bullets_derivative))
    print(len(dataframe['HP'].tolist()))
    print(len(collection_time))

    df = pd.DataFrame(data)
    pd.DataFrame.to_csv(df, path + '/processed/' + phase)