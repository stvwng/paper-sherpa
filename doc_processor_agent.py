# import tabula
# import faiss
import json
import base64
# import pymupdf
import requests
import os
import logging
import numpy as np
import warnings
from tqdm import tqdm
from langchain_text_splitters import RecursiveCharacterTextSplitter
from IPython import display

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

warnings.filterwarnings("ignore")

# TODO write code for generating a filename
attention_url = "https://arxiv.org/pdf/1706.03762" # Attention is All You Need paper
attention_filename = "attention_paper.pdf"
# create data directory if it doesn't exist
os.makedirs("data", exist_ok=True) #TODO move to Orchestrator

def get_paper_from_url(url=attention_url, filename=attention_filename, directory="data"):
    filepath = os.path.join(directory, filename)
    response = requests.get(url)
    if response.status_code == 200:
        with open(filepath, 'wb') as file:
            file.write(response.content)
        print(f"File downloaded successfully: {filepath}")
    else:
        print(f"Failed to download file, status code: {response.status_code}")
    
    
# display pdf
# display.IFrame(filepath, width=1000, height=600)

get_paper_from_url()
