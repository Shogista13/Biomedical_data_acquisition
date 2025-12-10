from scipy.signal import butter,sosfiltfilt,firwin,lfilter,filtfilt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


dataframe = pd.read_csv("untitled2.txt", header=None,sep = '\t').to_numpy()
sos = butter(4, (0.05, 1), 'bp', output="sos", fs=500)
gsr = dataframe[:, 1]
gsr_no_nan = gsr[~np.isnan(gsr)]
#filter = firwin(501, [0.05,1], pass_zero=False,fs=500)
filtered_gsr = sosfiltfilt(sos, gsr)
#filtered_gsr = lfilter(filter,1,gsr_no_nan)
f,axes = plt.subplots(2)
axes[0].plot([i for i in range(len(gsr_no_nan))],gsr_no_nan)
axes[1].plot([i for i in range(len(filtered_gsr))],filtered_gsr)
plt.show()