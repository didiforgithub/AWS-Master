from sentence_transformers import SentenceTransformer
# import typing like List etc
from typing import List
import openai
import os
import numpy as np
import faiss
import pickle
import hashlib
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.document_loaders import TextLoader
from langchain.document_loaders import TextLoader
from langchain.document_loaders import PyPDFLoader
openai.api_key = "sk-hzqDmA2VFMqIXEOo4aE36e753fC145808178FcDcA6D3627d"
openai.api_base = "https://api.ai-yyds.com/v1"


class FaissDB:
    """
    vectorize the ./data folder and store it in a faiss name by md5hash
    """
    def __init__(self, dim, path='./data'):
        self.dim = dim
        self.path = path
        # list the filesname in the path, and get the total md5hash
        files = [f for f in os.listdir(path) if f.endswith('.pdf') and not f.endswith('db')]

        self.hashes = hashlib.md5(','.join(files).encode('utf-8')).hexdigest()
        self.db_file_path = path + f"/{self.hashes}.db"
        self.index = None
        self.key2vector = {}
        
        # 加载已存在的数据库
        if os.path.exists(self.db_file_path):
            print('Loading database from', self.db_file_path)
            self._load_db()
        else:
            print('Creating new database', self.db_file_path)
            self._init_db()

    def _init_db(self):
        # 初始化数据库
        self.index = faiss.IndexFlatIP(self.dim) # cosine is better than L2?

    def _load_db(self):
        # 加载数据库
        with open(self.db_file_path, 'rb') as f:
            data = pickle.load(f)
            self.index = faiss.deserialize_index(data['index'])
            self.key2vector = data['key2vector']

    def _save_db(self):
        # 保存数据库
        with open(self.db_file_path, 'wb') as f:
            data = {
                'index': faiss.serialize_index(self.index),
                'key2vector': self.key2vector,
            }
            pickle.dump(data, f)

    def put(self, key, vector):
        # 存储向量
        # assert key not in self.key2vector, "The key already exists in the database."
        assert len(vector) == self.dim, "The dimension of the vector does not match the database."
        self.key2vector[key] = np.array(vector, dtype=np.float32)
        self.index.add(np.array([self.key2vector[key]]))
    
    def save(self):
        self._save_db()

    def search(self, vector, k=1, thresh=0.8):
        # 搜索向量
        assert len(vector) == self.dim, "The dimension of the vector does not match the database."
        vector = np.array([vector], dtype=np.float32)
        D, I = self.index.search(vector, k)
        # normalize each vector
        D = D / np.linalg.norm(D, axis=1, keepdims=True)
        keys = []
        distances = []
        for i, d in zip(I[0], D[0]):
            # 对于L2距离，阈值应该是最大距离
            # 对于余弦相似性，阈值应该是最小距离
            if d > thresh:  # 修改这里以适应你的度量
                keys.append(list(self.key2vector.keys())[i])
                distances.append(d)
        return keys, distances

    def remove(self):
        # 删除向量数据库文件
        os.remove(self.db_file_path)

def get_embedding(sentences:List[str], model_name='paraphrase-MiniLM-L6-v2'): # all-MiniLM-L6-v2
    list_of_embeddings = []
    model = SentenceTransformer(model_name) # https://huggingface.co/sentence-transformers
    for sentence in sentences:
        embedding = model.encode(sentence)
        list_of_embeddings.append(embedding)
    return list_of_embeddings

def split_into_sentences(pdf_name="test.pdf",chunk_size=1000,chunk_overlap=20):
    """
    return ["str","str2"]
    """
    loader = PyPDFLoader(pdf_name)
    text_splitter = RecursiveCharacterTextSplitter(
        # Set a really small chunk size, just to show.
        chunk_size = chunk_size,
        chunk_overlap  = chunk_overlap,
        length_function = len,
        is_separator_regex = False,
    )
    # check pkl file
    
    pages = loader.load_and_split(text_splitter=text_splitter)
    # pickle.dump(pages, open("pages.pkl", "wb"))
    return [page.page_content for page in pages]    

def llm_call(model:str="gpt-3.5-turbo", prompt:str="Hello world"):
    # make a call to gpt 
    response = openai.Completion.create(
        model=model,
        prompt=prompt,
        temperature=0.5,
        max_tokens=100,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response

def query_pdf_folder(queries:List[str], pdf_folder="./data", model_name='all-MiniLM-L6-v2', dim = 384, chunk_size=1000, chunk_overlap=20):
    # calc db file name
    files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf') and not f.endswith('db')]
    pdf_names = [pdf_folder + '/' + f for f in files if f.endswith('.pdf') and not f.endswith('db')]
    print(pdf_names)
    hashes = hashlib.md5(','.join(files).encode('utf-8')).hexdigest()
    vdb_name = pdf_folder + f'/{hashes}.db'
    # check if pdf is stored in FAISS, if not, create a new database
    if not os.path.exists(vdb_name):
        print('Creating new database', vdb_name)
        vdb = FaissDB(dim=dim, path=pdf_folder)
        for pdf in pdf_names:
            # split pdf
            print('Splitting pdf into sentences:', pdf)
            sentences = split_into_sentences(pdf) # return ["str","str2"]
            # get embeddings of pdf 
            print('Getting embeddings:',pdf)
            embeddings = get_embedding(sentences, model_name) # return [vector1, vector2]  
            print('Putting embeddings into database:',pdf)
            # put embeddings into database, key is the content of sentences
            for key, vector in zip(sentences, embeddings):
                vdb.put(key, vector)
            vdb.save()
        print('database created at ', vdb_name)
    else:
        print('Loading database from', vdb_name)
        vdb = FaissDB(dim=dim, path=pdf_folder)
        print('database loaded from ', vdb_name)
    
    # search text for each query
    print('Searching')
    response = {}
    for query in queries:
        print('Query:', query)
        # get embeddings of query
        query_embedding = get_embedding([query], model_name)[0]
        # search database
        results = vdb.search(query_embedding, k=10, thresh=0.33)
        response[query] = results
    return response
        