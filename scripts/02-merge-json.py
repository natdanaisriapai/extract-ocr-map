import os
import json
from pathlib import Path

# Set up paths
input_dir = os.path.abspath("./data/data-output-json")
output_dir = os.path.abspath("./data/json-merge")
output_file = os.path.join(output_dir, "merged_land_deeds.json")

def merge_json_files():
    """Merge all JSON files from input directory into a single JSON file."""
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # List to store all JSON data
        all_data = []
        
        # Counter for processed files
        file_count = 0
        
        print(f"Scanning directory: {input_dir}")
        
        # Walk through all directories and files
        for root, dirs, files in os.walk(input_dir):
            for file in files:
                if file.lower().endswith('.json'):
                    file_path = os.path.join(root, file)
                    print(f"Processing: {file_path}")
                    
                    try:
                        # Read and parse JSON file
                        with open(file_path, 'r', encoding='utf-8') as f:
                            json_data = json.load(f)
                            
                        # Add source file information
                        json_data['source_file'] = os.path.relpath(file_path, input_dir)
                        
                        # Add to our collection
                        all_data.append(json_data)
                        file_count += 1
                        
                    except json.JSONDecodeError as e:
                        print(f"Error reading {file_path}: Invalid JSON format - {str(e)}")
                    except Exception as e:
                        print(f"Error processing {file_path}: {str(e)}")
        
        if file_count == 0:
            print("\nNo JSON files were found in the input directory!")
            print("Please check that:")
            print("1. The input directory path is correct")
            print("2. JSON files exist in the input directory")
            print(f"3. The script has access to read files in: {input_dir}")
            return
        
        # Sort the data by เลขโฉนดที่ดิน if available
        try:
            all_data.sort(key=lambda x: x.get('เลขโฉนดที่ดิน', ''))
        except Exception as e:
            print(f"Warning: Could not sort data - {str(e)}")
        
        # Create the final merged data structure
        merged_data = {
            "total_records": len(all_data),
            "data": all_data
        }
        
        # Save the merged data
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=2)
        
        print(f"\nSuccessfully merged {file_count} JSON files")
        print(f"Output saved to: {output_file}")
        print(f"Total records: {len(all_data)}")
        
    except Exception as e:
        print(f"Error during merge process: {str(e)}")

if __name__ == "__main__":
    print("Starting JSON merge process...")
    merge_json_files()
    print("Merge process complete!")
