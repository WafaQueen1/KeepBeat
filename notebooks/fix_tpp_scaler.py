import json

filepath = r'D:\Vibe Coding\TwinPacemaker\notebooks\tpp.ipynb'
try:
    with open(filepath, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    # find the cell with scaler = MinMaxScaler()
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            source_text = ''.join(cell['source'])
            if 'scaler = MinMaxScaler()' in source_text and 'from sklearn.preprocessing import MinMaxScaler' not in source_text:
                # Add the import at the beginning
                cell['source'] = ["from sklearn.preprocessing import MinMaxScaler\n", "\n"] + cell['source']
                break

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)
    
    print('Successfully added the import to tpp.ipynb')
except Exception as e:
    print(f'Error: {e}')
