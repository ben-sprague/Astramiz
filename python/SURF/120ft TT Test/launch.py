#Dashboard to control Ping360 SONAR for use during testing in the USNA 120ft Tow Tank
#Dashboard is build on Dash and runs in the browser

#Import Dash and Plotly
from dash import Dash, dcc, html, Input, Output, State
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd

#Import SONAR Related Packages
from brping import Ping360
import pingHelper as ph
from speedOfSound import speed_of_sound
from serial.tools import list_ports

#Import other stuff
from datetime import datetime
import math
import numpy as np
import os


external_stylesheets = [dbc.themes.CERULEAN]
app = Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = dbc.Container([
    dbc.Row([
        html.H1('120ft Tow Tank SONAR Testing Dashboard')
    ],className="mb-3 mt-3"),
    dbc.Row([
        html.H4("ISO TIME",id = 'iso_time'),
        dcc.Interval(
            id='time_update',
            interval=100, # in milliseconds
            n_intervals=0
        )      
    ]),
    dbc.Row([
        html.H4("EPOCH TIME",id = 'epoch_time'),
    ], className = "mb-3"),
    dbc.Row([
        html.H3("COMM Ports")        
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id = "comm_port_menu",
                options=[
                ],
                placeholder="COMM Port",
                className="col-16"
            ),
        ]),
        dbc.Col([
            dbc.Button(
                "Update",
                id = "comm_port_menu_update",
                color="secondary",
                className="d-grid gap-2 col-6 mx-auto",
            )    
        ]),
        dbc.Col([
            dcc.Input(value = 2000000, type='number',id = 'baudrate', className=' d-grid col-8')
        ]),
        dbc.Col([
            html.H5("Status: \U0001F534", id = "comm_port_status")
        ]),  
        dbc.Col([
            dbc.Button(
                "Connect",
                id = "comm_port_connect",
                color="secondary",
                className="d-grid gap-2 col-6 mr-0",
            )    
        ]), 
        dbc.Col([
            dbc.Button(
                "Disconnect",
                id = "comm_port_disconnect",
                color="secondary",
                className="d-grid mx-auto",
            )    
        ]),
    ], className = 'mb-5'),
    dbc.Row([
        dbc.Col([
            html.H6("Test Duration (s)")
        ]),
        dbc.Col([
            dcc.Input(value=1, type="number", id = 'test_duration')
        ]),
        dbc.Col([
            html.H6("Sample Frequency (hz)")
        ]),
        dbc.Col([
            dcc.Input(value=100, type="number", id = 'sample_frequency')
        ]),
    ], className="mb-2"),
    dbc.Row([
        dbc.Col([
            html.H6("Head Azmiuth (grad, 0-399)")
        ]),
        dbc.Col([
            dcc.Input(value=200, type="number", id = 'head_azimuth')
        ]),
        dbc.Col([
            html.H6("Transmit Duration (us, 1-1000)")
        ]),
        dbc.Col([
            dcc.Input(value=30, type="number", id = 'transmit_duration')
        ])
    ], className="mb-2"),
    dbc.Row([
        dbc.Col([
            html.H6("Samples Period (25*ns, 80-40000)")
        ]),
        dbc.Col([
            dcc.Input(value=150, type="number", id = 'sample_period')
        ]),
        dbc.Col([
            html.H6("Samples Per Ping (20-1200)")
        ]),
        dbc.Col([
            dcc.Input(value=1024, type="number", id = 'num_samples')
        ]),
    ], className="mb-2"),
    dbc.Row([
        dbc.Col([
            "MAX RANGE"
        ],  id = "max_range"),
        dbc.Col([
            "MAX FREQUENCY"
        ],  id = "max_frequency"),
    ], className="mb-2 mx-auto",),
    dbc.Row([
        dbc.Col([
            html.H6("Water Temperature (C)")
        ]),
        dbc.Col([
            dcc.Input(value=65, type="number", id = 'water_temp')
        ]),
        dbc.Col([
            "Speed of Sound = "
        ], id = "speed_of_sound")
    ], className="mb-2"),
    dbc.Row([
        dbc.Button("Sample", id="sample"),
        dcc.Interval(
            id='data_update',
            interval=1000, # in milliseconds
            n_intervals=0
        ),
        dcc.Store(id = "collection_complete", data = True)
    ], className="mb-5"),
    dbc.Row([
        "Live Plot (1hz refresh)"
    ]),
    dbc.Row([
        dcc.Graph(id = "live_plot")
    ]),
    dbc.Row([
        "Waterfall Plot"
    ]),
    dbc.Row([
        dcc.Graph(id = "waterfall_plot")
    ]),
    # dbc.Row([
    #     "Single Range Plot"
    # ]),
    # dbc.Row([
    #     dcc.Graph(id = "singe_range_plot")
    # ]),
    # dbc.Row([
    #     dcc.Slider(0,5,1/1024,value=0,marks={0:"0",5:"5"},id = "single_range_slider")
    # ], class_name = "mb-5"),
    dbc.Row([
        html.H4("Save Data")
    ]),
    dbc.Row([
        dbc.Col([
            "Directory Path"
        ]),
        dbc.Col([
            dcc.Input(value = "./data", type = "text", id = "dir_path")
        ]),
        dbc.Col([
            "File Name (no file extension)"
        ]),
        dbc.Col([
            dcc.Input(value = "test", type = "text", id = "file_name")
        ]),
    ], class_name="mb-4"),
    dbc.Row([
        dbc.Button([
            "Save File"
        ], id = "save")
    ],class_name="mb-6")
])


