# REPLACE EMPTY VALUES <..> FOR YOUR VALUES

# GCP VARIABLES ----------------------------- 

# GCP Setup

PROJECT =<PROJECT ID>
LOCATION=<REGION> # default "us"

# DocAI processors 

FORM_PROCESSOR_ID=<FORM PROCESSOR ID>
FORM_PROCESSOR_VERSION=<FORM PROCESSOR VERSION>
CDE_PROCESSOR_ID=<CDE PROCESSOR ID>
CDE_PROCESSOR_VERSION=<CDE PROCESSOR VERSION>

# UI OPTIONS ---------------------------------

APP_TYPE="chat" # options: ["search","chat"] 

# RAG OPTIONS -------------------------------- 

FILENAME="../docs/2024q1-alphabet-earnings-release-pdf_pg2.pdf" # only supports PDF files 
DOC_DESCRIPTION = "financial results from Alphabet Google, Includes things like revenues and operating income and operating margin"

# Parsing Unstructured Text Blocks

INCLUDE_UNSTRUCTURED_TEXT_PARSING = True # True or False. If True, requires a valid FORM_PROCESSOR_ID (See "DocAI processors" section)
CHUNK_SIZE=1000 # by number of tokens. Valid if INCLUDE_UNTRUCTURED_TEXT_PARSING = True 
CHUNK_OVERLAP=100 # by number of tokens. Valid if INCLUDE_UNTRUCTURED_TEXT_PARSING = True 

# Parsing Structured Tables

INCLUDE_TABLE_PARSING=True # True or False. If True, requires a valid FORM_PROCESSOR_ID (See "DocAI processors" section)
TABLE_CHUNKING_OPTIONS="by_table" # if INCLUDE_TABLE_PARSING is True. Options: "by_row" or "by_table". 

# Parsing Entities

INCLUDE_ENTITY_PARSING=True # True or False. If True, requires a valid CDE_PROCESSOR_ID (See "DocAI processors" section)

# Vector Search Options

EMBEDDINGS_MODEL="google-gecko" # options: "google-gecko"
RETRIEVER_DB="faiss" # options: "faiss"
LLM_MODEL="gemini" # options: "gemini"
