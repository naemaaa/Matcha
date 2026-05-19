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
# Top navigation + Header
st.markdown("""
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem;">
    <div style="display:flex;align-items:center;gap:1rem;">
        <div style="font-weight:800;color:var(--accent-color);font-size:1.1rem;padding:0.2rem 0.6rem;border-radius:8px;">Matcha</div>
        <nav style="display:flex;gap:1rem;color:#555;align-items:center;">
            <a href="#" style="text-decoration:none;color:#2D5C30;font-weight:600;">Dashboard</a>
            <a href="#" style="text-decoration:none;color:#7A7A7A;">Career Path</a>
            <a href="#" style="text-decoration:none;color:#7A7A7A;">Resources</a>
        </nav>
    </div>
    <div style="display:flex;gap:0.6rem;align-items:center;">
        <button style="background:transparent;border:0;color:#666;padding:0.3rem 0.6rem;border-radius:8px;">🔔</button>
        <div style="width:36px;height:36px;border-radius:18px;background:#E8F5E9;display:flex;align-items:center;justify-content:center">M</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-container">
        <h1 class="header-title">🍵 Selamat Datang di Matcha</h1>
        <p class="header-subtitle">Asisten Karir Adaptif — Temukan Jalur Karir Idealmu</p>
</div>
""", unsafe_allow_html=True)

# Layout: tiga kolom (kiri: dokumen/status, tengah: chat + analisis, kanan: profil)
left_col, center_col, right_col = st.columns([1, 3, 1.2])

with left_col:
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown('<h3 style="margin-top:0;margin-bottom:8px;">📁 Dokumen</h3>', unsafe_allow_html=True)
    # Show uploaded files
    cv_text = st.session_state.agent_state.get("cv_text")
    linkedin_text = st.session_state.agent_state.get("linkedin_text")
    if cv_text:
        st.markdown('<div style="padding:0.6rem;border-radius:8px;border:1px solid #E8F5E9;margin-bottom:0.6rem;">CV Utama.pdf <span style="float:right;color:#2E7D32;">✓</span></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="padding:0.6rem;border-radius:8px;border:1px dashed #E0E0E0;margin-bottom:0.6rem;color:#888;">Upload CV (opsional)</div>', unsafe_allow_html=True)

    if linkedin_text:
        st.markdown('<div style="padding:0.6rem;border-radius:8px;border:1px solid #E8F5E9;margin-bottom:0.6rem;">LinkedIn Profile.pdf <span style="float:right;color:#2E7D32;">✓</span></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="padding:0.6rem;border-radius:8px;border:1px dashed #E0E0E0;margin-bottom:0.6rem;color:#888;">Upload Profil LinkedIn (opsional)</div>', unsafe_allow_html=True)

    st.file_uploader('Drag file ke sini atau klik Browse', type=['pdf','docx'], key='cv_uploader_small')
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown('<h4 style="margin:0 0 8px 0;">Status Review</h4>', unsafe_allow_html=True)
    st.markdown('<ul style="padding-left:1rem;margin-top:0"><li>Review CV — Belum dianalisis</li><li>Review LinkedIn — Belum dianalisis</li></ul>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with center_col:
    # Main chat card
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown('<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">\n        <strong>Matcha Career Assistant</strong>\n        <div style="color:#888">Aktif</div>\n    </div>', unsafe_allow_html=True)

    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history[-20:]:
            role = msg.get('role')
            content = msg.get('content')
            if role == 'assistant':
                st.markdown(f"<div style='background:#F6FFF7;padding:0.8rem;border-radius:12px;margin-bottom:0.6rem;border-left:4px solid var(--secondary-color);'>{content}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='background:#FFFFFF;padding:0.6rem;border-radius:12px;margin-bottom:0.6rem;text-align:right;border:1px solid #EEE'>{content}</div>", unsafe_allow_html=True)

    # Chat input
    if user_input := st.chat_input('Ceritakan situasimu atau tujuan karirmu...'):
        st.session_state.chat_history.append({'role':'user','content':user_input})
        current_state = st.session_state.agent_state
        current_state['user_input'] = user_input
        current_state['messages'] = st.session_state.chat_history

        loading_container = st.empty()
        with loading_container:
            st.markdown(show_loading_popup('🍵 Matcha sedang menganalisis...','Memberikan insight terbaik untuk karirmu...'), unsafe_allow_html=True)

        result = matcha_graph.invoke(current_state)
        loading_container.empty()

        st.session_state.agent_state = result
        save_session(st.session_state.session_id, result)
        response = result.get('agent_response','Maaf, terjadi error. Coba lagi nanti.')
        st.session_state.chat_history.append({'role':'assistant','content':response})
        st.experimental_rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # Analysis / Skill gap preview
    skill_gaps = st.session_state.agent_state.get('skill_gaps')
    if skill_gaps:
        st.markdown('<div class="info-card" style="margin-top:1rem">', unsafe_allow_html=True)
        st.markdown('<h4>Analisis Gap Ilmu</h4>', unsafe_allow_html=True)
        st.markdown(skill_gaps)
        st.markdown('</div>', unsafe_allow_html=True)

    # Learning Path card (preview)
    st.markdown('<div class="info-card" style="margin-top:1rem">', unsafe_allow_html=True)
    st.markdown('<h4>Peta Jalan Belajar Terpersonalisasi</h4>', unsafe_allow_html=True)
    st.markdown('<ol style="margin-left:1rem"><li>Minggu 1 — Advanced Interaction Design</li><li>Minggu 2 — Modern Design Systems</li><li>Minggu 3 — User Research Ethics</li></ol>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown('<h3 style="margin-top:0;margin-bottom:8px;">👤 Profil Karir</h3>', unsafe_allow_html=True)
    profile = st.session_state.agent_state.get('user_profile') or {}
    st.markdown(f"<div style='margin-bottom:0.6rem'><strong>Posisi Saat Ini:</strong><br>{profile.get('current_role','-')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='margin-bottom:0.6rem'><strong>Target Karir:</strong><br>{profile.get('target_role','-')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='margin-bottom:0.6rem'><strong>Waktu/Minggu:</strong><br>{profile.get('hours_per_week','-')} jam</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="info-card" style="margin-top:1rem">', unsafe_allow_html=True)
    st.markdown('<h4>Jelajahi Lowongan</h4>', unsafe_allow_html=True)
    jd_input = st.text_area('Paste job description di sini', height=100, placeholder='Copy-paste job description...')
    if st.button('Analisis Ulang'):
        if jd_input:
            st.session_state.agent_state['job_description'] = jd_input
            current_state = st.session_state.agent_state
            current_state['user_input'] = 'tolong analisis job description ini dan bandingkan dengan profilku'
            current_state['messages'] = st.session_state.chat_history
            loading_container = st.empty()
            with loading_container:
                st.markdown(show_loading_popup('🍵 Matcha sedang menganalisis job...','Mencocokkan skill dan requirement job description...'), unsafe_allow_html=True)
            result = matcha_graph.invoke(current_state)
            loading_container.empty()
            st.session_state.agent_state = result
            save_session(st.session_state.session_id, result)
            st.experimental_rerun()
        else:
            st.warning('Paste job description dulu ya!')
    st.markdown('</div>', unsafe_allow_html=True)
    