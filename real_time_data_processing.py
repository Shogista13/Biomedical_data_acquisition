
import pandas as pd
#from biosppy.signals.ppg import ppg
#from biosppy.signals.eda import biosppy_decomposition
from scipy.signal import butter,filtfilt
import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy

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

def get_timeline(HP,sampling_rate):
    time = 0
    timeline = []
    for value in HP:
        timeline.append(time*sampling_rate/5)
        if value == 0:
            time += 1000
        time += 1
    return timeline

def get_time_of_collection(timeline,exists,sampling_rate):
    collection_times = []
    for i,frame in enumerate(exists[1:]):
        if exists[i-1] and not frame:
            collection_times.append(timeline[(i-10)/5*sampling_rate:(i+20)/5*sampling_rate])
    return collection_times



time = np.array([i for i in range(120001)])
dataframe = pd.read_csv("Pomiar0.txt",header=None).to_numpy()
b,a = butter(4, (1,4), 'bp',output="ba", fs=500)
pulse = dataframe[:,0]
pulse_no_nan = pulse[~np.isnan(pulse)]
#original_unfiltered = deepcopy(pulse_no_nan)
filtered_pulse = filtfilt(b,a,pulse_no_nan)
#original_filtered = deepcopy(filtered_pulse)
#minimum = min(filtered_pulse.tolist())
#pulse_normalized = np.subtract(filtered_pulse,minimum)
pulse_normalized = normalize_the_signal(filtered_pulse,500)
peaks = find_ppg_peaks(pulse_normalized.tolist(),500)
heart_rate = get_HR(pulse_normalized,peaks,500)
plt.plot(np.array([i for i in range(235)]),np.array(heart_rate))
plt.show()









'''for i in range(6):
    f,ax = plt.subplots(3)
    ax[0].plot(time[20000*i:20000*(i+1)],original_unfiltered[20000*i:20000*(i+1)])
    ax[1].plot(time[20000*i:20000*(i+1)],original_filtered[20000*i:20000*(i+1)])
    chosen_peaks = np.array([peak for peak in peaks if 20000 * i< peak < 20000*(i+1)])
    ax[2].plot(time[20000*i:20000*(i+1)],pulse_normalized[20000*i:20000*(i+1)])
    ax[2].plot(chosen_peaks,pulse_normalized[chosen_peaks])
    plt.show()'''



'''eda = dataframe[:,1]
eda_no_nan = eda[~np.isnan(eda)]
b,a = butter(4, 3, 'lp', fs=500)
filtered_eda = filtfilt(b,a,eda_no_nan)
processed_eda = biosppy_decomposition(filtered_eda,sampling_rate=500)
pulse = dataframe[:,0]
pulse_no_nan = pulse[~np.isnan(pulse)]
filtered_HR = ppg(pulse_no_nan,sampling_rate=500)
f, ax = plt.subplots(5)

ax[0].plot(time,processed_eda[0][:120000])
ax[1].plot(time,processed_eda[1][:120000])
ax[2].plot(filtered_HR[5],filtered_HR[6][:120000])
ax[3].plot(time,eda_no_nan[:120000])
ax[4].plot(time,pulse_no_nan[:120000])
ax[0].set_ylim(ymin=0)
plt.show()
'''