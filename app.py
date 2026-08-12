import streamlit as st
import json
import os
from core.analyzer import analyze_brand_voice
from core.generator import generate_marketing_content, evaluate_consistency
from core.gemini_client import get_gemini_client, get_active_model_name
from utils.visualization import create_keyword_chart
from utils.db import init_db, register_user, authenticate_user, save_chat_session, get_user_chat_history

# Initialize Database
init_db()

HISTORY_FILE = "brand_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_profile_to_history(brand_name: str, profile: dict):
    history = load_history()
    history[brand_name] = profile
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def refine_content_with_chat(current_text: str, refinement_instruction: str, brand_profile: dict) -> str:
    client = get_gemini_client()
    model_name = get_active_model_name(client)
    
    prompt = f"""
You are an expert copywriter refining marketing content.

BRAND VOICE CONSTRAINTS:
- Core Tones: {', '.join(brand_profile.get('brand_tone', []))}

CURRENT CONTENT:
\"\"\"
{current_text}
\"\"\"

USER REFINEMENT INSTRUCTION:
"{refinement_instruction}"

Rewrite and adjust the content according to the instruction while maintaining the brand voice.
Output ONLY the revised marketing content without extra commentary.
"""
    response = client.models.generate_content(
        model=model_name,
        contents=prompt
    )
    return response.text.strip()

# Page Configuration
st.set_page_config(page_title="AI Brand Voice Generator", page_icon="⚡", layout="wide")

# Custom Styling
st.markdown("""
    <style>
    .main { padding: 1.5rem; }
    .stButton>button { width: 100%; background-color: #4F46E5; color: white; border-radius: 8px; font-weight: 600; }
    .chat-bubble-user { background-color: #374151; padding: 10px 14px; border-radius: 12px; margin-bottom: 8px; color: white; }
    .chat-bubble-assistant { background-color: #1E293B; padding: 10px 14px; border-radius: 12px; margin-bottom: 8px; border-left: 4px solid #4F46E5; color: white; }
    </style>
""", unsafe_allow_html=True)

# Session State Initialization
if "authenticated_user" not in st.session_state:
    st.session_state.authenticated_user = None
if "brand_profile" not in st.session_state:
    st.session_state.brand_profile = None
if "current_brand_name" not in st.session_state:
    st.session_state.current_brand_name = ""
if "generated_copy" not in st.session_state:
    st.session_state.generated_copy = ""
if "audit_score" not in st.session_state:
    st.session_state.audit_score = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "sample_1_val" not in st.session_state:
    st.session_state.sample_1_val = ""
if "sample_2_val" not in st.session_state:
    st.session_state.sample_2_val = ""

