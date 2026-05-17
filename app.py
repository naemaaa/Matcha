import streamlit as st
import uuid
from agent.graph import matcha_graph
from agent.memory import init_db, save_session, load_session

init_db()

# Helper function untuk loading indicator
def show_loading_popup(message: str, submessage: str = ""):
    """Menampilkan loading popup yang menarik"""
    loading_html = f"""
    <div class="loading-overlay">
        <div class="loading-popup">
            <div class="loading-spinner">
                <div class="spinner-leaf" style="font-size: 3rem;">🍵</div>
            </div>
            <div class="loading-text">{message}</div>
            {f'<div class="loading-subtext">{submessage}</div>' if submessage else ''}
        </div>
    </div>
    """
    return loading_html

st.set_page_config(
    page_title="Matcha - Asisten Karir Adaptif",
    page_icon="🍵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk styling yang lebih menarik
st.markdown("""
<style>
    /* Main styling */
    :root {
        --primary-color: #3D7B3E;
        --secondary-color: #7ECE8F;
        --accent-color: #2D5C30;
        --light-bg: #F0F8F1;
        --text-dark: #1A1A1A;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #3D7B3E 0%, #7ECE8F 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(61, 123, 62, 0.2);
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        color: white;
    }
    
    .header-subtitle {
        font-size: 1rem;
        margin-top: 0.5rem;
        opacity: 0.95;
        color: rgba(255, 255, 255, 0.9);
    }
    
    /* Card styling */
    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #3D7B3E;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
    }
    
    .info-card:hover {
        box-shadow: 0 4px 12px rgba(61, 123, 62, 0.15);
        transform: translateY(-2px);
    }
    
    .profile-metric {
        background: #F0F8F1;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.8rem;
        border-left: 3px solid #7ECE8F;
    }
    
    /* Chat message styling */
    .stChatMessage {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        border-left: 4px solid #7ECE8F;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #3D7B3E 0%, #2D5C30 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(61, 123, 62, 0.3);
    }
    
    /* File uploader styling */
    .stFileUploader {
        border: 2px dashed #7ECE8F;
        border-radius: 12px;
        padding: 1rem;
        background: #F0F8F1;
    }
    
    /* Text area styling */
    .stTextArea textarea {
        border: 2px solid #E0E0E0;
        border-radius: 8px;
        padding: 1rem;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .stTextArea textarea:focus {
        border-color: #3D7B3E;
        box-shadow: 0 0 8px rgba(61, 123, 62, 0.2);
    }
    
    /* Section headers */
    .section-header {
        border-bottom: 2px solid #7ECE8F;
        padding-bottom: 0.8rem;
        margin-bottom: 1rem;
        color: #3D7B3E;
        font-weight: 700;
        font-size: 1.2rem;
    }
    
    /* Status badges */
    .status-badge-success {
        background: #E8F5E9;
        color: #2E7D32;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .status-badge-warning {
        background: #FFF3E0;
        color: #E65100;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    /* Sidebar styling */
    .sidebar-header {
        background: #F0F8F1;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        border-left: 4px solid #3D7B3E;
    }
    
    /* Spinner text */
    .stSpinner {
        color: #3D7B3E;
    }
    
    /* Loading modal overlay */
    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.6);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        backdrop-filter: blur(4px);
    }
    
    /* Loading popup */
    .loading-popup {
        background: white;
        padding: 3rem;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        text-align: center;
        animation: popIn 0.3s ease-out;
    }
    
    @keyframes popIn {
        0% {
            transform: scale(0.8);
            opacity: 0;
        }
        100% {
            transform: scale(1);
            opacity: 1;
        }
    }
    
    /* Animated spinner */
    .loading-spinner {
        display: inline-block;
        width: 60px;
        height: 60px;
        margin-bottom: 1.5rem;
    }
    
    .spinner-leaf {
        animation: spin 1.2s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .loading-text {
        font-size: 1.2rem;
        font-weight: 600;
        color: #3D7B3E;
        margin-bottom: 0.5rem;
    }
    
    .loading-subtext {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.5rem;
    }
    
    /* Pulse animation */
    .pulse {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }
</style>
""", unsafe_allow_html=True)

# Session State
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]

