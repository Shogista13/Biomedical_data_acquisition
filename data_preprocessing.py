import math
import statistics
from biosppy.signals.ppg import ppg #needs a citation
from biosppy.signals.eda import biosppy_decomposition #needs a citation
from scipy.ndimage import gaussian_filter1d
import numpy as np
import pandas as pd

def calculate_collection_time(dataframe):


def calculate_conductance(sample):
    voltage = 5 / 65535 * sample
    return 1000*(5 - voltage) / (10 * voltage) #w mikrosiemensach

def get_gsr(signal):
    conductance = list(map(calculate_conductance,signal))
    return biosppy_decomposition(conductance,sampling_rate = 5) #zwraca EDA i EDR

def normalize_pulse_volume(sample,min,max): #normalizuje do [0;1]
    return (sample-min)/(max-min)

def get_pulse(signal):
    minimum = min(signal)
    maximum = max(signal)
    normalized_signal = [normalize_pulse_volume(sample,minimum,maximum) for sample in signal]
    features = ppg(normalized_signal,sampling_rate = 20)
    heart_rate_interpolated = np.interp(list(range(len(signal))),features[5],features[6])#oś czasu i BPM
    return heart_rate_interpolated

def process_spatial_parameters_in_single_frame(player_x,player_y,other_objects_x,other_objects_y):
    number_of_objects = len(other_objects_x)
    distances = [math.sqrt((player_x[i]-other_objects_x[i])**2+(player_y[i]-other_objects_y[i])**2) for i in range(number_of_objects)]
    if distances:
        collapsed = statistics.harmonic_mean(distances)
    else:
        collapsed = None
    return number_of_objects,collapsed

def process_spatial_parameters(player_x_list,player_y_list,other_objects_x_list,other_objects_y_list):
    numbers_of_objects = []
    collapsed_distances = []
    for frame in range(len(player_x_list)):
        number_of_objects,collapsed = process_spatial_parameters_in_single_frame(player_x_list[frame],player_y_list[frame],other_objects_x_list[frame],other_objects_y_list[frame])
        numbers_of_objects.append(number_of_objects)
        collapsed_distances.append(collapsed)
    return numbers_of_objects,collapsed_distances

#def smooth(signal,filter_length):
#    if len(signal) > filter_length:
#        smoothed_signal = [statistics.mean(signal[i-filter_length//2:i+filter_length//2]) for i in range(filter_length//2,len(signal)-filter_length//2-1)]
#        return smoothed_signal
#    else:
#        return None

def calculate_derivative(signal):
    smoothed_signal = gaussian_filter1d(signal, sigma=2)
    return np.gradient(smoothed_signal)

def process_data(dataframe,path,phase,number):
    eda,era = get_gsr(dataframe['Skin conductance'].tolist())
    heart_rate = get_pulse([sample for samples in dataframe['Relative blood volume'].tolist() for sample in samples])
    humidity = calculate_derivative(dataframe['Humidity'].tolist())
    number_of_enemies,collapsed_distances_to_enemies = process_spatial_parameters([dataframe['Player x'].tolist(),dataframe['Player y'].tolist()
                                                                                      ,dataframe['Enemy x'].tolist(),dataframe['Enemy y'].tolist()])
    collapsed_distances_to_enemies_derivative = calculate_derivative(collapsed_distances_to_enemies)

    number_of_enemy_bullets, collapsed_distances_to_enemy_bullets = process_spatial_parameters([dataframe['Player x'].tolist(),dataframe['Player y'].tolist()
                                                                                      ,dataframe['Bullet x'].tolist(),dataframe['Bullet y'].tolist()])
    collapsed_distances_to_enemy_bullets_derivative = calculate_derivative(collapsed_distances_to_enemy_bullets)
    data = dict({"eda":eda,
                 "era":era,
                 "heart rate":heart_rate,
                 "humidity derivative":humidity,
                 "number_of_enemies":number_of_enemies,
                 "collapsed_distances_to_enemies":collapsed_distances_to_enemies,
                 "collapsed_distances_to_enemies_derivative":collapsed_distances_to_enemies_derivative,
                 "number_of_enemy_bullets": number_of_enemy_bullets,
                 "collapsed_distances_to_enemy_bullets": collapsed_distances_to_enemy_bullets,
                 "collapsed_distances_to_enemy_bullets_derivative": collapsed_distances_to_enemy_bullets_derivative,
                 "HP":dataframe['Skin conductance'].tolist(),
                 })
    df = pd.DataFrame(data)
    pd.DataFrame.to_csv(df, path + "/" + phase + '/processed/subject' + number)