import pandas as pd

# Read the CSV file
input_file = '/home/loch/python-scripts/Processed_GitHub_Repo_Names_With_Emails_Final_Set_output.csv'
df = pd.read_csv(input_file)

# Extract the first column and remove duplicates
first_column = df.iloc[:, 0].drop_duplicates()

# Save the first column to a new CSV file
output_file = '/home/loch/python-scripts/Processed_GitHub_Repo_Names_Final_Set.csv'
first_column.to_csv(output_file, index=False, header=True)