if "agent_state" not in st.session_state:
    saved = load_session(st.session_state.session_id)
    st.session_state.agent_state = {
        "messages": [],
        "profile_complete": False,
        "drift_detected": False,
        "previous_intent_history": [],
        **saved
    }

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Header
st.markdown("""
<div class="header-container">
    <h1 class="header-title">🍵 Matcha</h1>
    <p class="header-subtitle">Asisten Karir Adaptif — Temukan Jalur Karir Idealmu</p>
</div>
""", unsafe_allow_html=True)

# Layout
col_chat, col_info = st.columns([2, 1])

with col_chat:
    # Upload section
    st.markdown('<div class="section-header">📄 Dokumen Kamu</div>', unsafe_allow_html=True)
    
    upload_tabs = st.tabs(["CV", "LinkedIn"])
    
    with upload_tabs[0]:
        st.markdown("**Upload CV Kamu** (opsional)")
        uploaded_file = st.file_uploader(
            "Pilih file CV",
            type=["pdf", "docx"],
            key="cv_uploader",
            help="Upload CV untuk rekomendasi yang lebih personal"
        )
        
        if uploaded_file:
            from utils.helpers import extract_cv_text
            cv_text = extract_cv_text(uploaded_file)
            if cv_text:
                st.session_state.agent_state["cv_text"] = cv_text
                st.markdown(
                    '<div class="status-badge-success">✓ CV berhasil diupload!</div>',
                    unsafe_allow_html=True
                )
                st.caption("💡 Tanya 'review CV aku' untuk mendapatkan feedback detail")
    
    with upload_tabs[1]:
        st.markdown("**Upload Profil LinkedIn Kamu** (opsional)")
        linkedin_file = st.file_uploader(
            "Pilih file LinkedIn PDF",
            type=["pdf"],
            key="linkedin_uploader",
            help="Export PDF dari LinkedIn → Me → Save to PDF"
        )
        
        if linkedin_file:
            from utils.helpers import extract_cv_text
            linkedin_text = extract_cv_text(linkedin_file)
            if linkedin_text:
                st.session_state.agent_state["linkedin_text"] = linkedin_text
                st.markdown(
                    '<div class="status-badge-success">✓ Profil LinkedIn berhasil diupload!</div>',
                    unsafe_allow_html=True
                )
    
    # Chat section
    st.markdown('<div class="section-header" style="margin-top: 2rem;">💬 Chat Dengan Matcha</div>', unsafe_allow_html=True)
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"], avatar="🍵" if msg["role"] == "assistant" else "👤"):
                st.markdown(msg["content"])
    
    # Chat input
    if user_input := st.chat_input("Ceritakan situasimu, pertanyaanmu, atau tujuan karirmu..."):
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        current_state = st.session_state.agent_state
        current_state["user_input"] = user_input
        current_state["messages"] = st.session_state.chat_history

        # Show loading indicator
        loading_container = st.empty()
        with loading_container:
            st.markdown(show_loading_popup(
                "🍵 Matcha sedang menganalisis...",
                "Memberikan insight terbaik untuk karirmu..."
            ), unsafe_allow_html=True)
        
        result = matcha_graph.invoke(current_state)
        loading_container.empty()  # Clear loading

        st.session_state.agent_state = result
        save_session(st.session_state.session_id, result)

        response = result.get("agent_response", "Maaf, terjadi error. Coba lagi nanti.")
        with st.chat_message("assistant", avatar="🍵"):
            st.markdown(response)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()

