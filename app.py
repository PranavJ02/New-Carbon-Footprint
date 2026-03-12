import streamlit as st
from supabase_db import supabase
import re
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Carbon Footprint Tracker",
    page_icon="🌍",
    layout="wide"
)

# ---------------- CSS STYLING ----------------
t.markdown("""
<style>

/* Hide Streamlit header and menu */
header {visibility: hidden;}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Remove top padding */
.block-container {
    padding-top: 1rem;
}

/* Full background */
.stApp {
    background: linear-gradient(135deg, #667eea, #764ba2);
    font-family: 'Segoe UI', sans-serif;
}

/* Card */
.card {
    background: white;
    border-radius: 20px;
    padding: 2rem;
    width: 420px;
    margin: auto;
    box-shadow: 0 15px 40px rgba(0,0,0,0.2);
}

/* Titles */
.main-title {
    font-size: 2.2rem;
    font-weight: 700;
    color: white;
    text-align: center;
}

.subtitle {
    font-size: 1rem;
    color: #e0e0e0;
    text-align: center;
    margin-bottom: 2rem;
}

.metric-box {
    background: #e8f4ff;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    font-size: 22px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

# ---------------- PASSWORD CHECK ----------------
def password_strength(password):
    if len(password) < 8:
        return "Password must be at least 8 characters"
    if not re.search("[A-Z]", password):
        return "Add uppercase letter"
    if not re.search("[0-9]", password):
        return "Add number"
    if not re.search("[@#$%^&+=!]", password):
        return "Add special character"
    return "Strong Password ✅"

# ---------------- REGISTER ----------------
def register_user(name,email,username,password):
    existing = supabase.table("users").select("*").eq("username",username).execute()
    if existing.data:
        return False
    data={
        "name":name,
        "email":email,
        "username":username,
        "password":password
    }
    supabase.table("users").insert(data).execute()
    return True

# ---------------- LOGIN ----------------
def login_user(username,password):
    result = supabase.table("users")\
        .select("*")\
        .eq("username",username)\
        .eq("password",password)\
        .execute()
    if result.data:
        user = result.data[0]
        st.session_state.logged_in = True
        st.session_state.user_id = user["id"]
        st.session_state.username = user["username"]
        return True
    return False

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = ""

# ---------------- HEADER ----------------
st.markdown("<div class='main-title'>🌍 Carbon Footprint Tracker</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Track and reduce your daily carbon emissions</div>", unsafe_allow_html=True)

menu = ["Login","Register"]
choice = st.sidebar.selectbox("Menu", menu)

# ================= REGISTER =================
if choice == "Register" and not st.session_state.logged_in:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Create Account")
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")
    if password:
        st.info(password_strength(password))
    if st.button("Register"):
        if password != confirm:
            st.error("Passwords do not match")
        else:
            success = register_user(name, email, username, password)
            if success:
                st.success("Account created! Please login.")
            else:
                st.error("Username already exists")
    st.markdown("</div>", unsafe_allow_html=True)

# ================= LOGIN =================
elif choice == "Login" and not st.session_state.logged_in:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if login_user(username, password):
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")
    st.markdown("</div>", unsafe_allow_html=True)

# ================= DASHBOARD =================
if st.session_state.logged_in:
    st.sidebar.success(f"Welcome {st.session_state.username}")
    st.header("Carbon Footprint Calculator")
    col1, col2, col3 = st.columns(3)
    with col1:
        transport = st.number_input("🚗 Transport CO₂ (kg)", min_value=0.0)
    with col2:
        electricity = st.number_input("💡 Electricity CO₂ (kg)", min_value=0.0)
    with col3:
        diet = st.number_input("🍔 Diet CO₂ (kg)", min_value=0.0)

    if st.button("Calculate & Save"):
        total = transport + electricity + diet
        st.markdown(f"<div class='metric-box'>Total Emission : {total} kg CO₂</div>", unsafe_allow_html=True)
        data = {
            "user_id": st.session_state.user_id,
            "username": st.session_state.username,
            "transport": transport,
            "electricity": electricity,
            "diet": diet,
            "total": total
            # created_at handled automatically by Supabase
        }
        supabase.table("emissions").insert(data).execute()
        st.success("Data saved")

    st.subheader("Daily Carbon Emissions Graph")
    # Fetch records for logged-in user
    records = supabase.table("emissions")\
        .select("*")\
        .eq("user_id", st.session_state.user_id)\
        .order("created_at", desc=False)\
        .execute()

    if records.data:
        df = pd.DataFrame(records.data)
        df['created_at'] = pd.to_datetime(df['created_at'])
        df_chart = df.set_index('created_at')[['total']]
        st.line_chart(df_chart)
    else:
        st.info("No records yet")

    st.subheader("Emission History")
    if records.data:
        st.dataframe(pd.DataFrame(records.data).sort_values(by='created_at', ascending=False), use_container_width=True)

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.user_id = None

        st.rerun()
