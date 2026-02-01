from copy import deepcopy
import matplotlib.pyplot as plt
import pandas as pd
from scipy.signal import firwin,filtfilt,decimate,spectrogram,correlate,correlation_lags
from scipy.stats import spearmanr,combine_pvalues
import scipy.special
import numpy as np
from biosppy.signals.ppg import ppg
import seaborn
import os
import math
import statistics
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def read_list(list):# reads a list from pandas dataframe where it is stored as text for example [1,2,3]
    return [int(i) for i in list.strip("[]").split(",") if i]

def calculate_distance(point0,point1):# Pythagorean theorem
    return math.sqrt((point1[0]-point0[0])**2+(point1[1]-point0[1])**2)

def patient_ID(path):# reads the patient name from the file path
    return path[1].split('/')[-3]

def comparison_test(stat0,stat1,stat_name,test_name):
    # shapiro-wilk -> paired t-test/wilcoxon -> cohen's d/rank biserial correlation
    plt.figure()
    seaborn.boxplot(data = [stat0,stat1])
    plt.title(test_name + " " + stat_name)
    os.makedirs("DistributionPlots/KDE_for_comparison/"+ test_name.replace(" ","_"),exist_ok=True)
    plt.savefig(("DistributionPlots/KDE_for_comparison/"+ test_name + "/" + stat_name).replace(" ","_"))
    plt.close()
    stat0 = np.array(stat0)
    stat1 = np.array(stat1)
    normality = scipy.stats.shapiro(stat0-stat1).pvalue
    if normality > 0.05:
        test_result = scipy.stats.ttest_rel(stat0,stat1)# paired t-test
        s = math.sqrt((np.std(stat0)**2+np.std(stat1)**2)/2) # average std
        cohens_d = np.mean(stat0-stat1)/s
        return (normality,test_result.pvalue,cohens_d)
    else:
        test_result = scipy.stats.wilcoxon(stat0-stat1,alternative = 'two-sided')
        # the p-values changed from the presentation, because we did a one-sided test by mistake previously
        n = np.count_nonzero(stat0 - stat1)
        number_of_ranks = n*(n+1)/2 # the test only returns the higher from the 2 sums of ranks
        # and does not return Z statistic for that number of samples, so we had to calculate the numebr of ranks manually
        rank_biserial = (2*test_result.statistic)/number_of_ranks - 1
        return (normality,test_result.pvalue,rank_biserial)

