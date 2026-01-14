import pandas as pd
import os
from scipy.signal import decimate
import numpy as np
path = "Data_project/ML08/biosignals/reward_in_installments.txt"

#files = os.listdir(path)
#for file in files:
data = pd.read_csv(path, header=None,sep='\t')
data_cleaned = data.drop(2, axis=1)
data_purged = data_cleaned.drop([i for i in range(len(data_cleaned)) if i%4!=0])
data_purged.to_csv(path,header=False,index=False)
