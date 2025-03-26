import csv
import re

input_file = '/home/loch/python-scripts/Registration_Details_20.csv'
output_file = '/home/loch/python-scripts/PersonalEmails_20.csv'

# Regular expression for validating an email
email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

with open(input_file, mode='r') as infile, open(output_file, mode='w', newline='') as outfile:
    reader = csv.DictReader(infile)
    writer = csv.writer(outfile)
    
    # Write the header
    writer.writerow(['PersonalEmail'])
    
    # Write the valid PersonalEmail column
    for row in reader:
        email = row['PersonalEmail']
        if email and email_regex.match(email):
            writer.writerow([email])