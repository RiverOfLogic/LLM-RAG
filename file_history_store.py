import os,json
from langchain_core.messages import message_to_dict, messages_from_dict,BaseMessage
from langchain_core.chat_history import BaseChatMessageHistory

class FileChatMessageHistory(BaseChatMessageHistory):
    def __init__(self,session_id,storage_path="./chatfile"):
        self.session_id = session_id #会话ID
        self.storage_path = storage_path #不同会话id的存储文件，所在的文件夹路径

        self.file_path = os.path.join(self.storage_path,self.session_id)

        #确保文件夹存在
        os.makedirs(os.path.dirname(self.file_path),exist_ok=True)

    def add_messages(self,messages) -> None:
        all_messages = list(self.messages)
        all_messages.extend(messages)

        #写入本地文件中
        new_messages = [message_to_dict(message) for message in all_messages]

        with open(self.file_path,"w",encoding="utf-8") as f:
            json.dump(new_messages,f)
    
    @property
    def messages(self) -> list[BaseMessage]:
        try:
            with open(self.file_path,"r",encoding="utf-8") as f:
                messages_data = json.load(f)
                return messages_from_dict(messages_data)
        except FileNotFoundError:
            return []
    
    def clear(self) -> None:
        with open(self.file_path,"w",encoding="utf-8") as f:
            json.dump([],f)
            
def get_history(session_id):
    return FileChatMessageHistory(session_id,"./chatfile")