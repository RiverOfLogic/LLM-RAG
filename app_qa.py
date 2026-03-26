import streamlit as st
from rag import RagService
import config_data as config


st.set_page_config(
    page_title="猫娘",
    page_icon="😽",
    layout="centered",
    initial_sidebar_state="expanded"
)
#标题
st.title("😽猫娘🐱")
st.divider() #分隔符

if "message" not in st.session_state:
    st.session_state["message"] = [{"role":"assistant","content":"你好呀！"}]

if "rag" not in st.session_state:
    st.session_state["rag"] = RagService()

for message in st.session_state["message"]:
    st.chat_message(message["role"]).write(message["content"])

#用户输入
prompt = st.chat_input()

if prompt:
    #在页面输出
    st.chat_message("user").write(prompt)
    st.session_state["message"].append({"role":"user","content":prompt})

    with st.spinner("猫娘思考中🐱🐈🐈‍⬛"):
        res_stream = st.session_state["rag"].chain.stream({"input":prompt},config.session_config)
        res = st.chat_message("assistant").write_stream(res_stream)
        st.session_state["message"].append({"role":"assistant","content":res})