from scipy.optimize import minimize_scalar
from numpy import isclose

class LineOfSight:
    def __init__(self, sea_obj, x_camera, x_object, t):
        self.sea = sea_obj
        self.time = t
        self.x_camera = x_camera
        self.z_camera = sea_obj.height(self.x_camera,self.time)[0]
        self.x_object = x_object
        self.z_object = sea_obj.height(self.x_object,self.time)[0]

        #Calculate line properties
        self.slope = (self.z_camera - self.z_object)/(self.x_camera - self.x_object)
    
    def line_value(self, x):
        return self.slope*(x-self.x_camera)+self.z_camera

    def calc_height_difference(self, x):
        return self.line_value(x) - self.sea.height(x,self.time)
    
    def calc_height_difference_dervative(self, x):
        return self.slope - self.sea.height_dervative_x(x,self.time)
    
    def calc_height_difference_second_dervative(self, x):
        return -self.sea.height_second_dervative_x(x,self.time)

    def solve_intersection(self):
        x_midpoint = (self.x_camera+self.x_object)/2
        mini_result = minimize_scalar(self.calc_height_difference, bounds = (self.x_camera, self.x_object))
        absolutetol = 1e-3
        if isclose(mini_result.x, self.x_camera, atol = absolutetol) or isclose(mini_result.x, self.x_object, atol = absolutetol):
            return None
        else:
            return mini_result.x
