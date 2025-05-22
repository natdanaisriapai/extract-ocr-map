import os
import sys
import argparse
import subprocess
from pathlib import Path
from typing import Optional
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'pipeline_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)

class OCRPipeline:
    def __init__(
        self,
        input_dir: str,
        parsed_md_dir: Optional[str] = None,
        output_json_dir: Optional[str] = None,
        merged_json_dir: Optional[str] = None
    ):
        """
        Initialize the OCR pipeline with configurable paths.
        
        Args:
            input_dir: Directory containing input documents
            parsed_md_dir: Directory for parsed markdown files (default: ./data/data-parsed-md)
            output_json_dir: Directory for individual JSON files (default: ./data/data-output-json)
            merged_json_dir: Directory for merged JSON file (default: ./data/json-merge)
        """
        self.base_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.input_dir = Path(input_dir)
        
        # Set default output directories if not specified
        self.parsed_md_dir = Path(parsed_md_dir) if parsed_md_dir else self.base_dir / "data" / "data-parsed-md"
        self.output_json_dir = Path(output_json_dir) if output_json_dir else self.base_dir / "data" / "data-output-json"
        self.merged_json_dir = Path(merged_json_dir) if merged_json_dir else self.base_dir / "data" / "json-merge"
        
        # Validate input directory
        if not self.input_dir.exists():
            raise ValueError(f"Input directory does not exist: {self.input_dir}")
        
        # Create output directories
        self.parsed_md_dir.mkdir(parents=True, exist_ok=True)
        self.output_json_dir.mkdir(parents=True, exist_ok=True)
        self.merged_json_dir.mkdir(parents=True, exist_ok=True)

    def run_script(self, script_name: str, env_vars: dict = None) -> bool:
        """
        Run a Python script and wait for it to complete.
        
        Args:
            script_name: Name of the script to run (e.g., "00-llama-parsed-ocr.py")
            env_vars: Additional environment variables to set
            
        Returns:
            bool: True if script completed successfully, False otherwise
        """
        script_path = self.base_dir / "scripts" / script_name
        if not script_path.exists():
            logger.error(f"Script not found: {script_path}")
            return False

        # Prepare environment variables
        env = os.environ.copy()
        if env_vars:
            env.update(env_vars)

        try:
            logger.info(f"Running {script_name}...")
            result = subprocess.run(
                [sys.executable, str(script_path)],
                env=env,
                check=True,
                capture_output=True,
                text=True
            )
            
            # Log script output
            if result.stdout:
                logger.info(f"Script output:\n{result.stdout}")
            if result.stderr:
                logger.warning(f"Script warnings/errors:\n{result.stderr}")
                
            logger.info(f"Completed {script_name} successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error running {script_name}:")
            logger.error(f"Exit code: {e.returncode}")
            logger.error(f"Output: {e.output}")
            logger.error(f"Error: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error running {script_name}: {str(e)}")
            return False

    def run_pipeline(self) -> bool:
        """
        Run the complete OCR pipeline in sequence.
        
        Returns:
            bool: True if all steps completed successfully, False otherwise
        """
        # Set environment variables for each script
        env_vars = {
            "INPUT_DIR": str(self.input_dir),
            "PARSED_MD_DIR": str(self.parsed_md_dir),
            "OUTPUT_JSON_DIR": str(self.output_json_dir),
            "MERGED_JSON_DIR": str(self.merged_json_dir)
        }

        # Step 1: Convert documents to Markdown
        logger.info("Starting Step 1: Converting documents to Markdown")
        if not self.run_script("00-llama-parsed-ocr.py", env_vars):
            logger.error("Step 1 failed")
            return False

        # Step 2: Convert Markdown to JSON
        logger.info("Starting Step 2: Converting Markdown to JSON")
        if not self.run_script("01-convert-md_to_json.py", env_vars):
            logger.error("Step 2 failed")
            return False

        # Step 3: Merge JSON files
        logger.info("Starting Step 3: Merging JSON files")
        if not self.run_script("02-merge-json.py", env_vars):
            logger.error("Step 3 failed")
            return False

        logger.info("Pipeline completed successfully!")
        return True

def main():
    parser = argparse.ArgumentParser(description="OCR Data Extraction Pipeline")
    parser.add_argument(
        "--input-dir",
        default="./data/data-input",
        help="Directory containing input documents (default: ./data/data-input)"
    )
    parser.add_argument(
        "--parsed-md-dir",
        help="Directory for parsed markdown files (default: ./data/data-parsed-md)"
    )
    parser.add_argument(
        "--output-json-dir",
        help="Directory for individual JSON files (default: ./data/data-output-json)"
    )
    parser.add_argument(
        "--merged-json-dir",
        help="Directory for merged JSON file (default: ./data/json-merge)"
    )

    args = parser.parse_args()

    try:
        pipeline = OCRPipeline(
            input_dir=args.input_dir,
            parsed_md_dir=args.parsed_md_dir,
            output_json_dir=args.output_json_dir,
            merged_json_dir=args.merged_json_dir
        )
        
        success = pipeline.run_pipeline()
        sys.exit(0 if success else 1)
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
