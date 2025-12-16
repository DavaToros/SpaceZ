import numpy as np
import matplotlib.pyplot as plt
from ksp_module import times_ksp, speeds_ksp, altitudes_ksp

# параметры
G = 6.7 * 10**(-11)    
M = 6 * 10**24
r = 6.4 * 10**6    
dt = 0.1  
total_time = 225
p0 = 101325 
H = 7500  
drag_coef = 0.6
area = 4  

# начальные условия
t = 0
h = 0   
x = 0        
v = 0          
M1 = 298400  
M2 = 24500
k = (M1 - M2) / total_time
m = M1


Pn_1 = 4000000
Pn_2 = 900000
Sa = 0.04 

# массовый расход
def get_m(t):
    return M1 - k*t

# давление атмосферы
def p_a(h):       
    return p0 * np.exp(-h / H)

# плотность воздуха
def get_density(h):
    return 1.225 * np.exp(-h / H)

# считаем как меняется g, от высоты
def get_g(h):
    return G*M/(r + h)**2

# программа управления
def get_thrust_and_angle(t, h=0):
    if t < 100:
        thrust = Pn_1 - Sa * p_a(h)
        angle = 90 - 0.4*t if t > 10 else 90  
    else:
        thrust = Pn_2 - Sa * p_a(h)  
        angle = 30  
    return thrust, max(angle, 0)  


times, heights, velocities, accels = [], [], [], []

while t < total_time:
    # получаем тягу и угол
    thrust, angle_deg = get_thrust_and_angle(t, h)
    angle = np.radians(angle_deg)
    
    # разложение тяги на X и Y
    thrust_x = thrust * np.cos(angle)
    thrust_y = thrust * np.sin(angle)
    
    # сопротивление воздуха 
    density = get_density(h)
    drag = 0.5 * density * v**2 * drag_coef * area
    
    # разложение сопротивления
    drag_x = drag * np.cos(angle) if v > 0 else 0
    drag_y = drag * np.sin(angle) if v > 0 else 0

    # ускорение по осям
    a_x = (thrust_x - drag_x) / m
    a_y = (thrust_y - drag_y - m*get_g(h)) / m
    
    # общее ускорение
    a = np.sqrt(a_x**2 + a_y**2)
    
    # обновление скорости и высоты
    v += a * dt
    h += v * dt * np.sin(angle) 

    times.append(t)
    heights.append(h)
    velocities.append(v)
    accels.append(a)
    t += dt

    m = get_m(t)

# График 1 Высота
plt.figure(figsize=(10, 6))
plt.plot(times, heights, label='МАТ МОДЕЛЬ')
plt.plot(times_ksp, altitudes_ksp, label='ДАННЫЕ KSP')
plt.legend()
plt.xlabel('Время (с)')
plt.ylabel('Высота (м)')
plt.title('Высота ракеты')
plt.grid(True)
# График 2 Скорость
plt.figure(figsize=(10, 6))
plt.plot(times, velocities, label='МАТ МОДЕЛЬ')
plt.plot(times_ksp, speeds_ksp, label='ДАННЫЕ KSP')
plt.legend()
plt.xlabel('Время (с)')
plt.ylabel('Скорость (м/с)')
plt.title('Скорость ракеты')
plt.grid(True)



plt.tight_layout()
plt.show()
