# Introduction

![alt text](images/image1.png "APP UI")
![alt text](images/image2.png "Sample table from document")

A customizable GenAI RAG application using Google Cloud components:
- Gemini: LLM
- textembedding-gecko: embedding model
- Cloud Run: app deployment
- DocAI: document parsing  

The app also uses the following open source components:
- gradio: UI 
- langchain: orchestration of RAG components

The project has quick customizable options in [src/config.py](https://github.com/felipecastrillon/GenAIRagApp/blob/main/src/config.py):
- unstructured text parsing
- table parsing
- entity parsing
- advanced options for each parsing strategy

# Roadmap:
- :white_check_mark:  Add retrieval snippets to UI 
- :white_check_mark: Integrate DocAI Form Parser for tables. Remove table snippets from unstructured text parsing 
- :white_check_mark: Integrate DocAI GenAI CDE 2.0 parser for entity extraction
- :white_large_square: Read directory instead of one file
- :white_large_square: Read files from GCS 
- :white_large_square: Include Vertex Search as a retrieval source
- :white_large_square: Include Vertex Vector Search as a retrieval source
- :white_large_square: Filtered retrieval based on document metadata (year, customer, etc...)
- :white_large_square: Evaluation job of RAG model for accuracy
- :white_large_square: Add github actions

# Requirements
Google Cloud Platform (GCP) project
python version  >= 3.8

# Setup

## Google Cloud Project Setup

Enable the following APIs
- Cloud Document AI API
- Vertex AI API
- Cloud Run API
- Generative Language API

[Create Service Account](https://cloud.google.com/iam/docs/service-accounts-create) with following roles: 
- Vertex AI Administrator
- Document AI API User
- Cloud Run Developer

[Create a service account key](https://cloud.google.com/iam/docs/keys-create-delete#creating) which automatically downloads a json file with your key:

Next, edit src/config.py to include your GCP project:
```
PROJECT = <PROJECT_ID> 
```

## Setup Documents and Parser

Add the pdf document that you are trying to ask questions from to the "docs/" directory and modify src/config.py:
```
FILENAME=<DOCUMENT_LOCATION>
``` 

[Create a DocAI processor](https://cloud.google.com/document-ai/docs/create-processor) and modify src/config.py:

For this project you will need two processors of two different types: One is the FORM_PARSER_PROCESSOR ([setup](https://cloud.google.com/document-ai/docs/form-parser)) and the CUSTOM_EXTRACTION_PROCESSOR ([setup](https://cloud.google.com/document-ai/docs/custom-based-extraction)). The form parser will be used to parse unstructured text blocks and tables while the custom extraction processor will be used to pull entities. Note that the custom extraction processor has some new [Generative AI features](https://cloud.google.com/document-ai/docs/cde-with-genai) that make it easier to extract entities.

```
FORM_PROCESSOR_ID=<ID> 
FORM_PROCESSOR_VERSION=<VERSION>
CDE_PROCESSOR_ID=<ID>
CDE_PROCESSOR_VERSION=<VERSION>
```

## Running the App Locally or in Cloud Run

### Option: Runing Locally

Find the location of the json service account file that was downloaded and run on terminal:
```
export GOOGLE_APPLICATION_CREDENTIALS = <SERVICE ACCOUNT FILE LOCATION>
```

Clone this terminal and run:
```
cd src
python main.py
```

### Option: Running in Cloud Run

Modify Dockerfile to include your own project:
```
ENV GOOGLE_CLOUD_PROJECT <PROJECT_ID> 
```

Deploy to cloud run:
```
gcloud run deploy <ANY APP NAME> --source . --region <REGION> --service-account=<SERVICE_ACCOUNT>
```



