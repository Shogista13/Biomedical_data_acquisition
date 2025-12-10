from scipy.signal.windows import hamming
from scipy.signal import ShortTimeFFT,butter,sosfiltfilt,decimate,firwin,lfilter
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pywt import wavedec,cwt

def get_spectrogram(ppg_signal,sampling_rate):
    window = hamming(5*sampling_rate,sym=True)
    SFT = ShortTimeFFT(window, hop=len(window)//2, fs=sampling_rate, scale_to='psd')
    spectrogram = SFT.spectrogram(ppg_signal)
    return spectrogram,SFT.t(len(ppg_signal)),SFT.f

def plot_spectrogram(ppg_signal,sampling_rate):
    spec, time, freq = get_spectrogram(ppg_signal, sampling_rate)
    spec_db = 10 * np.log10(spec + 1e-10)
    plt.imshow(spec_db, aspect='auto', origin='lower', extent=[time[0], time[-1], freq[0], freq[-1]])
    plt.show()

def eda_wavelet_transform(eda_signal,sampling_rate):
    eda_signal_decimated = decimate(decimate(eda_signal, 10), 5)
    sos = butter(4, (0.05, 0.1), 'bp', output="sos", fs=10)
    eda_filtered = sosfiltfilt(sos, eda_signal_decimated, padlen=100)
    #decomposed = wavedec(eda_filtered,wavelet='haar')
    #continously_decomposed = cvt()
    plt.plot(np.array([i for i in range(len(eda_filtered))]),eda_filtered)
    plt.show()

eda_wavelet_transform(pd.read_csv("Pomiar0.txt",header=None).to_numpy()[:,1],500)

'''

eda_signal_decimated = decimate(decimate(eda_signal,10),5)
sos = butter(4, (0.05, 1), 'bp', output="sos", fs=10)
eda_filtered = sosfiltfilt(sos,eda_signal_decimated,padlen = 100)
    
filter = firwin(500,(0.05,1),fs=10,pass_zero=False)
eda_filtered = lfilter(filter,1,eda_signal_decimated)
print(eda_filtered)

dataframe = pd.read_csv("Pomiar0.txt",header=None).to_numpy()
pulse = dataframe[:,0]
b,a = butter(4, (1,8), 'bp',output="ba", fs=500)
f,axes = plt.subplots(2)
axes[0].plot(np.array([i for i in range(20000)]),pulse[100000:120000])
pulse_filtered = filtfilt(b,a,pulse)
axes[1].plot(np.array([i for i in range(20000)]),pulse_filtered[100000:120000])
plt.show()
plot_spectrogram(pulse_filtered,500)
'''