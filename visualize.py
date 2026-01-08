from copy import deepcopy
import matplotlib.pyplot as plt
import pandas as pd
from scipy.signal import firwin,filtfilt,decimate,spectrogram,correlate,correlation_lags
from scipy.stats import spearmanr,combine_pvalues
import scipy.special
import numpy as np
from biosppy.signals.ppg import ppg
import os
import math
import statistics
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from colorama import Fore, Back, Style

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

def patient_ID(path):
    return path[1].split('/')[-3]


class Database:
    def __init__(self):
        path = "Data_project/"
        dirs = os.listdir(path)
        self.biosignal_files = [["Data_project/" + dir + "/biosignals/" + file for file in os.listdir("Data_project/" + dir + "/biosignals")] for dir in dirs]
        self.game_files = [["Data_project/" + dir + "/unprocessed/" + file for file in os.listdir("Data_project/" + dir + "/unprocessed")] for dir in dirs]
        self.patients = [Database.Patient(self.biosignal_files[i],self.game_files[i],patient_ID(self.biosignal_files[i])) for i in range(len(self.biosignal_files))]
        self.data = self.load_data()
        self.bullet_nr_HR, self.bullet_close_HR, self.HP_HR = self.correlate()
        self.metaanalyses_of_correlations()
        self.data_for_tests = self.feature_extraction()
        self.verify_normality()
        self.test()

    class Patient:
        def __init__(self,biosignal_files,game_files,patient_name):
            self.patient_name = patient_name
            self.biosignals = Database.Patient.BiosignalPipeline(biosignal_files)
            self.game_data = Database.Patient.GameParametersPipeline(game_files,patient_name)
            #self.CreateInteractiveGraphs()

        def CreateInteractiveGraphs(self): #better than 700 graphs showing 6 seconds each like previously
            fig = make_subplots(rows=6, cols=6)
            for column in range(6):

                pulse = self.biosignals.pulse_pipeline.filtered_pulses[column]
                pulse_time_axis = [i / 250 for i in range(0, len(pulse))]
                fig.add_trace(go.Scatter(x=pulse_time_axis,y=pulse, name="Filtered pulse"), row=1, col=column+1)

                HR = self.biosignals.HR_pipeline.HRs[column]
                HR_time_axis = self.biosignals.HR_pipeline.HR_time_axes[column]
                fig.add_trace(go.Scatter(x=HR_time_axis,y=HR, name="Heart rate"), row=2, col=column+1)

                eda = self.biosignals.eda_pipeline.filtered_edas[column]
                eda_time_axis = [i / 10 for i in range(0, len(eda))]
                fig.add_trace(go.Scatter(x=eda_time_axis,y=eda, name="EDA"), row=3, col=column+1)

                game_time_axes = self.game_data.time[column]
                HP = self.game_data.HP[column]
                fig.add_trace(go.Scatter(x=game_time_axes,y=HP, name="HP"), row=4, col=column+1)

                nr_of_bullets = self.game_data.bullet_nr[column]
                fig.add_trace(go.Scatter(x=game_time_axes,y=nr_of_bullets, name="Number of bullets"), row=5, col=column+1)

                distance_from_bullets = self.game_data.bullet_close[column]
                fig.add_trace(go.Scatter(x=game_time_axes, y=distance_from_bullets, name="Distance from bullets"), row=6, col=column+1)

                fig.write_html("Graphs/"+self.patient_name+".html")

        class BiosignalPipeline:
            def __init__(self,biosignal_files):
                self.biosignal_files = biosignal_files
                self.pulses, self.edas = self.get_biosignals()
                self.pulse_pipeline = Database.Patient.BiosignalPipeline.PulsePipeline(self.pulses)
                self.HR_pipeline = Database.Patient.BiosignalPipeline.HRPipeline(self.pulses)
                self.eda_pipeline = Database.Patient.BiosignalPipeline.EDAPipeline(self.edas)

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
                    self.HRs,self.HR_time_axes = self.process_heart_rate()

                def process_heart_rate(self):
                    HRs = []
                    HR_time_axes = []
                    h = firwin(51, [4, 8], pass_zero=True, fs=250)
                    for pulse in self.pulses:
                        results = ppg(filtfilt(h,1.0,pulse), sampling_rate=250, show=False)
                        heart_rate_time_axis = results[5]
                        heart_rate_values = results[6]
                        HRs.append(heart_rate_values)
                        HR_time_axes.append(heart_rate_time_axis)
                    return HRs,HR_time_axes

            class EDAPipeline:
                def __init__(self,edas):
                    self.edas = edas
                    self.filtered_edas = []
                    self.decomposed_edas = self.preprocess_eda()
                    self.eda_power_spectral_density = self.get_eda_power_spectral_density()
                    self.eda_power_spectral_density_normalized = pd.DataFrame(self.normalize_eda_psd())

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
                        self.filtered_edas.append(eda_no_noise)
                        for filter in filters.keys():
                            decomposed_edas[filter].append(filtfilt(filters[filter], 1.0, eda_no_noise))
                    return decomposed_edas

                def get_eda_power_spectral_density(self): #bands chosen based on the article in the document
                    eda_psd = {
                                        "VLF": [],
                                       "LF": [],
                                       "HF1": [],
                                       "HF2": [],
                                       'VHF': []
                                       }
                    for freq_bin in self.decomposed_edas.keys():
                        for phase in self.decomposed_edas[freq_bin]:
                            sample_squared = np.square(phase)
                            sample_energy = np.sum(sample_squared)
                            eda_psd[freq_bin].append(sample_energy)
                            #phase_psd = []
                            #for window in range(15):
                            #    sample = np.array(phase[window*len(phase)//16:(window+2)*len(phase)//16])
                            #    sample_squared = np.square(sample)
                            #    sample_energy = np.sum(sample_squared)
                            #    phase_psd.append(sample_energy)
                            #eda_psd[freq_bin].append(phase_psd)
                    return eda_psd

                def normalize_eda_psd(self):
                    eda_power_spectral_density_normalized = dict(self.eda_power_spectral_density) #creates a deepcopy
                    #for window in range(15):
                    for phase in range(len(self.eda_power_spectral_density["VLF"])):
                        sum = 0
                        for freq_bin in self.eda_power_spectral_density.keys():
                            sum += self.eda_power_spectral_density[freq_bin][phase]#[window]
                        for freq_bin in self.eda_power_spectral_density.keys():
                            eda_power_spectral_density_normalized[freq_bin][phase]/= sum#[window]
                    return eda_power_spectral_density_normalized

        class GameParametersPipeline:
            def __init__(self,game_files,patient_name):
                self.patient_name = patient_name
                self.game_files = game_files
                self.game_data = self.get_game_data()
                self.player_pos = self.game_data[0]
                self.enemy_bullet_pos = self.game_data[2]
                self.time = self.game_data[3]
                self.HP = self.game_data[4]
                self.bullet_nr,self.bullet_close = self.get_distances_from_bullets()

            def get_game_data(self):
                player_x = []
                player_y = []
                enemy_x = []
                enemy_y = []
                enemy_bullet_x = []
                enemy_bullet_y = []
                time_axes = []
                HP = []
                for file in self.game_files:
                    dataframe = pd.read_csv(file)
                    player_x.append(dataframe["Player x"].tolist())
                    player_y.append(dataframe["Player y"].tolist())
                    enemy_x.append([read_list(i) for i in dataframe["Enemy x"].tolist()])
                    enemy_y.append([read_list(i) for i in dataframe["Enemy y"].tolist()])
                    enemy_bullet_x.append([read_list(i) for i in dataframe["Enemy bullet x"].tolist()])
                    enemy_bullet_y.append([read_list(i) for i in dataframe["Enemy bullet y"].tolist()])
                    time_axes.append(dataframe["Time"].tolist())
                    HP.append(dataframe["HP"].tolist())
                player_position = [list(zip(player_x[i],y)) for i,y in enumerate(player_y)]
                enemy_position = [[list(zip(enemy,enemy_y[i][j])) for j,enemy in enumerate(frame)] for i,frame in enumerate(enemy_x) ]
                enemy_bullet_position = [[list(zip(enemy_bullet,enemy_bullet_y[i][j])) for j,enemy_bullet in enumerate(frame)] for i,frame in enumerate(enemy_bullet_x)]
                return player_position,enemy_position,enemy_bullet_position,time_axes,HP

            def get_distances_from_bullets(self):
                feature_0_list = [[] for _ in range(6)]
                feature_1_list = [[] for _ in range(6)]
                for i,phase in enumerate(self.player_pos):
                    for j,player_pos_in_frame in enumerate(phase):
                        distances = []
                        for enemy_bullet in self.enemy_bullet_pos[i][j]:
                            distances.append(calculate_distance(player_pos_in_frame,enemy_bullet))
                        feature_0 = len(distances)
                        feature_1 = 1/statistics.harmonic_mean(distances) if len(distances) else 0 #len equals 0 makes the expression false
                        feature_0_list[i].append(feature_0)
                        feature_1_list[i].append(feature_1)
                return feature_0_list,feature_1_list

    def load_data(self):
        data = {
        "Patient ID": [patient.patient_name for patient in self.patients],
        "HR time axes": [patient.biosignals.HR_pipeline.HR_time_axes for patient in self.patients],
        "HR": [patient.biosignals.HR_pipeline.HRs for patient in self.patients],
        "EDA_PSD": [patient.biosignals.eda_pipeline.eda_power_spectral_density_normalized for patient in self.patients],
        "game time": [patient.game_data.time for patient in self.patients],
        "bullet_nr": [patient.game_data.bullet_nr for patient in self.patients],
        "bullet_close": [patient.game_data.bullet_close for patient in self.patients],
        "HP": [patient.game_data.HP for patient in self.patients]
        }
        return data

    def correlate(self):
        bullet_nr_HR = Database.Correlation2TypesOfSignals(self.data["bullet_nr"], self.data["HR"],
                                                           self.data["game time"], self.data["HR time axes"], 0,
                                                           'greater')
        bullet_close_HR = Database.Correlation2TypesOfSignals(self.data["bullet_close"], self.data["HR"],
                                                              self.data["game time"], self.data["HR time axes"], 0,
                                                              'greater')
        HP_HR = Database.Correlation2TypesOfSignals(self.data["HP"], self.data["HR"], self.data["game time"],
                                                    self.data["HR time axes"], 0, "less")
        return bullet_nr_HR,bullet_close_HR,HP_HR

    def metaanalyses_of_correlations(self):
        average_r_bullet_nr_HR = np.tanh(np.mean(np.arctanh(self.bullet_nr_HR.stats)))
        average_r_bullet_close_HR = np.tanh(np.mean(np.arctanh(self.bullet_close_HR.stats)))
        average_r_HP_HR = np.tanh(np.mean(np.arctanh(self.HP_HR.stats)))

        print("Correlation result (bullet nr and HR): "+ str(average_r_bullet_nr_HR))
        print("Correlation result (inverse of bullet distance and HR): "+ str(average_r_bullet_close_HR))
        print("Correlation result (HP and HR): "+ str(average_r_HP_HR),end = '\n\n')

    def feature_extraction(self):
        features_dict_standard = {"HR_mean":[],
                                "HR_std":[],
                                "HR_skewness":[],
                                "HR_kurtosis":[],
                                "EDA_VLF":[],
                                "EDA_LF":[],
                                "EDA_HF1": [],
                                "EDA_HF2": [],
                                "EDA_VHF":[]
                                }

        phases = {'busy music':deepcopy(features_dict_standard),
                  'control':deepcopy(features_dict_standard),
                  'soft music':deepcopy(features_dict_standard),
                  'subdued colors':deepcopy(features_dict_standard)
        }

        for i,phase in [(0,"busy music"),(1,"control"),(4,"soft music"),(5,"subdued colors")]:
            for patient in range(len(self.data["Patient ID"])):
                phases[phase]['HR_mean'].append(np.mean(self.data["HR"][patient][i]))
                phases[phase]['HR_std'].append(np.std(self.data["HR"][patient][i]))
                phases[phase]['HR_skewness'].append(scipy.stats.skew(self.data["HR"][patient][i]))
                phases[phase]['HR_kurtosis'].append(scipy.stats.kurtosis(self.data["HR"][patient][i]))
                phases[phase]["EDA_VLF"].append(self.data["EDA_PSD"][patient]["VLF"][i])
                phases[phase]["EDA_LF"].append(self.data["EDA_PSD"][patient]["LF"][i])
                phases[phase]["EDA_HF1"].append(self.data["EDA_PSD"][patient]["HF1"][i])
                phases[phase]["EDA_HF2"].append(self.data["EDA_PSD"][patient]["HF2"][i])
                phases[phase]["EDA_VHF"].append(self.data["EDA_PSD"][patient]["VHF"][i])
        return phases

    def verify_normality(self):
        if True: #disabled for now
            for phase,phase_values in self.data_for_tests.items():
                for stat,stat_values in phase_values.items():
                    result = scipy.stats.shapiro(stat_values).pvalue
                    print(phase+' -> '+ stat + ' -> ' + str(result),end=' -> ')
                    if result > 0.05:
                        print("NORMAL")
                    else:
                        print("NOPE")

    def test(self):
        print('Busy music')
        print("HR mean: " + str(scipy.stats.ttest_rel(self.data_for_tests['control']['HR_mean'],self.data_for_tests['busy music']['HR_mean']).pvalue))
        print("HR std: " + str(scipy.stats.wilcoxon(self.data_for_tests['control']['HR_std'],self.data_for_tests['busy music']['HR_std']).pvalue))
        print("HR skewness: " + str(scipy.stats.ttest_rel(self.data_for_tests['control']['HR_skewness'],self.data_for_tests['busy music']['HR_skewness']).pvalue))
        print("HR kurtosis: " + str(scipy.stats.ttest_rel(self.data_for_tests['control']['HR_kurtosis'],self.data_for_tests['busy music']['HR_kurtosis']).pvalue))
        print("EDA VLF: " + str(scipy.stats.ttest_rel(self.data_for_tests['control']['EDA_VLF'],self.data_for_tests['busy music']['EDA_VLF']).pvalue))
        print("EDA LF: " + str(scipy.stats.ttest_rel(self.data_for_tests['control']['EDA_LF'],self.data_for_tests['busy music']['EDA_LF']).pvalue))
        print("EDA HF1: " + str(scipy.stats.wilcoxon(self.data_for_tests['control']['EDA_HF1'],self.data_for_tests['busy music']['EDA_HF1']).pvalue))
        print("EDA HF2: " + str(scipy.stats.wilcoxon(self.data_for_tests['control']['EDA_HF2'],self.data_for_tests['busy music']['EDA_HF2']).pvalue))
        print("EDA VHF: " + str(scipy.stats.wilcoxon(self.data_for_tests['control']['EDA_VHF'],self.data_for_tests['busy music']['EDA_VHF']).pvalue))

        print('Soft music')
        print("HR mean: " + str(scipy.stats.ttest_rel(self.data_for_tests['control']['HR_mean'],self.data_for_tests['soft music']['HR_mean']).pvalue))
        print("HR std: " + str(scipy.stats.wilcoxon(self.data_for_tests['control']['HR_std'],self.data_for_tests['soft music']['HR_std']).pvalue))
        print("HR skewness: " + str(scipy.stats.ttest_rel(self.data_for_tests['control']['HR_skewness'],self.data_for_tests['soft music']['HR_skewness']).pvalue))
        print("HR kurtosis: " + str(scipy.stats.ttest_rel(self.data_for_tests['control']['HR_kurtosis'],self.data_for_tests['soft music']['HR_kurtosis']).pvalue))
        print("EDA VLF: " + str(scipy.stats.ttest_rel(self.data_for_tests['control']['EDA_VLF'],self.data_for_tests['soft music']['EDA_VLF']).pvalue))
        print("EDA LF: " + str(scipy.stats.ttest_rel(self.data_for_tests['control']['EDA_LF'],self.data_for_tests['soft music']['EDA_LF']).pvalue))
        print("EDA HF1: " + str(scipy.stats.wilcoxon(self.data_for_tests['control']['EDA_HF1'],self.data_for_tests['soft music']['EDA_HF1']).pvalue))
        print("EDA HF2: " + str(scipy.stats.wilcoxon(self.data_for_tests['control']['EDA_HF2'],self.data_for_tests['soft music']['EDA_HF2']).pvalue))
        print("EDA VHF: " + str(scipy.stats.wilcoxon(self.data_for_tests['control']['EDA_VHF'],self.data_for_tests['soft music']['EDA_VHF']).pvalue))

        print('Subdued colors')
        print("HR mean: " + str(scipy.stats.ttest_rel(self.data_for_tests['control']['HR_mean'],self.data_for_tests['subdued colors']['HR_mean']).pvalue))
        print("HR std: " + str(scipy.stats.wilcoxon(self.data_for_tests['control']['HR_std'],self.data_for_tests['subdued colors']['HR_std']).pvalue))
        print("HR skewness: " + str(scipy.stats.ttest_rel(self.data_for_tests['control']['HR_skewness'],self.data_for_tests['subdued colors']['HR_skewness']).pvalue))
        print("HR kurtosis: " + str(scipy.stats.wilcoxon(self.data_for_tests['control']['HR_kurtosis'],self.data_for_tests['subdued colors']['HR_kurtosis']).pvalue))
        print("EDA VLF: " + str(scipy.stats.ttest_rel(self.data_for_tests['control']['EDA_VLF'],self.data_for_tests['subdued colors']['EDA_VLF']).pvalue))
        print("EDA LF: " + str(scipy.stats.ttest_rel(self.data_for_tests['control']['EDA_LF'],self.data_for_tests['subdued colors']['EDA_LF']).pvalue))
        print("EDA HF1: " + str(scipy.stats.wilcoxon(self.data_for_tests['control']['EDA_HF1'],self.data_for_tests['subdued colors']['EDA_HF1']).pvalue))
        print("EDA HF2: " + str(scipy.stats.wilcoxon(self.data_for_tests['control']['EDA_HF2'],self.data_for_tests['subdued colors']['EDA_HF2']).pvalue))
        print("EDA VHF: " + str(scipy.stats.wilcoxon(self.data_for_tests['control']['EDA_VHF'], self.data_for_tests['subdued colors']['EDA_VHF']).pvalue))

        print("Busy music vs soft music")
        print("HR mean: " + str(scipy.stats.ttest_rel(self.data_for_tests['soft music']['HR_mean'],self.data_for_tests['busy music']['HR_mean']).pvalue))
        print("HR std: " + str(scipy.stats.ttest_rel(self.data_for_tests['soft music']['HR_std'],self.data_for_tests['busy music']['HR_std']).pvalue))
        print("HR skewness: " + str(scipy.stats.ttest_rel(self.data_for_tests['soft music']['HR_skewness'],self.data_for_tests['busy music']['HR_skewness']).pvalue))
        print("HR kurtosis: " + str(scipy.stats.ttest_rel(self.data_for_tests['soft music']['HR_kurtosis'],self.data_for_tests['busy music']['HR_kurtosis']).pvalue))
        print("EDA VLF: " + str(scipy.stats.ttest_rel(self.data_for_tests['soft music']['EDA_VLF'],self.data_for_tests['busy music']['EDA_VLF']).pvalue))
        print("EDA LF: " + str(scipy.stats.ttest_rel(self.data_for_tests['soft music']['EDA_LF'],self.data_for_tests['busy music']['EDA_LF']).pvalue))
        print("EDA HF1: " + str(scipy.stats.wilcoxon(self.data_for_tests['soft music']['EDA_HF1'],self.data_for_tests['busy music']['EDA_HF1']).pvalue))
        print("EDA HF2: " + str(scipy.stats.ttest_rel(self.data_for_tests['soft music']['EDA_HF2'],self.data_for_tests['busy music']['EDA_HF2']).pvalue))
        print("EDA VHF: " + str(scipy.stats.wilcoxon(self.data_for_tests['soft music']['EDA_VHF'],self.data_for_tests['busy music']['EDA_VHF']).pvalue))

    class Correlation2TypesOfSignals:
        def __init__(self,signals0,signals1,signal_0_time_axes,signal_1_time_axes,which_time_axis_stays,alternative):
            self.correlations = [Database.Correlation2TypesOfSignals.CorrelationPairOfSignals(signals0[i][j],signals1[i][j],signal_0_time_axes[i][j],
                                 signal_1_time_axes[i][j],which_time_axis_stays,alternative) for i,patient in enumerate(signals0) for j in range(len(patient))]
            self.stats = [patient_results.stat_n_pvalue.statistic for patient_results in self.correlations]
            self.pvals = [patient_results.stat_n_pvalue.pvalue for patient_results in self.correlations]

        class CorrelationPairOfSignals:
            def __init__(self,signal0,signal1,signal0_time_axis,signal1_time_axis,time_axis_that_stays,alternative):
                self.alternative = alternative
                self.signal0 = np.array(signal0)
                self.signal1 = np.array(signal1) #biosignal which is supposed to be lagged
                self.signal0_time_axis = signal0_time_axis
                self.signal1_time_axis = signal1_time_axis
                self.time_axis_that_stays = time_axis_that_stays

                self.signal0_interpolated,self.signal1_interpolated = self.interpolate_signals()
                self.signal0_normalized,self.signal1_normalized = self.signal_post_pre_processing()

                self.lag = self.find_lag()
                self.stat_n_pvalue = self.correlate_signals()

            def interpolate_signals(self):
                if self.time_axis_that_stays == 0:
                    signal_0_interpolated = self.signal0
                    signal_1_interpolated = np.interp(self.signal0_time_axis,self.signal1_time_axis,self.signal1)
                else:
                    signal_1_interpolated = self.signal1
                    signal_0_interpolated = np.interp(self.signal1_time_axis, self.signal0_time_axis, self.signal0)
                return signal_0_interpolated,signal_1_interpolated

            def signal_post_pre_processing(self):  #:) preparing for cross correlation to find the lag before using Spearman according to Gemini's instruction (Z-score)
                signal0_normalized = (self.signal0_interpolated-np.mean(self.signal0_interpolated))/np.std(self.signal0_interpolated)
                signal1_normalized = (self.signal1_interpolated-np.mean(self.signal1_interpolated))/np.std(self.signal1_interpolated)
                return signal0_normalized,signal1_normalized

            def find_lag(self):
                correlation_results = np.array(correlate(self.signal0_normalized,self.signal1_normalized))
                correlation_lags_result = correlation_lags(len(self.signal0_normalized),len(self.signal1_normalized))
                if self.alternative == 'less':
                    lag = correlation_lags_result[len(self.signal0_normalized) + np.argmin(correlation_results[len(self.signal0_normalized):len(self.signal0_normalized) + len(self.signal1_normalized) // 60])]
                else:
                    lag = correlation_lags_result[len(self.signal0_normalized)+np.argmax(correlation_results[len(self.signal0_normalized):len(self.signal0_normalized)+len(self.signal1_normalized)//60])]
                return lag

            def correlate_signals(self):
                return spearmanr(self.signal0_interpolated[self.lag:],self.signal1_interpolated[:-self.lag],nan_policy='raise',alternative = self.alternative)

baza = Database()




#def get_HR(signal,peaks,sampling_rate):
#    HR = []
#    for i in range(len(signal)//(sampling_rate)-5):
#        heart_beats = [beat for beat in peaks if  i*sampling_rate<= beat < (i+5)*sampling_rate]
#        HR.append((len(heart_beats)-1)/(heart_beats[-1]-heart_beats[0])*sampling_rate*60)
#    return HR
# self.save_custom_features()

'''def save_custom_features(self):
    nazwy = ["busy music", "control", "power up in installments with sound effect",
             "reward in installments", "soft music", "subdued colors"]
    for i,feature_0 in enumerate(self.bullet_nr):
        if feature_0:
            f, axes = plt.subplots(2,figsize=(20, 20))
            axes[0].plot(self.time[i], feature_0)
            axes[0].set_title("Number of bullets")
            axes[1].plot(self.time[i], self.bullet_close[i])
            axes[1].set_title("1/harmonic mean of distances to bullets")
            plt.suptitle("Patient " + str(self.patient_nr), fontsize=20)
            plt.subplots_adjust(hspace=0.5, top=0.85, bottom=0.05)
            plt.savefig("Graphs/Custom_features/Patient" + str(self.patient_nr) + "Phase" + nazwy[i].replace(" ","_"))
            plt.close()'''


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

'''colorama.init()

for i in bullet_close_HR.pvals:
    if float(i) > 0.05:
        print(Style.RESET_ALL + str(float(i)),end=', ')
    else:
        print(Fore.RED + str(float(i)),', ')

for i in bullet_nr_HR.pvals:
    if float(i) > 0.05:
        print(Style.RESET_ALL + str(float(i)),end=', ')
    else:
        print(Fore.RED + str(float(i)),', ')

for i in HP_HR.pvals:
    if float(i) > 0.05:
        print(Style.RESET_ALL + str(float(i)),end=', ')
    else:
        print(Fore.RED + str(float(i)),', ')'''