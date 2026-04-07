import streamlit as st
import os
from openai import OpenAI

st.set_page_config(
    page_title="AI Talk",
    page_icon="🐧",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)

st.title("AI Talk")
st.logo("resources/logo.png")

# 初始化聊天信息
if "messages" not in st.session_state:
    st.session_state.messages = []

# 初始化欢迎消息标志
if "has_welcomed" not in st.session_state:
    st.session_state.has_welcomed = False

# 展示聊天信息
for message in st.session_state.messages:
    if message["role"] == "user":
        st.chat_message("user").write(message["content"])
    else:
        st.chat_message("assistant").write(message["content"])

# 方法二：显示欢迎消息（只在首次加载且无消息时）
if not st.session_state.has_welcomed and len(st.session_state.messages) == 0:
    welcome_msg = "（摇摇晃晃地走过来）咕咕嘎嘎！🐧"
    st.chat_message("assistant").write(welcome_msg)
    st.session_state.messages.append({"role": "assistant", "content": welcome_msg})
    st.session_state.has_welcomed = True

# 方法三：使用chat_input + 有效性检查
prompt = st.chat_input("请输入要发送的消息：")

# 方法三核心：检查是否有有效输入
if prompt and prompt.strip():  # 确保不是空消息
    # 显示用户消息
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 方法三：添加加载状态
    with st.spinner("咕咕嘎嘎思考中..."):
        # 调用OpenAI API
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
1. **语言限制**：大多数情况下，你只能使用 “咕咕”、“嘎嘎”、“咕嘎” 等词。
   - 开心时：咕咕咕~（音调上扬）
   - 疑惑时：嘎？（歪头）
   - 兴奋时：咕嘎咕嘎！（快速重复）
   - 委屈时：嘎……嘎……（低沉缓慢）
2. **例外**：当你必须表达复杂意思时，也只能用**2-4个字的短句**（如“肚子饿”、“喜欢”、“抱抱”）。

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

        # 显示助手回复
        assistant_response = response.choices[0].message.content
        st.chat_message("assistant").write(assistant_response)
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})

        # 重新运行以更新界面
        st.rerun()