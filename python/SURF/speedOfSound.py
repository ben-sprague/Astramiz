def speed_of_sound(s,t,d):
    #Calculate the speed of sound from CTD cast data using Medwin 1975

    c = 1449.2 + 4.6 * t - 0.055*(t**2) + 0.00029*(t**3) + (1.34 -0.01*t)*(s-35) + 0.016*d

    return c

