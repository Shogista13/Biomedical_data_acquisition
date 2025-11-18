import math
import statistics
from biosppy.signals.ppg import ppg #needs a citation
from biosppy.signals.eda import biosppy_decomposition #needs a citation
from scipy.ndimage import gaussian_filter1d
import numpy as np
import pandas as pd

def calculate_collection_time(dataframe):
    power_up_exists = dataframe["Power up"]
    nr_of_samples = len(power_up_exists)
    collected = [i for i,value in enumerate(power_up_exists[0:-2]) if value and not power_up_exists[i+1]] #get the time of collection of the power up
    time_to_analyze = []
    for i in collected:
        time_to_analyze.extend(list(range(max(0,i-200),min(nr_of_samples,i+1000))))
    #bierzemy około 2 sekundy przed i 15 sekund po zebraniu power_upa
    time_to_analyze = [i in time_to_analyze for i in range(nr_of_samples)]
    return time_to_analyze

def calculate_conductance(sample):
    voltage = 3.3 / 65535 * sample
    return (3.3 - voltage) / (10 * voltage) #w mikrosiemensach

def get_gsr(signal):
    conductance = list(map(calculate_conductance,signal))
    return biosppy_decomposition(conductance,sampling_rate = 5) #zwraca EDA i EDR

def normalize_pulse_volume(sample,min,max): #normalizuje do [-1;1]
    return (sample-min)/(max-min)

def get_pulse(signal):
    minimum = min(signal)
    maximum = max(signal)
    normalized_signal = [normalize_pulse_volume(sample,minimum,maximum) for sample in signal]
    features = ppg(normalized_signal,sampling_rate = 100)
    #5 - 6 to oś czasu i BPM (bo ten algorytm nie zwraca BPM w jednakowych odstępach tylko w takich gdzie obliczy
    heart_rate_interpolated = np.interp(list(range(len(signal)//20)),features[5],features[6])
    #interpolujemy BPM w czasie, kiedy są inne parametry, żeby łatwiej porównywać
    return heart_rate_interpolated

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

def calculate_derivative(signal):
    smoothed_signal = gaussian_filter1d(signal, sigma=2)
    return np.gradient(smoothed_signal) #filtruje noise i lizy pochodną

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