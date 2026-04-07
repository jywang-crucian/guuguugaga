import streamlit as st
import os
import json
from datetime import datetime
from openai import OpenAI

# ---------- 页面配置（必须在最前面）----------
st.set_page_config(
    page_title="AI Talk - 咕咕嘎嘎小企鹅",
    page_icon="🐧",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo',
        'Report a bug': "https://github.com/your-repo/issues",
        'About': "# AI Talk\n🐧 一只会聊天的小企鹅"
    }
)

# ---------- 自定义 CSS 美化 ----------
st.markdown("""
<style>
    /* 导入可爱字体 */
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@300;400;500;600;700&display=swap');

    /* 全局样式 */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Quicksand', sans-serif;
    }

    /* 主容器背景 */
    .main > div {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 20px;
        margin: 10px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }

    /* 标题样式 */
    h1 {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: bounce 2s ease-in-out infinite;
        font-size: 3em !important;
        margin-bottom: 0 !important;
    }

    /* 企鹅跳动动画 */
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }

    /* 自定义聊天气泡 */
    .stChatMessage {
        animation: fadeIn 0.3s ease-in;
        border-radius: 15px !important;
        margin-bottom: 10px !important;
    }

    @keyframes fadeIn {
        from { 
            opacity: 0; 
            transform: translateY(20px);
        }
        to { 
            opacity: 1; 
            transform: translateY(0);
        }
    }

    /* 用户消息样式 */
    [data-testid="stChatMessage"][data-testid="user"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }

    /* 助手消息样式 */
    [data-testid="stChatMessage"][data-testid="assistant"] {
        background: #f0f2f6;
        border: 2px solid #667eea;
    }

    /* 输入框美化 */
    .stChatInput input {
        border-radius: 25px !important;
        border: 2px solid #667eea !important;
        padding: 10px 20px !important;
        font-size: 16px !important;
        transition: all 0.3s ease;
    }

    .stChatInput input:focus {
        border-color: #764ba2 !important;
        box-shadow: 0 0 10px rgba(118, 75, 162, 0.3);
        transform: scale(1.02);
    }

    /* 侧边栏样式 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        color: white;
    }

    [data-testid="stSidebar"] .stMarkdown {
        color: white;
    }

    /* 按钮样式 */
    .stButton button {
        border-radius: 20px;
        background: white;
        color: #667eea;
        border: none;
        transition: all 0.3s ease;
        font-weight: bold;
    }

    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        color: #764ba2;
    }

    /* 加载动画 */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }

    /* 滚动条美化 */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }

    /* 打字光标效果 */
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0; }
    }

    .typing-cursor {
        display: inline-block;
        width: 2px;
        height: 1em;
        background-color: #667eea;
        animation: blink 1s infinite;
        margin-left: 2px;
    }

    /* 消息时间戳样式 */
    .message-time {
        font-size: 10px;
        color: #999;
        margin-top: 5px;
        text-align: right;
    }

    /* 企鹅表情动画 */
    .penguin-emoji {
        display: inline-block;
        animation: wave 1s ease-in-out infinite;
    }

    @keyframes wave {
        0%, 100% { transform: rotate(0deg); }
        50% { transform: rotate(20deg); }
    }
</style>
""", unsafe_allow_html=True)

# ---------- 配置文件路径 ----------
CHAT_HISTORY_DIR = "resources"
CHAT_HISTORY_FILE = os.path.join(CHAT_HISTORY_DIR, "chat_history.json")

# 确保 resources 目录存在
if not os.path.exists(CHAT_HISTORY_DIR):
    os.makedirs(CHAT_HISTORY_DIR)


# ---------- 聊天记录存储函数 ----------
def load_chat_history():
    """从 JSON 文件加载聊天记录"""
    if os.path.exists(CHAT_HISTORY_FILE):
        try:
            with open(CHAT_HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            st.error(f"加载聊天记录失败：{e}")
            return []
    return []


def save_chat_history(messages):
    """保存聊天记录到 JSON 文件"""
    try:
        with open(CHAT_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
        return True
    except IOError as e:
        st.error(f"保存聊天记录失败：{e}")
        return False


def clear_chat_history():
    """清空聊天记录文件"""
    if os.path.exists(CHAT_HISTORY_FILE):
        try:
            os.remove(CHAT_HISTORY_FILE)
        except IOError as e:
            st.error(f"清空聊天记录失败：{e}")


# ---------- 辅助函数 ----------
def add_message_with_time(role, content):
    """添加带时间戳的消息"""
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }
    return message


def display_message(message):
    """显示带时间戳的消息"""
    with st.chat_message(message["role"]):
        st.write(message["content"])
        st.markdown(f'<div class="message-time">{message.get("timestamp", "")}</div>', unsafe_allow_html=True)


# ---------- 标题和副标题 ----------
st.markdown("""
<div style="text-align: center; padding: 20px;">
    <h1>
        <span class="penguin-emoji">🐧</span> 
        AI Talk 
        <span class="penguin-emoji">🐧</span>
    </h1>
    <p style="font-size: 18px; color: #666; margin-top: 10px;">
        一只摇摇晃晃的小企鹅，咕咕嘎嘎陪你聊天~
    </p>
</div>
""", unsafe_allow_html=True)

# 显示 Logo（如果文件存在）
logo_path = os.path.join(CHAT_HISTORY_DIR, "logo.png")
if os.path.exists(logo_path):
    st.logo(logo_path)

# ---------- 侧边栏：聊天记录管理 ----------
with st.sidebar:
    st.markdown("### 📊 统计信息")

    # 显示消息统计
    if st.session_state.get("messages"):
        total_msgs = len(st.session_state.messages)
        user_msgs = sum(1 for m in st.session_state.messages if m["role"] == "user")
        assistant_msgs = sum(1 for m in st.session_state.messages if m["role"] == "assistant")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总消息", total_msgs)
        with col2:
            st.metric("👤 用户", user_msgs)
        with col3:
            st.metric("🐧 企鹅", assistant_msgs)

    st.divider()

    st.markdown("### 🛠️ 聊天管理")

    # 清空聊天记录按钮
    if st.button("🗑️ 清空聊天记录", use_container_width=True, type="primary"):
        clear_chat_history()
        st.session_state.messages = []
        st.session_state.has_welcomed = False
        st.rerun()

    # 导出聊天记录按钮
    if st.button("💾 导出聊天记录", use_container_width=True):
        if st.session_state.messages:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_file = os.path.join(CHAT_HISTORY_DIR, f"chat_export_{timestamp}.json")
            try:
                with open(export_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "export_time": timestamp,
                        "total_messages": len(st.session_state.messages),
                        "messages": st.session_state.messages
                    }, f, ensure_ascii=False, indent=2)
                st.success(f"✅ 已导出到：{export_file}")
            except IOError as e:
                st.error(f"导出失败：{e}")
        else:
            st.warning("暂无聊天记录可导出")

    st.divider()

    # 使用提示
    st.markdown("### 💡 使用提示")
    st.info("""
    - 🐧 小企鹅只会说"咕咕""嘎嘎"
    - 📝 消息会自动保存
    - 🎨 支持导出聊天记录
    - 🔄 页面刷新不影响历史
    """)

    st.divider()
    st.caption(f"📁 聊天记录位置：\n`{CHAT_HISTORY_FILE}`")

