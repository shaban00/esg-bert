import os
import re
import json
from datetime import datetime
import argparse
import requests
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from tika import parser
from tqdm import tqdm


def is_valid_pdf_url(url):
    try:
        response = requests.head(url)
        content_type = response.headers.get('content-type')
        if 'application/pdf' in content_type:
            return True
        elif 'text/plain' in content_type:
            return True
        else:
            print(f"Invalid content type for URL: {content_type}")
            return False
    except Exception as e:
        return False


def is_valid_pdf_file(file_path_or_url):
    if file_path_or_url.startswith('http://') or file_path_or_url.startswith('https://'):
        return is_valid_pdf_url(file_path_or_url)
    return os.path.isfile(file_path_or_url) and (file_path_or_url.lower().endswith('.pdf') or file_path_or_url.lower().endswith('.txt'))


def text_to_sentences(text):
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    sentences = text.split('.')
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
    return sentences

    
def pdf_parser(file_path):
    parsed = parser.from_file(file_path)
    content = parsed["content"]
    sentences = text_to_sentences(content)
    return sentences


def extract_file_info(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

        data = {}
        
        conformed_period_match = re.search(r'CONFORMED PERIOD OF REPORT:\s*(.*)', content)
        data['Conformed_Period'] = conformed_period_match.group(1) if conformed_period_match else None

        filed_date_match = re.search(r'FILED AS OF DATE:\s*(.*)', content)
        data['Year'] = filed_date_match.group(1)[:4] if filed_date_match else None

        company_name_match = re.search(r'COMPANY CONFORMED NAME:\s*(.*)', content)
        data['Company_Name'] = company_name_match.group(1) if company_name_match else None

        central_index_key_match = re.search(r'CENTRAL INDEX KEY:\s*(.*)', content)
        try:
            data['Central_Index_Key'] = int(central_index_key_match.group(1)) if central_index_key_match else None
        except (ValueError, TypeError):
            data['Central_Index_Key'] = central_index_key_match.group(1) if central_index_key_match else None

        return data
        

def process_sentences(sentences):
    tokenizer = AutoTokenizer.from_pretrained("nbroad/ESG-BERT")
    model = AutoModelForSequenceClassification.from_pretrained("nbroad/ESG-BERT")
    classifier = pipeline('text-classification', model=model, tokenizer=tokenizer)

    chunk_size = 150
    results = []

    for i in tqdm(range(0, len(sentences), chunk_size), desc="Processing"):
        chunk = [sentence[:tokenizer.model_max_length - 2] for sentence in sentences[i:i + chunk_size]]
        chunk_result = classifier(chunk)
        results.extend(chunk_result)


    data_frame = pd.DataFrame(results)
    
    # Filter results with score >= 0.75
    filtered_results = data_frame[data_frame['score'] >= 0.75]
    
    num_sentences = len(sentences)
    output = filtered_results.groupby('label').size().to_dict()
    output['Sentences'] = num_sentences

    return output


def save_output_to_json(data, filename):
    file_exists = os.path.exists(filename)
    
    if not file_exists or os.stat(filename).st_size == 0:
        with open(filename, "w") as json_file:
            json.dump([data], json_file, indent=4)
    else:
        with open(filename, "r") as json_file:
            existing_data = json.load(json_file)
        
        existing_data.append(data)
        
        with open(filename, "w") as json_file:
            json.dump(existing_data, json_file, indent=4)


def main():
    parser = argparse.ArgumentParser(description='Process PDF and text files.')
    parser.add_argument('--directory', '-d', type=str, help='Directories containing files to process, separated by commas')
    parser.add_argument('--files', '-f', type=str, help='Files to process, separated by commas')
    parser.add_argument('--output', '-o', type=str, help='Output file name for saving JSON data')

    args = parser.parse_args()

    if not (args.directory or args.files):
        parser.print_help()
        return

    directories = args.directory.split(',') if args.directory else []
    files = args.files.split(',') if args.files else []
    output_filename = args.output if args.output else None

    files_to_process = []

    for directory in directories:
        if os.path.isdir(directory):
            for root, _, filenames in os.walk(directory):
                files_to_process.extend([os.path.join(root, filename) for filename in filenames])
        else:
            print(f"Invalid directory: {directory}")

    for file_path in files:
        if os.path.isfile(file_path) or file_path.startswith('http://') or file_path.startswith('https://'):
            if is_valid_pdf_file(file_path):
                files_to_process.append(file_path)
            else:
                print(f"Invalid file path or URL: {file_path}")
        else:
            print(f"Invalid file path or URL: {file_path}")
    
    if output_filename is None:
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        output_filename = f"{timestamp}.json"


    for file_path in files_to_process:
        if is_valid_pdf_file(file_path):
            if file_path.lower().endswith('.pdf'):
                sentences = pdf_parser(file_path)
                output = process_sentences(sentences)
                save_output_to_json(output, output_filename)

            elif file_path.lower().endswith('.txt'):
                file_info = extract_file_info(file_path)
                    
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    sentences = text_to_sentences(content)
                
                output = process_sentences(sentences)
                file_info.update(output)
                save_output_to_json(file_info, output_filename)
            
        else:
            print(f"Invalid file: {file_path}")


if __name__ == "__main__":
    main()