with col_info:
    st.markdown('<div class="section-header">👤 Profil Karir</div>', unsafe_allow_html=True)
    
    profile = st.session_state.agent_state.get("user_profile")

    if profile:
        profile_items = []
        if profile.get("current_role"):
            profile_items.append(("📍 Posisi Saat Ini", profile["current_role"]))
        if profile.get("target_role"):
            profile_items.append(("🎯 Target Karir", profile["target_role"]))
        if profile.get("experience_years"):
            profile_items.append(("📅 Pengalaman", f"{profile['experience_years']} tahun"))
        if profile.get("hours_per_week"):
            profile_items.append(("⏱️ Waktu/Minggu", f"{profile['hours_per_week']} jam"))
        if profile.get("budget_idr"):
            profile_items.append(("💰 Budget", f"Rp {profile['budget_idr']:,}"))
        
        for label, value in profile_items:
            st.markdown(f"""
            <div class="profile-metric">
                <strong>{label}</strong><br>
                {value}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("🔄 Profil akan terisi seiring percakapan kita")

    # Drift detection
    if st.session_state.agent_state.get("drift_detected"):
        st.markdown(
            '<div class="status-badge-warning">⚠️ Perubahan tujuan terdeteksi. Profil sedang diperbarui.</div>',
            unsafe_allow_html=True
        )
    
    # Skill gaps
    skill_gaps = st.session_state.agent_state.get("skill_gaps")
    if skill_gaps:
        st.markdown('<div class="section-header" style="margin-top: 1.5rem;">🎓 Skill Gap</div>', unsafe_allow_html=True)
        st.markdown(skill_gaps)
    
    # CV Status
    st.markdown('<div class="section-header" style="margin-top: 1.5rem;">📝 Review Dokumen</div>', unsafe_allow_html=True)
    
    cv_text = st.session_state.agent_state.get("cv_text")
    if cv_text:
        st.markdown(
            '<div class="status-badge-success">✓ CV Terupload</div>',
            unsafe_allow_html=True
        )
        if st.button("📄 Review CV Sekarang", use_container_width=True):
            current_state = st.session_state.agent_state
            current_state["user_input"] = "tolong review CV aku secara detail dan berikan feedback untuk improvement"
            current_state["messages"] = st.session_state.chat_history

            # Show loading indicator
            loading_container = st.empty()
            with loading_container:
                st.markdown(show_loading_popup(
                    "🍵 Matcha sedang review CV...",
                    "Menganalisis pengalaman dan skill kamu..."
                ), unsafe_allow_html=True)
            
            result = matcha_graph.invoke(current_state)
            loading_container.empty()  # Clear loading

            st.session_state.agent_state = result
            save_session(st.session_state.session_id, result)

            response = result.get("agent_response", "")
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
    else:
        st.caption("📄 Belum ada CV (opsional)")
    
    # LinkedIn Status
    linkedin_text = st.session_state.agent_state.get("linkedin_text")
    if linkedin_text:
        st.markdown(
            '<div class="status-badge-success">✓ LinkedIn Terupload</div>',
            unsafe_allow_html=True
        )
        if st.button("💼 Review LinkedIn Sekarang", use_container_width=True):
            current_state = st.session_state.agent_state
            current_state["user_input"] = "tolong review profil LinkedIn aku dan berikan saran untuk meningkatkan visibility"
            current_state["messages"] = st.session_state.chat_history

            # Show loading indicator
            loading_container = st.empty()
            with loading_container:
                st.markdown(show_loading_popup(
                    "🍵 Matcha sedang review LinkedIn...",
                    "Memeriksa headline, experience, dan endorsement kamu..."
                ), unsafe_allow_html=True)
            
            result = matcha_graph.invoke(current_state)
            loading_container.empty()  # Clear loading

            st.session_state.agent_state = result
            save_session(st.session_state.session_id, result)

            response = result.get("agent_response", "")
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
    else:
        st.caption("💼 Belum ada profil LinkedIn (opsional)")

    # Job Description Analysis
    st.markdown('<div class="section-header" style="margin-top: 1.5rem;">🔍 Analisis Job</div>', unsafe_allow_html=True)
    
    jd_input = st.text_area(
        "Paste job description di sini",
        height=150,
        placeholder="Copy-paste job description dari Glints, LinkedIn, JobStreet, dll...",
        label_visibility="collapsed"
    )
    if st.button("🔎 Analisis Job Ini", use_container_width=True):
        if jd_input:
            st.session_state.agent_state["job_description"] = jd_input
            current_state = st.session_state.agent_state
            current_state["user_input"] = "tolong analisis job description ini dan bandingkan dengan profilku. Beri tahu seberapa match aku dan skill apa yang perlu dipelajari"
            current_state["messages"] = st.session_state.chat_history

            # Show loading indicator
            loading_container = st.empty()
            with loading_container:
                st.markdown(show_loading_popup(
                    "🍵 Matcha sedang menganalisis job...",
                    "Mencocokkan skill dan requirement job description..."
                ), unsafe_allow_html=True)
            
            result = matcha_graph.invoke(current_state)
            loading_container.empty()  # Clear loading

            st.session_state.agent_state = result
            save_session(st.session_state.session_id, result)

            response = result.get("agent_response", "")
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
        else:
            st.warning("⚠️ Paste job description dulu ya!")