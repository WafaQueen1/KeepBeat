import json
filepath = r'D:\Vibe Coding\TwinPacemaker\notebooks\02_cardiac_training.ipynb'
with open(filepath, 'r', encoding='utf-8') as f:
    nb = json.load(f)

source_code_load = nb['cells'][3]['source']
for i, line in enumerate(source_code_load):
    if "'/content/mitbih_train.csv'," in line and "'/content/sample_data/mitbih_train.csv'," not in ''.join(source_code_load):
        source_code_load.insert(i, "    '/content/sample_data/mitbih_train.csv',\n")
    elif "'/content/mitbih_test.csv'," in line and "'/content/sample_data/mitbih_test.csv'," not in ''.join(source_code_load):
        source_code_load.insert(i, "    '/content/sample_data/mitbih_test.csv',\n")
    elif "'/content/ptbdb_normal.csv'," in line and "'/content/sample_data/ptbdb_normal.csv'," not in ''.join(source_code_load):
        source_code_load.insert(i, "    '/content/sample_data/ptbdb_normal.csv',\n")
    elif "'/content/ptbdb_abnormal.csv'," in line and "'/content/sample_data/ptbdb_abnormal.csv'," not in ''.join(source_code_load):
        source_code_load.insert(i, "    '/content/sample_data/ptbdb_abnormal.csv',\n")

nb['cells'][3]['source'] = source_code_load

with open(filepath, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)
