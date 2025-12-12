from scipy.signal import butter,sosfiltfilt,firwin,lfilter,filtfilt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

dataframe = pd.read_csv("Data_project/ML08/biosignals/unprocessed/power_up_in_installments_with_sound_effect.txt", header=None,sep = '\t').to_numpy()
sos = butter(4, (0.05, 1), 'bp', output="sos", fs=1000)
gsr = dataframe[:, 1]
gsr_no_nan = gsr[~np.isnan(gsr)]
#filter = firwin(501, [0.05,1], pass_zero=False,fs=500)
filtered_gsr = sosfiltfilt(sos, gsr)
#filtered_gsr = lfilter(filter,1,gsr_no_nan)
f,axes = plt.subplots(2)
axes[0].plot([i/1000 for i in range(len(gsr_no_nan))],gsr_no_nan)
axes[1].plot([i/1000 for i in range(len(filtered_gsr))],filtered_gsr)
#plt.savefig("Data_project/ML08/biosignals/gsr/power_up_in_installments_with_sound_effect.jpg")
plt.show()