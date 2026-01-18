import pandas as pd
from scipy.signal import butter,sosfiltfilt
import matplotlib.pyplot as plt
import numpy as np
import os
from biosppy.signals.ppg import ppg
#from copy import deepcopy

def normalize_the_signal(signal,sampling_rate):
    multipliers = []
    minimums = []
    for sample in range(len(signal)):
        surrounding = signal[max(0,sample-sampling_rate//2):min(len(signal)-1,sample+sampling_rate//2)]
        minimums.append(min(surrounding))
    for sample in range(len(signal)):
        signal[sample] -= minimums[sample]
    for sample in range(len(signal)):
        surrounding = signal[max(0,sample-sampling_rate//2):min(len(signal)-1,sample+sampling_rate//2)]
        multipliers.append(max(surrounding))
    for sample in range(len(signal)):
        signal[sample] /= multipliers[sample]
    return signal

def find_first_peak(signal,sampling_rate):
    first_peak = max(signal[:sampling_rate])
    first_peak_index = signal.index(first_peak)
    return first_peak,first_peak_index

def find_ppg_peaks(signal,sampling_rate):
    previous_peak,previous_peak_index = find_first_peak(signal,sampling_rate)
    peaks = [0]
    threshold = previous_peak * 0.99
    interval_start = 0
    for timestamp,sample in enumerate(signal):
        if sample > threshold and interval_start == 0 and timestamp - peaks[-1] > 0.25 *sampling_rate:
            interval_start = timestamp
        elif sample < threshold and interval_start>0:
            peak = max(signal[interval_start:timestamp])
            peaks.append(signal[interval_start:timestamp].index(peak)+interval_start)
            threshold = 0.99 * peak
            interval_start = -1
        elif sample < threshold:
            interval_start = 0
    peaks.pop(0)
    return peaks

def get_HR(signal,peaks,sampling_rate):
    HR = []
    for i in range(len(signal)//(sampling_rate)-5):
        heart_beats = [beat for beat in peaks if  i*sampling_rate<= beat < (i+5)*sampling_rate]
        HR.append((len(heart_beats)-1)/(heart_beats[-1]-heart_beats[0])*sampling_rate*60)
    return HR

def show(save_path,filtered_pulse,heart_rate,pulse_time_axis,heart_rate_time_axis,raw_pulse):
    k = 40
    for i in range(k):
        f, axes = plt.subplots(3)
        #axes[0].plot([i for i in range(len(filtered_pulse)//k)],filtered_pulse[len(filtered_pulse)//k*i:(len(filtered_pulse)//k)*(i+1)])
        #axes[1].plot([i for i in range(len(heart_rate)//k)],heart_rate[len(heart_rate)//k*i:(len(heart_rate)//k)*(i+1)])
        axes[0].plot(pulse_time_axis[len(raw_pulse)//k*i:(len(raw_pulse)//k)*(i+1)],raw_pulse[len(raw_pulse)//k*i:(len(raw_pulse)//k)*(i+1)])
        axes[1].plot(pulse_time_axis[len(filtered_pulse)//k*i:(len(filtered_pulse)//k)*(i+1)],filtered_pulse[len(filtered_pulse)//k*i:(len(filtered_pulse)//k)*(i+1)])
        axes[2].plot(heart_rate_time_axis[len(heart_rate)//k*i:(len(heart_rate)//k)*(i+1)],heart_rate[len(heart_rate)//k*i:(len(heart_rate)//k)*(i+1)])
        plt.savefig(save_path+str(i)+'.jpg')
        plt.close()


def calculate_HR_pipeline(load_path,save_path):
    dataframe = pd.read_csv(load_path,header=None,sep = '\t').to_numpy()
    sos = butter(4, (4,8), 'bs',output="sos", fs=1000)
    pulse = dataframe[:,0]
    pulse_no_nan = pulse[~np.isnan(pulse)]
    filtered_pulse = sosfiltfilt(sos,pulse_no_nan)
    #pulse_normalized = normalize_the_signal(filtered_pulse,500)
    #peaks = find_ppg_peaks(pulse_normalized.tolist(),500)
    #heart_rate = get_HR(pulse_normalized,peaks,500)
    result = ppg(filtered_pulse)
    #show(save_path,filtered_pulse,heart_rate)

    show(save_path,result[1],result[6],result[0],result[5],pulse_no_nan)
    #return heart_rate

path = "saved/ML08/biosignals/"
files = os.listdir(path+"unprocessed")
for file in files:
    calculate_HR_pipeline(path+"unprocessed/"+file,path+"graphs/"+file.replace(".txt",""))