#CALLBACKS

#Update Timestamps
@app.callback(
    Output("iso_time",'children'),
    Output("epoch_time",'children'),
    Input("time_update","n_intervals")
)
def update_time(n):
    return datetime.now().strftime("%d %b %Y %H:%M:%S"), math.floor(datetime.now().timestamp())

#Update Comm Port Dropdown Timestamp
@app.callback(
    Output("comm_port_menu",'options'),
    Input("comm_port_menu_update","n_clicks")
)
def update_comm_port_list(n):
    port_paths = []
    for port in list_ports.comports():
        port_paths.append(port.device)

    return port_paths

#Connect to selected comm port
@app.callback(
    Output("comm_port_status",'children', allow_duplicate=True),
    Input("comm_port_connect","n_clicks"),
    State("comm_port_menu", "value"),
    State("baudrate", "value"),
    prevent_initial_call = True

)
def update_comm_port_list(n, port, baud_str):
    if ph.sonar is None:
        ph.sonar = Ping360()
    
    emoji = "\U0001F534" #Red dot
    ph.sonar_connected = False
    if port:
        ph.sonar.connect_serial(port, int(baud_str))
        if ph.sonar.initialize():
            emoji = "\U0001F7E2" #Green dot
            ph.sonar_connected = True

    return f"Status: {emoji}"

#Disconnect from sensor
@app.callback(
    Output("comm_port_status",'children', allow_duplicate=True),
    Input("comm_port_disconnect","n_clicks"),
    prevent_initial_call = True
)
def disconnect_sensor(n):
    ph.sonar_connected = False
    ph.sonar = None
    emoji = "\U0001F534" #Red dot
    return f"Status: {emoji}"

#Calculate the speed of sound when water temp is changed
@app.callback(
    Output("speed_of_sound", "children"),
    Input("water_temp", "value")
)
def display_speed_of_sound(temp):
    if temp:
        return f"Speed of sound = {speed_of_sound(0,temp,0)} m/s"

#Calculate the max range when either the transmit period, number of samples, or water temp are changed
@app.callback(
    Output("max_range", "children"),
    Output("transmit_duration", "value"),
    Input("sample_period", "value"),
    Input("num_samples", "value"),
    Input("water_temp", "value"),
)
def display_max_range(period, sample_count, temp):
    c = speed_of_sound(0,temp,0)
    distance_per_sample = c*period*25/10**9/2 #meters
    range_str = f"Max range = {round(max_range:=(sample_count*distance_per_sample),3)} m"
    tx_duration_guess_1 = max_range*8000/c
    if tx_duration_guess_1 > (tx_duration_guess_2 := (2.5 * period*25 / 1000)):
        tx_duration = tx_duration_guess_1
    else:
        tx_duration = tx_duration_guess_2

    return range_str, round(tx_duration)
    
