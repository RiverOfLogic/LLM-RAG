"""
基于Streamlit完成web网页上传
"""
import streamlit as st
from knowledge_base import KnowledgeBaseService
import time

#添加网页标题
st.title("知识库更新服务")

#文件上传
uploader_file = st.file_uploader(
    label="请上传txt文件",
    type=['txt'],
    accept_multiple_files=False)

if "service" not in st.session_state:
    st.session_state["service"] = KnowledgeBaseService()

if uploader_file is not None:
    file_name = uploader_file.name
    file_type = uploader_file.type
    file_size = uploader_file.size/1024

    st.subheader(f"文件名：{file_name}")
    st.write(f"格式:{file_type} | 大小：{file_size:.4f} kb")

    #获取内容
    text = uploader_file.getvalue().decode("utf-8")

    with st.spinner("载入知识库中..."):
        time.sleep(1)
        result = st.session_state["service"].upload_by_str(text,file_name)
        st.write(result)