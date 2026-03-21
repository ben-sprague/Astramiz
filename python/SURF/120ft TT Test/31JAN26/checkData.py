import pandas as pd
import argparse

from matplotlib import pyplot as plt

def plotData(fileNum):
    file = f"data{fileNum}"
    #Unpack wave data from excel file
    wave_df = pd.read_excel(f"{file}.xlsx", usecols='A:E', skiprows=list(range(1,6)), names = ['Time','SonHt', 'SonWav', 'IceHt', 'IceWav'], index_col=0)
    wave_df.index = wave_df.index.astype(float) #convert indexes (times) from strings to floats
    wave_df = wave_df/100 #convert cm to meters    
    
    #Read SONAR data
    sonar_df = pd.read_csv(f"{file}.csv", index_col='time')

    sonar_df.drop(sonar_df.columns[0], axis=1, inplace=True) #Drop column of row indeicies at the left of the dataframe
    sonar_df.index = sonar_df.index.astype(float) #convert indexes (times) from strings to floats
    sonar_df.columns = sonar_df.columns.astype(float) #convert columns (ranges) from strings to floats

    fig, (ax1, ax2, ax3) = plt.subplots(3,1)

    ax1.plot(wave_df['SonHt'],'b-')
    ax1.plot(wave_df['SonWav'], 'r--')
    ax1.set_title(f"data{fileNum}")

    ax2.plot(wave_df['IceHt'],'b-')
    ax2.plot(wave_df['IceWav'], 'r--')

    ax3.imshow(sonar_df.to_numpy(), aspect="auto", interpolation='nearest')
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--startNum', required=True, type=int, help='Data number to start with')
    parser.add_argument('--endNum', required=True, type=int, help='Data number to end with')

    args = parser.parse_args()

    for i in range (args.startNum, args.endNum):
        plotData(i)

    

