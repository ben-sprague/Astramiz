import pandas as pd
import numpy as np

from speedOfSound import speed_of_sound

class towTankTest:
    def __init__(self, csv_file_path, txt_file_path, wave_data_path):
        self.full_dataframe = pd.read_csv(csv_file_path)
        with open(txt_file_path, 'r') as file:
            self.unpackTxt(file)
        self.unpackWaveData(wave_data_path)

    
            
        
test = towTankTest('./python/SURF/120ft TT Test/sonar data/18NOV/test19.csv', './python/SURF/120ft TT Test/sonar data/18NOV/test19.txt', './python/SURF/120ft TT Test/wave data/data19.xlsx')