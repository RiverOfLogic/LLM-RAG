"""
知识库
"""
import os
import config_data
import hashlib
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from datetime import datetime

def check_md5(md5_str):
    """
    检查传入的md5字符串是否已经被处理过了
    return False(文件未处理过)
    """
    if not os.path.exists(config_data.md5_path):
        open(config_data.md5_path,'w',encoding="utf-8").close()
        return False
    else:
        for line in open(config_data.md5_path,'r',encoding="utf-8").readlines():
            line = line.strip()
            if line ==md5_str:
                return True
        return False
    
def save_md5(md5_str):
    """传入的md5举例道文件保存"""
    with open(config_data.md5_path,'a',encoding="utf-8") as f:
        f.write(md5_str+'\n')

def get_string_md5(input_str,encoding="utf-8"):
    """传入的str转换为md5字符串"""
    str_bytes = input_str.encode(encoding=encoding)
    md5_obj = hashlib.md5()
    md5_obj.update(str_bytes)
    return md5_obj.hexdigest()

class KnowledgeBaseService(object):
    def __init__(self):
        os.makedirs(config_data.persist_directory,exist_ok=True)
        self.chroma = Chroma(
            collection_name=config_data.collection_name,
            embedding_function=DashScopeEmbeddings(model="text-embedding-v4"),
            persist_directory=config_data.persist_directory
        ) #向量存储的示例Chroma向量库对象
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=config_data.chunk_size,
            chunk_overlap=config_data.chunk_overlap,
            separators=config_data.separators,
            length_function=len
        ) #文本分割器的对象

    def upload_by_str(self,data,filename):
        """传入字符串向量化，存入向量数据库中"""
        md5_hex = get_string_md5(data)
        if check_md5(md5_hex):
            return "[skip]内容已在知识库中"
        if len(data)>config_data.max_spliter_char_number:
            knowledge_chunks = self.spliter.split_text(data)
        else:
            knowledge_chunks = [data]

        metadata = {
            "source":filename,
            "create_time":datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.chroma.add_texts(knowledge_chunks,
                              metadatas=[metadata for _ in knowledge_chunks])

        save_md5(md5_hex)
        return "[success]内容已成功载入向量库"

if __name__ == "__main__":
    service = KnowledgeBaseService()
    print(service.upload_by_str(data="杨宁",filename="testfile"))