class Database:
    # the whole data processing pipeline
    def __init__(self):
        path = "Data_project/"
        dirs = os.listdir(path)
        self.biosignal_files = [["Data_project/" + dir + "/biosignals/" + file for file in os.listdir("Data_project/" + dir + "/biosignals")] for dir in dirs]
        self.game_files = [["Data_project/" + dir + "/unprocessed/" + file for file in os.listdir("Data_project/" + dir + "/unprocessed")] for dir in dirs]
        self.patients = [Database.Patient(self.biosignal_files[i],self.game_files[i],patient_ID(self.biosignal_files[i])) for i in range(len(self.biosignal_files))]
        self.normality = pd.DataFrame(columns = ['HR_mean','HR_std','HR_skewness','HR_kurtosis','EDA_VLF','EDA_LF','EDA_HF1','EDA_HF2','EDA_VHF'],index = ['Control vs busy music','Control vs soft music','Control vs subdued colors','Busy music vs soft music'])
        self.pvalues = pd.DataFrame(columns = ['HR_mean','HR_std','HR_skewness','HR_kurtosis','EDA_VLF','EDA_LF','EDA_HF1','EDA_HF2','EDA_VHF'],index = ['Control vs busy music','Control vs soft music','Control vs subdued colors','Busy music vs soft music'])
        self.effect_sizes = pd.DataFrame(columns = ['HR_mean','HR_std','HR_skewness','HR_kurtosis','EDA_VLF','EDA_LF','EDA_HF1','EDA_HF2','EDA_VHF'],index = ['Control vs busy music','Control vs soft music','Control vs subdued colors','Busy music vs soft music'])
        self.data = self.load_data()
        self.bullet_nr_HR, self.bullet_close_HR, self.HP_HR = self.correlate()
        self.metaanalyses_of_correlations()
        self.data_for_tests = self.feature_extraction()
        self.test()

    class Patient:
        def __init__(self,biosignal_files,game_files,patient_name):
            self.patient_name = patient_name
            self.biosignals = Database.Patient.BiosignalPipeline(biosignal_files)
            self.game_data = Database.Patient.GameParametersPipeline(game_files,patient_name)
            self.CreateInteractiveGraphs()

        def CreateInteractiveGraphs(self): # creates the html files in PlotsOfSignals
            fig = make_subplots(rows=6, cols=1)
            os.makedirs("PlotsOfSignals/"+self.patient_name,exist_ok = True)
            nazwy = ["busy music", "control", "power up in installments with sound effect", "reward in installments",
                     "soft music", "subdued colors"]
            for column in range(6):
                pulse = self.biosignals.pulse_pipeline.filtered_pulses[column] # pulse
                pulse_time_axis = [i / 250 for i in range(0, len(pulse))]
                fig.add_trace(go.Scatter(x=pulse_time_axis,y=pulse, name="Filtered pulse"), row=1, col=1)

                HR = self.biosignals.HR_pipeline.HRs[column] # heart rate
                HR_time_axis = self.biosignals.HR_pipeline.HR_time_axes[column]
                fig.add_trace(go.Scatter(x=HR_time_axis,y=HR, name="Heart rate"), row=2, col=1)

                eda = self.biosignals.eda_pipeline.filtered_edas[column] # EDA
                eda_time_axis = [i / 10 for i in range(0, len(eda))]
                fig.add_trace(go.Scatter(x=eda_time_axis,y=eda, name="EDA"), row=3, col=1)

                game_time_axes = self.game_data.time[column] # the real-world time during the game
                # those sharp cliffs in the plots of the game data mean deaths (there aren't any measurements during this time)
                HP = self.game_data.HP[column] # HP
                fig.add_trace(go.Scatter(x=game_time_axes,y=HP, name="HP"), row=4, col=1)

                nr_of_bullets = self.game_data.bullet_nr[column] # bullet number
                fig.add_trace(go.Scatter(x=game_time_axes,y=nr_of_bullets, name="Number of bullets"), row=5, col=1)

                distance_from_bullets = self.game_data.bullet_close[column] # the inverse of the harmonic mean of the distances to bullets
                fig.add_trace(go.Scatter(x=game_time_axes, y=distance_from_bullets, name="Distance from bullets"), row=6, col=1)

                fig.write_html("PlotsOfSignals/"+self.patient_name+"/"+nazwy[column]+".html")
                fig.data = []

        class BiosignalPipeline:
            def __init__(self,biosignal_files):
                self.biosignal_files = biosignal_files
                self.pulses, self.edas = self.get_biosignals()
                self.pulse_pipeline = Database.Patient.BiosignalPipeline.PulsePipeline(self.pulses)
                self.HR_pipeline = Database.Patient.BiosignalPipeline.HRPipeline(self.pulses)
                self.eda_pipeline = Database.Patient.BiosignalPipeline.EDAPipeline(self.edas)

            def get_biosignals(self):# reads the csv with the biosignals
                pulses = []
                edas = []
                for file in self.biosignal_files:
                    dataframe = pd.read_csv(file, header=None).to_numpy()
                    pulse = dataframe[:,0]
                    eda = dataframe[:,1]
                    pulses.append(pulse[~np.isnan(pulse)])
                    edas.append(eda[~np.isnan(eda)])
                return pulses,edas

            class PulsePipeline:# filters the pulse
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

            class HRPipeline:# calculates the heart rate
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

                def preprocess_eda(self):# filters EDA and decomposes it into
                    # frequency bands
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

                def get_eda_power_spectral_density(self): # bands chosen based on the article in the document
                    # we calculated the energy of the whole signal at once without dividing into segments
                    # because the signal is in really low frequencies, also each recording has the same lenght,
                    # so they are normalized. The energy is calculated from the time-domain representation
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
                    return eda_psd

                def normalize_eda_psd(self):# we divided the power of the signal in a frequency band
                    # by the sum of powers of the signal in all frequency bands
                    eda_power_spectral_density_normalized = dict(self.eda_power_spectral_density) # creates a deepcopy
                    for phase in range(len(self.eda_power_spectral_density["VLF"])):
                        sum = 0
                        for freq_bin in self.eda_power_spectral_density.keys():
                            sum += self.eda_power_spectral_density[freq_bin][phase]# [window]
                        for freq_bin in self.eda_power_spectral_density.keys():
                            eda_power_spectral_density_normalized[freq_bin][phase]/= sum# [window]
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
                # reads the csv with the data extracted from the game
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
                # calculates the distances from the player to the bullets
                feature_0_list = [[] for _ in range(6)]
                feature_1_list = [[] for _ in range(6)]
                for i,phase in enumerate(self.player_pos):
                    for j,player_pos_in_frame in enumerate(phase):
                        distances = []
                        for enemy_bullet in self.enemy_bullet_pos[i][j]:
                            distances.append(calculate_distance(player_pos_in_frame,enemy_bullet))
                        feature_0 = len(distances)
                        feature_1 = 1/statistics.harmonic_mean(distances) if len(distances) else 0 # len equals 0 makes the expression false
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

    def correlate(self):# uses an object that will be defined later in the code, where it is going to be explained
        bullet_nr_HR = Database.Correlation2TypesOfSignals(self.data["bullet_nr"], self.data["HR"],
                                                           self.data["game time"], self.data["HR time axes"], 0,
                                                           'greater',"bullet number","HR")
        bullet_close_HR = Database.Correlation2TypesOfSignals(self.data["bullet_close"], self.data["HR"],
                                                              self.data["game time"], self.data["HR time axes"], 0,
                                                              'greater',"bullets close","HR")
        HP_HR = Database.Correlation2TypesOfSignals(self.data["HP"], self.data["HR"], self.data["game time"],
                                                    self.data["HR time axes"], 0, "less","HP","HR")
        return bullet_nr_HR,bullet_close_HR,HP_HR

    def metaanalyses_of_correlations(self):
        # Fisher's method: we cannot just take the mean of the r values from all teh Spearmans,
        # because their distribution is skewed,
        # we need to take their arctanh, then calculate the mean and take the tanh
        average_r_bullet_nr_HR = np.tanh(np.mean(np.arctanh(self.bullet_nr_HR.stats)))
        average_r_bullet_close_HR = np.tanh(np.mean(np.arctanh(self.bullet_close_HR.stats)))
        average_r_HP_HR = np.tanh(np.mean(np.arctanh(self.HP_HR.stats)))

        print("Correlation result (bullet nr and HR): "+ str(average_r_bullet_nr_HR))
        print("Correlation result (inverse of bullet distance and HR): "+ str(average_r_bullet_close_HR))
        print("Correlation result (HP and HR): "+ str(average_r_HP_HR),end = '\n\n')

    def feature_extraction(self):# calculates the statistical features of the heart rate signal
        # calculated from the PPG signal, and just rewrites the calculated normalized PSD of the EDA signal
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

    def compare_two_groups(self,group0_name,group1_name):
        #  shapiro-wilk -> paired t-test/wilcoxon -> cohen's d/rank biserial correlation
        features = ['HR_mean','HR_std','HR_skewness','HR_kurtosis','EDA_VLF','EDA_LF','EDA_HF1','EDA_HF2','EDA_VHF']
        results = []
        for feature in features:
            results.append(comparison_test(self.data_for_tests[group0_name][feature], self.data_for_tests[group1_name][feature],feature, group0_name +' vs ' + group1_name))
        results = np.array(results)
        return results.T # transposed for it to be written to a csv more easily

    def test(self):
        keys = ['Control vs busy music','Control vs soft music','Control vs subdued colors','Busy music vs soft music']
        results = [self.compare_two_groups('control','busy music'),
        self.compare_two_groups('control','soft music'),
        self.compare_two_groups('control','subdued colors'),
        self.compare_two_groups('busy music','soft music')] # makes all the tests

        for i,result in enumerate(results):# prepares for writing to csv
            self.normality.loc[keys[i]] = result[0]
            self.pvalues.loc[keys[i]] = result[1]
            self.effect_sizes.loc[keys[i]] = result[2]
        self.normality.to_csv('normality.csv')
        self.pvalues.to_csv('pvalues.csv')
        self.effect_sizes.to_csv('effect_sizes.csv')

    class Correlation2TypesOfSignals:# previously used object that wil be shown now
        def __init__(self,signals0,signals1,signal_0_time_axes,signal_1_time_axes,which_time_axis_stays,alternative,name0,name1):
            self.correlations = [Database.Correlation2TypesOfSignals.CorrelationPairOfSignals(signals0[i][j],signals1[i][j],signal_0_time_axes[i][j],
                                 signal_1_time_axes[i][j],which_time_axis_stays,alternative) for i,patient in enumerate(signals0) for j in range(len(patient))]
            self.stats = [patient_results.stat_n_pvalue.statistic for patient_results in self.correlations]
            self.pvals = [patient_results.stat_n_pvalue.pvalue for patient_results in self.correlations]
            self.signals0 = [i for patient_results in self.correlations for i in patient_results.signal0_interpolated[patient_results.lag:]]
            self.signals1 = [i for patient_results in self.correlations for i in patient_results.signal1_interpolated[:-patient_results.lag]]

            # Scatter plots
            plt.figure(figsize=(11,11),dpi=300)
            plt.scatter(self.signals0,self.signals1,s=0.25)
            plt.title(name0 +" vs " + name1)
            plt.savefig(("DistributionPlots/scatter_for_correlation/" + (name0 +" vs " + name1)).replace(" ", "_"))
            plt.close()

        class CorrelationPairOfSignals:
            def __init__(self,signal0,signal1,signal0_time_axis,signal1_time_axis,time_axis_that_stays,alternative):
                self.alternative = alternative# 
                self.signal0 = np.array(signal0)
                self.signal1 = np.array(signal1) # biosignal which is supposed to be lagged
                self.signal0_time_axis = signal0_time_axis
                self.signal1_time_axis = signal1_time_axis

                # the "opposite" signal is interpolated according to the time axis "that stays"
                self.time_axis_that_stays = time_axis_that_stays
                self.signal0_interpolated,self.signal1_interpolated = self.interpolate_signals()
                # subtract the mean, divide by std
                self.signal0_normalized,self.signal1_normalized = self.signal_post_pre_processing()

                self.lag = self.find_lag()
                self.stat_n_pvalue = self.correlate_signals()

            def interpolate_signals(self):# the "opposite" signal is interpolated according to the time axis "that stays"
                if self.time_axis_that_stays == 0:
                    signal_0_interpolated = self.signal0
                    signal_1_interpolated = np.interp(self.signal0_time_axis,self.signal1_time_axis,self.signal1)
                else:
                    signal_1_interpolated = self.signal1
                    signal_0_interpolated = np.interp(self.signal1_time_axis, self.signal0_time_axis, self.signal0)
                return signal_0_interpolated,signal_1_interpolated

            def signal_post_pre_processing(self):
                # subtract the mean, divide by std
                signal0_normalized = (self.signal0_interpolated-np.mean(self.signal0_interpolated))/np.std(self.signal0_interpolated)
                signal1_normalized = (self.signal1_interpolated-np.mean(self.signal1_interpolated))/np.std(self.signal1_interpolated)
                return signal0_normalized,signal1_normalized

            def find_lag(self):
                # finds the maximum positive/negative correlation by shifting them relative to each other
                correlation_results = np.array(correlate(self.signal0_normalized,self.signal1_normalized))
                correlation_lags_result = correlation_lags(len(self.signal0_normalized),len(self.signal1_normalized))
                if self.alternative == 'less':
                    lag = correlation_lags_result[len(self.signal0_normalized) + np.argmin(correlation_results[len(self.signal0_normalized):len(self.signal0_normalized) + len(self.signal1_normalized) // 60])]
                else:
                    lag = correlation_lags_result[len(self.signal0_normalized)+np.argmax(correlation_results[len(self.signal0_normalized):len(self.signal0_normalized)+len(self.signal1_normalized)//60])]
                return lag

            def correlate_signals(self):# does the spearman
                return spearmanr(self.signal0_interpolated[self.lag:],self.signal1_interpolated[:-self.lag],nan_policy='raise',alternative = self.alternative)

baza = Database()
