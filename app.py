import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Pharmacology Exam 2025", layout="wide")

# --- CSS for styling ---
st.markdown("""
    <style>
    .stRadio > label {font-weight: bold; font-size: 16px;}
    .correct {color: #155724; background-color: #d4edda; padding: 10px; border-radius: 5px; border: 1px solid #c3e6cb;}
    .incorrect {color: #721c24; background-color: #f8d7da; padding: 10px; border-radius: 5px; border: 1px solid #f5c6cb;}
    .explanation {margin-top: 10px; font-style: italic; color: #555;}
    </style>
""", unsafe_allow_html=True)

# --- App Title ---
st.title("💊 Top Student Pharmacology Test")
st.markdown("Based on *Farmakologia SPECIFIC tables.pdf* and *Pgarma general tables.pdf*")

# --- Sidebar: File Selection ---
st.sidebar.header("Exam Settings")

# Find available CSV files in the current directory that start with 'q'
# Or just hardcode the expected files as requested
available_files = ['q1.csv', 'q2.csv']
existing_files = [f for f in available_files if os.path.exists(f)]

if not existing_files:
    st.error("No question files found! Please run the setup script to generate 'q1.csv' and 'q2.csv'.")
    st.stop()

selected_file = st.sidebar.selectbox("Select Question Set:", existing_files)

# --- Load Data ---
@st.cache_data
def load_data(filename):
    try:
        df = pd.read_csv(filename)
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return pd.DataFrame()

df = load_data(selected_file)

if df.empty:
    st.stop()

# --- Initialize Session State for Score ---
if "score" not in st.session_state:
    st.session_state.score = 0

# --- Display Questions ---
score = 0
total_questions = len(df)

# We use a form so the page doesn't reload on every radio click
with st.form("quiz_form"):
    user_answers = {}
    
    for index, row in df.iterrows():
        st.subheader(f"Q{index + 1}: {row['Question']}")
        
        # Options list
        options = [
            f"A: {row['Option A']}",
            f"B: {row['Option B']}",
            f"C: {row['Option C']}",
            f"D: {row['Option D']}",
            f"E: {row['Option E']}"
        ]
        
        # Radio button for selection
        # We use a key based on index to keep state unique
        user_choice = st.radio(
            "Choose your answer:", 
            options, 
            index=None, 
            key=f"q_{index}",
            label_visibility="collapsed"
        )
        
        user_answers[index] = user_choice
        st.markdown("---")

    submitted = st.form_submit_button("Submit Exam")

# --- Grading Logic (Runs after submit) ---
if submitted:
    st.header("📝 Results")
    current_score = 0
    
    for index, row in df.iterrows():
        st.markdown(f"**Q{index + 1}: {row['Question']}**")
        
        selected_option_text = user_answers[index]
        
        # Extract "Option X" from the user's selected string
        if selected_option_text:
            selected_option_label = "Option " + selected_option_text.split(":")[0].strip() # e.g., "Option A"
        else:
            selected_option_label = None

        correct_option_label = row['Correct Answer'].strip() # e.g., "Option C"
        
        # Check correctness
        if selected_option_label == correct_option_label:
            current_score += 1
            st.markdown(f"<div class='correct'>✅ <b>Correct!</b> You chose {selected_option_label}.</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='incorrect'>❌ <b>Incorrect.</b> You chose {selected_option_label if selected_option_label else 'Nothing'}. The correct answer was <b>{correct_option_label}</b>.</div>", unsafe_allow_html=True)
        

        # Show Explanation
        st.markdown(f"<div class='explanation'>📖 <b>Notes Source:</b> {row['Explanation']}</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # --- Final Score Calculation ---
    final_percentage = (current_score / total_questions) * 100
    
    st.markdown("### Final Score")
    col1, col2, col3 = st.columns(3)
    col1.metric("Correct", current_score)
    col2.metric("Total", total_questions)
    col3.metric("Percentage", f"{final_percentage:.1f}%")

    if final_percentage >= 90:
        st.balloons()
        st.success("🌟 OUSTANDING! You are definitely a top student.")
    elif final_percentage >= 50:
        st.warning("⚠️ You passed, but study the 'Specific Tables' more.")
    else:
        st.error("💀 FAILED. These questions are very hard. Review the notes.")