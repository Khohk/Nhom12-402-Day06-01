import gradio as gr
import re
from agent import graph
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv

# Load env variables
load_dotenv()

def chat_response(message, history):
    """
    Hàm xử lý tin nhắn cho Gradio.
    history: list of lists [[user_msg, bot_msg], ...]
    """
    # 1. Chuyển đổi lịch sử Gradio sang định dạng LangChain Messages
    langchain_history = []
    for user_msg, bot_msg in history:
        langchain_history.append(HumanMessage(content=user_msg))
        langchain_history.append(AIMessage(content=bot_msg))
    
    # Thêm tin nhắn hiện tại
    langchain_history.append(HumanMessage(content=message))
    
    try:
        # 2. Gọi Agent xử lý
        result = graph.invoke({"messages": langchain_history})
        response = result["messages"][-1].content
        return response
    except Exception as e:
        # Xử lý lỗi
        err_str = str(e).lower()
        if "401" in err_str or "invalid_api_key" in err_str:
            return "⚠️ **Lỗi xác thực:** API Key OpenAI không hợp lệ. Vui lòng kiểm tra lại file .env!"
        return f"🚨 **Lỗi hệ thống:** {str(e)}"

# --- Giao diện Gradio High Fidelity ---
CSS = """
:root {
  --primary-blue: #00b5ad;
  --bg-light: #f7f9fc;
  --bg-page: #f0f4f8;
  --text-dark: #1a1a2e;
  --text-muted: #718096;
  --white: #ffffff;
  --shadow-soft: 0 1px 4px rgba(0,0,0,0.08);
  --shadow-medium: 0 30px 80px rgba(0,0,50,0.18), 0 0 0 1px #d0d8e4;
}

body {
    background-color: var(--bg-page) !important;
}

/* Biến Gradio thành điện thoại */
.phone-wrapper {
    width: 380px !important;
    margin: 40px auto !important;
    background: var(--white) !important;
    border-radius: 44px !important;
    box-shadow: var(--shadow-medium) !important;
    border: 1px solid #d0d8e4 !important;
    overflow: hidden !important;
    display: flex !important;
    flex-direction: column !important;
    padding: 0 !important;
}

/* Custom Chatbot */
#chatbot {
    height: 520px !important;
    background-color: var(--bg-light) !important;
    border: none !important;
}

#chatbot .message.user {
    background-color: var(--primary-blue) !important;
    color: white !important;
    border-radius: 18px 18px 4px 18px !important;
}

#chatbot .message.bot {
    background-color: var(--white) !important;
    color: var(--text-dark) !important;
    border-radius: 18px 18px 18px 4px !important;
    box-shadow: var(--shadow-soft) !important;
}

/* Status Bar */
.status-bar {
    background: var(--primary-blue);
    padding: 12px 24px 4px;
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
.header-info h2 { font-size: 16px !important; margin: 0 !important; font-weight: 700 !important; color: white !important; }
.header-info p { font-size: 12px !important; margin: 2px 0 0 0 !important; color: rgba(255,255,255,0.8) !important; }

/* Input area */
.input-container {
    padding: 12px 16px !important;
    background: white !important;
    border-top: 1px solid #e8edf3 !important;
}

.input-container input {
    border-radius: 24px !important;
    border: 1px solid #e2e8f0 !important;
    background: #f7f9fc !important;
}

footer { display: none !important; }
"""

with gr.Blocks(css=CSS, title="Vinmec AI Mobile") as demo:
    with gr.Column(elem_classes="phone-wrapper"):
        # 1. Status Bar
        gr.HTML("""
            <div class="status-bar">
                <span class="time">9:41</span>
                <div style="display:flex; gap: 6px; align-items:center;">
                    <span>●●●●</span>
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                    <span>95%</span>
                </div>
            </div>
        """)
        
        # 2. App Header
        gr.HTML("""
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
                </div>
            </div>
        """)
        
        # 3. Chatbot
        chatbot = gr.Chatbot(
            elem_id="chatbot",
            show_label=False,
            container=False,
            height=520,
            bubble_full_width=False,
        )
        
        # 4. Input Area
        with gr.Row(elem_classes="input-container"):
            msg = gr.Textbox(
                placeholder="Nhắn tin cho Vinmec...",
                show_label=False,
                container=False,
                scale=7
            )
            submit_btn = gr.Button("S", scale=1, variant="primary")

    # Examples (Chips-like)
    with gr.Row():
        gr.Examples(
            examples=["Tôi muốn đặt lịch khám tổng quát", "Tôi bị đau đầu", "Mấy tuổi thì khám nhi?"],
            inputs=msg,
            label="Gợi ý",
        )

    # Logic
    def handle_submit(message, history):
        response = chat_response(message, history)
        return "", history + [[message, response]]

    msg.submit(handle_submit, [msg, chatbot], [msg, chatbot])
    submit_btn.click(handle_submit, [msg, chatbot], [msg, chatbot])

if __name__ == "__main__":
    demo.launch()
