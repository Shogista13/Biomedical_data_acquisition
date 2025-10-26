import statistics

def smooth(signal,filter_length):
    if len(signal) > filter_length:
        smoothed_signal = [statistics.mean(signal[i-filter_length//2:i+filter_length//2]) for i in range(filter_length//2,len(signal)-filter_length//2-1)]
        return smoothed_signal
    else:
        return None