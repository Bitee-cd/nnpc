import csv
import os
import shutil
from datetime import datetime
from django.http import HttpResponse, FileResponse
from django.conf import settings

def parse_date(date_str):
    try:
        formatted_date = datetime.strptime(date_str, "%Y-%m-%d")
        return formatted_date
    except ValueError:
        print("Invalid start date format. Please provide the start date in the format YYYY-MM-DD.",date_str)
        return None


def parse_and_reformat_date(date_str):
    parts = date_str.split('-')

    parts[1] = parts[1][:3].upper()  # Convert to uppercase to match the format in the date string

    reformatted_date_str = '-'.join(parts)
    try:
        formatted_date = datetime.strptime(reformatted_date_str, "%d-%b-%y")
        return formatted_date
    except ValueError:
        print("Error: Invalid date format in date string:", date_str)
        return None

def get_headers(file_name):
        with open(file_name, 'r') as file:
            csvreader = csv.DictReader(file)
            headers = csvreader.fieldnames
            return headers
def appendAsteriskToHeaderColumn(general_file_name, general_header_name, non_duplicates):
    # Create a temporary file to write modified rows
    temp_file_name = general_file_name + '.temp'

    with open(general_file_name, 'r') as general_file:
        with open(temp_file_name, 'w', newline='') as temp_file:
            csvreader = csv.DictReader(general_file)
            headers = csvreader.fieldnames
            writer = csv.DictWriter(temp_file, fieldnames=headers)
            writer.writeheader()

            for row in csvreader:
                if row[general_header_name] in non_duplicates:
                    # Append "*" to the cell in the general header column
                    row[general_header_name] += "*"
                writer.writerow(row)

    # Replace the original file with the modified file
    import shutil
    shutil.move(temp_file_name, general_file_name)


# get list of header names starting from date -> List of meter ticket numbers'
def searchFileStartingFromDate(file_name, header_name, start_date,keyword):
    start_date = parse_date(start_date)
    if start_date is None:
        return []
  

    with open(file_name, 'r') as file:
        csvreader = csv.DictReader(file)
        headers = csvreader.fieldnames
        if header_name not in headers:
            print("Header not found:", header_name)
            return []

        data = []
        for row in csvreader:
            formatted_row_date = parse_and_reformat_date(row['DATE'])
            if header_name in row and formatted_row_date >= start_date:
                if keyword in row[header_name]:
                    data.append(row[header_name])
    return data


def searchForDuplicates(company_file_name, company_header_name, data, general_file_name, general_header_name):
    general_data = set(data)
    if not general_data:
        return None, None,  

    duplicates = set()

    # Create a temporary file to store non-duplicate rows
    temp_file_name = company_file_name + '.temp'
    with open(company_file_name, 'r') as company_file:
        csvreader = csv.DictReader(company_file)
        headers = csvreader.fieldnames
        print("company headers name",headers)
        
        if company_header_name not in headers:
            return None, None  # Header not found

        with open(temp_file_name, 'w', newline='') as temp_file:
            writer = csv.DictWriter(temp_file, fieldnames=headers)
            writer.writeheader()

            for row in csvreader:
                if row[company_header_name] in general_data:
                    duplicates.add(row[company_header_name])
                else:
                    writer.writerow(row)

    # Replace the original file with the non-duplicate data
    shutil.move(temp_file_name, company_file_name)

    # Write the duplicates to a new file
    duplicates_file_name = os.path.join(settings.MEDIA_ROOT, "duplicates.csv")
    if duplicates:
        with open(duplicates_file_name, 'w', newline='') as duplicates_file:
            writer = csv.DictWriter(duplicates_file, fieldnames=headers)
            writer.writeheader()
            with open(company_file_name, 'r') as company_file:
                csvreader = csv.DictReader(company_file)
                for row in csvreader:
                    if row[company_header_name] in duplicates:
                        writer.writerow(row)

    # Write non-duplicates to a new file
    non_duplicates = general_data - duplicates
    non_duplicates_file_name = os.path.join(settings.MEDIA_ROOT, "non_duplicates.csv")
    if non_duplicates:
        with open(non_duplicates_file_name, 'w', newline='') as non_duplicates_file:
            writer = csv.writer(non_duplicates_file)
            writer.writerow([company_header_name])
            for item in non_duplicates:
                writer.writerow([item])

        appendAsteriskToHeaderColumn(general_file_name, general_header_name, non_duplicates)

    return duplicates_file_name, non_duplicates_file_name
