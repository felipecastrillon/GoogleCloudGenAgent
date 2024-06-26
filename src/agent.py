
import langchain as lc
import vertexai
import pdb
import config
import logging
import os
import vertexai.preview.generative_models as generative_models
from vertexai.preview.generative_models import GenerativeModel
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings.vertexai import VertexAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores.faiss import FAISS
from langchain_community.llms import VertexAI
from langchain.agents import Tool
from langchain.schema.document import Document
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentType
from langchain.chains import RetrievalQA
from langchain.agents import initialize_agent
from langchain.tools.retriever import create_retriever_tool
from tenacity import retry, stop_after_attempt
from parser import DocAIParser



class Agent:
  
  def __init__(self):
    
    self.form_parser = None
    self.form_processed = None  
    self.chunks = []
    self.embed_model = None
    self.llm_model = None
    self.db = None
    self.retriever = None
    self.retriever_tool = None
    self.qa_chain = None
    self.retriever = None

    self.read_document()
    self.get_embeddings()
    self.create_retriever()
    self.initialize_model()


  def read_document(self):

    if (config.INCLUDE_TABLE_PARSING == True or config.INCLUDE_UNSTRUCTURED_TEXT_PARSING == True):
      self.form_parser = DocAIParser(config.PROJECT, config.LOCATION, config.FORM_PROCESSOR_ID , config.FORM_PROCESSOR_VERSION) 
      self.form_processed = self.form_parser.process_document()
    
    # if document has tables that you want to parse
    table_indexes = []
    if (config.INCLUDE_TABLE_PARSING == True):
      tables, table_indexes = self.form_parser.read_tables(self.form_processed)
      for table in tables:
        doc =  Document(page_content=table, metadata={"source": "local"})
        self.chunks.append(doc) 
    
    # if document has unstructured text that you want to parse
    if (config.INCLUDE_UNSTRUCTURED_TEXT_PARSING == True):
      unstructured_text = self.form_parser.read_text(self.form_processed, config.INCLUDE_TABLE_PARSING, table_indexes)
      text_splitter = RecursiveCharacterTextSplitter(chunk_size = config.CHUNK_SIZE,
                                           chunk_overlap=config.CHUNK_OVERLAP)
      self.chunks += text_splitter.create_documents([unstructured_text])    
     
    # if document has specific entities you want to extract 
    if (config.INCLUDE_ENTITY_PARSING == True):
      cde_parser = DocAIParser(config.PROJECT, config.LOCATION, config.CDE_PROCESSOR_ID , config.CDE_PROCESSOR_VERSION) 
      cde_processed = cde_parser.process_document()
      entities = cde_parser.read_entities(cde_processed)
      for entity in entities:
        doc = Document(page_content=entity, metadata={"source" : "local"})
        self.chunks.append(doc)

  def get_embeddings(self):

    # create embeddings from chunks
    if config.EMBEDDINGS_MODEL == "google-gecko":
      self.embed_model= VertexAIEmbeddings(model_name="textembedding-gecko")
    else:
      raise ValueError("splitter input must be one of the following values [\"google-gecko\"]") 
  
  def create_retriever(self):
    # create retriever 
    db = None
    if config.RETRIEVER_DB == "faiss":
      self.db = FAISS.from_documents(self.chunks, self.embed_model)  
      self.retriever  = self.db.as_retriever()       
      self.qa_chain = RetrievalQA.from_chain_type(llm=VertexAI(), chain_type="stuff", retriever=self.retriever)
      self.retriever_tool = create_retriever_tool(
                        name = "retrieval from financial documents for Alphabet and Google",
                        retriever = self.retriever,
                        description = config.DOC_DESCRIPTION
                      )
    else:
      raise ValueError("splitter input must be one of the following values [\"faiss\"]") 
    
    
  
  def initialize_model(self):
    self.llm_model = None
    if config.APP_TYPE == "search":
      # initialize genai model
      
      if config.LLM_MODEL == "gemini":
        self.llm_model = GenerativeModel("gemini-pro")
      else:
        raise ValueError("splitter input must be one of the following values [\"gemini\"]") 
    elif config.APP_TYPE == "chat":
      memory = ConversationBufferMemory(memory_key="chat_history")

      self.llm_model = initialize_agent(
        tools = [self.retriever_tool],
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        llm=VertexAI(), 
        memory=memory, 
        verbose=True,
    )
    else:
      raise ValueError("APP_TYPE config input must be one of the following values [\"chat\",\"search\"]")


  def search(self,user_query):

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
    

  def chat(self,user_query):
    if user_query:
      text = self.llm_model.run(user_query)
      return text
  
