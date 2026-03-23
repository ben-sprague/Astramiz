import argparse
import numpy as np

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from matplotlib import pyplot as plt

from torchModel import Net, SONARDataset, device, NewNet

BATCH_SIZE = 64

if __name__ == '__main__':
    #Setup argument parser
    parser = argparse.ArgumentParser()
    #Data file paths
    parser.add_argument('--sonar_data', required=True, type=str, help='Path to SONAR data')
    parser.add_argument('--range_data', action="store", required=True, type=str, help="Path to range data")
    parser.add_argument('--model', action="store", required=True, type=str, help="Path to model weights")

    args = parser.parse_args()

    # testing_sonar_data = np.load('/Users/ben/Desktop/astramiz/python/SURF/120ft TT Test/deepSea/All Data/rawData/testingSONARData.npy')
    # testing_range_data = np.load('/Users/ben/Desktop/astramiz/python/SURF/120ft TT Test/deepSea/All Data/rawData/testingRangeData.npy')

    # testing_sonar_data = np.load('/Users/ben/Desktop/astramiz/python/SURF/120ft TT Test/deepSea/All Data/Squestered Data/fullSONARData.npy')
    # testing_range_data = np.load('/Users/ben/Desktop/astramiz/python/SURF/120ft TT Test/deepSea/All Data/Squestered Data/fullRangeData.npy')

    testing_sonar_data = np.load(args.sonar_data)
    testing_range_data = np.load(args.range_data)


    testing_data = SONARDataset(testing_sonar_data, testing_range_data)
    test_dataloader = DataLoader(testing_data, batch_size=BATCH_SIZE)

    net = NewNet()

    #Load Model weights
    PATH = args.model
    #PATH = '/Users/ben/Desktop/astramiz/python/SURF/120ft TT Test/deepSea/2s Period Only/modelWeights.pth'

    state_dict = torch.load(PATH, weights_only=True)
    net.load_state_dict(state_dict)
    net.to(device)

    criterion = nn.MSELoss(reduction='mean')
    running_loss = 0
    loss_history = list()

    mean_abs_range = np.mean(testing_range_data[1,:])
    SS_tot = np.sum((testing_range_data[1,:]-mean_abs_range)**2)
    SS_res = 0
    AE_sum = 0
    AE = np.ndarray((0,))

    for i, data in enumerate(test_dataloader, 0):
        sonar, range = data
        sonar = sonar.to(device)
        rel_range = range[:, 0].detach().numpy()
        abs_range = range[:, 1].detach().numpy()
        min_range = range[:, 2].detach().numpy()
        max_range = range[:, 3].detach().numpy()
        out = net(sonar) 
        est_rel_range = out.cpu().detach().numpy()
        est_rel_range = np.reshape(est_rel_range, (-1,))
        est_abs_range = est_rel_range*(max_range-min_range)+min_range
        SS_res = SS_res+np.sum((est_abs_range-abs_range)**2)
        AE_sum = AE_sum + np.sum(np.abs(est_abs_range-abs_range))
        AE = np.append(AE, est_abs_range-abs_range)


    R_squared = 1-(SS_res/SS_tot)
    MAE = AE_sum/testing_range_data.shape[1]
    RMSE = np.sqrt(SS_res/testing_range_data.shape[1])

    print(f'R Squared is {R_squared}')
    print(f'MAE is {MAE}')
    print(f'STD is {np.std(AE)}')
    print(f'RMSE is {RMSE}')

    plt.hist(AE)
    plt.show()