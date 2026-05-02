import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(name)s: %(message)s')
import json
import urllib.request

def call_llm(query: str):
    # Default Ollama local endpoint for chat
    url = "http://localhost:11434/api/chat"
    
    payload = {
        "model": "gemma4:26b",
        "messages": [
            {
                "role": "user",
                "content": query
            }
        ],
        # Set stream to False to get the entire response at once
        "stream": False
    }
    
    # Convert the payload to JSON bytes
    data = json.dumps(payload).encode('utf-8')
    
    # Prepare the request
    req = urllib.request.Request(
        url, 
        data=data, 
        headers={'Content-Type': 'application/json'}
    )
    
    logger.info(f"Sending request to local Ollama (Model: {payload['model']})...")
    logger.info("Waiting for response...\n")
    
    try:
        # Execute the request
        with urllib.request.urlopen(req) as response:
            result_str = response.read().decode('utf-8')
            result_json = json.loads(result_str)
            
            logger.info("=== Response ===")
            result = result_json["message"]["content"]
            logger.info(result)
            logger.info("================")
            return result
            
    except urllib.error.URLError as e:
        logger.error(f"Error: Could not connect to Ollama ({e.reason}).")
        logger.error("Please ensure that Ollama is running locally on port 11434.")
        logger.error("Command to run Ollama (if not running): ollama run gemma4:26b")
        return "unable to generate reponse"
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        return "unable to generate reponse"

if __name__ == "__main__":
    call_llm()
