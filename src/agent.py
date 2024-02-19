
import langchain as lc
import vertexai
import pdb
import vertexai.preview.generative_models as generative_models
from vertexai.preview.generative_models import GenerativeModel
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
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
    if config.SPLITTER == "text":
      
      # read document using DocAI parser
      parser = DocAIParser() 
      proc_document = parser.process_document()
      all_text = parser.read_text(proc_document)
      
      # split docs into splits
      text_splitter = RecursiveCharacterTextSplitter(chunk_size = config.CHUNK_SIZE,
                                             chunk_overlap=config.CHUNK_OVERLAP)
      documents = []
      splits = text_splitter.create_documents([all_text])    
      for split in splits:
        documents.append(split.page_content)
    
      # add tables if document has tables
      if (config.HAS_TABLES == "true"):
        tables = parser.read_tables(proc_document)
        for table in tables:
          documents.append(table) 


    else:
      raise ValueError("splitter input must be one of the following values [\"text\"]") 

    print("Read text document. Character length: " + str(len(all_text)))
    
    # create embeddings
    embed_model = None
    if config.EMBEDDINGS == "google-gecko":
      embed_model= VertexAIEmbeddings()
    else:
      raise ValueError("splitter input must be one of the following values [\"google-gecko\"]") 
    
    # create retriever 
    db = None
    if config.RETRIEVER == "faiss":
      self.db = FAISS.from_documents(splits, embed_model)         
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
    for doc in nearby_documents:
      context += doc.page_content + "\n\n"
    context += "END CONTEXT \n"
    instructions = "Please answer the below question based on the context above: \n"
    prompt = context + instructions + user_query

    # get response
    @retry(stop=stop_after_attempt(3))
    def generate(prompt):
      responses=[]    
      try:
        responses = self.llm_model.generate_content(
          prompt,
          generation_config={
            "max_output_tokens": 2048,
            "temperature": 0.9,
            "top_p": 1
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
       
      answers = [response.text for response in responses]
      return answers[0] 
    
    response = generate(prompt)
    return response

  
