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
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain.vectorstores import FAISS
from langchain.document_loaders import TextLoader
from langchain.document_loaders import TextLoader
from langchain.document_loaders import PyPDFLoader
# openai.api_key = "sk-hzqDmA2VFMqIXEOo4aE36e753fC145808178FcDcA6D3627d"
# openai.api_base = "https://api.ai-yyds.com/v1"


class FaissDB:
    """
    vectorize the ./data folder and store it in a faiss name by md5hash
    """
    def __init__(self, dim, path='./data', model_name='all-MiniLM-L6-v2',chunk_size=1000, chunk_overlap=20):
        self.dim = dim
        self.path = path
        # list the filesname in the path, and get the total md5hash
        files = [f for f in os.listdir(path) if f.endswith('.pdf') and not f.endswith('db')]

        self.db_file_path = get_vdb_name(file_folder=path, model_name=model_name, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
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
        """
        仅仅针对单个shape为（1,dim）的向量来搜索结果
        """
        # 搜索向量
        assert len(vector) == self.dim, "The dimension of the vector does not match the database."
        vector = np.array([vector], dtype=np.float32)
        D, I = self.index.search(vector, k)
        # D means the distance, I means the index
        # [[0.6773209  0.64655405 0.6324411  0.6121055  0.59962755 0.59577274
        #  0.59391075 0.59079045 0.5902481  0.5859808 ]] [[ 3585  3504  5020 10079  3589  6009 10007  5873  8242  8262]]
        # normalize each vector
        keys = []
        distances = []
        for i, d in zip(I[0], D[0]):
            # 对于L2距离，阈值应该是最大距离
            # 对于余弦相似性，阈值应该是最小距离
            if d > thresh:  # 修改这里以适应你的度量
                try:
                    keys.append(list(self.key2vector.keys())[i])
                    distances.append(d)
                except:
                    continue
        return keys, distances

    def remove(self):
        # 删除向量数据库文件
        os.remove(self.db_file_path)

def get_embedding(sentences: List[str], file_name: str = '', model_name: str = 'paraphrase-MiniLM-L6-v2', data_path: str = "./data", chunk_size: int = 1000, chunk_overlap: int = 20):
    """
    将file_name+model_name+chunk_size+chunk_overlap+embeded组成一个pkl文件的名字。
    在embedding之前先检查本地./data是否存在对应的pkl文件，如果存在则加载并返回，如果不存在则进行embedding并保存为pkl文件，然后返回embedding结果。
    如果是对query进行embedding，则不涉及pkl文件，直接进行embedding并返回结果。
    """
    if file_name:
        pkl_file = f"{file_name}_{model_name}_{chunk_size}_{chunk_overlap}_embeded.pkl"

        if os.path.exists(pkl_file):
            with open(pkl_file, 'rb') as f:
                embeddings = pickle.load(f)
            return embeddings

        model = SentenceTransformer(model_name)
        embeddings = []
        for sentence in sentences:
            embedding = model.encode(sentence)
            embeddings.append(embedding)

        with open(pkl_file, 'wb') as f:
            pickle.dump(embeddings, f)

        return embeddings
    else:
        model = SentenceTransformer(model_name)
        embeddings = []
        for sentence in sentences:
            embedding = model.encode(sentence)
            embeddings.append(embedding)
        return embeddings


def split_into_sentences(file_folder= "./data",pdf_name="./data/test.pdf",chunk_size=1000,chunk_overlap=20):
    """
    检测本地是否存在已经split好的对象pkl，如果存在则直接返回，如果不存在则进行split并pkl
    对象名为：namemd5_chunk_size_chunk_overlap.pkl
    return ["str","str2"]
    """
    # check if there is a pkl file
    file_name_hash = hashlib.md5(pdf_name.encode('utf-8')).hexdigest()
    pkl_name = pdf_name + "_" + str(chunk_size) + "_" + str(chunk_overlap) +"_splited.pkl"
    if os.path.exists(pkl_name):
        # if there is a pkl file, then load it， return it
        return pickle.load(open(pkl_name, "rb"))
    # if there is no pkl file, then split it
    
    ## if it's a pdf    
    if pdf_name.endswith('.pdf'):
        loader = PyPDFLoader(pdf_name)
        text_splitter = RecursiveCharacterTextSplitter(
            # Set a really small chunk size, just to show.
            chunk_size = chunk_size,
            chunk_overlap  = chunk_overlap,
            length_function = len,
            is_separator_regex = False,
        )
        pages = loader.load_and_split(text_splitter=text_splitter)
        result = [page.page_content for page in pages]    
        # dump the pkl
        pickle.dump(result, open(pkl_name, "wb"))
    ## if it's a txt
    if pdf_name.endswith('.txt'):
        with open(pdf_name, 'r') as f:
            file_str = f.read()
        text_splitter = RecursiveCharacterTextSplitter(
            # Set a really small chunk size, just to show.
            chunk_size = chunk_size,
            chunk_overlap  = chunk_overlap,
            length_function = len,
            is_separator_regex = False,
        )
        pages = text_splitter.create_documents([file_str])
        result = [page.page_content for page in pages]    
        # dump the pkl
        pickle.dump(result, open(pkl_name, "wb"))
        
    ## if it's a md
    if pdf_name.endswith('.md'):
        with open(pdf_name, 'r') as f:
            file_str = f.read()
        text_splitter = RecursiveCharacterTextSplitter(
            # Set a really small chunk size, just to show.
            chunk_size = chunk_size,
            chunk_overlap  = chunk_overlap,
            length_function = len,
            is_separator_regex = False,
        )
        pages = text_splitter.create_documents([file_str])
        result = [page.page_content for page in pages]
    ## if it's a html
    if pdf_name.endswith('.html'):
        with open(pdf_name, 'r') as f:
            file_str = f.read()
        text_splitter = RecursiveCharacterTextSplitter(
            # Set a really small chunk size, just to show.
            chunk_size = chunk_size,
            chunk_overlap  = chunk_overlap,
            length_function = len,
            is_separator_regex = False,
        )
        pages = text_splitter.create_documents([file_str])
        result = [page.page_content for page in pages]
    return result

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


def get_vdb_name(file_folder="./data", model_name='all-MiniLM-L6-v2', chunk_size=1000, chunk_overlap=20):
    """
    vdb_name = hashes + model_name + chunk_size + chunk_overlap + '.db'
    """
    files = filter_names(os.listdir(file_folder))
    files.append(model_name)
    hashes = hashlib.md5(','.join(files).encode('utf-8')).hexdigest()
    vdb_name = file_folder + f'/{hashes}_{model_name}_{chunk_size}_{chunk_overlap}.db'
    return vdb_name


def filter_names(files):
    """
    仅仅保留pdf,html,txt,md结尾的文件
    """
    allowed_extensions = ['.pdf', '.html', '.txt', '.md']
    filtered_files = [file for file in files if file.endswith(tuple(allowed_extensions))]
    return filtered_files

def check_file_exist(file_name):
    return os.path.exists(file_name)

def query_folder(queries:List[str], file_folder="./data", model_name='all-MiniLM-L6-v2', k=10, thresh=0.33, dim = 384, chunk_size=1000, chunk_overlap=20):
    # calc db file name
    files = filter_names(os.listdir(file_folder))
    pdf_names = [file_folder + '/' + f for f in files]
    print(pdf_names)
    vdb_name = get_vdb_name(file_folder=file_folder, model_name=model_name, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    # check if pdf is stored in FAISS, if not, create a new database
    if not os.path.exists(vdb_name):
        print('Creating new database', vdb_name)
        vdb = FaissDB(dim=dim, path=file_folder, model_name=model_name, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        for pdf in pdf_names:
            # split pdf
            print('Splitting pdf into sentences:', pdf)
            sentences = split_into_sentences(file_folder= "./data", pdf_name=pdf, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            # get embeddings of pdf 
            print('Getting embeddings:',pdf)
            embeddings = get_embedding(file_name = pdf, sentences = sentences, chunk_size=chunk_size, chunk_overlap=chunk_overlap, model_name=model_name, data_path=file_folder) # return [vector1, vector2]sentences, model_name) # return [vector1, vector2]  
            print('Putting embeddings into database:',pdf)
            # put embeddings into database, key is the content of sentences
            for key, vector in zip(sentences, embeddings):
                vdb.put(key, vector)
            vdb.save()
        print('database created at ', vdb_name)
    else:
        print('Loading database from', vdb_name)
        vdb = FaissDB(dim=dim, path=file_folder, model_name=model_name, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        print('database loaded from ', vdb_name)
    
    # search text for each query
    print('Searching')
    response = {}
    query_embedding = get_embedding(sentences = queries, chunk_size=chunk_size, chunk_overlap=chunk_overlap, model_name=model_name, data_path=file_folder)
    print("query_embedding", type(query_embedding), len(query_embedding), query_embedding[0].shape)
    for i, vec in enumerate(query_embedding):
        print('Query:', queries[i])
        # get embeddings of query
        # search database
        keys, distances = vdb.search(vec, k=k, thresh=thresh)
        response[queries[i]] = keys
    return response
        
# db = FaissDB(768)
# db.put('hello', np.array([1.0]*768))
# db.put('helloooooo', np.array([1.2]*768))
# db.put('world', np.array([100.0]*768))
# db.search(np.array([1.1]*768),k=2)