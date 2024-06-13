import json
import csv
import argparse
from openpyxl import Workbook

def json_to_csv(input_file, output_name):
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    output_csv = output_name + '.csv'
    with open(output_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f"CSV file '{output_csv}' generated successfully.")

def json_to_excel(input_file, output_name):
    wb = Workbook()
    ws = wb.active

    with open(input_file, 'r') as f:
        data = json.load(f)

    # Write header
    headers = list(data[0].keys())
    ws.append(headers)

    # Write data
    for entry in data:
        row_data = [entry[header] for header in headers]
        ws.append(row_data)

    output_excel = output_name + '.xlsx'
    wb.save(output_excel)
    print(f"Excel file '{output_excel}' generated successfully.")

def main():
    parser = argparse.ArgumentParser(description='Convert JSON to CSV and Excel')
    parser.add_argument('-i', '--input', help='Input JSON file', required=True)
    parser.add_argument('-o', '--output', help='Output file name (without extension)', required=True)
    args = parser.parse_args()

    input_file = args.input
    output_name = args.output

    json_to_csv(input_file, output_name)
    json_to_excel(input_file, output_name)

if __name__ == "__main__":
    main()
