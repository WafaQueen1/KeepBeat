import json
import os

filepath = r'D:\Vibe Coding\TwinPacemaker\notebooks\02_cardiac_training.ipynb'
with open(filepath, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# 1. Add Colab Upload Code Cell
upload_code = """# ===========================
# COLAB SPECIFIC: UPLOAD DATA
# ===========================
import os
try:
    from google.colab import files
    print("Running in Google Colab. Please upload the 4 CSV files:")
    print("mitbih_train.csv, mitbih_test.csv, ptbdb_normal.csv, ptbdb_abnormal.csv")
    print("(You can skip this if you already uploaded them to the left sidebar)\\n")
    
    # Check if files already exist to avoid re-uploading
    required_files = ['mitbih_train.csv', 'mitbih_test.csv', 'ptbdb_normal.csv', 'ptbdb_abnormal.csv']
    if not all(os.path.exists(f) for f in required_files):
        uploaded = files.upload()
    else:
        print("Files already exist in the working directory.")
except ImportError:
    print("Not running in Google Colab (Local environment detected). Using local files if available.")"""

upload_cell = {
    'cell_type': 'code',
    'execution_count': None,
    'metadata': {},
    'outputs': [],
    'source': [line + '\n' for line in upload_code.split('\n')]
}
nb['cells'].insert(1, upload_cell)

# 2. Update Markdown to be more explicit about GPU
new_markdown = [
    '## COLAB INSTRUCTIONS FOR THIS MODEL:\n',
    '\n',
    '1. Upload notebook to Colab\n',
    '2. **CRITICAL**: Enable GPU: `Runtime` → `Change runtime type` → Select `T4 GPU`\n',
    '   *(If you see `GPU: []` in the output of the first cell, it means GPU is not enabled!)*\n',
    '3. Run the first cell to upload the 4 CSV files from the Kaggle heartbeat dataset:\n',
    '   `mitbih_train.csv, mitbih_test.csv, ptbdb_normal.csv, ptbdb_abnormal.csv`\n',
    '4. `Runtime` → `Run all`\n',
    '5. Expected time: ~40 minutes on T4 GPU\n',
    '6. Download: `cardiac_bilstm.keras` + `cardiac_model_info.json`\n'
]
nb['cells'][0]['source'] = new_markdown

# 3. Add GPU warning in the main code block (now index 2)
source_code = nb['cells'][2]['source']
for i, line in enumerate(source_code):
    if "print(f\"GPU: {tf.config.list_physical_devices('GPU')}\")" in line:
        source_code.insert(i+1, "if len(tf.config.list_physical_devices('GPU')) == 0:\n")
        source_code.insert(i+2, "    print('\\n⚠️ WARNING: NO GPU DETECTED! Training will be very slow.')\n")
        source_code.insert(i+3, "    print('If in Colab, go to Runtime -> Change runtime type -> Hardware accelerator -> T4 GPU\\n')\n")
        break
nb['cells'][2]['source'] = source_code

# 4. Add /content/ fallback paths for Colab
source_code_load = nb['cells'][3]['source']
for i, line in enumerate(source_code_load):
    if "'mitbih_train.csv'," in line and "'/content/mitbih_train.csv'," not in ''.join(source_code_load):
        source_code_load.insert(i, "    '/content/mitbih_train.csv',\n")
    elif "'mitbih_test.csv'," in line and "'/content/mitbih_test.csv'," not in ''.join(source_code_load):
        source_code_load.insert(i, "    '/content/mitbih_test.csv',\n")
    elif "'ptbdb_normal.csv'," in line and "'/content/ptbdb_normal.csv'," not in ''.join(source_code_load):
        source_code_load.insert(i, "    '/content/ptbdb_normal.csv',\n")
    elif "'ptbdb_abnormal.csv'," in line and "'/content/ptbdb_abnormal.csv'," not in ''.join(source_code_load):
        source_code_load.insert(i, "    '/content/ptbdb_abnormal.csv',\n")
nb['cells'][3]['source'] = source_code_load

with open(filepath, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print("Updated notebook with Colab instructions and upload cell.")
