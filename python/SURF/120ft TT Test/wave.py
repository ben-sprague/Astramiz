import numpy as np
import torch

from scipy.interpolate import BSpline

if torch.backends.mps.is_available():
    device = torch.device("mps")
    print("MPS device found.")
else:
    device = torch.device("cpu")
    print("MPS device not found.")

def solve_wave(u_int, ut_int, bc_i, bc_e, target_distance, test_duration, dx,dt, c, device=device):
    '''
    Docstring for solve_wave

    Solve the wave equation from Target(Ice) and SONAR sea surface elevation data
    using a finite difference method running on the GPU

    Based on: https://hplgit.github.io/num-methods-for-PDEs/doc/pub/wave/pdf/wave-4print-A4-2up.pdf
    
    :param u_int: Intial sea surface elevation profile
    :param ut_int: Intial sea surface velocity profile (ie. du/dt)
    :param bc_i: Starting (x=0) boundary condition. Target sea surface elevation data
    :param bc_e: Starting (x=target dist) boundary condition. SONAR sea surface elevation data
    :param target_distance: distance from target to SONAR
    :param test_duration: time to calculate sea surface elevation profile at (measured in seconds from intial condition)
    :param dx: x resolution
    :param dt: t resolution
    :param c: wave phase speed
    :param device: PyTorch device to run solver on (ideally a GPU)

    NOTE: the Courant number (c*dt/dx) must be less than one for the solver to be stable
    '''
    x_array = np.arange(0,target_distance, dx, dtype=np.float32)
    t_array = np.arange(0,test_duration, dt, dtype=np.float32)
    x = torch.tensor(x_array, device=device)
    t = torch.tensor(t_array, device=device)

    Nx = x_array.size-1
    Nt = t_array.size-1

    C2 = (c*dt/dx)**2

    u = torch.zeros((Nx+1,), device=device)
    u_1 = torch.zeros((Nx+1,), device=device)
    u_2 = torch.zeros((Nx+1,), device=device)

    bc_int_tensor = torch.tensor(bc_i.astype(np.float32), device=device)
    bc_end_tensor = torch.tensor(bc_e.astype(np.float32), device=device)

    #Input IV into u matrix
    u[:] = torch.tensor(u_int.astype(np.float32), device=device)

    #Load initial du/dt into tenor
    ut_int_tensor = torch.tensor(ut_int.astype(np.float32), device=device)

    #Calculate u_1 and u_2 for the intial condition using a first order Taylor series
    u_1[:] = u[:]+ut_int_tensor*(-dt)
    u_2[:] = u[:]+ut_int_tensor*(-2*dt)
    
    #Set boundary conditions
    u_1[0] = bc_int_tensor[0]
    u_1[Nx] = bc_end_tensor[0]

    for n in range(1,Nt):
        #Calculate u for the rest of the time step
        u[1:-1] = C2*(u_1[2:]-2*u_1[1:-1]+u_1[:-2])+2*u_1[1:-1]-u_2[1:-1]

        #Boundary condition
        u[0] = bc_int_tensor[n]
        u[-1] = bc_end_tensor[n]
        # plt.close()
        # plt.plot(u[:,n])
        # plt.show()

        u, u_1, u_2 = u_2, u, u_1

    #Return u_2 because u was shifted into it at the end of the for loop
    return u_2.cpu().numpy()