import numpy as np
from scipy.special import comb, factorial
from numpy.polynomial import Polynomial
import numpy.polynomial.polynomial as poly
from matplotlib import pyplot as plt

class Wave:
    def __init__(self, k, omega):
        self.k = k
        self.omega = omega
        self.c = self.omega/self.k
        self.basePolynomial = Polynomial(self.generateBaseCoefficents())

    def generateBaseCoefficents(self):
        '''
        Docstring for generateBaseCoefficents

        Generate coefficents for a polynomial to solve for a "x" 
        given an "a" based on a of a Talor Series of sin(theta) centered at theta=pi
        
        :param self: Description
        '''

        ORDER = 13

        coeffs = np.zeros((ORDER+1,))

        odd_power_numers = np.arange(1,ORDER+1,2)

        negative_term = (-1)**((odd_power_numers-1)/2) #Alternating 1 and -1
        k_term = self.k**(odd_power_numers-1) #k raised to the n-1 power where n is power number


        coeffs[1::2] = negative_term*k_term/factorial(odd_power_numers)
        

        return coeffs

    def solveSingleA(self, x, input_poly):
        '''
        Docstring for solveSingleA
        
        :param x: single location to solve the sea surface elevation at
        :param coeffs: coefficents of a polynomial system (generated with generateCoefficents)
        '''

        wholeComponent = 2*np.pi*(x//(2*np.pi)) #Portion of x that is a whole multiple of 2pi
        partialComponent = x%(2*np.pi) #Portion of x that is not a whole multiple of 2pi
        
        coeff_correction = np.zeros_like(input_poly.coef)
        coeff_correction[0] = -x
        #Add one to the 1st order coefficent (for the +a term)
        coeff_correction[1] = 1

        roots = poly.polyroots((input_poly+coeff_correction).coef)
        real_root = roots[np.isreal(roots)][0]
        return real_root


    def solveSpacialWave(self, x, t):
        '''
        Docstring for solveSpacialWave
        
        :param x: arraylike of locations to calculate the sea surface elevation at
        :param t: time to solve the wave at
        '''

        ## Let U=kct-pi
        U = self.k*self.c*t-np.pi
        
        #working_polynomial = self.basePolynomial.convert(domain=[-1+U, 1+U])
        working_polynomial = self.basePolynomial

        a_mapping = np.full_like(x,np.nan)

        for i, position in enumerate(x):
            a_mapping[i] = self.solveSingleA(position,working_polynomial)

        return -np.cos(self.k*(a_mapping+self.c*t))
        

        




testWave = Wave(1,1)
elevation = testWave.solveSpacialWave(xvals:=np.linspace(0,4,300),0)
plt.plot(xvals, elevation)
plt.xlabel("Position (m)")
plt.ylabel("Sea Surface Elevation (m)")
plt.show()