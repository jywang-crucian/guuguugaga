import streamlit as st
import os
import json
from datetime import datetime
from openai import OpenAI
import requests
import base64

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


# ========== 登录功能 ==========
def check_password():
    """密码验证函数"""

    # 从 Secrets 获取密码（安全）
    if 'ADMIN_PASSWORD' in st.secrets:
        correct_password = st.secrets['ADMIN_PASSWORD']
    else:
        # 默认密码（仅用于测试，部署后务必在 Secrets 中设置）
        correct_password = "123456"
        st.warning("⚠️ 请在生产环境配置 ADMIN_PASSWORD 密码！")

    # 初始化登录状态
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    # 如果已经登录，直接返回 True
    if st.session_state.authenticated:
        return True

    # 显示登录界面
    st.markdown("""
    <div style="text-align: center; padding: 50px;">
        <h1>🐧 AI Talk</h1>
        <p style="font-size: 18px; color: #666;">请输入密码继续</p>
    </div>
    """, unsafe_allow_html=True)

    # 创建登录表单
    with st.form("login_form"):
        password = st.text_input("密码", type="password", placeholder="请输入访问密码")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            submitted = st.form_submit_button("登录", use_container_width=True)

        if submitted:
            if password == correct_password:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ 密码错误！")

    return False


# 检查登录状态（放在页面配置之后，其他内容之前）
if not check_password():
    st.stop()  # 未登录，停止执行后续代码
# ========== 登录功能结束 ==========


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


