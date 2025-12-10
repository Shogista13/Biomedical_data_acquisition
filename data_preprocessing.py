import numpy as np
import pandas as pd




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