#Calculate the max sampling frequency when either the transmit period, number of samples, transmit duration, or water temp are changed
@app.callback(
    Output("max_frequency", "children"),
    Input("sample_period", "value"),
    Input("num_samples", "value"),
    Input("water_temp", "value"),
    Input("transmit_duration", "value")
)
def display_max_frequency(period, sample_count, temp, duration):
    c = speed_of_sound(0,temp,0)
    distance_per_sample = c*period*25/10**9 #meters
    max_range = sample_count*distance_per_sample
    return f"Max sampling frequency = {round(1/(max_range/c+duration/10**6))} hz"

#Start the sampling thread when the sample button is pressed
@app.callback(
    Output("sample", "color", allow_duplicate=True),
    Output("comm_port_status", 'children', allow_duplicate=True),
    Input("sample", 'n_clicks'),
    State("test_duration", "value"),
    State("head_azimuth", 'value'),
    State("sample_period", "value"),
    State("num_samples", "value"),
    State("transmit_duration", "value"),
    State("comm_port_menu", "value"),
    State("baudrate", "value"),
    prevent_initial_call = True
)
def start_sampling(n, duration, angle, period, num_samples, transmit_duration, port, baud_str):
    sonar_settings = {
        'angle': int(angle),
        'transmit_duration': int(transmit_duration),
        'sample_period': int(period),
        'num_samples': int(num_samples),
    }
    if not ph.thread:
        #If there is not an active thead polling the sonar
        ph.working_df = None
        if not ph.sonar_connected:
            #Try to connect sonar if not already connected
            if port:
                #If the serial port is defined then try to intialize the device
                ph.sonar.connect_serial(port, int(baud_str))
                if ph.sonar.initialize():
                    #Connection is good
                    emoji = "\U0001F7E2" #Green dot
                    ph.sonar_connected = True
        if ph.sonar_connected:
            #If the sonar is now connected
            try:
                #Start a seperate thread to poll the sonar
                ph.thread = ph.start_test(int(duration), sonar_settings)
            except IOError:
                #Problem talking to the SONAR (likley that the serial connection went bad)
                ph.sonar_connected = False
                ph.thread = None
                emoji = "\U0001F534" #Red dot
                return "primary", f"Status: {emoji}"
            else:
                #The thread was started successfully
                ph.collection_complete = False
                emoji = "\U0001F7E2" #Green dot
                return "success", f"Status: {emoji}"
    else:
        #If there is a thread polling the SONAR
        if not ph.thread.is_alive():
            #If the thread is dead (ie. the trial is was created for perform is complete)
            ph.thread = None #Discard the thread
            if ph.sonar_connected:
                emoji = "\U0001F7E2" #Green dot
            else:
                emoji = "\U0001F534" #Red dot
            return "primary", f"Status: {emoji}"