# ---------- GitHub 存储函数 ----------
def load_from_github():
    """从 GitHub 仓库加载聊天记录"""
    try:
        # 检查是否配置了 GitHub Secrets
        if 'GITHUB_TOKEN' not in st.secrets or 'GITHUB_REPO' not in st.secrets:
            st.info("💡 首次使用，未配置 GitHub 存储，将使用本地会话存储")
            return []

        url = f"https://api.github.com/repos/{st.secrets['GITHUB_REPO']}/contents/resources/chat_history.json"
        headers = {
            "Authorization": f"token {st.secrets['GITHUB_TOKEN']}",
            "Accept": "application/vnd.github.v3+json"
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.json()
            decoded = base64.b64decode(content['content']).decode('utf-8')
            messages = json.loads(decoded)
            st.success("✅ 已从 GitHub 加载聊天记录")
            return messages
        elif response.status_code == 404:
            # 文件不存在，返回空列表
            return []
        else:
            st.warning(f"加载失败: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"从 GitHub 加载失败: {e}")
        return []


def save_to_github(messages):
    """保存聊天记录到 GitHub 仓库"""
    try:
        # 检查是否配置了 GitHub Secrets
        if 'GITHUB_TOKEN' not in st.secrets or 'GITHUB_REPO' not in st.secrets:
            return False

        url = f"https://api.github.com/repos/{st.secrets['GITHUB_REPO']}/contents/resources/chat_history.json"
        headers = {
            "Authorization": f"token {st.secrets['GITHUB_TOKEN']}",
            "Accept": "application/vnd.github.v3+json"
        }

        # 准备要保存的内容
        content = json.dumps(messages, ensure_ascii=False, indent=2)
        encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')

        # 先检查文件是否存在
        response = requests.get(url, headers=headers)
        sha = None
        if response.status_code == 200:
            # 文件存在，获取 sha 用于更新
            sha = response.json().get('sha')
        elif response.status_code == 404:
            # 文件不存在，将在下面创建
            pass
        else:
            # 其他错误（如权限问题）
            st.error(f"检查 GitHub 文件时出错: {response.status_code}")
            return False

        # 构建请求数据
        data = {
            "message": f"更新聊天记录 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "content": encoded_content,
            "branch": "master"
        }

        # 只有在更新已存在的文件时才需要 sha
        if sha:
            data["sha"] = sha

        # 发送请求
        response = requests.put(url, headers=headers, json=data)

        if response.status_code in [200, 201]:
            return True
        else:
            st.error(f"保存失败: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        st.error(f"保存到 GitHub 失败: {e}")
        return False


# ---------- 辅助函数 ----------
def add_message_with_time(role, content):
    """添加带时间戳的消息"""
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "full_time": datetime.now().isoformat()
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
logo_path = "resources/logo.png"
if os.path.exists(logo_path):
    st.logo(logo_path)

# ---------- 侧边栏：聊天记录管理 ----------
with st.sidebar:
    st.markdown("### 📊 统计信息")

    # 显示 GitHub 存储状态
    if 'GITHUB_TOKEN' in st.secrets and 'GITHUB_REPO' in st.secrets:
        st.success("💾 GitHub 存储已启用")
    else:
        st.warning("⚠️ GitHub 存储未配置\n聊天记录仅保存在当前会话")

    st.divider()

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

    # 手动保存按钮
    if st.button("💾 手动保存到 GitHub", use_container_width=True):
        if st.session_state.messages:
            if save_to_github(st.session_state.messages):
                st.success("✅ 保存成功！")
            else:
                st.error("❌ 保存失败，请检查配置")
        else:
            st.warning("暂无消息可保存")

    # 清空聊天记录按钮
    if st.button("🗑️ 清空聊天记录", use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.session_state.has_welcomed = False
        # 清空 GitHub 上的记录
        save_to_github([])
        st.rerun()

    # 导出聊天记录按钮
    if st.button("💾 导出聊天记录", use_container_width=True):
        if st.session_state.messages:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_file = f"chat_export_{timestamp}.json"
            try:
                with open(export_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "export_time": timestamp,
                        "total_messages": len(st.session_state.messages),
                        "messages": st.session_state.messages
                    }, f, ensure_ascii=False, indent=2)
                with open(export_file, 'r', encoding='utf-8') as f:
                    st.download_button(
                        label="📥 点击下载",
                        data=f.read(),
                        file_name=export_file,
                        mime="application/json"
                    )
            except Exception as e:
                st.error(f"导出失败：{e}")
        else:
            st.warning("暂无聊天记录可导出")

    st.divider()

    # 使用提示
    st.markdown("### 💡 使用提示")
    st.info("""
    - 🐧 小企鹅只会说"咕咕""嘎嘎"
    - 💾 配置 GitHub 后记录永久保存
    - 🔄 重新部署后记录自动恢复
    - 📝 支持导出聊天记录
    """)

    st.divider()
    if 'GITHUB_REPO' in st.secrets:
        st.caption(f"📁 存储位置：\n`{st.secrets['GITHUB_REPO']}`")

# ---------- 会话状态初始化 ----------
if "messages" not in st.session_state:
    # 尝试从 GitHub 加载
    loaded_messages = load_from_github()
    if loaded_messages:
        st.session_state.messages = loaded_messages
    else:
        st.session_state.messages = []
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
        st.markdown('<div class="message-time">' + welcome_message["timestamp"] + '</div>', unsafe_allow_html=True)

    st.session_state.messages.append(welcome_message)
    st.session_state.has_welcomed = True
    # 保存到 GitHub
    save_to_github(st.session_state.messages)

# ---------- 获取用户输入 ----------
prompt = st.chat_input("🐧 在这里输入消息...")

# ---------- 处理用户输入 ----------
if prompt and prompt.strip():
    # 添加用户消息
    user_message = add_message_with_time("user", prompt)
    display_message(user_message)
    st.session_state.messages.append(user_message)
    # 保存到 GitHub
    save_to_github(st.session_state.messages)

    # 显示加载动画
    with st.spinner("🐧 咕咕嘎嘎思考中..."):
        # 获取 API Key
        if hasattr(st, 'secrets') and 'DEEPSEEK_API_KEY' in st.secrets:
            api_key = st.secrets["DEEPSEEK_API_KEY"]
        else:
            api_key = os.environ.get('DEEPSEEK_API_KEY')

        if not api_key:
            st.error("❌ 未找到 API Key！请在 Streamlit Cloud 的 Secrets 中设置 DEEPSEEK_API_KEY")
            st.stop()

        # 调用 API
        client = OpenAI(
            api_key=api_key,
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
        # 保存到 GitHub
        save_to_github(st.session_state.messages)

        # 刷新页面
        st.rerun()

# ---------- 页脚 ----------
st.markdown("""
<div style="text-align: center; padding: 20px; margin-top: 30px; color: #999; font-size: 12px;">
    <p>🐧 AI Talk | 小企鹅管理员 | 咕咕嘎嘎~</p>
</div>
""", unsafe_allow_html=True)