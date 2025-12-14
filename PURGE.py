import pandas as pd

path = "Data_project/CJ07/biosignals/control.txt"

data = pd.read_csv(path, header=None)
data_cleaned = data.drop(2,axis=1)
data_purged = data_cleaned.drop([i for i in range(len(data_cleaned)) if i%4!=0 or i >= 240000])
data_purged.head()
print(len(data_purged))
data_purged.to_csv("control",header=False,index=False)