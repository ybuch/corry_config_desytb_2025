import yaml
import sys

# Check if a filename was provided
if len(sys.argv) < 2:
    print('''Usage: python script.py <yaml_file> \n 
    Optionally use >> to append the output to an existing mask txt file. \n 
    Remember to clean up the mask txt file before processing a new run.''')
    sys.exit(1)

# Get the filename from command line argument
yaml_file = sys.argv[1]

# Read the YAML file
try:
    with open(yaml_file, 'r') as file:
        data = yaml.safe_load(file)
except FileNotFoundError:
    print(f"Error: File '{yaml_file}' not found.")
    sys.exit(1)
except yaml.YAMLError as e:
    print(f"Error parsing YAML file: {e}")
    sys.exit(1)

# Extract and print row and column values
for pixel in data['masked_pixels']:
    print(f'p {pixel["col"]} {pixel["row"]}')

