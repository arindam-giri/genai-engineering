import urllib.request
import json

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
    
    print(f"Sending request to local Ollama (Model: {payload['model']})...")
    print("Waiting for response...\n")
    
    try:
        # Execute the request
        with urllib.request.urlopen(req) as response:
            result_str = response.read().decode('utf-8')
            result_json = json.loads(result_str)
            
            print("=== Response ===")
            result = result_json["message"]["content"]
            print(result)
            print("================")
            return result
            
    except urllib.error.URLError as e:
        print(f"Error: Could not connect to Ollama ({e.reason}).")
        print("Please ensure that Ollama is running locally on port 11434.")
        print("Command to run Ollama (if not running): ollama run gemma4:26b")
        return "unable to generate reponse"
    except Exception as e:
        print(f"An error occurred: {e}")
        return "unable to generate reponse"

if __name__ == "__main__":
    call_llm()