# ==========================================
# AUTHENTICATION SCREEN (IF NOT LOGGED IN)
# ==========================================
if not st.session_state.authenticated_user:
    st.title("🔒 Welcome to AI Brand Voice Generator")
    st.caption("Please sign in or create an account to access the platform.")
    
    auth_tab1, auth_tab2 = st.tabs(["Sign In", "Sign Up / Google Login"])
    
    with auth_tab1:
        st.subheader("Sign In with Email")
        login_email = st.text_input("Email Address", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("🔑 Sign In"):
            if authenticate_user(login_email, login_password):
                st.session_state.authenticated_user = login_email
                st.success(f"Welcome back, {login_email}!")
                st.rerun()
            else:
                st.error("Invalid email or password.")
                
    with auth_tab2:
        st.subheader("Create New Account")
        reg_email = st.text_input("Email Address", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_pass")
        
        if st.button("✨ Register Account"):
            if reg_email and reg_password:
                success, msg = register_user(reg_email, reg_password)
                if success:
                    st.session_state.authenticated_user = reg_email
                    st.success("Account created successfully!")
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.warning("Please fill in both fields.")
                
        st.divider()
        st.subheader("Or Continue with Google")
        if st.button("🌐 Quick Sign-In with Google"):
            google_email = "user.google@gmail.com"
            register_user(google_email, auth_provider="google")
            st.session_state.authenticated_user = google_email
            st.success(f"Signed in as {google_email}")
            st.rerun()

    st.stop()

# ==========================================
# MAIN APPLICATION (LOGGED IN)
# ==========================================

# Title Bar & Logout
col_title, col_logout = st.columns([4, 1])
with col_title:
    st.title("⚡ AI Brand Voice Generator")
    st.caption(f"Logged in as: **{st.session_state.authenticated_user}**")
with col_logout:
    if st.button("🚪 Logout"):
        st.session_state.authenticated_user = None
        st.rerun()

# Sidebar: Profiles & Past Chat History
with st.sidebar:
    st.header("📚 Saved Brand Profiles")
    saved_history = load_history()
    brand_options = ["-- Create New Profile --"] + list(saved_history.keys())
    
    selected_saved = st.selectbox("Load Previous Brand", options=brand_options)
    if selected_saved != "-- Create New Profile --":
        if st.button("📁 Load Selected Profile"):
            prof = saved_history[selected_saved]
            st.session_state.brand_profile = prof
            st.session_state.current_brand_name = selected_saved
            
            # Auto-restore saved sample texts into session state
            saved_samples = prof.get("raw_samples", ["", ""])
            st.session_state.sample_1_val = saved_samples[0] if len(saved_samples) > 0 else ""
            st.session_state.sample_2_val = saved_samples[1] if len(saved_samples) > 1 else ""
            
            st.success(f"Loaded '{selected_saved}' and restored sample texts!")

    st.divider()
    st.header("📜 User Chat & Search History")
    past_sessions = get_user_chat_history(st.session_state.authenticated_user)
    
    if not past_sessions:
        st.info("No past chat history found.")
    else:
        for idx, sess in enumerate(past_sessions[:5]):
            with st.expander(f"{sess['brand_name']} - {sess['content_type']} ({sess['timestamp'][:10]})"):
                st.write(f"**Topic:** {sess['topic']}")
                if st.button(f"Load Chat #{sess['id']}", key=f"load_chat_{idx}"):
                    st.session_state.generated_copy = sess["generated_copy"]
                    st.session_state.chat_history = sess["chat_logs"]
                    st.session_state.current_brand_name = sess["brand_name"]
                    st.success("Loaded chat session!")

    st.divider()
    st.header("⚙️ Dynamic Tone Sliders")
    formality = st.slider("Formality Level", 1, 10, 5)
    humor = st.slider("Humor / Playfulness", 1, 10, 4)
    urgency = st.slider("Urgency / CTA Strength", 1, 10, 7)

# Tabs
tab1, tab2, tab3 = st.tabs(["1️⃣ Voice Analysis Engine", "2️⃣ Copy Generator & AI Chat", "3️⃣ Quality Audit & Export"])

# ---------------- TAB 1: VOICE ANALYSIS ----------------
with tab1:
    st.subheader("Analyze & Save New Brand Profile")
    brand_name_input = st.text_input("Brand Name", value=st.session_state.current_brand_name, placeholder="e.g., Raymond, Nike")
    sample_text_1 = st.text_area("Sample Content 1", value=st.session_state.sample_1_val, height=100)
    sample_text_2 = st.text_area("Sample Content 2", value=st.session_state.sample_2_val, height=100)
    
    if st.button("🚀 Analyze & Save Brand Voice"):
        samples = [s for s in [sample_text_1, sample_text_2] if s.strip()]
        if not brand_name_input.strip():
            st.warning("Please enter a Brand Name.")
        elif not samples:
            st.warning("Please enter content samples.")
        else:
            with st.spinner("Analyzing brand voice..."):
                profile = analyze_brand_voice(samples)
                st.session_state.brand_profile = profile
                st.session_state.current_brand_name = brand_name_input.strip()
                save_profile_to_history(brand_name_input.strip(), profile)
                st.success("Brand Profile Saved!")

    if st.session_state.brand_profile:
        st.divider()
        prof = st.session_state.brand_profile
        col1, col2 = st.columns([1, 1])
        with col1:
            st.write("**Core Tones:**", ", ".join(prof.get("brand_tone", [])))
            st.write("**Vocabulary Style:**", prof.get("vocabulary_style", "N/A"))
        with col2:
            metrics = prof.get("nlp_metrics", {})
            fig = create_keyword_chart(metrics.get("top_keywords", []))
            st.pyplot(fig)

# ---------------- TAB 2: GENERATOR & CHAT ----------------
with tab2:
    st.subheader("Generate & Tailor Content")
    if not st.session_state.brand_profile:
        st.warning("Please analyze or select a brand profile first.")
    else:
        col_type, col_topic = st.columns([1, 2])
        with col_type:
            content_type = st.selectbox("Select Format", ["LinkedIn Post", "Marketing Email", "X / Twitter Post", "Ad Copy"])
        with col_topic:
            topic = st.text_input("Product / Topic Details")
            
        if st.button("✨ Generate Marketing Copy"):
            if topic:
                with st.spinner("Generating copy..."):
                    generated = generate_marketing_content(
                        content_type=content_type,
                        topic=topic,
                        brand_profile=st.session_state.brand_profile,
                        formality_slider=formality,
                        humor_slider=humor,
                        urgency_slider=urgency
                    )
                    st.session_state.generated_copy = generated
                    st.session_state.chat_history = []
                    st.session_state.audit_score = evaluate_consistency(generated, st.session_state.brand_profile)
                    
                    save_chat_session(
                        user_email=st.session_state.authenticated_user,
                        brand_name=st.session_state.current_brand_name or "General",
                        content_type=content_type,
                        topic=topic,
                        generated_copy=generated,
                        chat_logs=[]
                    )

        if st.session_state.generated_copy:
            st.divider()
            col_left, col_right = st.columns([1, 1])
            with col_left:
                st.subheader("📄 Current Copy Output")
                st.text_area("Live Copy", value=st.session_state.generated_copy, height=350)
            with col_right:
                st.subheader("💬 AI Tailoring Chat")
                chat_container = st.container(height=230)
                with chat_container:
                    for role, msg in st.session_state.chat_history:
                        if role == "user":
                            st.markdown(f"<div class='chat-bubble-user'>👤 <b>You:</b> {msg}</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div class='chat-bubble-assistant'>🤖 <b>AI:</b> {msg}</div>", unsafe_allow_html=True)
                
                user_prompt = st.chat_input("How would you like to refine this copy?")
                if user_prompt:
                    st.session_state.chat_history.append(("user", user_prompt))
                    with st.spinner("Refining..."):
                        refined_copy = refine_content_with_chat(
                            st.session_state.generated_copy, user_prompt, st.session_state.brand_profile
                        )
                        st.session_state.generated_copy = refined_copy
                        st.session_state.chat_history.append(("assistant", "Updated copy!"))
                        
                        save_chat_session(
                            user_email=st.session_state.authenticated_user,
                            brand_name=st.session_state.current_brand_name or "General",
                            content_type=content_type if 'content_type' in locals() else "Custom",
                            topic=topic if 'topic' in locals() else "Refinement",
                            generated_copy=refined_copy,
                            chat_logs=st.session_state.chat_history
                        )
                        st.rerun()

# ---------------- TAB 3: AUDIT ----------------
with tab3:
    st.subheader("📊 AI Consistency Scorecard")
    if st.session_state.audit_score:
        audit = st.session_state.audit_score
        st.metric("Brand Consistency Score", f"{audit.get('score', 0)} / 10")
        for s in audit.get("strengths", []):
            st.write(f"- 🌟 {s}")