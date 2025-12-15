f = open('flight_data.txt', 'r', encoding='utf-8')

times_ksp, speeds_ksp, altitudes_ksp = [], [], []
for line in f:
    line = line.strip()
    if line:  
        t_ksp, s, a, acc, m = line.split(',') 
        times_ksp.append(float(t_ksp))
        speeds_ksp.append(float(s))
        altitudes_ksp.append(float(a))

f.close()

