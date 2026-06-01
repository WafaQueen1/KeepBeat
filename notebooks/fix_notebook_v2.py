import json

filepath = r'D:\Vibe Coding\TwinPacemaker\notebooks\02_cardiac_training.ipynb'
with open(filepath, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Find the upload cell and replace it with a markdown cell explaining how to upload via sidebar
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code' and 'COLAB SPECIFIC: UPLOAD DATA' in ''.join(cell['source']):
        # Replace this cell with a markdown cell
        nb['cells'][i] = {
            'cell_type': 'markdown',
            'metadata': {},
            'source': [
                "### ⚠️ HOW TO UPLOAD DATA IN COLAB ⚠️\n",
                "Since the CSV files are very large (over 500MB total), the standard upload button often crashes the browser.\n",
                "\n",
                "**Instead, please use the sidebar:**\n",
                "1. Click the **Folder icon** 📁 on the left side of the Colab screen.\n",
                "2. Drag and drop the 4 CSV files directly into that panel.\n",
                "3. Wait for the circular upload progress indicators to finish completely before running the cells below.\n"
            ]
        }
        break

with open(filepath, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print("Updated notebook to remove the broken upload code and add manual sidebar instructions.")
