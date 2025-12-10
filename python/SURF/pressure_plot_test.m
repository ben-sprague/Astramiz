t = 0;
x = [0:0.1:100];

%Ocean wave
omega_sea = 2*pi/10;
a_sea = 0.5;
k_sea = 2*pi/100;
z = -0.3;

eta = a_sea*cos(k_sea.*x - omega_sea*t);
ux = omega_sea*a_sea*exp(k_sea*z)*cos(k_sea.*x - omega_sea*t);
uz = omega_sea*a_sea*exp(k_sea*z)*sin(k_sea.*x - omega_sea*t);

plot(x,ux+,x,uz)


%Sound wave
omega_sound = 2*pi*750e3;
c = 1500; %m/s
k_sound = 2*pi/(c/750e3);



