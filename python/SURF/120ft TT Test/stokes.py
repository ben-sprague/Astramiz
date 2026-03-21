import numpy as np
from scipy.optimize import minimize
import pandas as pd

class StokesWave:
    '''
    Implimentation of third order stokes wave solution described in 
    "Stokes Third Order Approximation Tables of Functions" by Lars Skjelbreia (1958)
    '''
    def __init__(self, wave_period, wave_height, water_depth):
        '''
        Intialize class and calculate coefficents described in Skjelbreia (1958)

        water_depth: Depth of water from mean water line to bottom in meters
        wave_period: Period of the wave in seconds
        wave_height: Height of the wave in meters
        '''
        self.T = wave_period
        self.H = wave_height
        self.h= water_depth
        self.g = 9.81

        #Estimate wave length with linear wave theory
        [self.L, self.a0] = self.solve_stokes_wave_length_a0()

        self.c = self.L/self.T

        #Calculate coefficents described in Skjelbreia (1958)
        self.k = 2*np.pi/self.L
        f2 = np.cosh(2*np.pi*self.h/self.L)*(np.cosh(4*np.pi*self.h/self.L)+2)/2/np.sinh(2*np.pi*self.h/self.L)**3
        f3 = 3/16*(8*np.cosh(2*np.pi*self.h/self.L)**6+1)/np.sinh(2*np.pi*self.h/self.L)**6
        self.a1 = np.pi*(self.a0**2)*f2/self.L
        self.a2 = (np.pi**2)*(self.a0**3)*f3/(self.L**2)

        self.phase = 0

    def _wave_length_difference(self, inputs):
        #Solve for the difference between Skjelbreia Equation I-7 and I-10)
        '''
        Eqn I-7: H/h = L/h[2*A1 + 2pi^2*(A1)^3*f3]
        Eqn I-10: h/(gT^2/2pi) = h/L0 = h/L*tanh[1 + (2pi(A1))^2 * (cosh(8pi*h/L) + 8) / (8sinh(2pi*h/L)^4)]
        Where:
        A1 = a/L
        f3 = 3/16 * (8cosh(2pih/L)^6 + 1) / (sinh(2pih/L)^6)
        '''
        [A1, dL] = inputs

        L0 = self.g/2/np.pi*self.T**2
        f3 = 3/16*(8*np.cosh(2*np.pi*dL)**6+1)/np.sinh(2*np.pi*dL)**6

        I7 = self.H/self.h - 1/dL*(2*A1 + 2*np.pi**2*(A1)**3*f3)
        I10 = self.h/L0 - dL*np.tanh(2*np.pi*dL)*(1 + (2*np.pi*(A1))**2 * (np.cosh(8*np.pi*dL) + 8) / (8*np.sinh(2*np.pi*dL)**4))
        self.I7 = I7
        self.I10 = I10
        return np.abs(I7)+np.abs(I10)
    def solve_stokes_wave_length_a0(self):
        #Use airy deep water approximation as intial guess for fsolve
        L_deep = self.g/2/np.pi*self.T**2
        L_shallow = self.T*np.sqrt(self.g*self.H)
        #Numerically solve for the wave lenght based on a third order stokes wave (Skjelbreia Equation I-10)
        result = minimize(self._wave_length_difference, (self.H/2/L_deep, self.h/L_deep), method="Nelder-Mead")
        [A1, dL] = result.x
        L = self.h/dL
        a = A1*L
        return [L, a]
    
    def set_phase(self, phase):
        self.phase = phase

    def calculateWave(self, x, t):

        if type(x) is not np.ndarray and type(t) is np.ndarray:
            x = np.full_like(t, x)
        elif type(x) is np.ndarray and type(t) is not np.ndarray:
            t = np.full_like(x, t)
        elif type(x) is not np.ndarray and type(t) is not np.ndarray:
            x = np.array([x])
            t = np.array([t])

        theta = self.k*(x-self.c*t)
            
        heights = self.a0*np.cos(theta+self.phase)+self.a1*np.cos(2*(theta+self.phase))+self.a2*np.cos(3*(theta+self.phase))

        
        return np.array(heights)
         

    def _calc_rms_error(self, x ,t_array, measured_data):
        #Calculate the RMS error between the measured temporal signal and the modeled signal
        residuals = self.calculateWave(x,t_array)-measured_data
        RMSE = np.sqrt(np.mean(residuals**2))
        return RMSE


    def find_phase(self, temporal_df, data_x):
        t_array = temporal_df.index.total_seconds().to_numpy()
        measured_data = temporal_df.to_numpy()
        minimize_start_x = minimize(lambda x:self._calc_rms_error(x, t_array, measured_data), [0], bounds=[(-self.L/2, self.L/2)])
        start_x = minimize_start_x.x-data_x
        print(start_x)
        phase = self.k*start_x
        return phase

