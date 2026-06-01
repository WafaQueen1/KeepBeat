import json

filepath = r'D:\Vibe Coding\TwinPacemaker\notebooks\tpp.ipynb'
try:
    with open(filepath, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    new_source = [
        "from google.colab import drive\n",
        "import pandas as pd\n",
        "\n",
        "# 1. Mount Google Drive\n",
        "drive.mount('/content/drive')\n",
        "\n",
        "# 2. Load the dataset directly from Google Drive\n",
        "file_name = '/content/drive/MyDrive/TwinPacemaker/NASA Battery Dataset/battery_cycle_level_dataset_CLEAN_FINAL.csv'\n",
        "df = pd.read_csv(file_name)\n",
        "\n",
        "print('Loaded:', file_name)\n",
        "print(df.head())\n"
    ]

    found = False
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            source_text = ''.join(cell['source'])
            if 'files.upload()' in source_text or 'google.colab import files' in source_text:
                cell['source'] = new_source
                found = True
                break
    
    if not found:
        print("Could not find the exact files.upload() cell, replacing the first code cell just in case.")
        for cell in nb['cells']:
            if cell['cell_type'] == 'code':
                cell['source'] = new_source
                break

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)
    
    print('Successfully updated the cell in tpp.ipynb')
except Exception as e:
    print(f'Error: {e}')
