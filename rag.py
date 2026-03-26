from vector_stores import VectorStoreService
from langchain_community.embeddings import DashScopeEmbeddings
import config_data as config
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from file_history_store import get_history
from langchain_core.runnables import RunnableLambda
import streamlit as st

class RagService(object):
    def __init__(self):
        dashscope_api_key = st.secrets.get("DASHSCOPE_API_KEY")
        self.vector_service = VectorStoreService(
            embedding=DashScopeEmbeddings(model=config.embedding_model_name, dashscope_api_key=dashscope_api_key))
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system","你是一个法学家。这是你的参考资料:“{context}”。"),
                MessagesPlaceholder("history"),
                ("human","{input}")
            ]
        )
        self.chat_model = ChatTongyi(model=config.chat_model_name,api_key=dashscope_api_key)
        self.chain = self._get_chain()
    
    def _get_chain(self):
        """获取最终的执行链"""
        retriever = self.vector_service.get_retriever()

        def format_document(docs):
            if not docs:
                return "无相关参考资料"
            formatted_str = ""
            for doc in docs:
                formatted_str += f"文档片段：{doc.page_content}\n文档元数据：{doc.metadata}\n\n"
            return formatted_str
        
        def temp1(value):
            return value["input"]
        
        def temp2(value):
            new_value = {}
            new_value["input"] = value["input"]["input"]
            new_value["context"] = value["context"]
            new_value["history"] = value["input"]["history"]

            return new_value

        chain = (
            {"input":RunnablePassthrough(),
             "context":RunnableLambda(temp1) | retriever | format_document
            } |RunnableLambda(temp2)|self.prompt_template | self.chat_model | StrOutputParser()
        )

        conversation_chain = RunnableWithMessageHistory(
            chain,
            get_history,
            input_messages_key="input",
            history_messages_key="history",
        )

        return conversation_chain

if __name__ == "__main__":
    session_config = {
        "configurable":{
            "session_id":"user1"
        }
    }
    res = RagService().chain.invoke({"input":"你在干什么"},session_config)
    print(res)