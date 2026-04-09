import streamlit as st
from agent import graph
from langchain_core.messages import HumanMessage, AIMessage
import time
import re

# --- Page Config ---
st.set_page_config(
    page_title="Vinmec AI Mobile",
    page_icon="🏥",
    layout="centered"
)

# --- High Fidelity CSS ---
st.markdown("""
<style>
    :root {
      --primary-blue: #00b5ad;
      --bg-light: #f7f9fc;
      --bg-page: #f0f4f8;
      --text-dark: #1a1a2e;
      --text-muted: #718096;
      --white: #ffffff;
      --shadow-soft: 0 1px 4px rgba(0,0,0,0.08);
      --shadow-medium: 0 30px 80px rgba(0,0,50,0.18), 0 0 0 1px #d0d8e4;
      --border-radius-lg: 48px;
      --border-radius-md: 18px;
      --border-radius-sm: 8px;
    }

    /* 1. Ẩn các thành phần mặc định của Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {display: none !important;}
    
    /* 2. Style cho background toàn trang */
    .stApp {
        background-color: var(--bg-page) !important;
        font-family: 'Segoe UI', -apple-system, system-ui, sans-serif;
    }

    /* 3. BIẾN CONTAINER CỦA STREAMLIT THÀNH CÁI ĐIỆN THOẠI */
    .block-container {
        width: 380px !important;
        min-width: 380px !important;
        height: 800px !important;
        max-height: 92vh !important;
        background: var(--white) !important;
        border-radius: 40px !important;
        box-shadow: var(--shadow-medium) !important;
        border: 1px solid #d0d8e4 !important;
        margin: 20px auto !important;
        padding: 0 !important; /* Xóa padding mặc định */
        display: flex !important;
        flex-direction: column !important;
        overflow: hidden !important;
    }

    /* Loại bỏ khoảng trống thừa giữa các block của Streamlit */
    div[data-testid="stVerticalBlock"] {
        gap: 0 !important;
    }

    /* Status bar */
    .status-bar {
        background: var(--primary-blue);
        padding: 12px 24px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: var(--white);
        font-size: 11px;
        font-weight: 600;
    }
    .status-bar .time { font-size: 15px; font-weight: 700; }

    /* App Header */
    .app-header {
        background: var(--primary-blue);
        padding: 10px 16px 16px;
        color: var(--white);
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .header-avatar {
        width: 40px; height: 40px; background: var(--white);
        border-radius: 50%; display: flex; align-items: center; justify-content: center;
    }
    .header-info { flex: 1; }
    .header-info h2 { font-size: 16px !important; margin: 0 !important; font-weight: 700 !important; color: var(--white) !important;}
    .header-info p { font-size: 12px !important; margin: 2px 0 0 0 !important; color: rgba(255,255,255,0.8) !important; }

    /* VÙNG CHAT (Scrollable) */
    .message-list {
        height: 560px;
        overflow-y: auto;
        background: var(--bg-light);
        padding: 16px;
        display: flex;
        flex-direction: column;
        gap: 12px;
        scrollbar-width: thin;
        scrollbar-color: rgba(0,0,0,0.1) transparent;
        overflow-anchor: auto;
    }
    .message-list > :last-child {
        overflow-anchor: none;
    }
    /* Anchor element để giữ scroll ở cuối */
    .scroll-anchor {
        overflow-anchor: auto;
        height: 1px;
    }
    .message-list::-webkit-scrollbar { width: 4px; }
    .message-list::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.1); border-radius: 10px; }

    /* Tin nhắn */
    .message { 
        max-width: 80%; padding: 10px 14px; font-size: 14px; line-height: 1.5; 
        animation: fadeUp 0.3s ease; width: fit-content;
    }
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .message.bot { align-self: flex-start; background: var(--white); color: var(--text-dark); border-radius: var(--border-radius-md); border-bottom-left-radius: 4px; box-shadow: var(--shadow-soft); }
    .message.user { align-self: flex-end; background: var(--primary-blue); color: var(--white); border-radius: var(--border-radius-md); border-bottom-right-radius: 4px; }

    /* VÙNG NHẬP TIN NHẮN (Ghim ở đáy) */
    [data-testid="stForm"] { 
        border: none !important; 
        padding: 12px 16px !important; 
        background: var(--white) !important; 
        border-top: 1px solid #e8edf3 !important; 
        margin: 0 !important;
        height: 100%;
    }
    [data-testid="stHorizontalBlock"] { gap: 10px !important; align-items: center !important; }
    
    /* Ô input */
    .stTextInput input {
        background: #f7f9fc !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 24px !important;
        padding: 10px 16px !important;
        font-size: 14px !important;
        outline: none !important;
        box-shadow: none !important;
    }
    .stTextInput input:focus {
        box-shadow: none !important;
        border-color: #e2e8f0 !important;
    }
    /* Ẩn "Press Enter to submit form" */
    .stTextInput [data-testid="InputInstructions"] {
        display: none !important;
    }
    
    /* Typing Indicator (Ba dấu chấm nhảy) */
    .typing-bubble {
        width: 50px !important;
        padding: 10px 14px !important;
        margin-left: 16px !important;
        margin-top: 5px !important;
        margin-bottom: 5px !important;
        background: var(--white);
        border-radius: var(--border-radius-md);
        border-bottom-left-radius: 4px;
        box-shadow: var(--shadow-soft);
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .typing-indicator {
        display: flex;
        gap: 4px;
    }
    .typing-indicator span {
        width: 6px;
        height: 6px;
        background: var(--text-muted);
        border-radius: 50%;
        animation: typing-bounce 1.4s infinite ease-in-out;
        opacity: 0.4;
    }
    .typing-indicator span:nth-child(1) { animation-delay: 0s; }
    .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
    .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes typing-bounce {
        0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
        40% { transform: scale(1.1); opacity: 1; }
    }

    /* Option cards */
    .option-cards {
        display: flex;
        flex-direction: column;
        gap: 8px;
        margin-top: 8px;
        width: 100%;
        align-items: flex-start;
    }
    .option-card {
        background: var(--white);
        border: 1.5px solid #e2e8f0;
        border-radius: 12px;
        padding: 10px 14px;
        font-size: 13px;
        color: var(--text-dark);
        cursor: pointer;
        transition: all 0.15s ease;
        width: 100%;
        box-shadow: var(--shadow-soft);
        line-height: 1.4;
    }
    .option-card:hover {
        border-color: var(--primary-blue);
        background: #f0fffe;
        color: var(--primary-blue);
    }

    /* Nút gửi */
    [data-testid="stFormSubmitButton"] {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
    }
    [data-testid="stFormSubmitButton"] button {
        width: 40px !important; height: 40px !important; min-width: 40px !important;
        background: var(--primary-blue) !important; color: white !important;
        border-radius: 50% !important; border: none !important;
        position: relative !important;
        padding: 0 !important;
        margin: 0 auto !important;
    }
    [data-testid="stFormSubmitButton"] p { display: none; }
    [data-testid="stFormSubmitButton"] button::after {
        content: "";
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 18px;
        height: 18px;
        background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'><path d='M2.01 21L23 12 2.01 3 2 10l15 2-15 2z'/></svg>");
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
    }

    /* Nút lựa chọn (Menu Items) */
    div.stButton > button {
        border-radius: 12px !important;
        border: 1px solid #eef2f6 !important;
        background-color: var(--white) !important; 
        color: var(--text-dark) !important;
        padding: 5px 12px !important; /* Thu nhỏ padding */
        font-size: 13px !important; /* Giảm size chữ */
        text-align: left !important;
        justify-content: flex-start !important;
        transition: all 0.2s ease !important;
        margin-bottom: 4px !important; /* Giảm gap giữa các nút */
        width: auto !important; /* Không bắt buộc full width */
        min-width: 120px !important;
        max-width: 100% !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02) !important;
    }
    div.stButton > button:hover {
        border-color: var(--primary-blue) !important;
        background-color: #f0fdfa !important;
        color: var(--primary-blue) !important;
    }
    
    /* Thu hẹp khoảng cách giữa các block của Streamlit */
    [data-testid="stVerticalBlock"] > div {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Initial State ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "bot", "content": "Xin kính chào quý khách! Tôi là trợ lý ảo Vinmec. Rất hân hạnh được hỗ trợ đặt lịch khám tại hệ thống y tế Vinmec."}
    ]
if "is_thinking" not in st.session_state:
    st.session_state.is_thinking = False

# --- 1. HEADER CỦA APP ---
st.markdown("""
    <div class="status-bar">
        <span class="time">9:41</span>
        <div style="display:flex; gap: 6px; align-items:center;">
            <span>●●●●</span>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
            <span>95%</span>
        </div>
    </div>
    <div class="app-header">
        <div class="header-avatar">
            <svg viewBox="0 0 40 40" style="width: 28px; height: 28px;">
               <circle cx="20" cy="20" r="20" fill="#00b5ad"/>
               <rect x="17" y="8" width="6" height="24" rx="3" fill="white"/>
               <rect x="8" y="17" width="24" height="6" rx="3" fill="white"/>
            </svg>
        </div>
        <div class="header-info">
            <h2>Trợ lý đặt lịch Vinmec</h2>
            <p>🟢 Đang hoạt động</p>
        </div>
        <div style="display: flex; gap: 12px; color: white; align-items: center;">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="cursor:pointer;"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="cursor:pointer;"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 2. VÙNG HIỂN THỊ TIN NHẮN ---
# Gom toàn bộ tin nhắn vào 1 chuỗi HTML duy nhất để cuộn mượt mà
chat_html = '<div class="message-list" id="chat-container">'

# Dòng chữ chào mừng ban đầu
if len(st.session_state.messages) == 1:
    chat_html += '''
    <div style="text-align: center; padding: 10px 0 20px; width: 100%;">
         <h3 style="font-size: 18px; font-weight: 700; color: #1a1a2e; margin:0;">Bạn muốn hỏi gì hôm nay?</h3>
         <p style="font-size: 13px; color: #718096; margin-top: 4px;">Em sẵn sàng hỗ trợ anh/chị 24/7</p>
    </div>
    '''

# Render các tin nhắn
for m in st.session_state.messages:
    role_type = "user" if m["role"] == "user" else "bot"
    content_html = m["content"].replace("\n", "<br/>")
    chat_html += f'<div class="message {role_type}">{content_html}</div>'

# Hiệu ứng "Đang xử lý" (Ba dấu chấm) tích hợp thẳng vào danh sách chat
if st.session_state.get("is_thinking", False):
    chat_html += '''
        <div class="message bot typing-bubble" style="margin-bottom: 20px;">
            <div class="typing-indicator">
                <span></span><span></span><span></span>
            </div>
        </div>
    '''

# Auto scroll xuống dưới cùng bằng CSS
chat_html += '</div>'
st.markdown(chat_html, unsafe_allow_html=True)

# --- 3. LỰA CHỌN NHANH (ACTION MENU) ---
if st.session_state.messages[-1]["role"] == "bot" and not st.session_state.is_thinking:
    last_content = st.session_state.messages[-1]["content"]
    options = re.findall(r"\d+\.\s+\*\*([^*]+)\*\*", last_content)
    if not options:
        options = re.findall(r"\d+\.\s+([^\n:]+)", last_content)
    
    if options:
        with st.container():
            st.markdown('<div style="height: 0px; margin-top: -10px;"></div>', unsafe_allow_html=True)
            all_short = all(len(opt) < 15 for opt in options[:4])
            if all_short:
                cols = st.columns(len(options[:4]))
                for i, opt in enumerate(options[:4]):
                    with cols[i]:
                        if st.button(f"🔘 {opt}", key=f"menu_{i}", use_container_width=True):
                            st.session_state.messages.append({"role": "user", "content": opt})
                            st.session_state.is_thinking = True
                            st.rerun()
            else:
                for i, opt in enumerate(options[:6]):
                    sub_cols = st.columns([0.8, 0.2]) 
                    with sub_cols[0]:
                        if st.button(f"📍 {opt}", key=f"menu_{i}"):
                            st.session_state.messages.append({"role": "user", "content": opt})
                            st.session_state.is_thinking = True
                            st.rerun()

# --- 4. KHUNG NHẬP DỮ LIỆU ---
with st.form("chat_form", clear_on_submit=True):
    cols = st.columns([0.85, 0.15])
    with cols[0]:
        user_input = st.text_input("Nhập tin nhắn", label_visibility="collapsed", placeholder="Nhắn tin cho Vinmec...", disabled=st.session_state.is_thinking)
    with cols[1]:
        submitted = st.form_submit_button("S", disabled=st.session_state.is_thinking)
        
# --- 5. LOGIC XỬ LÝ TIN NHẮN ---
# 1. Nếu user nhấn gửi -> bật mode thinking và rerun
if submitted and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.is_thinking = True
    st.rerun()

# 2. Khi ở mode thinking -> gọi AI xử lý
if st.session_state.is_thinking:
    history = []
    for m in st.session_state.messages:
        if m["role"] == "user": history.append(HumanMessage(content=m["content"]))
        else: history.append(AIMessage(content=m["content"]))
    
    try:
        # Gọi Agent (trang web vẫn hiển thị 3 dấu chấm vì is_thinking đang True)
        result = graph.invoke({"messages": history})
        response = result["messages"][-1].content
        st.session_state.messages.append({"role": "bot", "content": response})
    except Exception as e:
        err_str = str(e).lower()
        if "401" in err_str or "invalid_api_key" in err_str:
            st.session_state.messages.append({"role": "bot", "content": "⚠️ **Lỗi xác thực:** API Key OpenAI không hợp lệ hoặc đã hết hạn. Vui lòng kiểm tra lại file `.env`!"})
        else:
            st.session_state.messages.append({"role": "bot", "content": f"🚨 **Lỗi hệ thống:** {str(e)}"})
    
    # Hoàn tất -> tắt mode thinking và rerun để hiện câu trả lời
    st.session_state.is_thinking = False
    st.rerun()