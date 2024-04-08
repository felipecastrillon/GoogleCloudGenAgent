# REPLACE EMPTY VALUES <..> FOR YOUR VALUES

# GCP VARIABLES ----------------------------- 

# GCP Setup

PROJECT = <PROJECT_ID> 
LOCATION=<LOCATION> # default "us"

# DocAI processors 

FORM_PROCESSOR_ID=<ID> 
FORM_PROCESSOR_VERSION=<VERSION>
CDE_PROCESSOR_ID=<ID>
CDE_PROCESSOR_VERSION=<VERSION>


# RAG OPTIONS -------------------------------- 

FILENAME=<FILE_LOCATION_PATH> # only supports PDF files 

# Parsing Unstructured Text Blocks

INCLUDE_UNSTRUCTURED_TEXT_PARSING = True # True or False. If True, requires a valid FORM_PROCESSOR_ID (See "DocAI processors" section)
CHUNK_SIZE=1000 # by number of tokens. Valid if INCLUDE_UNTRUCTURED_TEXT_PARSING = True 
CHUNK_OVERLAP=100 # by number of tokens. Valid if INCLUDE_UNTRUCTURED_TEXT_PARSING = True 

# Parsing Structured Tables

INCLUDE_TABLE_PARSING=True # True or False. If True, requires a valid FORM_PROCESSOR_ID (See "DocAI processors" section)
TABLE_CHUNKING_OPTIONS="by_row" # if INCLUDE_TABLE_PARSING is True. Options: "by_row" or "by_table". 

# Parsing Entities

INCLUDE_ENTITY_PARSING=True # True or False. If True, requires a valid CDE_PROCESSOR_ID (See "DocAI processors" section)

# Vector Search Options

EMBEDDINGS_MODEL="google-gecko" # options: "google-gecko"
RETRIEVER_DB="faiss" # options: "faiss"
LLM_MODEL="gemini" # options: "gemini"
