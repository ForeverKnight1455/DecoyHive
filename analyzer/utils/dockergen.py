import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("honeypot.log"),
        logging.StreamHandler()
    ]
)

# Load environment variables from .env file
load_dotenv()

def get_project_root():
    """Get the project root directory."""
    # Get the directory containing this file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to get to the analyzer directory
    analyzer_dir = os.path.dirname(current_dir)
    # Go up one more level to get to the project root
    return os.path.dirname(analyzer_dir)

def generate_dockerfile(json_file: str, output_directory: str = ".") -> bool:
    """
    Generate a Dockerfile based on system configuration.
    
    Args:
        json_file (str): Path to the configuration JSON file
        output_directory (str): Directory where the Dockerfile will be saved
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get project root and make paths absolute
        project_root = get_project_root()
        json_file = os.path.join(project_root, json_file)
        output_directory = os.path.join(project_root, output_directory)
        
        # Ensure output directory exists
        os.makedirs(output_directory, exist_ok=True)
        
        # Read and validate config file
        if not os.path.exists(json_file):
            logging.error(f"Config file not found: {json_file}")
            return False
            
        with open(json_file, "r") as f:
            config = json.load(f)
        
        # Configure the Google Gemini API key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logging.error("GEMINI_API_KEY not found in environment variables")
            return False
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        system_instruction = """You will receive a JSON file containing detailed information about a computer system.  
This includes:
- Hardware specifications (CPU, RAM, Storage, etc.)
- Installed software and applications  
- Running services  
- Network configurations  
- User accounts  

### **Task:**  
1. Analyze the provided JSON input.  
2. Generate a **Dockerfile** that accurately replicates the system's environment inside a container.  
3. Ensure that the Dockerfile includes all necessary installations, configurations, and services.  

### **Important Instructions:**  
- **Only** return the Dockerfile **without** using any formatting markers like ```dockerfile or ```.  
- Do **not** include any explanations, comments, or additional text—just the raw Dockerfile content.  
- If certain hardware or configurations are not directly replicable in Docker, approximate them using software-based equivalents.  
"""

        prompt = json.dumps(config, indent=2)

        # Generate the content
        response = model.generate_content(
            [system_instruction, prompt],
            generation_config={
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
        )

        dockerfile_content = response.text

        # Write the Dockerfile
        dockerfile_path = os.path.join(output_directory, "Dockerfile")
        with open(dockerfile_path, "w") as file:
            file.write(dockerfile_content)

        logging.info(f"Dockerfile has been successfully written to {dockerfile_path}")
        return True

    except Exception as e:
        logging.error(f"Error generating Dockerfile: {str(e)}")
        return False

if __name__ == "__main__":
    # Example usage with relative paths from project root
    config_file = "config_exports/config.json"
    output_dir = "output"
    generate_dockerfile(config_file, output_dir)
