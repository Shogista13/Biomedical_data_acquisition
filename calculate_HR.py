import pandas as pd
#from biosppy.signals.ppg import ppg
#from biosppy.signals.eda import biosppy_decomposition
from scipy.signal import butter,filtfilt
#import matplotlib.pyplot as plt
import numpy as np
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
        HR.append((len(heart_beats)-1)/(heart_beats[-1]-heart_beats[0])*500*60)
    return HR

def calculate_HR_pipeline():
    dataframe = pd.read_csv("Pomiar0.txt",header=None).to_numpy()
    b,a = butter(4, (1,4), 'bp',output="ba", fs=500)
    pulse = dataframe[:,0]
    pulse_no_nan = pulse[~np.isnan(pulse)]
    filtered_pulse = filtfilt(b,a,pulse_no_nan)
    pulse_normalized = normalize_the_signal(filtered_pulse,500)
    peaks = find_ppg_peaks(pulse_normalized.tolist(),500)
    heart_rate = get_HR(pulse_normalized,peaks,500)
    return heart_rate