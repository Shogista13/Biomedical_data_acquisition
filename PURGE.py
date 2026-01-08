import pandas as pd
import os
from scipy.signal import decimate
import numpy as np
path = "Data_project/MD09/biosignals/"

files = os.listdir(path)
for file in files:
    data = pd.read_csv(path+file, header=None,sep='\t')
    data_cleaned = data.drop(2, axis=1)
    data_purged = data_cleaned.drop([i for i in range(len(data_cleaned)) if i%2!=0])
    data_purged.to_csv(path+file,header=False,index=False)
