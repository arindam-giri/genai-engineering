import os
import yaml
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma


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
        print(f"Vector database not found at '{persist_directory}'. Please run vector_creator.py first.")
        return

    print(f"Loading vector database from '{persist_directory}'...")
    embeddings = OllamaEmbeddings(model=embedding_model, base_url=ollama_base_url)
    
    # Load the existing Chroma vector database
    vector_store = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )
    
    print(f"\nSearching for: '{query}'")
    # Perform similarity search
    results = vector_store.similarity_search(query, k=k)
    
    if not results:
        print("No matching results found.")
        return

    print(f"\n--- Top {len(results)} Results ---")
    for i, doc in enumerate(results, 1):
        source = doc.metadata.get('source', 'Unknown')
        page = doc.metadata.get('page', 'Unknown')
        print(f"\nResult {i} (Source: {source}, Page: {page}):")
        print(doc.page_content)
        print("-" * 50)

if __name__ == "__main__":
    # A simple interactive loop for retrieval
    print("Welcome to the Document Retrieval System!")
    print("Type 'exit' or 'quit' to stop.")
    
    while True:
        user_query = input("\nEnter your query: ")
        if user_query.lower() in ['exit', 'quit']:
            break
            
        if user_query.strip():
            retrieve_documents(user_query)
