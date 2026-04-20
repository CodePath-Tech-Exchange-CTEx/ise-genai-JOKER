import streamlit as st
from datetime import datetime, date
from data_fetcher import (
    get_user_profile, 
    update_user_profile_details, 
    update_user_password
)

def display_profile_page(user_id):
    st.markdown("<h1 style='font-size: 3.5em; line-height: 1; margin-bottom: 20px;'>Profile</h1>", unsafe_allow_html=True)
    
    user_profile = get_user_profile(user_id)
    if not user_profile:
        st.error('Could not load your profile.')
        return

    # Toggle state for View vs Edit mode
    edit_key = f"edit_mode_{user_id}"
    if edit_key not in st.session_state:
        st.session_state[edit_key] = False

    # ---------------------------------------------------------
    # VIEW MODE
    # ---------------------------------------------------------
    if not st.session_state[edit_key]:
        # Clean up data for display
        full_name = user_profile.get('full_name') or 'Unknown User'
        username = user_profile.get('username') or user_id
        profile_img = user_profile.get('profile_image') or "https://via.placeholder.com/150/222222/FFFFFF?text=+"
        
        # Calculate Age safely
        raw_dob = user_profile.get('date_of_birth')
        age_display = "Age Unknown"
        if raw_dob:
            try:
                if isinstance(raw_dob, str):
                    dob = datetime.fromisoformat(raw_dob.replace('Z', '+00:00')).date()
                elif isinstance(raw_dob, datetime):
                    dob = raw_dob.date()
                else:
                    dob = raw_dob
                
                today = date.today()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                age_display = f"{age} YEARS OLD"
            except:
                pass

        # Profile Card HTML
        profile_html = f"""
        <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,wght@0,400;0,500;0,700;1,400&display=swap" rel="stylesheet">
        <style>
            .profile-card {{
                background: rgba(255,255,255,0.02);
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 16px;
                padding: 40px;
                display: flex;
                align-items: center;
                gap: 40px;
                margin-bottom: 30px;
                max-width: 680px;
            }}
            .profile-avatar {{
                width: 140px;
                height: 140px;
                border-radius: 50%;
                object-fit: cover;
                border: 3px solid #fa114f;
                box-shadow: 0 0 20px rgba(250, 17, 79, 0.3);
            }}
            .profile-info {{
                flex: 1;
            }}
            .profile-name {{
                font-family: 'Bebas Neue', sans-serif;
                font-size: 3.5em;
                color: #ffffff;
                line-height: 1;
                letter-spacing: 0.05em;
                margin-bottom: 5px;
            }}
            .profile-username {{
                font-family: 'DM Sans', sans-serif;
                font-size: 1.2em;
                color: #fa114f;
                font-weight: bold;
                margin-bottom: 15px;
            }}
            .profile-stat {{
                font-family: 'DM Sans', sans-serif;
                font-size: 0.8em;
                color: #bcbcbc;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                background: rgba(255,255,255,0.04);
                padding: 6px 12px;
                border-radius: 6px;
                display: inline-block;
            }}
        </style>
        
        <div class="profile-card">
            <img src="{profile_img}" alt="Profile Avatar" class="profile-avatar" onerror="this.src='https://via.placeholder.com/150/222222/FFFFFF?text=?'">
            <div class="profile-info">
                <div class="profile-name">{full_name}</div>
                <div class="profile-username">@{username}</div>
                <div class="profile-stat">🎂 {age_display}</div>
            </div>
        </div>
        """
        st.markdown(profile_html, unsafe_allow_html=True)

        # Edit Button
        st.markdown("""
        <style>
            .edit-btn-container button {
                border-radius: 9999px !important;
                padding: 6px 24px !important;
                border: 1px solid rgba(255,255,255,0.2) !important;
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Put button in a small column so it doesn't stretch
        col1, _ = st.columns([1, 4])
        with col1:
            st.markdown('<div class="edit-btn-container">', unsafe_allow_html=True)
            if st.button("✏️ Edit Profile", use_container_width=True):
                st.session_state[edit_key] = True
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # ---------------------------------------------------------
    # EDIT MODE
    # ---------------------------------------------------------
    else:
        # Cancel Button
        if st.button("⬅ Back to Profile"):
            st.session_state[edit_key] = False
            st.rerun()
            
        st.markdown("<br>", unsafe_allow_html=True)

        image_url_default = user_profile.get('profile_image') or ''
        raw_dob = user_profile.get('date_of_birth')

        if isinstance(raw_dob, datetime):
            dob_default = raw_dob.date()
        elif isinstance(raw_dob, date):
            dob_default = raw_dob
        else:
            try:
                dob_default = datetime.fromisoformat(str(raw_dob)).date() if raw_dob else date(2000, 1, 1)
            except (TypeError, ValueError):
                dob_default = date(2000, 1, 1)

        with st.form('profile_edit_form'):
            updated_image_url = st.text_input('Profile Image URL', value=image_url_default)
            updated_dob = st.date_input('Date of Birth', value=dob_default)
            update_profile_submitted = st.form_submit_button('Save Profile Changes')

        if update_profile_submitted:
            try:
                update_user_profile_details(user_id, updated_image_url, updated_dob)
                st.success('Profile updated successfully.')
                st.session_state[edit_key] = False # Send them back to view mode on success
                st.rerun()
            except ValueError as err:
                st.error(str(err))
            except Exception:
                st.error('Could not update profile right now. Please try again.')
                
        st.markdown("<h2 style='font-size: 2em; margin-top: 30px;'>Change Password</h2>", unsafe_allow_html=True)
        with st.form('password_change_form'):
            new_password = st.text_input('New Password', type='password')
            confirm_password = st.text_input('Confirm New Password', type='password')
            update_password_submitted = st.form_submit_button('Update Password')

        if update_password_submitted:
            if not new_password:
                st.error('Please enter a new password.')
            elif new_password != confirm_password:
                st.error('Passwords do not match.')
            else:
                try:
                    update_user_password(user_id, new_password)
                    st.success('Password updated successfully.')
                    st.session_state[edit_key] = False
                    st.rerun()
                except ValueError as err:
                    st.error(str(err))
                except Exception:
                    st.error('Could not update password right now. Please try again.')