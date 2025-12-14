import matplotlib.pyplot as plt
import pandas as pd
from scipy.signal import firwin,filtfilt,decimate
from scipy import integrate
import numpy as np
from biosppy.signals.ppg import ppg
import os
import math
import statistics

def show(pulses,patient,k,sampling_rate,path):
    nazwy = ["busy music","control","power up in installments with sound effect","reward in installments","soft music","subdued colors"]
    for i in range(k):
        f, axes = plt.subplots(len(pulses),figsize=(20, 20))
        for j in range(len(pulses)):
            pulse = pulses[j][len(pulses[j]) // k * i:(len(pulses[j]) // k) * (i + 1)]
            axes[j].plot([i/sampling_rate for i in range(len(pulses[j]) // k * i,len(pulses[j])// k * (i + 1))],pulse)
            axes[j].set_title(nazwy[j])
        plt.suptitle("Patient " + str(patient),fontsize = 20)
        plt.subplots_adjust(hspace=0.5,top=0.9,bottom=0.05)
        plt.savefig("Graphs/"+path+"/P"+str(patient)+"S"+str(i))
        plt.close()

def read_list(list):
    return [int(i) for i in list.strip("[]").split(",") if i]

def calculate_distance(point0,point1):
    return math.sqrt((point1[0]-point0[0])**2+(point1[1]-point0[1])**2)

class Database:
    def __init__(self):
        path = "Data_project/"
        dirs = os.listdir(path)
        self.biosignal_files = [["Data_project/" + dir + "/biosignals/" + file for file in os.listdir("Data_project/" + dir + "/biosignals")] for dir in dirs]
        self.game_files = [["Data_project/" + dir + "/unprocessed/" + file for file in os.listdir("Data_project/" + dir + "/unprocessed")] for dir in dirs]
        self.patients = [Database.Patient(biosignal_file,game_file) for biosignal_file,game_file in list(zip(self.biosignal_files,self.game_files))]

    class Patient:
        def __init__(self,biosignal_files,game_files):
            self.biosignals = Database.Patient.BiosignalPipeline(biosignal_files)
            self.game_data = Database.Patient.GameParametersPipeline(game_files)

        class BiosignalPipeline:
            def __init__(self,biosignal_files):
                self.biosignal_files = biosignal_files
                self.pulses, self.edas = self.get_biosignals()
                #self.pulse_pipeline = Database.Patient.BiosignalPipeline.PulsePipeline(self.pulses)
                #self.HR_pipeline = Database.Patient.BiosignalPipeline.HRPipeline(self.pulses)
                #self.eda_pipeline = Database.Patient.BiosignalPipeline.EDAPipeline(self.edas)

            def get_biosignals(self):
                pulses = []
                edas = []
                for file in self.biosignal_files:
                    dataframe = pd.read_csv(file, header=None).to_numpy()
                    pulse = dataframe[:,0]
                    eda = dataframe[:,1]
                    pulses.append(pulse[~np.isnan(pulse)])
                    edas.append(eda[~np.isnan(eda)])
                return pulses,edas

            class PulsePipeline:
                def __init__(self,pulses):
                    self.pulses = pulses
                    self.filtered_pulses = self.preprocess_pulse()

                def preprocess_pulse(self):
                    h = firwin(51, [1, 8], pass_zero=False, fs=250)
                    filtered_pulses = []
                    for pulse in self.pulses:
                        filtered_pulse = filtfilt(h, 1.0, pulse)
                        filtered_pulses.append(filtered_pulse)
                    return filtered_pulses

            class HRPipeline:
                def __init__(self,pulses):
                    self.pulses = pulses
                    self.HRs = self.process_heart_rate()

                def process_heart_rate(self):
                    HRs = []
                    for pulse in self.pulses:
                        results = ppg(pulse, sampling_rate=250, show=False)
                        time_axis_s = [i / 250 for i in range(0, len(pulse), 250)]
                        heart_rate_time_axis = results[5]
                        heart_rate_values = results[6]
                        HR_interpolated = np.interp(time_axis_s, heart_rate_time_axis, heart_rate_values)
                        HRs.append(HR_interpolated)
                    return HRs

            class EDAPipeline:
                def __init__(self,edas):
                    self.edas = edas
                    self.decomposed_edas = self.preprocess_eda()
                    self.eda_power_spectral_density = self.get_eda_power_spectral_density()
                    self.eda_power_spectral_density_normalized = pd.DataFrame(self.normalize_eda_psd())
                    #self.eda_power_spectral_density_normalized.to_csv("nowe.csv")

                def preprocess_eda(self):
                    anti_noise_filter = firwin(101, [0.05, 0.5], pass_zero=False, fs=10)
                    filters = {
                        "VLF": firwin(101,0.045,fs=10),
                         "LF": firwin(101, [0.045, 0.15], pass_zero=False, fs=10),
                         "HF1": firwin(101, [0.15,0.25], pass_zero=False, fs=10),
                         "HF2": firwin(101, [0.25, 0.4], pass_zero=False, fs=10),
                         'VHF': firwin(101, 0.5, pass_zero=False, fs=10)
                    }
                    decomposed_edas = {"VLF":[],
                                       "LF":[],
                                       "HF1":[],
                                       "HF2":[],
                                       'VHF':[]
                                       }
                    for eda in self.edas:
                        eda_decimated = decimate(decimate(eda, 5), 5)
                        eda_no_noise = filtfilt(anti_noise_filter, 1.0, eda_decimated)
                        for filter in filters.keys():
                            decomposed_edas[filter].append(filtfilt(filters[filter], 1.0, eda_no_noise))
                    return decomposed_edas

                def get_eda_power_spectral_density(self):
                    eda_psd = {
                                        "VLF": [],
                                       "LF": [],
                                       "HF1": [],
                                       "HF2": [],
                                       'VHF': []
                                       }
                    for freq_bin in self.decomposed_edas.keys():
                        for phase in self.decomposed_edas[freq_bin]:
                            phase_psd = []
                            for window in range(15):
                                sample = np.array(phase[window*len(phase)//16:(window+2)*len(phase)//16])
                                sample_squared = np.square(sample)
                                sample_energy = np.sum(sample_squared)
                                phase_psd.append(sample_energy)
                            eda_psd[freq_bin].append(phase_psd)
                    return eda_psd

                def normalize_eda_psd(self):
                    eda_power_spectral_density_normalized = dict(self.eda_power_spectral_density) #creates a deepcopy
                    for window in range(15):
                        for phase in range(len(self.eda_power_spectral_density["VLF"])):
                            sum = 0
                            for freq_bin in self.eda_power_spectral_density.keys():
                                sum += self.eda_power_spectral_density[freq_bin][phase][window]
                            for freq_bin in self.eda_power_spectral_density.keys():
                                eda_power_spectral_density_normalized[freq_bin][phase][window] /= sum
                    return eda_power_spectral_density_normalized

        class GameParametersPipeline:
            def __init__(self,game_files):
                self.game_files = game_files
                self.game_data = self.get_game_data()
                self.player_pos = self.game_data[0]
                self.enemy_bullet_pos = self.game_data[2]
                self.get_distances_from_bullets()

            def get_game_data(self):
                player_x = []
                player_y = []
                enemy_x = []
                enemy_y = []
                enemy_bullet_x = []
                enemy_bullet_y = []
                for file in self.game_files:
                    dataframe = pd.read_csv(file)
                    player_x.append(dataframe["Player x"].tolist())
                    player_y.append(dataframe["Player y"].tolist())
                    enemy_x.append([read_list(i) for i in dataframe["Enemy x"].tolist()])
                    enemy_y.append([read_list(i) for i in dataframe["Enemy y"].tolist()])
                    enemy_bullet_x.append([read_list(i) for i in dataframe["Enemy bullet x"].tolist()])
                    enemy_bullet_y.append([read_list(i) for i in dataframe["Enemy bullet y"].tolist()])
                player_position = [list(zip(player_x[i],y)) for i,y in enumerate(player_y)]
                enemy_position = [list(zip(enemy,enemy_y[i][j])) for i,frame in enumerate(enemy_x) for j,enemy in enumerate(frame)]
                enemy_bullet_position = [list(zip(enemy_bullet,enemy_bullet_y[i][j])) for i,frame in enumerate(enemy_bullet_x) for j,enemy_bullet in enumerate(frame)]
                return player_position,enemy_position,enemy_bullet_position

            def get_distances_from_bullets(self):
                print(np.array(self.player_pos).shape)
                print(np.array(self.enemy_bullet_pos).shape)
                for i,phase in enumerate(self.player_pos):
                    for j,player_pos_in_frame in enumerate(phase):
                        distances = []
                        for enemy_bullet in self.enemy_bullet_pos[i][j]:
                            distances.append(calculate_distance(player_pos_in_frame,enemy_bullet))
                            print(distances)

baza = Database()




#def get_HR(signal,peaks,sampling_rate):
#    HR = []
#    for i in range(len(signal)//(sampling_rate)-5):
#        heart_beats = [beat for beat in peaks if  i*sampling_rate<= beat < (i+5)*sampling_rate]
#        HR.append((len(heart_beats)-1)/(heart_beats[-1]-heart_beats[0])*sampling_rate*60)
#    return HR

'''def processing_pipeline(load_paths,pulse = False,eda=False,heart_rate = False,just_graph=False):
    for nr, path in enumerate(load_paths):
        if pulse: pulse_array = []
        if eda: eda_array = []
        if heart_rate: heart_rate_array = []
        for file in path:
            if just_graph:
            if pulse:
                filtered_pulse = process_pulse(dataframe)
                pulse_array.append(filtered_pulse)
            if eda:
                filtered_eda = process_eda(dataframe)
                eda_array.append(filtered_eda)
            if heart_rate:
                filtered_heart_rate = process_heart_rate(dataframe)
                heart_rate_array.append(filtered_heart_rate)
        if just_graph:
            if pulse: show(pulse_array,nr,40,250,"Pulse")
            if eda: show(eda_array, nr, 8, 5, "EDA")
            if heart_rate: show(heart_rate_array,nr,8,1,"Heart rate")'''