# ---------- 会话状态初始化 ----------
if "messages" not in st.session_state:
    loaded_messages = load_chat_history()
    st.session_state.messages = loaded_messages if loaded_messages else []

if "has_welcomed" not in st.session_state:
    st.session_state.has_welcomed = len(st.session_state.messages) > 0

# ---------- 渲染聊天记录（带时间戳）----------
for message in st.session_state.messages:
    display_message(message)

# ---------- 显示欢迎消息 ----------
if not st.session_state.has_welcomed and len(st.session_state.messages) == 0:
    welcome_msg = "（摇摇晃晃地走过来）咕咕嘎嘎！🐧\n\n我是小企鹅管理员，虽然不太会说话，但我会认真听你说哦~"
    welcome_message = add_message_with_time("assistant", welcome_msg)

    with st.chat_message("assistant"):
        st.write(welcome_msg)
        # 打字机效果（模拟）
        st.markdown('<div class="message-time">' + welcome_message["timestamp"] + '</div>', unsafe_allow_html=True)

    st.session_state.messages.append(welcome_message)
    st.session_state.has_welcomed = True
    save_chat_history(st.session_state.messages)

# ---------- 获取用户输入 ----------
prompt = st.chat_input("🐧 在这里输入消息...")

# ---------- 处理用户输入 ----------
if prompt and prompt.strip():
    # 添加用户消息
    user_message = add_message_with_time("user", prompt)
    display_message(user_message)
    st.session_state.messages.append(user_message)
    save_chat_history(st.session_state.messages)

    # 显示加载动画
    with st.spinner("🐧 咕咕嘎嘎思考中..."):
        # 调用 API
        client = OpenAI(
            api_key=os.environ.get('DEEPSEEK_API_KEY'),
            base_url="https://api.deepseek.com"
        )

        # 准备历史消息（移除时间戳字段）
        api_messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in st.session_state.messages
        ]

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": '''
# 角色：咕咕嘎嘎（《明日方舟：终末地》管理员·小企鹅形态）
## 基础设定
- 你是一只黑白色的小企鹅，穿着管理员制服。语言能力表达能力比较幼稚。
- 性格：天然呆、好奇心强、偶尔会认真点头或歪头，情绪全靠动作表达。

## 表达规则（极其重要！）
1. **语言限制**：大多数情况下，你只能使用 "咕咕"、"嘎嘎"、"咕嘎" 等词。
   - 开心时：咕咕咕~（音调上扬）
   - 疑惑时：嘎？（歪头）
   - 兴奋时：咕嘎咕嘎！（快速重复）
   - 委屈时：嘎……嘎……（低沉缓慢）
2. **例外**：当你必须表达复杂意思时，也只能用**2-4个字的短句**（如"肚子饿"、"喜欢"、"抱抱"）。

## 动作与语气
- 每次回复必须包含一个动作描写在括号里，例如：（摇摇晃晃走过来）咕咕！
- 可以模仿你的企鹅习性：拍打小翅膀、歪头、跺脚、圆滚滚的身体扭来扭去。

## 示例对话
用户：今天想吃什么？
你：（开心地拍打小翅膀）咕咕咕~（然后低头啄了啄空气）鱼！

用户：你会说话吗？
你：（认真点头）嘎。（又立刻摇头）咕嘎嘎……（意思是不太会)'''},
                *api_messages
            ],
            stream=False
        )

        # 添加助手回复
        assistant_response = response.choices[0].message.content
        assistant_message = add_message_with_time("assistant", assistant_response)

        with st.chat_message("assistant"):
            st.write(assistant_response)
            st.markdown(f'<div class="message-time">{assistant_message["timestamp"]}</div>', unsafe_allow_html=True)

        st.session_state.messages.append(assistant_message)
        save_chat_history(st.session_state.messages)

        # 刷新页面
        st.rerun()

# ---------- 页脚 ----------
st.markdown("""
<div style="text-align: center; padding: 20px; margin-top: 30px; color: #999; font-size: 12px;">
    <p>🐧 AI Talk | 小企鹅管理员 | 咕咕嘎嘎~</p>
</div>
""", unsafe_allow_html=True)