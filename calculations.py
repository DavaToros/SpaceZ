import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# Константы
g0 = 9.8665
R_earth = 6371000.0
omega = 7.292115e-5
rho0 = 1.225
gamma = 1.4
R_gas = 287.0
lat = np.radians(45.6)
azimuth = np.radians(63.0)

# Параметры ракеты
m0 = 287000.0
D = 2.68
S = np.pi * (D/2)**2

# Программа тяги
def thrust(t):
    if t < 120:
        return 4040000.0
    elif t < 200:
        return 941000.0
    else:
        return 298000.0

def mass_flow(t):
    if t < 120:
        Isp = 250.0
    elif t < 200:
        Isp = 280.0
    else:
        Isp = 315.0
    return thrust(t) / (Isp * g0)

def pitch_angle(t):
    if t < 10:
        return np.radians(90.0)
    elif t < 120:
        return np.radians(90 - 0.5*(t-10))
    else:
        return np.radians(30 - 0.1*(t-120))

def atmosphere(h):
    if h < 11000:
        T = 288.15 - 0.0065*h
        rho = 1.225 * (288.15/T)**4.256
    elif h < 25000:
        rho = 0.364 * np.exp(-(h-11000)/6340.0)
        T = 216.65
    else:
        T = 216.65 + 0.001*(h-25000)
        rho = 0.041 * (216.65/T)**17.69
    a = np.sqrt(gamma * R_gas * T)
    return rho, a

def cx_coefficient(M):
    Cx0 = 0.8
    if M < 0.8:
        return Cx0
    elif M < 1.2:
        return Cx0 + 0.3*(M-0.8)**2
    else:
        return 0.9 - 0.1*(M-1.2)

def equations(t, Y):
    x, y, vx, vy, m = Y
    
    r = np.sqrt(x**2 + (R_earth + y)**2)
    alpha = np.arctan2(x, R_earth + y)
    v = np.sqrt(vx**2 + vy**2)
    phi = np.arctan2(vy, vx) if v > 0 else 0
    
    rho, a_sound = atmosphere(y)
    M = v / a_sound if a_sound > 0 else 0
    
    g = g0 * (R_earth / (R_earth + y))**2
    
    Cx = cx_coefficient(M)
    F_drag = 0.5 * rho * v**2 * Cx * S
    F_drag_x = F_drag * np.cos(phi)
    F_drag_y = F_drag * np.sin(phi)
    
    F_cent = m * omega**2 * R_earth * np.cos(lat)**2
    F_cent_x = F_cent * np.sin(azimuth)
    F_cent_y = F_cent * np.cos(lat)
    
    F_cor_x = 2 * m * omega * (vy * np.cos(lat))
    F_cor_y = -2 * m * omega * vx * np.cos(lat)
    
    theta = pitch_angle(t)
    F_thrust = thrust(t)
    F_thrust_x = F_thrust * np.cos(theta)
    F_thrust_y = F_thrust * np.sin(theta)
    
    dxdt = vx
    dydt = vy
    dvxdt = (F_thrust_x - F_drag_x - m*g*np.sin(alpha) + F_cent_x + F_cor_x) / m
    dvydt = (F_thrust_y - F_drag_y - m*g*np.cos(alpha) + F_cent_y + F_cor_y) / m
    dmdt = -mass_flow(t)
    
    return [dxdt, dydt, dvxdt, dvydt, dmdt]

# Начальные условия
v0_rot = omega * R_earth * np.cos(lat)
Y0 = [0.0, 0.0, v0_rot * np.sin(azimuth), 0.0, m0]

# Интегрирование до 200 секунд
t_span = (0, 200)
t_eval = np.linspace(0, 200, 1000)

sol = solve_ivp(equations, t_span, Y0, t_eval=t_eval, method='RK45', 
                rtol=1e-8, atol=1e-8)

# Извлечение результатов
x = sol.y[0]
y = sol.y[1]
vx = sol.y[2]
vy = sol.y[3]
m = sol.y[4]
t = sol.t

# Расчет полной высоты и скорости
h = np.sqrt(x**2 + (R_earth + y)**2) - R_earth
v = np.sqrt(vx**2 + vy**2)

# График 1: Высота от времени
plt.figure(figsize=(10, 6))
plt.plot(t, h, 'b-', linewidth=2)
plt.xlabel('Время, с')
plt.ylabel('Высота, м')
plt.title('Высота ракеты "Восход" от времени')
plt.grid(True)
plt.xlim(0, 200)
plt.show()

# График 2: Скорость от времени
plt.figure(figsize=(10, 6))
plt.plot(t, v, 'r-', linewidth=2)
plt.xlabel('Время, с')
plt.ylabel('Скорость, м/с')
plt.title('Скорость ракеты "Восход" от времени')
plt.grid(True)
plt.xlim(0, 200)
plt.show()