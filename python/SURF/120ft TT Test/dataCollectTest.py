import pingHelper as ph
import time
import pandas as pd

working_df = pd.DataFrame(columns=['time', 'data'])

ph.sonar.connect_serial('/dev/tty.usbserial-DK0IHGWO')
sonar_settings = {
    'angle': 0,
    'transmit_duration': 80,
    'sample_period': 80,
    'num_samples': 200,
}
# ph.sonar_worker(5,10,sonar_settings)
thread = ph.start_test(2, sonar_settings)
while thread.is_alive():
    pass

df = ph.read_data()
print(df.iloc[-1,:].size)