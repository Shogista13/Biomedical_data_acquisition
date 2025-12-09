from scipy.signal import butter,sosfiltfilt,firwin,lfilter,filtfilt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


dataframe = pd.read_csv("Pomiar0.txt", header=None).to_numpy()
#sos = butter(4, (0.05, 1), 'bp', output="sos", fs=500)
gsr = dataframe[:, 1]
gsr_no_nan = gsr[~np.isnan(gsr)]
filter = firwin(501, [0.05,1], pass_zero=False,fs=500)
#filtered_gsr = sosfiltfilt(sos, gsr)
filtered_gsr = lfilter(filter,1,gsr_no_nan)
plt.plot([i for i in range(400,len(filtered_gsr))],filtered_gsr[400:])
plt.show()