import tabula
import faiss
import json
import base64
import pymupdf
import requests
import os
import logging
import numpy as np
import warnings
from tqdm import tqdm # progress bar
from langchain_text_splitters import RecursiveCharacterTextSplitter
from IPython import display
import typing

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

warnings.filterwarnings("ignore")

# TODO write code for generating a filename
attention_url = "https://arxiv.org/pdf/1706.03762" # Attention is All You Need paper
attention_filename = "attention_paper.pdf"
# create data directory if it doesn't exist
os.makedirs("data", exist_ok=True) #TODO move to Orchestrator
attention_filepath = os.path.join("data", attention_filename)

def get_paper_from_url(url: str = attention_url, filename: str = attention_filename, directory: str = "data") -> None:
    filepath = os.path.join(directory, filename)
    response = requests.get(url)
    if response.status_code == 200:
        with open(filepath, 'wb') as file:
            file.write(response.content)
        print(f"File downloaded successfully: {filepath}")
    else:
        print(f"Failed to download file, status code: {response.status_code}")
        
def generate_filename():
    pass

def create_directories(base_directory: str = "data") -> None:
    directories = ["images", "tables", "text", "page_images"]
    for d in directories:
        os.makedirs(os.path.join(base_directory, d), exist_ok=True)
        
# Process tables
def process_tables(filepath, page_num: int, items: list, base_dir: str = "data") -> None:
    try:
        tables = tabula.read_pdf(filepath, pages=page_num + 1, multiple_tables=True)
        if not tables:
            return
        for table_idx, table in enumerate(tables):
            table_text = "\n".join([" | ".join(map(str, row)) for row in table.values])
            table_file_name = f"{base_dir}/tables/{os.path.basename(filepath)}_table_{page_num}_{table_idx}.txt"
            with open(table_file_name, 'w') as f:
                f.write(table_text)
            items.append({"page": page_num, "type": "table", "text": table_text, "path": table_file_name})
    except Exception as e:
        print(f"Error extracting tables from page {page_num}: {str(e)}")

# Process text chunks
def process_text_chunks(filepath, text, text_splitter, page_num, base_dir, items):
    chunks = text_splitter.split_text(text)
    for i, chunk in enumerate(chunks):
        text_file_name = f"{base_dir}/text/{os.path.basename(filepath)}_text_{page_num}_{i}.txt"
        with open(text_file_name, 'w') as f:
            f.write(chunk)
        items.append({"page": page_num, "type": "text", "text": chunk, "path": text_file_name})

# Process images
def process_images(filepath, doc, page, page_num, base_dir, items):
    images = page.get_images()
    for idx, image in enumerate(images):
        xref = image[0]
        pix = pymupdf.Pixmap(doc, xref)
        image_name = f"{base_dir}/images/{os.path.basename(filepath)}_image_{page_num}_{idx}_{xref}.png"
        pix.save(image_name)
        with open(image_name, 'rb') as f:
            encoded_image = base64.b64encode(f.read()).decode('utf8')
        items.append({"page": page_num, "type": "image", "path": image_name, "image": encoded_image})

# Process page images
def process_page_images(page, page_num, base_dir, items):
    pix = page.get_pixmap()
    page_path = os.path.join(base_dir, f"page_images/page_{page_num:03d}.png")
    pix.save(page_path)
    with open(page_path, 'rb') as f:
        page_image = base64.b64encode(f.read()).decode('utf8')
    items.append({"page": page_num, "type": "page", "path": page_path, "image": page_image})
    
# Creating the directories
# TODO move to Orchestrator, instantiate text splitter in Orchestrator and pass to process_pdf
create_directories("data")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=200, length_function=len)
items = []
   
def process_pdf(text_splitter, base_dir: str = "data", items: list = items, filepath: str = attention_filepath) -> None:
    try:
        # Open pdf file, creating a pymupdf Document object
        # filetype is optional, specifying pdf restricts this method to opening only pdfs
        doc = pymupdf.open(filepath, filetype="pdf")
        num_pages = len(doc)
        # Process each page of the PDF 
        for page_num in tqdm(range(num_pages), desc="Processing PDF pages"):
            page = doc[page_num] # Document page
            text = page.get_text()
            process_tables(filepath, page_num, items, base_dir)
            process_text_chunks(filepath, text, text_splitter, page_num, base_dir, items)
            process_images(filepath, doc, page, page_num, base_dir, items)
            process_page_images(page, page_num, base_dir, items)        
    except Exception as e:
        print(f"Failed to process document at {filepath}: {str(e)} ")
    

    
    
# display pdf
# display.IFrame(filepath, width=1000, height=600)

# get_paper_from_url(url='https://ml-site.cdn-apple.com/papers/the-illusion-of-thinking.pdf', filename="illusion_of_thinking.pdf")

process_pdf(text_splitter)
# table items
table_items = [i for i in items if i['type'] == 'table']

# text items
text_items = [i for i in items if i['type'] == 'text']

# image items
image_items = [i for i in items if i['type'] == 'image']

print(f"number of tables: {len(table_items)}")
print(f"number of text items: {len(text_items)}")
print(f"number of images: {len(image_items)}")

print()
if len(table_items) > 0:
    print("first table")
    print(table_items[0])
print()
if len(text_items) > 1:
    print("2nd text item")
    print(text_items[1])
print()
if len(image_items) > 0:
    image_0 = image_items[0]
    print("attributes of 1st image")
    print(image_0['path'])
    print(image_0['image'][:10])

