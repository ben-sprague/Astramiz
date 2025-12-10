from brping import definitions
from brping import Ping360

import threading
import queue

from datetime import datetime

import pandas as pd
import numpy as np

#Init SONAR
sonar = Ping360()
sonar_connected = False

#Threading data queue
data_queue = queue.Queue()
thread = None

#Working DataFrame
working_df = None

#Plotting Control Variables
collection_complete = True

def sonar_worker(test_duration, sonar_settings):
    start_time = datetime.now().timestamp()
    while datetime.now().timestamp() < start_time+test_duration:
        sonar.control_transducer(
            mode = 1,
            gain_setting = 0,
            angle = sonar_settings["angle"],
            transmit_duration = sonar_settings["transmit_duration"],
            sample_period = sonar_settings["sample_period"],
            transmit_frequency = 750,
            number_of_samples = sonar_settings["num_samples"],
            transmit=True,
            reserved = False
        )
        message = sonar.wait_message([definitions.PING360_DEVICE_DATA])
        if message:
            data_queue.put({'time':datetime.now().timestamp(), 'data':message.data})

def start_test(test_duration, sonar_settings):
    t = threading.Thread(target=sonar_worker, args=(test_duration, sonar_settings))
    t.start()
    return t

def read_data():
    new_data = []
    if not data_queue.empty():
        while not data_queue.empty():
            item = data_queue.get()
            data_queue.task_done()
            data_list = list(item['data'])
            data_line = [item['time']]+data_list
            new_data.append(data_line)
        num_samples = len(data_line)-1

        return pd.DataFrame(np.array(new_data).reshape((-1,num_samples+1)), columns=["time"]+list(range(0,num_samples)))
    else:
        return None

def single_ping(sonar_settings):
    sonar.control_transducer(
        mode = 1,
        gain_setting = 0,
        angle = sonar_settings["angle"],
        transmit_duration = sonar_settings["transmit_duration"],
        sample_period = sonar_settings["sample_period"],
        transmit_frequency = 750,
        number_of_samples = sonar_settings["num_samples"],
        transmit=True,
        reserved = False
    )
    message = sonar.wait_message([definitions.PING360_DEVICE_DATA])
    if message:
        num_samples = len(data_list:= list(message.data))
        data_line = np.array([datetime.now().timestamp]+data_list).reshape((1,-1))
        return pd.DataFrame(data_line, columns=["time"]+list(range(0,num_samples)))
    else:
        return pd.DataFrame(columns=['time']+list(range(0,sonar_settings["num_samples"])))