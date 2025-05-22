import os
import sys
from dotenv import load_dotenv, dotenv_values
from llama_parse import LlamaParse
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from utils.prompt_instructions import parsing_instruction

# Load environment variables
config = dotenv_values(".env")

openai_api_key = config.get("OPENAI_API_KEY")
openai_model = config.get("OPENAI_MODEL")
llama_cloud_api_key = config.get("LLAMA_CLOUD_API_KEY")

# Set up paths from environment variables or use defaults
input_dir = os.path.abspath(os.getenv("INPUT_DIR", "./data/data-input"))
output_dir = os.path.abspath(os.getenv("PARSED_MD_DIR", "./data/data-parsed-md"))

# Initialize OpenAI (GPT-4o) LLM
llm = OpenAI(model=openai_model)

# Initialize LlamaParse
parsing_instruction_to_use = """
The document provided may contain tables, images, and text. Extract all detailed information.
If the document contains images that illustrate examples or solutions to resolve cases, please extract and include detailed descriptions of these examples in the output.
"""

parser = LlamaParse(
    api_key=llama_cloud_api_key,
    user_prompt=parsing_instruction_to_use,
    result_type="markdown",
    use_vendor_multimodal_model=True,
    vendor_multimodal_model_name="openai-gpt4o",
    vendor_multimodal_model_api_key=openai_api_key,
    verbose=True
)

def process_file(input_path, rel_path):
    """Process a single file and save the parsed output."""
    try:
        # Create output path maintaining directory structure
        output_filename = f"{os.path.splitext(os.path.basename(input_path))[0]}_parsed.md"
        output_subdir = os.path.join(output_dir, rel_path)
        output_path = os.path.join(output_subdir, output_filename)

        if os.path.exists(output_path):
            print(f"File already exists: {output_path}")
            return

        # Create output directory if it doesn't exist
        os.makedirs(output_subdir, exist_ok=True)

        print(f"Processing: {input_path}")

        # Parse the entire document
        documents = parser.load_data(input_path)

        # Combine all parsed content into a single string
        total_pages = len(documents)
        combined_content = f'# Parsed content from "{os.path.join(rel_path, os.path.basename(input_path))}"\n\n'
        for i, doc in enumerate(documents):
            combined_content += f"# Page {i+1}/{total_pages}\n\n" + doc.text + "\n\n"

        # Save the combined parsed content
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(combined_content)
        print(f"Saved parsed content to {output_path}")

    except Exception as e:
        print(f"Error processing {input_path}: {str(e)}")

def process_directory(input_dir):
    """Recursively process all files in the input directory."""
    # File type that can be processed
    
    file_types = (".pdf", ".pptx", ".ppt", ".docx", ".doc", ".txt", ".csv", ".json", ".html", ".xml", ".png", ".jpeg", ".jpg")
    # Convert to absolute path
    input_dir = os.path.abspath(input_dir)
    print(f"\nScanning directory: {input_dir}")
    
    # Keep track of processed files
    file_count = 0
    
    # Walk through all directories and files
    for root, dirs, files in os.walk(input_dir):
        # Calculate the relative path from input_dir
        rel_path = os.path.relpath(root, input_dir)
        print(f"\nChecking directory: {root}")
        print(f"Found files: {files}")
        
        # Process each Excel file in the current directory
        for file in files:
            if file.lower().endswith(file_types):  # Handle both Excel, PDF, PowerPoint files
                file_count += 1
                input_path = os.path.join(root, file)
                print(f"\nFound file: {input_path}")
                process_file(input_path, rel_path)
    
    if file_count == 0:
        print("\nNo Excel or PDF files were found in the input directory!")
        print("Please check that:")
        print("1. The input directory path is correct")
        print("2. Excel/PDF files exist in the input directory")
        print(f"3. The script has access to read files in: {input_dir}")
    else:
        print(f"\nProcessed {file_count} files")

if __name__ == "__main__":
    # Create the base output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Start processing
    print(f"Starting to process files from {input_dir} to {output_dir}")
    process_directory(input_dir)
    print("Processing complete!")