#Monitor sampling thread and read out data
@app.callback(
    Output("sample", "color"),
    Output("comm_port_status", "children"),
    Output("live_plot", 'figure'),
    Output("collection_complete", "data"),
    Input("data_update", "n_intervals"),
    State("head_azimuth", 'value'),
    State("sample_period", "value"),
    State("num_samples", "value"),
    State("transmit_duration", "value"),
    State("water_temp", "value"),
    State("collection_complete", "data")
)
def check_data(n, angle, period, num_samples, transmit_duration, temp, collection_complete_status):
    if ph.thread is not None:
        #If there is an active thread, assume that the SONAR is working
        emoji = "\U0001F7E2" #Green dot
        #If there is a working thread
        if not ph.thread.is_alive():
            #If the thread is dead
            #Clear out the queue
            read_data_from_queue()
            ph.collection_complete = True
            fig = generate_fig_from_data(ph.working_df, period, temp)

            #Discard the old thread pointer
            ph.thread = None
            color = "primary"
        else:
            #If it's still alive

            #Read out data in the queue
            read_data_from_queue()
            fig = generate_fig_from_data(ph.working_df, period, temp)
            color = "success"
                
    else:
        #If there is not a thread active, send a single ping to update the plot
        sonar_settings = {
            'angle': int(angle),
            'transmit_duration': int(transmit_duration),
            'sample_period': int(period),
            'num_samples': int(num_samples),
        }

        if ph.sonar_connected:
            #If the sonar is connected
            try:
                fig = generate_fig_from_data(ph.single_ping(sonar_settings),period, temp)
            except IOError:
                #Problem talking to the SONAR
                emoji = "\U0001F534" #Red dot
                ph.sonar_connected = False
                fig = px.line(x=[0, 1], y=[0, 0])
            else:
                #It worked
                emoji = "\U0001F7E2" #Green dot
        else:
            emoji = "\U0001F534"
            fig = px.line(x=[0, 1], y=[0, 0])
        
        color = "primary"
        
    return color, f"Status: {emoji}", fig, ph.collection_complete
    

def read_data_from_queue():
    #Function to read data from the polling thread's queue and process it
    if (new_data := ph.read_data()) is not None:
        if ph.working_df is not None:
            #If there is already a running dataframe then append the new data to it
            ph.working_df = pd.concat([ph.working_df, new_data])
        else:
            #If there is not a running dataframe, then create one
            ph.working_df = new_data

def generate_fig_from_data(df, period, temp):
    #Function to generate a plotly figure from the last row of the working dataframe
    line = df.iloc[-1,1:] #Get last line
    num_sampled = line.size
    c = speed_of_sound(0,temp,0)
    distance_per_sample = c*period*25/10**9/2 #roundtrip distance in meters
    x_val = np.array(list(range(0,num_sampled)))*distance_per_sample #create x array (range) based on the distance per sample and number of samples
    return px.line(x = x_val,y = line, labels={'x': 'Range (m)', 'y': 'Intensity (0-255)'})

#Once collection is complete, generate waterfall plot
@app.callback(
    Output("waterfall_plot", 'figure'),
    Input("collection_complete", "data"),
    State("water_temp", "value"),
    State("transmit_duration", "value"),
)
def update_waterfall_plot(state, temp, period):
    if ph.working_df is not None:
        return generate_waterfall_plot(ph.working_df, period, temp)
    else:
        return None

def generate_waterfall_plot(df, period, temp):
    times = df.iloc[:,0].to_numpy()
    y_val = (times-times.min()) #s
    image = df.iloc[:,1:]
    num_sampled = image.shape[1]
    c = speed_of_sound(0,temp,0)
    distance_per_sample = c*period*25/10**9/2 #roundtrip distance in meters
    x_val = np.array(list(range(0,num_sampled)))*distance_per_sample
    return px.imshow(image.to_numpy(), x = x_val, y = y_val, labels={'x': "Range (m)", 'y':'Elapsed Time (s)'}, aspect="auto")

#Save data
@app.callback(
    Input("save", 'n_clicks'),
    State("dir_path", "value"),
    State("file_name", "value"),
    State("head_azimuth", 'value'),
    State("sample_period", "value"),
    State("num_samples", "value"),
    State("transmit_duration", "value"),
    State("water_temp", "value"),)
def save_data(n, path, name, angle, period, num_samples, transmit_duration, temp):
    if not os.path.exists(path):
        #Make sure directory exists and if it doesn't then create it
        os.makedirs(path)

    if ph.working_df is not None:
        ph.working_df.to_csv(f'{path}/{name}.csv')
        with open(f'{path}/{name}.txt', 'w') as file:
            file.write(f"Angle {angle}\nSample Period {period}\nNum Samples {num_samples}\nTx Duration {transmit_duration}\nTemp {temp}\n")
        print(f"File Saved to '{path}/{name}.csv'")


app.run(debug=True)