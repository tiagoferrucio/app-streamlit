import os
import PyPDF2
import re
import json
import oci

from langchain.text_splitter import RecursiveCharacterTextSplitter,CharacterTextSplitter

def load_oci_config():
    # read OCI config to connect to OCI with API key
    # are you using default profile?
    oci_config = oci.config.from_file("~/.oci/config", "DEFAULT")

    return oci_config

def read_pdf(files):
    all_text = []
    
    for file in files:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)
                
        for page_num in range(num_pages):
            page = reader.pages[page_num]
            text = page.extract_text()
            text = re.sub(r'\_+', '', text)
            text = text.replace('DO NOT DISTRIBUTE OR SHARE OUTSIDE OF ORACLE', '')
            text = text.replace('Oracle Confidential - Restricted', '')
            text = re.sub(r'CSA Sales Guide Release October\s+\[\s*\],\s*2023', '', text)
            text = text.replace('\uf0b7', '')
            text = re.sub(r'Page \d+', '', text)
            text = re.sub(r'\s+', ' ', text)
            all_text.append(text)
        
    return "\n".join([str(el) for el in all_text])

def text_translate(text_document, config):
    
    ai_language_client = oci.ai_language.AIServiceLanguageClient(config)
    
    text_doc = oci.ai_language.models.TextDocument(
        key="example1",
        text=text_document,
        language_code="en"
    )
    
    text_translation = ai_language_client.batch_language_translation(
    batch_language_translation_details=oci.ai_language.models.BatchLanguageTranslationDetails(
        documents=[text_doc],
        target_language_code="pt"
    )
    )

    return text_translation.data.documents[0].translated_text

def text_chunk(text):
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len,
        is_separator_regex=True,
        separators=[
            r"(?<=\.) ",
        ],
    )
    
    # Divide o texto em chunks com base em frases
    chunks = splitter.split_text(text)
    
    return chunks