import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(name)s: %(message)s')
import os
import yaml
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

def load_config(config_path="config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def create_vector_db():
    # Load configuration
    config = load_config()
    
    data_dir = config.get("data_dir", "data")
    persist_directory = config.get("chroma_persist_dir", "chroma_db")
    chunk_size = config.get("chunk_size", 1000)
    chunk_overlap = config.get("chunk_overlap", 200)
    embedding_model = config.get("embedding_model", "embeddinggemma:300m")
    ollama_base_url = config.get("ollama_base_url", "http://localhost:11434")

    # Ensure data directory exists
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    logger.info(f"Created '{data_dir}' directory. Please add PDF files there before running.")
        return

    logger.info(f"Scanning for PDFs in '{data_dir}'...")
    # Load all PDFs from the data directory
    loader = DirectoryLoader(data_dir, glob="**/*.pdf", loader_cls=PyPDFLoader)
    try:
        documents = loader.load()
    except Exception as e:
        print(f"Error loading PDFs: {e}")
        return
    
    if not documents:
        print(f"No PDF documents found in '{data_dir}'. Please add some PDFs and try again.")
        return

    logger.info(f"Successfully loaded {len(documents)} document pages.")
    
    logger.info("Splitting documents into chunks...")
    # Use RecursiveCharacterTextSplitter as requested
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split documents into {len(chunks)} chunks.")

    logger.info(f"Generating embeddings with local Ollama model '{embedding_model}'...")
    embeddings = OllamaEmbeddings(model=embedding_model, base_url=ollama_base_url)
    
    # Create and persist the vector database
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    
    logger.info(f"Vector database successfully created and persisted to '{persist_directory}'.")

if __name__ == "__main__":
    logger.info("Running as script: create vector DB...")
    create_vector_db()
