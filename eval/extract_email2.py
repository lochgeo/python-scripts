import csv
import re

input_file = '/home/loch/python-scripts/Processed_GitHub_Repo_Names_With_Emails_Final_Set_output.csv'
output_file = '/home/loch/python-scripts/Unique_Emails_Final_Set.csv'

emails = set()
email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

with open(input_file, mode='r') as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        email_list = eval(row['PersonalEmail'])
        for email in email_list:
            if email_pattern.match(email):
                emails.add(email)

with open(output_file, mode='w', newline='') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(['Email'])
    for email in sorted(emails):
        writer.writerow([email])

print(f"Unique emails have been extracted to {output_file}")