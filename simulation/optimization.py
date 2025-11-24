import numpy as np
from astropy.time import Time
from astropy.coordinates import get_body
from astropy import units as u

# 물리 상수
G0 = 9.80665

def calculate_rotation_matrix(target_vec):
    u_vec = target_vec / np.linalg.norm(target_vec)
    x_axis = np.array([1, 0, 0])
    if np.allclose(u_vec, x_axis): return np.eye(3)
    v = np.cross(x_axis, u_vec)
    s = np.linalg.norm(v)
    c = np.dot(x_axis, u_vec)
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    if s == 0: return np.eye(3)
    return np.eye(3) + vx + np.dot(vx, vx) * ((1 - c) / (s**2))

def get_moon_state(date_time):
    try:
        t = Time(date_time)
        moon = get_body("moon", t)
        pos_km = moon.cartesian.xyz.to(u.km).value
        dist = np.linalg.norm(pos_km)
        dec = moon.dec.degree
        return {"vec": pos_km, "dist": dist, "dec": dec}
    except:
        return {"vec": np.array([384400.0, 0, 0]), "dist": 384400.0, "dec": 0.0}

def calculate_fuel(dry_mass, delta_v, isp):
    if delta_v <= 0: return 0
    return dry_mass * (np.exp(delta_v / (isp * G0)) - 1)

def generate_path_points(target_pos, mode, dist):
    points = 100
    t = np.linspace(0, 1, points)
    x_local = dist * t
    y_local = np.zeros_like(t)
    z_local = np.zeros_like(t)
    
    if mode == "fast": y_local = (dist * 0.05) * np.sin(np.pi * t)
    elif mode == "balanced": y_local = (dist * 0.2) * np.sin(np.pi * t)
    elif mode == "fuel_opt": y_local = (dist * 0.35) * np.sin(np.pi * t)
    elif mode == "hohmann": y_local = (dist * 0.4) * np.sin(np.pi * t)
    elif mode == "free_return":
        t_fr = np.linspace(0, 1.2, points)
        scale = dist * 0.15
        x_local = dist * t_fr
        y_local = scale * np.sin(2 * np.pi * t_fr) * t_fr
        z_local = (scale * 0.5) * np.sin(1 * np.pi * t_fr)
        x_local = x_local * (dist / x_local[np.argmin(np.abs(t_fr - 1.0))])

    R = calculate_rotation_matrix(target_pos)
    coords = np.vstack((x_local, y_local, z_local)).T
    rotated_coords = coords @ R.T

    if mode != "free_return": rotated_coords[-1] = target_pos
    return rotated_coords[:,0], rotated_coords[:,1], rotated_coords[:,2]

def solve_trajectory(launch_date, vehicle, mode):
    moon = get_moon_state(launch_date)
    r_target = moon["vec"]
    dist = moon["dist"]
    dec = moon["dec"]
    
    dist_f = dist / 384400.0
    penalty_dv = 0
    if abs(dec) > 10:
        penalty_dv = 7800 * 2 * np.sin(np.deg2rad((abs(dec)-10)/2)) * 0.5
    
    # 이름에서 AI 제거 및 직관적 변경
    if mode == "fast":
        base_dv, time_h, name, color = 4100*dist_f, 35.0*dist_f, "High Speed Injection", "#FF00FF"
        desc = "Hyperbolic Trajectory (Fastest)"
    elif mode == "balanced":
        base_dv, time_h, name, color = 3250*dist_f, 55.0*dist_f, "Balanced Profile", "#FFA500"
        desc = "Optimal Cost-Benefit"
    elif mode == "fuel_opt":
        base_dv, time_h, name, color = 3120*dist_f, 75.0*dist_f, "Min-Fuel Optimized", "#3388FF"
        desc = "Numerical Minimum Energy"
    elif mode == "hohmann":
        base_dv, time_h, name, color = 3150*dist_f, 72.0*dist_f, "Standard Hohmann", "#00FF00"
        desc = "Theoretical Reference"
    elif mode == "free_return":
        base_dv, time_h, name, color = 3300*dist_f, 144.0, "Free Return", "#00FFFF"
        desc = "Safety Loop"
        
    total_dv = base_dv + penalty_dv
    fuel = calculate_fuel(vehicle.mass, total_dv, vehicle.isp)
    x, y, z = generate_path_points(r_target, mode, dist)
    
    return {
        "name": name, "x": x, "y": y, "z": z, "color": color,
        "delta_v": f"{total_dv:.1f}", "fuel_mass": f"{fuel:.0f}",
        "time": f"{time_h:.1f} h", "desc": desc, "target_pos": r_target, "penalty": penalty_dv
    }

def generate_trajectories(launch_date, vehicle):
    return {
        "fast": solve_trajectory(launch_date, vehicle, "fast"),
        "bal": solve_trajectory(launch_date, vehicle, "balanced"),
        "opt": solve_trajectory(launch_date, vehicle, "fuel_opt"),
        "ho": solve_trajectory(launch_date, vehicle, "hohmann"),
        "fr": solve_trajectory(launch_date, vehicle, "free_return")
    }
