import numpy as np

class SeaSurface:
    def __init__(self,an,a0,f1,phase):
        self.a0 = a0
        self.an = an
        self.fundi_frequency = f1
        self.g = 9.81
        self.phase = phase

    def height(self,x,t):
        #Calculate the sea surface height at a given position and time
        sea_surface_height = self.a0
        for component in self.solve_height(x,t):
            sea_surface_height += component
            
        return sea_surface_height.reshape(-1,)
            
    def height_dervative_x(self, x:np.array,t:np.array):
        #Calculate the dervative of the sea surface height with respect to x at a given position and time
        der_x = 0
        for component in self.solve_height_dir_x(x,t):
            der_x += component

        return der_x.reshape(-1,)
    
    def height_second_dervative_x(self, x:np.array,t:np.array):
        #Calculate the dervative of the sea surface height with respect to x at a given position and time
        der_x = 0
        for component in self.solve_height_second_dir_x(x,t):
            der_x += component

        return der_x.reshape(-1,)

    def solve_height(self,x,t):
        q = 1 #harmonic number 
        while q in range (len(self.an)+1):
            omega = 2*np.pi*q*self.fundi_frequency
            #Assume deep water and apply dispersion relationship
            k = self.g*omega**2

            yield self.an[q-1]*np.cos(x*k-omega*t+self.phase[q-1])
            q += 1
    
    def solve_height_dir_x(self,x,t):
        q = 1 #harmonic number 
        while q in range (len(self.an)+1):
            omega = 2*np.pi*q*self.fundi_frequency
            #Assume deep water and apply dispersion relationship
            k = self.g*omega**2

            yield -self.an[q-1]*k*np.sin(x*k-omega*t+self.phase[q-1])
            q += 1
    
    def solve_height_second_dir_x(self,x,t):
        q = 1 #harmonic number 
        while q in range (len(self.an)+1):
            omega = 2*np.pi*q*self.fundi_frequency
            #Assume deep water and apply dispersion relationship
            k = self.g*omega**2

            yield -self.an[q-1]*(k**2)*np.cos(x*k-omega*t+self.phase[q-1])
            q += 1

        
