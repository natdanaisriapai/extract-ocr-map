import os
import json
from dotenv import load_dotenv, dotenv_values
from openai import OpenAI
# import glob

# Load environment variables
config = dotenv_values(".env")
openai_api_key = config.get("OPENAI_API_KEY")
openai_model = config.get("OPENAI_MODEL")

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

# Set up paths from environment variables or use defaults
input_dir = os.path.abspath(os.getenv("PARSED_MD_DIR", "./data/data-parsed-md"))
output_dir = os.path.abspath(os.getenv("OUTPUT_JSON_DIR", "./data/data-output-json"))

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Prompt for OpenAI
SYSTEM_PROMPT = """You are given a structured Markdown document that contains information from a Thai land deed.

Your task is to extract relevant key-value pairs from the Markdown and convert them into a clean JSON object using the exact field structure provided below.

Extraction Instructions:
Parse the Markdown content carefully.
Focus only on important fields typically found in Thai land deeds.
Use the Thai field names as JSON keys (e.g., "เลขโฉนดที่ดิน", "หน้าสำรวจ", "เลขที่ดิน").
If any value is missing in the document, skip that field (do not include nulls or placeholders).
Ensure all values are returned as strings.
If a value is a coordinate or URL, include it as a string.
Do not include any Markdown syntax in the output (no #, |, **, etc.).
Output format:
Return a single valid JSON object in the following format:
{
  "เลขโฉนดที่ดิน": "<string>",
  "หน้าสำรวจ": "<string>",
  "เลขที่ดิน": "<string>",
  "ระวาง": "<string>",
  "ตำบล": "<string>",
  "อำเภอ": "<string>",
  "จังหวัด": "<string>",
  "เนื้อที่": "<string>",
  "ราคาประเมินที่ดิน": "<string>",
  "ค่าพิกัดแปลง": "<latitude,longitude>",
  "ข้อมูลการเดินทาง": "<string>"
}"""

def convert_md_to_json(md_content):
    """Convert markdown content to JSON using OpenAI API."""
    try:
        response = client.chat.completions.create(
            model=openai_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": md_content}
            ],
            temperature=0.1,  # Low temperature for more consistent output
            response_format={"type": "json_object"}
        )
        
        # Extract the JSON string from the response
        json_str = response.choices[0].message.content
        
        # Parse the JSON string to validate it
        json_data = json.loads(json_str)
        return json_data
    
    except Exception as e:
        print(f"Error converting content: {str(e)}")
        return None

def process_file(input_path, rel_path):
    """Process a single markdown file and save as JSON."""
    try:
        # Create output path maintaining directory structure
        output_filename = f"{os.path.splitext(os.path.basename(input_path))[0]}.json"
        output_subdir = os.path.join(output_dir, rel_path)
        output_path = os.path.join(output_subdir, output_filename)

        if os.path.exists(output_path):
            print(f"File already exists: {output_path}")
            return

        # Create output directory if it doesn't exist
        os.makedirs(output_subdir, exist_ok=True)

        print(f"Processing: {input_path}")

        # Read markdown content
        with open(input_path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # Convert to JSON
        json_data = convert_md_to_json(md_content)
        
        if json_data:
            # Save the JSON data
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            print(f"Saved JSON to {output_path}")
        else:
            print(f"Failed to convert {input_path} to JSON")

    except Exception as e:
        print(f"Error processing {input_path}: {str(e)}")

def process_directory(input_dir):
    """Process all markdown files in the input directory."""
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
        
        # Process each markdown file in the current directory
        for file in files:
            if file.lower().endswith('.md'):
                file_count += 1
                input_path = os.path.join(root, file)
                print(f"\nFound file: {input_path}")
                process_file(input_path, rel_path)
    
    if file_count == 0:
        print("\nNo markdown files were found in the input directory!")
        print("Please check that:")
        print("1. The input directory path is correct")
        print("2. Markdown files exist in the input directory")
        print(f"3. The script has access to read files in: {input_dir}")
    else:
        print(f"\nProcessed {file_count} files")

if __name__ == "__main__":
    # Start processing
    print(f"Starting to process files from {input_dir} to {output_dir}")
    process_directory(input_dir)
    print("Processing complete!")
