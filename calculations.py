import numpy as np
import matplotlib.pyplot as plt

# Параметры
g = 9.8          
dt = 0.1         
total_time = 200 

# Начальные условия
t = 0
h = 0           
v = 0           
m = 298400      
Pn_1 = 4000000
Pn_2 = 900000
Sa = 4 # Площадь среза сопла

# Программа управления (упрощенная)
def get_thrust_and_angle(t, h=0):
    if t < 100:
        thrust = Pn_1 - Sa * p_a(h)
        angle = 90 - 0.4*t if t > 10 else 90  
    else:
        thrust = Pn_2 - Sa * p_a(h)  
        angle = 30       
    return thrust, max(angle, 0)  

# Давление атмосферы
def p_a(h):
    p0 = 101325 
    H = 7500     
    return p0 * np.exp(-h / H)

# Плотность воздуха
def get_density(h):
    return 1.225 * np.exp(-h / 7500)

# Основной цикл
times, heights, velocities = [], [], []

while t < total_time:
    # Получаем тягу и угол
    thrust, angle_deg = get_thrust_and_angle(t, h)
    angle = np.radians(angle_deg)
    
    # Разложение тяги на X и Y
    thrust_x = thrust * np.cos(angle)
    thrust_y = thrust * np.sin(angle)
    
    # Сопротивление воздуха 
    density = get_density(h)
    drag_coef = 0.6
    area = 2  
    drag = 0.5 * density * v**2 * drag_coef * area
    
    # Разложение сопротивления
    drag_x = drag * np.cos(angle) if v > 0 else 0
    drag_y = drag * np.sin(angle) if v > 0 else 0

    # Ускорение по осям
    a_x = (thrust_x - drag_x) / m
    a_y = (thrust_y - drag_y - m*g) / m
    
    # Общее ускорение
    a = np.sqrt(a_x**2 + a_y**2)
    
    # Обновление скорости и высоты
    v += a * dt
    h += v * dt * np.sin(angle) 
    
    if t < 100:
        m -= 1200 * dt 
    elif t < 200:
        m -= 300 * dt
    else:
        m -= 100 * dt  
    
    # Сохранение результатов
    times.append(t)
    heights.append(h * 1000)
    velocities.append(v)
    
    # Увеличение времени
    t += dt

# График 1: Высота
plt.figure(figsize=(10, 6))
plt.plot(times, np.array(heights)/1000, 'b-')
plt.xlabel('Время (с)')
plt.ylabel('Высота (м)')
plt.title('Высота ракеты')
plt.grid(True)
plt.xlim(0, 200)

# График 2: Скорость
plt.figure(figsize=(10, 6))
plt.plot(times, velocities, 'r-')
plt.xlabel('Время (с)')
plt.ylabel('Скорость (м/с)')
plt.title('Скорость ракеты')
plt.grid(True)
plt.xlim(0, 200)

plt.tight_layout()
plt.show()
