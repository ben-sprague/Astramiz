import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset

from matplotlib import pyplot as plt

if torch.backends.mps.is_available():
    device = torch.device("mps")
    print("MPS device found.")
else:
    device = torch.device("cpu")
    print("MPS device not found.")

class Net(nn.Module):

    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1,4,kernel_size=(2,5), padding=(0,1))
        self.conv2 = nn.Conv2d(4,16,kernel_size=(2,5), padding=(0,1))
        self.conv3 = nn.Conv2d(16,32,kernel_size=(2,5), padding=(0,1))

        self.fc1 = nn.Linear(3904, 240)
        self.fc2 = nn.Linear(240, 160)
        self.fc3 = nn.Linear(160, 100)
        self.fc4 = nn.Linear(100, 54)
        self.fc5 = nn.Linear(54, 1)
     
    def forward(self, input):
        #First convolution layer: 1 input image, 4 output channels, 5x5 kernel
        # plt.imshow(input[0,0,:,:].cpu().detach().numpy(), aspect='auto')
        # plt.show()
        c1 = F.relu(self.conv1(input))
        # plt.imshow(c1[0,0,:,:].cpu().detach().numpy(), aspect='auto')
        # plt.show()
        s2 = F.max_pool2d(c1, (2,2))
        # plt.imshow(s2[0,0,:,:].cpu().detach().numpy(), aspect='auto')
        # plt.show()
        c3 = F.relu(self.conv2(s2))
        # plt.imshow(c3[0,0,:,:].detach().numpy(), aspect='auto')
        # plt.show()
        s4 = F.max_pool2d(c3, (2,2))
        # plt.imshow(s4[0,0,:,:].cpu().detach().numpy(), aspect='auto')
        # plt.show()
        c5 = F.relu(self.conv3(s4))
        # plt.imshow(c5[0,0,:,:].detach().numpy(), aspect='auto')
        # plt.show()
        s6 = F.max_pool2d(c5, (2,2))

        s6 = torch.flatten(s6,1)

        f7 = (self.fc1(s6))
        f8 = (self.fc2(f7))
        f9 = (self.fc3(f8))
        f10 = (self.fc4(f9))
        output = (self.fc5(f10))

        return output
    
class NewNet(nn.Module):

    def __init__(self):
        super(NewNet, self).__init__()
        # self.conv1 = nn.Conv2d(1,4,kernel_size=(3,3), padding=(0,2))
        # self.conv2 = nn.Conv2d(4,8,kernel_size=(3,3), padding=(0,2))
        # self.conv3 = nn.Conv2d(8,16,kernel_size=(3,3), padding=(0,2))

       


        self.conv1 = nn.Conv2d(1,4,kernel_size=(3,3), padding=(0,2))
        self.conv2 = nn.Conv2d(4,8,kernel_size=(3,1), padding=(0,0))
        self.conv3 = nn.Conv2d(8,16,kernel_size=(3,1), padding=(0,0))

        self.fc1 = nn.Linear(2560, 256)
        self.fc2 = nn.Linear(256, 1)
     
    def forward(self, input):
        #First convolution layer: 1 input image, 4 output channels, 5x5 kernel
        # plt.imshow(input[0,0,:,:].cpu().detach().numpy(), aspect='auto')
        # plt.show()
        c1 = F.relu(self.conv1(input))
        # plt.imshow(c1[0,0,:,:].cpu().detach().numpy(), aspect='auto')
        # plt.show()
        s2 = F.max_pool2d(c1, (3,3))
        # plt.imshow(s2[0,0,:,:].cpu().detach().numpy(), aspect='auto')
        # plt.show()
        c3 = F.relu(self.conv2(s2))
        # plt.imshow(c3[0,0,:,:].detach().numpy(), aspect='auto')
        # plt.show()
        s4 = F.max_pool2d(c3, (2,2))
        # plt.imshow(s4[0,0,:,:].cpu().detach().numpy(), aspect='auto')
        # plt.show()
        c5 = F.relu(self.conv3(s4))
        # plt.imshow(c5[0,0,:,:].detach().numpy(), aspect='auto')
        # plt.show()
        s6 = F.max_pool2d(c5, (1,2))
        # plt.imshow(s6[0,0,:,:].cpu().detach().numpy(), aspect='auto')
        # plt.show()
        # plt.imshow(s6[0,1,:,:].cpu().detach().numpy(), aspect='auto')
        # plt.show()
        # plt.imshow(s6[0,2,:,:].cpu().detach().numpy(), aspect='auto')
        # plt.show()
        # plt.imshow(s6[0,3,:,:].cpu().detach().numpy(), aspect='auto')
        # plt.show()
        # plt.imshow(s6[0,4,:,:].cpu().detach().numpy(), aspect='auto')
        # plt.show()
        # plt.imshow(s6[0,5,:,:].cpu().detach().numpy(), aspect='auto')
        # plt.show()
        s6 = torch.flatten(s6,1)
        
        
        f7 = F.relu(self.fc1(s6))
        output = (self.fc2(f7))

        return output

class SONARDataset(Dataset):
    def __init__(self, sonar_data, range_data):
        self.sonar_data = sonar_data
        self.range_data = range_data


    def __len__(self):
        return self.range_data.shape[1]

    def __getitem__(self, idx):
        return np.reshape(self.sonar_data[:,:,idx], (1,self.sonar_data.shape[0], self.sonar_data.shape[1])), self.range_data[:,idx]