
import langchain as lc
import vertexai
import pdb
import vertexai.preview.generative_models as generative_models
from vertexai.preview.generative_models import GenerativeModel
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain.schema.document import Document
from tenacity import retry, stop_after_attempt
from parser import DocAIParser
import config
import logging
import os

class Agent:
  
  def __init__(self):
    items = os.listdir(os.getcwd())
    obj = []
    for item in items:
      obj.append(item)
    logging.warning(os.getcwd())
    logging.warning(",".join(obj))
    # load file
    documents = []
      
    # initialize DocAI parser
    parser = DocAIParser() 
    proc_document = parser.process_document()
    chunks = []
    
    # if document has tables
    table_indexes = []
    if (config.INCLUDE_TABLE_PARSING == True):
      tables, table_indexes = parser.read_tables(proc_document)
      for table in tables:
        doc =  Document(page_content=table, metadata={"source": "local"})
        chunks.append(doc) 
    
    # if document has unstructured text 
    if (config.INCLUDE_UNSTRUCTURED_TEXT_PARSING == True):
      unstructured_text = parser.read_text(proc_document, config.INCLUDE_TABLE_PARSING, table_indexes)
      text_splitter = RecursiveCharacterTextSplitter(chunk_size = config.CHUNK_SIZE,
                                           chunk_overlap=config.CHUNK_OVERLAP)
      chunks += text_splitter.create_documents([unstructured_text])    
      
    else:
      raise ValueError("splitter input must be one of the following values [\"text\"]") 

    # create embeddings
    embed_model = None
    if config.EMBEDDINGS_MODEL == "google-gecko":
      embed_model= VertexAIEmbeddings()
    else:
      raise ValueError("splitter input must be one of the following values [\"google-gecko\"]") 
    
    # create retriever 
    db = None
    if config.RETRIEVER_DB == "faiss":
      self.db = FAISS.from_documents(chunks, embed_model)         
    else:
      raise ValueError("splitter input must be one of the following values [\"faiss\"]") 
    
    # initialize model
    self.llm_model = ""
    if config.LLM_MODEL == "gemini":
       self.llm_model = GenerativeModel("gemini-pro")
    else:
      raise ValueError("splitter input must be one of the following values [\"gemini\"]") 

  def run(self,user_query):

    # create prompt
    nearby_documents = self.db.similarity_search(user_query)
    context = "CONTEXT: \n"
    for i,doc in enumerate(nearby_documents):
      context += "[" + str(i) + "] \"..." + doc.page_content + "...\"\n\n\n"
    context += "END CONTEXT \n"
    instructions = "Please answer the question based on the context above: \n"
    prompt = context + instructions + user_query
    print(prompt)

    response = self.generate(prompt)
    return [response, context]

  # get response
  @retry(stop=stop_after_attempt(3))
  def generate(self, prompt):
    responses=[]    
    try:
      responses = self.llm_model.generate_content(
        prompt,
        generation_config={
          "max_output_tokens": 2048,
          "temperature": 0.2,
        },
        safety_settings={
          generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
          generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
          generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
          generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        },
        stream=True,
      )
    except Exception as inst:
      print ("Exception: " + str(inst)) 
     
    answers = ""
    for response in responses:
      answers+=response.text  
    return answers
    

  
