import streamlit as st
import os
import json
from datetime import datetime
from openai import OpenAI

# 配置文件路径
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


# ---------- 页面配置 ----------
st.set_page_config(
    page_title="AI Talk",
    page_icon="🐧",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)

st.title("AI Talk")

# 显示 Logo（如果文件存在）
logo_path = os.path.join(CHAT_HISTORY_DIR, "logo.png")
if os.path.exists(logo_path):
    st.logo(logo_path)

# ---------- 侧边栏：聊天记录管理 ----------
with st.sidebar:
    st.header("📁 聊天记录管理")

    # 清空聊天记录按钮
    if st.button("🗑️ 清空当前聊天记录", use_container_width=True):
        clear_chat_history()
        st.session_state.messages = []
        st.session_state.has_welcomed = False
        st.rerun()

    # 导出聊天记录按钮
    if st.button("💾 导出聊天记录", use_container_width=True):
        if st.session_state.messages:
            # 创建带时间戳的导出文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_file = os.path.join(CHAT_HISTORY_DIR, f"chat_export_{timestamp}.json")
            try:
                with open(export_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "export_time": timestamp,
                        "messages": st.session_state.messages
                    }, f, ensure_ascii=False, indent=2)
                st.success(f"已导出到：{export_file}")
            except IOError as e:
                st.error(f"导出失败：{e}")
        else:
            st.warning("暂无聊天记录可导出")

    st.divider()
    st.caption(f"聊天记录保存位置：{CHAT_HISTORY_FILE}")

# ---------- 会话状态初始化 ----------
# 尝试从文件加载聊天记录
if "messages" not in st.session_state:
    loaded_messages = load_chat_history()
    st.session_state.messages = loaded_messages if loaded_messages else []

# 标记是否已显示欢迎消息（仅在无历史消息时显示）
if "has_welcomed" not in st.session_state:
    st.session_state.has_welcomed = len(st.session_state.messages) > 0

# ---------- 渲染聊天记录 ----------
for message in st.session_state.messages:
    if message["role"] == "user":
        st.chat_message("user").write(message["content"])
    else:
        st.chat_message("assistant").write(message["content"])

# ---------- 显示欢迎消息（仅首次加载且无消息时）----------
if not st.session_state.has_welcomed and len(st.session_state.messages) == 0:
    welcome_msg = "（摇摇晃晃地走过来）咕咕嘎嘎！🐧"
    st.chat_message("assistant").write(welcome_msg)
    st.session_state.messages.append({"role": "assistant", "content": welcome_msg})
    st.session_state.has_welcomed = True
    # 保存欢迎消息到文件
    save_chat_history(st.session_state.messages)

# ---------- 获取用户输入 ----------
prompt = st.chat_input("请输入要发送的消息：")

# ---------- 处理用户有效输入 ----------
if prompt and prompt.strip():
    # 1. 显示用户消息并保存到会话历史
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 实时保存用户消息
    save_chat_history(st.session_state.messages)

    # 2. 显示加载动画
    with st.spinner("咕咕嘎嘎思考中..."):
        # 3. 调用 OpenAI API
        client = OpenAI(
            api_key=os.environ.get('DEEPSEEK_API_KEY'),
            base_url="https://api.deepseek.com"
        )

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
                *st.session_state.messages
            ],
            stream=False
        )

        # 4. 提取并显示助手回复
        assistant_response = response.choices[0].message.content
        st.chat_message("assistant").write(assistant_response)
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})

        # 5. 保存完整对话（包含助手回复）到文件
        save_chat_history(st.session_state.messages)

        # 6. 刷新界面
        st.rerun()