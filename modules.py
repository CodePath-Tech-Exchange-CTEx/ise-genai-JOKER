#############################################################################
# modules.py
#
# This file contains modules that may be used throughout the app.
#
# You will write these in Unit 2. Do not change the names or inputs of any
# function other than the example.
#############################################################################

import random
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime

def display_activity_summary(workouts_list):
    """Displays the total metrics of the user's workout (number of workouts, total time spent, total calories burned)
    
    Arg:
        workouts_list: list of workouts.
    """
    
    total_workouts = str(len(workouts_list)) + ' sessions' if len(workouts_list) > 1 else str(len(workouts_list)) + ' session'
    total_minutes = sum(w.get('duration', 0) for w in workouts_list)
    time_val = f"{total_minutes // 60}h {total_minutes % 60}m" if total_minutes > 60 else f"{total_minutes}m"
    total_calories = sum(w.get('calories_burned', 0) for w in workouts_list)
    calorie_goal = 600

    # calculate ring completion (0 to 100)
    percent = min(int((total_calories / calorie_goal) * 100), 100)
    
    # calculate SVG stroke-dasharray (Circumference is 2 * pi * r)
    # Scaled up: for r=65, circumference is ~408
    offset = 408 - (408 * percent / 100)

    html_content = f"""
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,wght@0,400;0,500;0,700;1,400&display=swap" rel="stylesheet">
    <style>
      .activity-card {{
        background: #0d0d0d;
        border-radius: 16px;
        padding: 50px 60px;
        margin: 20px auto;
        font-family: 'DM Sans', sans-serif;
        max-width: 680px; /* Matched to AI Advice card */
        display: flex;
        align-items: center;
        gap: 60px; /* Increased gap for larger card */
        box-shadow: 
          0 0 0 1px rgba(255,255,255,0.06), 
          0 24px 60px rgba(0,0,0,0.6);
        animation: adviceFadeUp 0.5s cubic-bezier(.22,.68,0,1.2) both;
      }}
      .ring-container {{
        position: relative;
        width: 160px; /* Scaled up from 120px */
        height: 160px;
      }}
      .ring-svg {{
        transform: rotate(-90deg);
      }}
      .ring-bg {{
        fill: none;
        stroke: rgba(255,255,255,0.05);
        stroke-width: 14; /* Thicker ring */
      }}
      .ring-progress {{
        fill: none;
        stroke: url(#activity-gradient);
        stroke-width: 14; /* Thicker ring */
        stroke-linecap: round;
        transition: stroke-dashoffset 1s cubic-bezier(0.4, 0.0, 0.2, 1);
      }}
      .percent-text {{
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -45%);
        font-family: 'Bebas Neue', sans-serif;
        font-size: 2.4em; /* Scaled up */
        color: #ffffff;
        letter-spacing: 0.05em;
      }}
      .info-container {{
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 20px; /* More breathing room between stats */
      }}
      .stat-label {{
        color: #fa114f;
        font-size: 0.8em; /* Scaled up */
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.14em;
      }}
      .stat-value {{
        font-family: 'Bebas Neue', sans-serif;
        font-size: 2.4em; /* Scaled up */
        color: #ffffff;
        margin-top: 6px;
        line-height: 1;
        letter-spacing: 0.05em;
      }}
      .stat-sub {{
        font-family: 'DM Sans', sans-serif;
        font-size: 0.4em;
        color: #484848;
        letter-spacing: 0.02em;
      }}
      
      /* Mobile responsiveness for the larger card */
      @media (max-width: 600px) {{
        .activity-card {{
          flex-direction: column;
          padding: 40px 30px;
          gap: 40px;
          text-align: center;
        }}
      }}
    </style>

    <div class="activity-card">
      <div class="ring-container">
        <svg class="ring-svg" width="160" height="160">
          <defs>
            <linearGradient id="activity-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#fa114f" />
              <stop offset="100%" stop-color="#ff6b35" />
            </linearGradient>
          </defs>
          <circle class="ring-bg" cx="80" cy="80" r="65"></circle>
          <circle class="ring-progress" cx="80" cy="80" r="65" 
                  style="stroke-dasharray: 408; stroke-dashoffset: {offset};"></circle>
        </svg>
        <div class="percent-text">{percent}%</div>
      </div>
      <div class="info-container">
        <div>
            <div class="stat-label">Total Workouts</div>
            <div class="stat-value">{total_workouts}</div>
        </div>
        <div>
            <div class="stat-label">Time Spent</div>
            <div class="stat-value">{time_val}</div>
        </div>
        <div>
            <div class="stat-label">Move Goal</div>
            <div class="stat-value">{total_calories} <span class="stat-sub">/ {calorie_goal} KCAL</span></div>
        </div>
      </div>
    </div>
    """
    
    st.markdown(html_content, unsafe_allow_html=True)
