import krpc
import matplotlib.pyplot as plt
import time

conn = krpc.connect()
vessel = conn.space_center.active_vessel
ap = vessel.auto_pilot

target_altitude = 408000 
turn_start_alt = 10000
turn_end_alt = 45000

def setup_staging():
    vessel.control.throttle = 1.0
    vessel.control.sas = False
    vessel.control.rcs = False
    ap.reference_frame = vessel.surface_reference_frame
    ap.target_pitch_and_heading(90, 90)
    ap.engage()
    time.sleep(1)

def launch():
    times, speeds, altitudes, masses, accels = [], [], [], [], []
    start_time = conn.space_center.ut
    
    print('Запуск!')
    vessel.control.activate_next_stage()
    time.sleep(2)
    
    while vessel.flight().surface_altitude < 10:
        time.sleep(0.1)
    
    while vessel.flight().mean_altitude < turn_start_alt:
        t = conn.space_center.ut - start_time
        speed_alt = vessel.flight(vessel.orbit.body.reference_frame).speed
        altitude = vessel.flight().mean_altitude
        mass = vessel.mass
        acc = vessel.flight().g_force * 9.81

        times.append(t)
        speeds.append(speed_alt)
        altitudes.append(altitude)
        masses.append(mass)
        accels.append(acc)
        time.sleep(0.1)
        
    while vessel.flight().mean_altitude < turn_end_alt:
        alt = vessel.flight().mean_altitude
        frac = min((alt - turn_start_alt) / (turn_end_alt - turn_start_alt), 1.0)
        pitch = 90 * (1 - frac)
        ap.target_pitch_and_heading(pitch, 90)

        t = conn.space_center.ut - start_time
        speed_alt = vessel.flight(vessel.orbit.body.reference_frame).speed
        altitude = vessel.flight().mean_altitude
        mass = vessel.mass
        acc = vessel.flight().g_force * 9.81
        
        times.append(t)
        speeds.append(speed_alt)
        altitudes.append(altitude)
        masses.append(mass)
        accels.append(acc)

        check_staging_during_flight()
        time.sleep(0.1)
    
    ap.target_pitch_and_heading(0, 90)
    
    while vessel.orbit.apoapsis_altitude < target_altitude:
        t = conn.space_center.ut - start_time
        speed_alt = vessel.flight(vessel.orbit.body.reference_frame).speed
        altitude = vessel.flight().mean_altitude
        mass = vessel.mass
        acc = vessel.flight().g_force * 9.81

        times.append(t)
        speeds.append(speed_alt)
        altitudes.append(altitude)
        masses.append(mass)
        accels.append(acc)
        
        check_staging_during_flight()
        time.sleep(0.1)
    
    vessel.control.throttle = 0.0

    with open('flight_data.txt', 'w', encoding='utf-8') as f:
        for t, s, a, acc, m in zip(times, speeds, altitudes, accels, masses):
            f.write(f"{t:.2f},{s:.2f},{a:.2f},{acc:.2f},{m:.2f}\n")

def landing():
    altitude = conn.add_stream(getattr, vessel.flight(), 'surface_altitude')
    ap.target_pitch_and_heading(180, 90)
    time.sleep(2)
    
    while altitude() > 0:

        vessel.control.throttle = 0.5
        
        check_staging_during_flight()

        time.sleep(0.1)
        
        vessel.control.throttle = 0

def check_staging_during_flight():
    active_engines = [e for e in vessel.parts.engines if e.active]
    
    if not active_engines and vessel.flight().mean_altitude < target_altitude - 10000:
        vessel.control.activate_next_stage()
        time.sleep(1)
        return
        
    for engine in active_engines:
        if not engine.has_fuel:
            vessel.control.activate_next_stage()
            time.sleep(1)
            return
            
    resources = vessel.resources_in_decouple_stage(vessel.control.current_stage - 1)
    if resources and resources.amount('LiquidFuel') < 5.0:
        vessel.control.activate_next_stage()
        time.sleep(1)
            
setup_staging()
launch()
time.sleep(60)
landing()
ap.disengage()
