import os

# Directory containing the files
folder_path = './workflows/'

# Iterate over all files in the folder
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)

    # Check if it's a file
    if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()

        # Process the lines, replacing the patterns
        new_lines = [line.replace('="', '=').replace('"]', ']') for line in lines]

        # Write the changes back to the file
        with open(file_path, 'w') as file:
            file.writelines(new_lines)

        print(f"Processed {filename}")
