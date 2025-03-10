import chromadb
from fastapi import FastAPI, Path, Request
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel
import uvicorn
from backend.data_models.data_models import Corrections, MessageRequest
from service import correct_text, grammar_query, learn_characters
from pathlib import Path
import fitz  # PyMuPDF
import re

app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware
import random

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def initialize_grammar_chroma():
    """
    Initialize ChromaDB and load documents into the collection specifically for the
    previous grammar examples.

    Returns:
        The ChromaDB collection.
    """
    print("Initializing ChromaDB")

    chroma_client = chromadb.PersistentClient(path="./chroma_cache")

    # uncomment this line to reset the chroma cache, if needed
    # chroma_client.reset()

    # Get or create collection
    try:
        collection = chroma_client.get_collection(name="grammar_docs")
    except:
        collection = chroma_client.create_collection(name="grammar_docs")
        
        # Load and process the grammar_example.txt file
        docs_dir = Path("backend/static_docs")
        grammar_example_path = docs_dir / "grammar_examples.txt"
        with open(grammar_example_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=50,
            chunk_overlap=0
        )
        texts = text_splitter.split_text(content)
        
        # Add documents to collection with unique identifiers
        doc_id_prefix = grammar_example_path.stem  # Use the file name (without extension) as the prefix
        print(f"starting upload for {doc_id_prefix}")
        collection.add(
            documents=texts,
            ids=[f"{doc_id_prefix}_id{i}" for i in range(len(texts))],
            metadatas=[{"doc_id": doc_id_prefix} for _ in range(len(texts))]
        )
        print(f"done uploading {doc_id_prefix}")
    return collection


# Currently discontinued this function due to long wait times to ingest document using this 
# text splitter function. Retaining code for future reference. 
def chinese_character_pdf_text_splitter(text: str) -> list:
    """
    Custom text splitter to split the chinese character pdf into sections based on the pattern provided.

    Args:
        text (str): The text to split.

    Returns:
        list: A list of text sections.
    """
    pattern = re.compile(r'\d{1,4}[\u4e00-\u9fff].*?\[.*?STROKES RANK \d+\]', re.DOTALL)
    matches = pattern.findall(text)
    return matches

def initialize_chinese_characters_chroma():
    """
    Initialize ChromaDB and load Chinese characters information into the collection.

    Returns:
        The ChromaDB collection.
    """
    print("Initializing Chinese Characters ChromaDB")
    chroma_client = chromadb.PersistentClient(path="./chroma_cache")
    # chroma_client.reset()

    # Get or create collection
    try:
        collection = chroma_client.get_collection(name="chinese_characters_explanations")
    except:
        collection = chroma_client.create_collection(name="chinese_characters_explanations")
        
        # Load and process the PDF file
        docs_dir = Path("backend/static_docs")
        pdf_path = docs_dir / "chinese-characters-learn-amp-remember-2178-characters-and-their-meanings-0982232403-9780982232408_compress.pdf"
        doc = fitz.open(pdf_path)
        content = ""
        for page in doc:
            content += page.get_text()
        
        # Split into sections
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=250,
            chunk_overlap=10
        )
        texts = text_splitter.split_text(content)
        
        # Add documents to collection with unique identifiers
        doc_id_prefix = pdf_path.stem  # Use the file name (without extension) as the prefix
        print(f"starting upload for {doc_id_prefix}")
        collection.add(
            documents=texts,
            ids=[f"{doc_id_prefix}_id{i}" for i in range(len(texts))],
            metadatas=[{"doc_id": doc_id_prefix} for _ in range(len(texts))]
        )
        print(f"done uploading {doc_id_prefix}")
    return collection


async def romance_language_corrections(message: str, language: str):
    """
    Get corrections for a romance language message.

    Args:
        message (str): The message to correct.
        language (str): The target language.

    Returns:
        dict: The reply and corrections.
    """''
    
    corrections = await correct_text(message, language)

    # Get only the explanations from the corrections
    correction_list = [correction['explanation'] for correction in corrections]

    # Using the explanations of the corrections, query the collection for similar mistakes
    results = collection.query(
        query_texts=correction_list,
        n_results=5
    )

    context = " ".join([doc for doc in results['documents'][0]])

    # Send list of corrections and returned query results to an LLM call
    reply = await grammar_query(context=context, corrections=" ".join(correction_list))

    return {
        "reply": "Similar mistakes you've made before: \n" + reply, 
        "corrections": corrections
    }

async def chinese_language_corrections(message: str, language: str):
    """
    Get corrections for a Chinese language message.

    Args:
        message (str): The message to correct.
        language (str): The target language.

    Returns:
        dict: The reply and corrections.
    """

    corrections = await correct_text(message, language)

    # Get only the corrected words from the provided corrections
    words_list = " ".join([correction['corrected'] for correction in corrections])

    # Take a random 5 words from the corrected sentences
    words = words_list.split()
    random_words = random.sample(words, min(5, len(words)))

    # Query the collection for each of the random words
    results = []
    results = chinese_characters_collection.query(
        query_texts=random_words,
        n_results=5
    )
    context = " ".join([doc for doc in results['documents'][0]])
    
    # Send list of corrected words and returned query results to an LLM call
    reply = await learn_characters(pinyin_words=" ".join(random_words), context=context)
    
    return {
        "reply": "Learn these five characters \n" + reply, 
        "corrections": corrections
    }

@app.post("/send")
async def send_message(request: MessageRequest):
    """
    Handle the /send endpoint to process a message and return corrections.

    Args:
        request (MessageRequest): The request containing the message and language.

    Returns:
        dict: The reply and corrections.
    """

    print(f"Received message: {request.message}")
    print(f"Language: {request.language}")
    
    if request.language == "chinese":
        return await chinese_language_corrections(request.message, request.language)
    else:
        return await romance_language_corrections(request.message, request.language)

@app.get("/")
async def read_root():
    """
    Handle the root endpoint.

    Returns:
        dict: A welcome message.
    """
    return {"message": "Welcome to the FastAPI application!"}

if __name__ == "__main__":
    collection = initialize_grammar_chroma()
    chinese_characters_collection = initialize_chinese_characters_chroma()
    uvicorn.run(app, host="0.0.0.0", port=8000)