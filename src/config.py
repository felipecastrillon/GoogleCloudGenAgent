# GCP variables

PROJECT = "felipe-sandbox-354619"
LOCATION="us"

# GCP DocAI variables

FORM_PROCESSOR_ID="fe1b38732f911e11" 
FORM_PROCESSOR_VERSION="pretrained-form-parser-v2.1-2023-06-26"
CDE_PROCESSOR_ID="c25a7e228be5a2fd"
CDE_PROCESSOR_VERSION="pretrained-foundation-model-v1.0-2023-08-22"

# RAG Document Options 

FILENAME="../docs/I-9_doc.pdf" # only supports PDF files 

INCLUDE_UNSTRUCTURED_TEXT_PARSING = True # if True, requires a valid FORM_PROCESSOR_ID
CHUNK_SIZE=1000 # if INCLUDE_UNTRUCTURED_TEXT_PARSING is True 
CHUNK_OVERLAP=100 # if INCLUDE_UNTRUCTURED_TEXT_PARSING is True 

INCLUDE_TABLE_PARSING=True # if True, requires a valid FORM_PROCESSOR_ID
TABLE_CHUNKING_OPTIONS="by_row" # if INCLUDE_TABLE_PARSING is True. Options: "by_row" or "by_table". 

INCLUDE_KEY_VALUE_EXTRACTION=True # if True requires a valid CDE_PROCESSOR_ID  
KEYS_TO_SEARCH=["legal_name","effective_date","amount","issue_date"]

EMBEDDINGS_MODEL="google-gecko" # options: "google-gecko"
RETRIEVER_DB="faiss" # options: "faiss"
LLM_MODEL="gemini" # options: "gemini"
