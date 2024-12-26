import os

# Specify the directory
directory = "./healthline_complete_rag_input"

# Process all JSON file names to remove the .json suffix and replace hyphens with spaces
json_files = [
    file.replace('.json', '').replace('-', ' ')
    for file in os.listdir(directory)
    if file.endswith('.json')
]

