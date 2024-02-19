# Introduction

A customizable GenAI RAG application using Google Cloud components:
- Gemini: LLM 
- Cloud Run: app deployment
- DocAI: document parsing  

This project also uses the following open source components
- gradio: UI 
- langchain: orchestration of RAG components

The project has the following customizable components in src/config.py
- Text split chunk size and chunk overlap
- Select your own DocAI parser
- Include table parsing 

Roadmap:
- Add links to UI 
- Read more than one file
- Read files from GCS 
- Include Vertex Vector Search as a retrieval source
- Better retrieval based on document metadata (year, customer, etc...)
- Evaluation job of RAG model for accuracy

# Requirements
A Google Cloud Platform project
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

Edit src/config.py to include your GCP project:
```
PROJECT = <PROJECT_ID> 
```

## Runing Locally

Find the location of the json service account file and run on terminal:
```
export GOOGLE_APPLICATION_CREDENTIALS = <SERVICE ACCOUNT FILE LOCATION>
```

Clone this terminal and run:
```
cd src
python main.py
```

## Running in Cloud Run

Modify Dockerfile to include your own project:
```
ENV GOOGLE_CLOUD_PROJECT <PROJECT_ID> 
```

Deploy to cloud run:
```
gcloud run deploy <ANY APP NAME> --source . --region <REGION> --service-account=<SERVICE_ACCOUNT>
```



