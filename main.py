import streamlit as st
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, time, date
from simulation.spacecraft import VEHICLES
from simulation.optimization import generate_trajectories, get_moon_state

# --- [1] CONFIG & DESIGN ---
st.set_page_config(page_title="CELESTIUM", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
    
    * { font-family: 'Orbitron', sans-serif !important; }
    
    .stApp { background-color: #000000; color: #aaddff; }
    
    /* 프레임 스타일 */
    .sc-frame {
        border: 1px solid #004488; 
        background: rgba(5, 10, 20, 0.9);
        padding: 15px; margin-bottom: 15px;
        box-shadow: 0 0 10px rgba(0, 100, 255, 0.1);
        border-radius: 4px;
    }
    .sc-header {
        color: #00ffff; font-size: 1.0em; border-bottom: 1px solid #004488; 
        margin-bottom: 15px; padding-bottom: 5px; letter-spacing: 2px;
    }
    
    .hl-val { color: #ffcc00; } .hl-good { color: #33ff33; } .hl-bad { color: #ff3333; }
    
    .stButton>button { 
        border: 1px solid #00ffff; color: #00ffff; background: rgba(0, 50, 100, 0.5); 
        width: 100%; height: 45px; font-weight: bold; transition: 0.2s; 
    }
    .stButton>button:hover { background: #00ffff; color: #000; }
    
    /* 이미지 컨테이너 */
    .rocket-img img {
        border: 1px solid #333; border-radius: 5px;
        max-height: 200px; /* 이미지 높이 제한 */
        object-fit: cover;
    }
    </style>
""", unsafe_allow_html=True)

if 'page' not in st.session_state: st.session_state.page = 'start'
if 'sim_data' not in st.session_state: st.session_state.sim_data = {}
if 'vehicle_name' not in st.session_state: st.session_state.vehicle_name = list(VEHICLES.keys())[0]

# --- [2] START SCREEN ---
if st.session_state.page == 'start':
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: #00ffff;'>CELESTIUM</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; letter-spacing: 3px; color: #88ccff;'>ORBITAL SIMULATOR</p>", unsafe_allow_html=True)
        st.markdown("---")
        col_btn1, col_btn2, col_btn3 = st.columns([1,2,1])
        with col_btn2:
            if st.button("INITIALIZE SYSTEMS"):
                st.session_state.page = 'lobby'
                st.rerun()

# --- [3] LOBBY ---
elif st.session_state.page == 'lobby':
    st.title("MISSION CONFIGURATION")
    
    c_left, c_right = st.columns([1, 1.5])
    
    with c_left:
        st.markdown("<div class='sc-frame'><div class='sc-header'>TEMPORAL TARGETING</div>", unsafe_allow_html=True)
        d_in = st.date_input("Date", date.today())
        t_in = st.time_input("Time", time(12,0))
        ld = datetime.combine(d_in, t_in)
        
        ms = get_moon_state(ld)
        dist, dec = ms["dist"], ms["dec"]
        status = "OPTIMAL" if abs(dec) < 10 else "CRITICAL"
        color = "hl-good" if abs(dec) < 10 else "hl-bad"
        
        st.markdown(f"""
        <b>LUNAR DISTANCE:</b> {dist:,.0f} km<br>
        <b>DECLINATION:</b> {dec:.1f}°<br>
        <hr style='margin: 10px 0; border-color: #333;'>
        <div style='display: flex; align-items: center; justify-content: space-between;'>
            <span>WINDOW STATUS:</span>
            <span class='{color}' style='font-size: 1.2em; border: 1px solid; padding: 2px 10px;'>{status}</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c_right:
        st.markdown("<div class='sc-frame'><div class='sc-header'>VEHICLE SELECTION</div>", unsafe_allow_html=True)
        v_name = st.selectbox("Select Chassis", list(VEHICLES.keys()))
        st.session_state.vehicle_name = v_name
        veh = VEHICLES[v_name]
        
        # [요청 반영] 사진 작게(1) : 설명(2) 비율
        rc1, rc2 = st.columns([1, 2])
        with rc1:
            st.markdown(f"<div class='rocket-img'>", unsafe_allow_html=True)
            st.image(veh.img_url, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with rc2:
            st.markdown(veh.get_description(), unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("COMPUTE TRAJECTORIES"):
            st.session_state.sim_data = generate_trajectories(ld, veh)
            st.session_state.page = 'simulation'
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- [4] SIMULATION ---
elif st.session_state.page == 'simulation':
    st.title("TRAJECTORY ANALYSIS")
    
    if st.button("<< RETURN TO CONFIG"):
        st.session_state.page = 'lobby'
        st.rerun()
        
    data = st.session_state.sim_data
    veh = VEHICLES[st.session_state.vehicle_name]
    
    c1, c2 = st.columns([1, 2.5])
    
    with c1:
        # 데이터 탭
        st.markdown("<div class='sc-frame'><div class='sc-header'>TELEMETRY</div>", unsafe_allow_html=True)
        # 이름 변경: FAST, BAL, OPT, STD, RET
        tabs = st.tabs(["FAST", "BAL", "OPT", "STD", "RET"])
        keys = ["fast", "bal", "opt", "ho", "fr"]
        
        for i, k in enumerate(keys):
            with tabs[i]:
                d = data[k]
                st.markdown(f"<h4 style='color:{d['color']}'>{d['name']}</h4>", unsafe_allow_html=True)
                st.write(f"ΔV: {d['delta_v']} m/s")
                st.write(f"Time: {d['time']}")
                st.caption(d['desc'])
                
                fuel = float(d['fuel_mass'])
                cap = float(veh.fuel_capacity)
                pct = (fuel/cap)*100
                st.progress(min(pct/100, 1.0), text=f"Fuel: {pct:.1f}%")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 가시성 체크박스 (AI 제거된 이름)
        st.markdown("<div class='sc-frame'><div class='sc-header'>LAYER CONTROL</div>", unsafe_allow_html=True)
        v_fast = st.checkbox("High Speed", True)
        v_bal = st.checkbox("Balanced", True)
        v_opt = st.checkbox("Fuel Optimized", False)
        v_ho = st.checkbox("Standard Hohmann", False)
        v_fr = st.checkbox("Free Return", False)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='sc-frame'><div class='sc-header'>TACTICAL MAP (1:1 SCALE)</div>", unsafe_allow_html=True)
        fig = go.Figure()
        
        # 1. Earth & Moon (심플한 구체)
        def sphere(r, c, color, name, op=0.8):
            u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
            x = c[0] + r*np.cos(u)*np.sin(v)
            y = c[1] + r*np.sin(u)*np.sin(v)
            z = c[2] + r*np.cos(v)
            return go.Surface(x=x,y=y,z=z, colorscale=[[0, color], [1, color]], showscale=False, opacity=op, name=name, hoverinfo='name')
            
        fig.add_trace(sphere(6371, [0,0,0], 'blue', 'Earth'))
        moon_pos = data['fast']['target_pos']
        fig.add_trace(sphere(1737, moon_pos, 'gray', 'Moon'))

        # 2. Trajectories
        def plot(key, vis):
            if vis:
                d = data[key]
                fig.add_trace(go.Scatter3d(x=d['x'], y=d['y'], z=d['z'], mode='lines', line=dict(color=d['color'], width=3), name=d['name']))
        
        plot('fast', v_fast)
        plot('bal', v_bal)
        plot('opt', v_opt)
        plot('ho', v_ho)
        plot('fr', v_fr)
        
        # 별 배경 제거 (순수 블랙)
        fig.update_layout(
            scene=dict(
                xaxis=dict(visible=False, backgroundcolor="#050505"),
                yaxis=dict(visible=False, backgroundcolor="#050505"),
                zaxis=dict(visible=False, backgroundcolor="#050505"),
                bgcolor="#050505",
                aspectmode='data', 
                camera=dict(eye=dict(x=0.5, y=0.5, z=1.5))
            ),
            paper_bgcolor="#050505", margin=dict(l=0,r=0,t=0,b=0), height=700,
            showlegend=True, legend=dict(x=0, y=1, font=dict(color='white'), bgcolor="rgba(0,0,0,0.5)")
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
