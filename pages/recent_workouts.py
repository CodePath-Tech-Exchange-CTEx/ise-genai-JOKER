import streamlit as st
from datetime import datetime

def display_recent_workouts(workouts_list):
    """Displays a list of recent workouts as styled HTML cards instead of a raw dataframe."""
    if not workouts_list or len(workouts_list) == 0:
        st.info("No recent workouts found. Start your fitness journey today!")
        return
    
    st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,wght@0,400;0,500;0,700;1,400&display=swap" rel="stylesheet">
    <style>
    #   .recent-header {
    #     font-family: 'Bebas Neue', sans-serif;
    #     font-size: 2.2em;
    #     letter-spacing: 0.06em;
    #     color: #ffffff;
    #     margin: 0 0 14px 0;
    #     line-height: 1.05;
    #   }
    #   .recent-divider {
    #     width: 44px;
    #     height: 3px;
    #     background: linear-gradient(90deg, #fa114f, #ff6b35);
    #     border-radius: 2px;
    #     margin-bottom: 20px;
    #   }
      .workout-card {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 20px 25px;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: transform 0.2s ease, border-color 0.2s ease;
      }
      .workout-card:hover {
        transform: translateY(-2px);
        border-color: rgba(250, 17, 79, 0.4);
        background: rgba(255,255,255,0.04);
      }
      .workout-date {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 1.6em;
        color: #ffffff;
        letter-spacing: 0.05em;
        line-height: 1;
      }
      .workout-time {
        font-family: 'DM Sans', sans-serif;
        color: #bcbcbc;
        font-size: 0.85em;
        margin-top: 6px;
      }
      .workout-stats {
        display: flex;
        gap: 30px;
      }
      .stat-item {
        text-align: right;
      }
      .stat-val {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 1.6em;
        color: #ffffff;
        letter-spacing: 0.05em;
        line-height: 1;
      }
      .stat-val span {
        color: #fa114f;
      }
      .stat-lbl {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.7em;
        color: #657786;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 4px;
        font-weight: bold;
      }
    </style>

    """, unsafe_allow_html=True)
    
    for w in workouts_list:
        # Parse start and end timestamps safely
        start_str = w.get('start_timestamp', '')
        end_str = w.get('end_timestamp', '')
        
        display_date = "Unknown Date"
        time_range = ""
        duration_mins = w.get('duration', 0)

        try:
            if start_str:
                start_dt = datetime.fromisoformat(str(start_str).replace('Z', '+00:00'))
                display_date = start_dt.strftime("%b %d, %Y").upper()
                time_range = start_dt.strftime("%I:%M %p")
                
                # If we don't have a hardcoded duration, try to calculate it
                if not duration_mins and end_str:
                    end_dt = datetime.fromisoformat(str(end_str).replace('Z', '+00:00'))
                    duration_mins = int((end_dt - start_dt).total_seconds() / 60)
                    time_range += f" - {end_dt.strftime('%I:%M %p')}"
        except ValueError:
            display_date = str(start_str).split()[0] if start_str else "Unknown"

        steps = w.get('steps', 0)
        distance = w.get('distance', 0)
        calories = w.get('calories_burned', 0)

        # Build the stats dynamically based on what data exists
        stats_html = ""
        if duration_mins:
            stats_html += f'<div class="stat-item"><div class="stat-val"><span>{duration_mins}</span></div><div class="stat-lbl">Mins</div></div>'
        if distance:
            stats_html += f'<div class="stat-item"><div class="stat-val"><span>{distance}</span></div><div class="stat-lbl">Distance</div></div>'
        if steps:
            stats_html += f'<div class="stat-item"><div class="stat-val"><span>{steps:,}</span></div><div class="stat-lbl">Steps</div></div>'
        if calories:
            stats_html += f'<div class="stat-item"><div class="stat-val"><span>{calories}</span></div><div class="stat-lbl">Cals</div></div>'

        card_html = f"""
        <div class="workout-card">
            <div>
                <div class="workout-date">{display_date}</div>
                <div class="workout-time">&#128336; {time_range}</div>
            </div>
            <div class="workout-stats">
                {stats_html}
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

def display_recent_workouts_with_add_form(user_id, workouts_list):
    """Displays an 'Add Workout' form followed by the recent workouts list.
    
    Args:
        user_id: The current user's ID for creating new workouts.
        workouts_list: List of workout dictionaries to display.
    """
    from data_fetcher import create_user_workout
    
    display_recent_workouts(workouts_list)
    st.markdown("<h2 style='font-size: 2.2em; margin-bottom: 10px;'>Add New Workout</h2>", unsafe_allow_html=True)
    st.caption('Log a new workout to track your progress.')
    
    with st.expander("➕ Add Workout", expanded=False):
        with st.form("add_workout_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                distance = st.number_input(
                    "Distance (miles)",
                    min_value=0.0,
                    step=0.1,
                    format="%.1f",
                    help="Total distance covered during the workout"
                )
                calories = st.number_input(
                    "Calories Burned",
                    min_value=0.0,
                    step=10.0,
                    format="%.0f",
                    help="Estimated calories burned"
                )
            
            with col2:
                steps = st.number_input(
                    "Total Steps",
                    min_value=0,
                    step=100,
                    help="Number of steps taken"
                )
                time_col1, time_col2 = st.columns(2)
            with time_col1:
                start_date = st.date_input(
                    "Start Date",
                    help="Date when the workout started"
                )
                start_time = st.time_input(
                    "Start Time",
                    value=datetime.now().time().replace(second=0, microsecond=0),
                    help="Time when the workout started"
                )

            with time_col2:
                end_date = st.date_input(
                    "End Date",
                    value=start_date,
                    help="Date when the workout ended"
                )
                end_time = st.time_input(
                    "End Time",
                    value=datetime.now().time().replace(second=0, microsecond=0),
                    help="Time when the workout ended"
                )
            
            add_workout_submitted = st.form_submit_button("Log Workout", type="primary", use_container_width=True)
        
        if add_workout_submitted:
            if distance == 0 and steps == 0 and calories == 0:
                st.error("Please enter at least one workout metric (distance, steps, or calories).")
            else:
                try:
                    start_timestamp = datetime.combine(start_date, start_time)
                    end_timestamp = datetime.combine(end_date, end_time)
                    if end_timestamp < start_timestamp:
                        st.error("End timestamp must be after the start timestamp.")
                    else:
                        create_user_workout(
                            user_id=user_id,
                            total_distance=distance,
                            total_steps=int(steps),
                            calories_burned=calories,
                            start_timestamp=start_timestamp,
                            end_timestamp=end_timestamp,
                        )
                        st.success("✅ Workout logged successfully!")
                        st.rerun()
                except ValueError as err:
                    st.error(f"Invalid input: {str(err)}")
                except Exception as err:
                    st.error(f"Could not log workout: {str(err)}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    