from pathlib import Path

cwd = str(Path.cwd())
PROJECT = <PROJECT_ID> 
LOCATION="us"
PROCESSOR_ID="fe1b38732f911e11"
PROCESSOR_VERSION="pretrained-form-parser-v2.1-2023-06-26"
HAS_TABLES="true"
FILENAME= "../docs/alphabet-earnings-release.pdf"
SPLITTER="text" 
CHUNK_SIZE=1000
CHUNK_OVERLAP=100
EMBEDDINGS="google-gecko"
RETRIEVER="faiss"
LLM_MODEL="gemini"
