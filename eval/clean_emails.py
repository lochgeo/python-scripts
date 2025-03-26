import csv
import re

input_file = '/home/loch/python-scripts/PersonalEmails_20.csv'
output_file = '/home/loch/python-scripts/PersonalEmails_20_2.csv'

# Regular expression for validating an email
email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

# Set to store unique emails
unique_emails = set()

with open(input_file, mode='r') as infile, open(output_file, mode='w', newline='') as outfile:
    reader = csv.DictReader(infile)
    writer = csv.writer(outfile)
    
    # Write the header
    writer.writerow(['email'])
    
    # Write the valid PersonalEmail column
    for row in reader:
        email = row['email']
        if email and email_regex.match(email) and 'wellsfargo.com' not in email:
            if email not in unique_emails:
                unique_emails.add(email)
                writer.writerow([email])