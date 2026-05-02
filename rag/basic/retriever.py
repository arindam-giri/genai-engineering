import os
import yaml
import logging
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from llm import call_llm

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(name)s: %(message)s')

def load_config(config_path="config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def retrieve_documents(query, k=3):
    # Load configuration
    config = load_config()
    persist_directory = config.get("chroma_persist_dir", "chroma_db")
    embedding_model = config.get("embedding_model", "embeddinggemma:300m")
    ollama_base_url = config.get("ollama_base_url", "http://localhost:11434")
    
    if not os.path.exists(persist_directory):
        logger.info(f"Vector database not found at '{persist_directory}'. Please run vector_creator.py first.")
        return

    logger.info(f"Loading vector database from '{persist_directory}'...")
    embeddings = OllamaEmbeddings(model=embedding_model, base_url=ollama_base_url)
    
    # Load the existing Chroma vector database
    vector_store = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )
    
    logger.info(f"Searching for: '{query}'")
    # Perform similarity search
    results = vector_store.similarity_search(query, k=k)
    
    if not results:
        logger.warning("No matching results found.")
        return "No matching results found."

    logger.info(f"--- Top {len(results)} Results ---")
    result_list = []
    for i, doc in enumerate(results, 1):
        source = doc.metadata.get('source', 'Unknown')
        page = doc.metadata.get('page', 'Unknown')
        logger.info(f"Result {i} (Source: {source}, Page: {page}):")
        logger.info(doc.page_content)
        result_list.append(doc.page_content)
        print("-" * 50)
    return "\n".join(result_list)

base_prompt = "Analyse the user query and retrieved contents and respond."

if __name__ == "__main__":
    # A simple interactive loop for retrieval
    logger.info("Welcome to test retrieval")
    logger.info("Type 'exit' or 'quit' to stop.")
    
    while True:
        user_query = input("\nEnter your query: ")
        if user_query.lower() in ['exit', 'quit']:
            break
            
        if user_query.strip():
            vector_result = retrieve_documents(user_query)
            llm_input = base_prompt + "\n user query: " + user_query + "\n retrieved contents: " + vector_result
            llm_response = call_llm(llm_input)
            print(llm_response)
            
