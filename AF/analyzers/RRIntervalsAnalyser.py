import numpy as np
from matplotlib import pyplot as plt

from AF.medical_objects import rrInterval


class RRIntervalsAnalyser(object):

    def __init__(self, sampling_ratio, signals):

        self._sampling_ratio = sampling_ratio
        self._signals = signals

    def get_intervals(self, r_waves, channel_no, time_margin=0):

        samples_margin = time_margin * self._sampling_ratio
        channel = self._signals[:, channel_no]
        prev_r_wave_index = -1

        list_of_intervals = []
        rr_distanses = []

        for r_wave_index in r_waves:
            if prev_r_wave_index > 0:
                current_rr_interval = channel[int(prev_r_wave_index - samples_margin):int(r_wave_index + samples_margin)]
                if len(current_rr_interval) > 1:
                    list_of_intervals.append(rrInterval.RRInterval(current_rr_interval))
                    rr_distanses.append(int(r_wave_index - prev_r_wave_index))
            prev_r_wave_index = r_wave_index
        return list_of_intervals, rr_distanses

    # def get_list_of_intervals_isoelectric_line(self, list_of_intervals, margin_to_discard = 0.20):
    #
    #     # We don't want to modify existing list
    #     new_list_of_intervals = []
    #
    #     for interval_index, interval in enumerate(list_of_intervals):
    #
    #         interval_signal = interval.get_signal()
    #         length_of_interval = len(interval_signal)
    #
    #         start = int(round((margin_to_discard / 2 * length_of_interval), 0))
    #         stop = int(round(((1 - margin_to_discard / 2) * length_of_interval), 0))
    #
    #         new_interval_signal = interval_signal[start:stop]
    #
    #         new_interval = rrInterval.RRInterval()
    #         new_interval.set_signal(new_interval_signal)
    #
    #         new_list_of_intervals.append(new_interval)
    #
    #     return new_list_of_intervals

    def get_list_of_intervals_isoelectric_line(self, list_of_intervals, interval_samples=100):

        # We don't want to modify existing list
        new_list_of_intervals = []

        for interval_index, interval in enumerate(list_of_intervals):
            interval_signal = interval.get_signal()

            if len(interval_signal)< interval_samples:
                new_interval = None
                #new_list_of_intervals.append(new_interval)
            else:
                center_of_interval = len(interval_signal)/2
                start = center_of_interval - int(1/2 * interval_samples)
                stop = center_of_interval + int(1/2 * interval_samples) + 1
                new_interval_signal = interval_signal[int(start):int(stop)]
                new_interval = rrInterval.RRInterval()
                new_interval.set_signal(new_interval_signal)
                new_list_of_intervals.append(new_interval)

        return new_list_of_intervals



    def plot_histogram(self, signal, title):

        raw_signal = signal
        signal = np.multiply(signal, 1/self._sampling_ratio)

        plt.figure(1)
        plt.subplot(2,1,1)
        plt.title(title)

        plt.hist(raw_signal)
        plt.xlabel("[n]")
        plt.ylabel("Liczba zliczeń")

        plt.subplot(2,1,2)

        plt.hist(signal)
        plt.xlabel("[s]")
        plt.ylabel("Liczba zliczeń")

        plt.show()
