import sys
import argparse
from dotenv import load_dotenv

from web_research import WebAnalyzer
from utils import setup_logging, clean_url

def main():
    # Set up logging
    logger = setup_logging()
    
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Competitive Web Research Tool")
    parser.add_argument("url", nargs="?", help="URL of competitor website to analyze")
    parser.add_argument("--output", "-o", help="Output file name prefix")
    args = parser.parse_args()
    
    # If no URL provided via command line, prompt the user
    url = args.url
    if not url:
        url = input("Enter competitor's URL to analyze: ")
    
    # Clean URL
    url = clean_url(url)
    
    logger.info(f"Starting analysis for: {url}")
    
    try:
        # Initialize and run the analysis
        researcher = WebAnalyzer()
        report = researcher.generate_report(url)
        
        logger.info(f"Analysis complete. Report saved.")
        print(f"\nAnalysis complete! Check the generated JSON file for details.")
        
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        print(f"Error during analysis: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
