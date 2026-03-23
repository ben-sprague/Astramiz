import numpy as np

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

from matplotlib import pyplot as plt

from torchModel import Net, SONARDataset, device, NewNet

import progressbar
import argparse

BATCH_SIZE = 64

if __name__ == "__main__":
    #Setup argument parser
    parser = argparse.ArgumentParser()
    #Data file paths
    parser.add_argument('--sonar_data', required=True, type=str, help='Path to SONAR data')
    parser.add_argument('--range_data', action="store", required=True, type=str, help="Path to range data")
    parser.add_argument('--save_path', action="store", required=True, type=str, help="Path to write model weights to")
    parser.add_argument('--epoch', action='store', required=False, default=25, type=int, help='Numer of epochs to run')
    args = parser.parse_args()

    #Load training data
    # training_sonar_data = np.load('/Users/ben/Desktop/astramiz/python/SURF/120ft TT Test/deepSea/All Data/rawData/trainingSONARData.npy')
    # training_range_data = np.load('/Users/ben/Desktop/astramiz/python/SURF/120ft TT Test/deepSea/All Data/rawData/trainingRangeData.npy')
    training_sonar_data = np.load(args.sonar_data)
    training_range_data = np.load(args.range_data)

    training_data = SONARDataset(training_sonar_data, training_range_data)
    train_dataloader = DataLoader(training_data, batch_size=BATCH_SIZE, shuffle=True)
                
    net = NewNet()
    net.to(device)

    optimizer = optim.AdamW(net.parameters(), lr=0.013)
    criterion = nn.MSELoss()
    running_loss = 0
    loss_history = list()
    EPOCH_COUNT = args.epoch
    bar = progressbar.ProgressBar(max_value=EPOCH_COUNT)
    for epoch in range(EPOCH_COUNT):  # loop over the dataset multiple times
        for i, data in enumerate(train_dataloader, 0):
            sonar, range = data
            sonar = sonar.to(device)
            range = range[:,0].to(device)
            optimizer.zero_grad()
            out = net(sonar) 
            loss = criterion(range, out)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
            if i % 5 == 4:    # print every 2000 mini-batches
                #print(f'[{epoch + 1}, {i + 1:5d}] loss: {running_loss / 2000:.3f}')
                loss_history.append(running_loss/5)
                running_loss = 0.0
        bar.update(epoch)

    print('Finished Training')
    torch.save(net.state_dict(), f'./{args.save_path}modelWeights.pth')
    plt.semilogy(loss_history)
    plt.show()