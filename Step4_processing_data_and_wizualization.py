from Step2_reading_and_correcting import read_with_pickle
from AF.tools.pca_tools import PCADimensionAnalyser
from matplotlib import pyplot as plt
import numpy as np
from PyEMD import EMD
from sklearn.svm import LinearSVC
from AF.simple_medical_analysers.wavelet_analysis import  DWTWaveletAnalyser


def transform_dataset_into_pcas_datasets(dataset):
    new_dataset = dataset.copy()
    for patient in dataset:
        list_rr_channel0 = dataset[patient]["channel0"]
        list_rr_channel1 = dataset[patient]["channel1"]
        for index in range(len(list_rr_channel0)):

            # PCA
            input_PCA_dataset = [[el1, el2] for el1, el2 in zip(
                list_rr_channel0[index].get_signal(), list_rr_channel1[index].get_signal())]
            pca_a = PCADimensionAnalyser()
            pca_a.calculate_new_dimension(input_PCA_dataset, number_of_components=2)
            output_PCA_dataset = pca_a.get_new_dimension(input_PCA_dataset)
            signal_pca0 = [el[0] for el in output_PCA_dataset]
            signal_pca1 = [el[1] for el in output_PCA_dataset]


            # Updating
            new_dataset[patient]["channel0"][index].set_signal(signal_pca0)
            new_dataset[patient]["channel1"][index].set_signal(signal_pca1)



    return new_dataset


def transform_dataset_into_coeffs_dataset(dataset, wavelet="db2"):
    all = []
    new_dataset = dataset
    for patient in dataset:
        list_rr_channel0 = dataset[patient]["channel0"]
        list_rr_channel1 = dataset[patient]["channel1"]
        diagnose = dataset[patient]["diagnose"]
        dataset[patient]["coeffs"] = np.empty((len(list_rr_channel0),2))
        for index in range(len(list_rr_channel0)):
            signal0 = list_rr_channel0[index].get_signal()
            signal1 = list_rr_channel1[index].get_signal()



            # Calculate coeffs
            dwt_a = DWTWaveletAnalyser()
            norm_coeff0 = dwt_a.get_wavelet_af_energy(signal0, frequency=128, wavelet=wavelet)
            norm_coeff1 = dwt_a.get_wavelet_af_energy(signal1, frequency=128, wavelet=wavelet)

            # Updating
            record_data = [norm_coeff0, norm_coeff1, diagnose, patient]
            all.append(record_data)
            # new_dataset[patient]["coeffs"][index, :] = [norm_coeff0, norm_coeff1]
            # TODO Co zrobic z tym, ze wtedy nie bedzie mial pacjent w tym zalamku coeffsow
            pass
    return all

def calculate_emd_and_show(dataset):
    dictionary = {"aftdb": {"var":[],
                          "std":[]},
                  "ptb":   {"var":[],
                          "std":[]}
                  }
    for patient in dataset:
        list_rr_channel0 = dataset[patient]["channel0"]
        list_rr_channel1 = dataset[patient]["channel1"]

        if dataset[patient]["diagnose"] == "ptb":
            for index in range(len(list_rr_channel0)):
                signal0 = list_rr_channel0[index].get_signal()
                signal1 = list_rr_channel1[index].get_signal()

                emd = EMD()
                eIMFs0 = emd.emd(signal0)
                number_of_imfs = len(eIMFs0)
                for i in range(number_of_imfs):
                    fig = plt.figure(1)
                    plt.subplot(number_of_imfs,1,i+1)
                    plt.plot(eIMFs0[i, :])
                    fig.savefig(patient + "_" + str(dataset[patient]["diagnose"]) +  "_chann_0_" + ".jpg")

                emd = EMD()
                eIMFs1 = emd.emd(signal1)
                number_of_imfs = len(eIMFs1)
                for i in range(number_of_imfs):
                    fig = plt.figure(2)
                    plt.subplot(number_of_imfs, 1, i + 1)
                    plt.plot(eIMFs1[i, :])
                    fig.savefig(patient + "_" + str(dataset[patient]["diagnose"]) + "_chann_1_" + ".jpg")

                break


if __name__ == "__main__":

    directory = "database/step3"
    X_test = read_with_pickle(directory + "/" + "X_test.pkl")
    X_train = read_with_pickle(directory + "/" + "X_train.pkl")

    # TODO Add more features to dataset for classification


    # TODO Make X dataset for SVM  and SNN
    # TODO Make Y dataset for SVM and SNN

    # TODO Test SNN and SVM


    wavelet = "db6"
    X_test_wavelets_coeffs = np.array(transform_dataset_into_coeffs_dataset(X_test, wavelet=wavelet))
    X_train_wavelets_coeffs = np.array(transform_dataset_into_coeffs_dataset(X_train, wavelet=wavelet))

    # Data visualisation
    for element in X_test_wavelets_coeffs:
        color = "blue" if element[2] == "ptb" else "red"
        plt.scatter(element[0], element[1], color=color)
    plt.show()

    # SVM
    X = X_train_wavelets_coeffs[:,0:2]
    X = X.astype('float')
    y = [1 if element=="aftdb" else 0 for element in X_train_wavelets_coeffs[:,2]]
    clf = LinearSVC(random_state=0)
    clf.fit(X, y)
    dual_problem = False  # dual=False when n_samples > n_features.
    LinearSVC(C=1.0, class_weight=None, dual=dual_problem, fit_intercept=True,
              intercept_scaling=1, loss='squared_hinge', max_iter=1000,
              multi_class='ovr', penalty='l2', random_state=0, tol=0.0001,
              verbose=0)

    new_y = clf.decision_function(X)
    print(new_y)

    # Data visualisation
    plt.figure(2)
    for index, class_y in enumerate(new_y):
        color = "blue" if class_y < 0 else "red"
        plt.scatter(X[index,0], X[index,1] , color=color)
    plt.show()

    # # PARAMS
    # dual_problem = False  # dual=False when n_samples > n_features.
    # class1 = 1  # only for plotting
    # class2 = 0  # only for plotting
    #
    # LinearSVC(C=1.0, class_weight=None, dual=dual_problem, fit_intercept=True,
    #           intercept_scaling=1, loss='squared_hinge', max_iter=1000,
    #           multi_class='ovr', penalty='l2', random_state=0, tol=0.0001,
    #           verbose=0)
    #
    # new_y = clf.decision_function(X)
    # print(new_y)
    #
    # # PLOTTING
    # plt.figure(1)
    # for index, class_y in enumerate(y):
    #     color = "blue" if class_y == 0 else "red"
    #     plt.scatter([X[index, class1]], X[index, class2], color=color)
    #
    # # PLOTTING
    # plt.figure(2)
    # for index, class_y in enumerate(new_y):
    #     color = "blue" if class_y < 0 else "red"
    #     plt.scatter([X[index, class1]], X[index, class2], color=color)
    # plt.show()


    # TODO testy NN z obecnym stanem prac
    # TODO falki
    # TODO emd
