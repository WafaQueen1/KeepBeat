"""
NASA Battery Dataset Downloader
Downloads battery degradation data from NASA Prognostics Repository
"""
import os
import urllib.request
import zipfile
from pathlib import Path

# NASA Prognostics Data Repository URLs
NASA_BATTERY_URLS = {
    'B0005': 'https://ti.arc.nasa.gov/m/project/prognostic-repository/B0005.zip',
    'B0006': 'https://ti.arc.nasa.gov/m/project/prognostic-repository/B0006.zip',
    'B0007': 'https://ti.arc.nasa.gov/m/project/prognostic-repository/B0007.zip',
    'B0018': 'https://ti.arc.nasa.gov/m/project/prognostic-repository/B0018.zip'
}

def download_file(url, destination):
    """Download file with progress"""
    print(f"Downloading: {url}")
    
    try:
        urllib.request.urlretrieve(url, destination)
        print(f"✅ Downloaded: {destination}")
        return True
    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")
        return False

def extract_zip(zip_path, extract_to):
    """Extract ZIP file"""
    print(f"Extracting: {zip_path}")
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print(f"✅ Extracted to: {extract_to}")
        return True
    except Exception as e:
        print(f"❌ Failed to extract {zip_path}: {e}")
        return False

def download_nasa_batteries(output_dir='data/nasa_battery_raw'):
    """
    Download and extract NASA battery datasets
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("="*60)
    print("🔋 NASA Battery Dataset Downloader")
    print("="*60)
    print(f"Output directory: {output_path.absolute()}")
    print()
    
    success_count = 0
    
    for battery_id, url in NASA_BATTERY_URLS.items():
        print(f"\n[{battery_id}]")
        
        # Check if already downloaded
        mat_file = output_path / f"{battery_id}.mat"
        if mat_file.exists():
            print(f"✅ Already exists: {mat_file}")
            success_count += 1
            continue
        
        # Download ZIP
        zip_file = output_path / f"{battery_id}.zip"
        
        if download_file(url, zip_file):
            # Extract
            if extract_zip(zip_file, output_path):
                # Remove ZIP
                zip_file.unlink()
                success_count += 1
        
    print("\n" + "="*60)
    print(f"✅ Downloaded {success_count}/{len(NASA_BATTERY_URLS)} datasets")
    print("="*60)
    
    if success_count == 0:
        print("\n⚠️  No datasets downloaded.")
        print("Alternative: Download manually from:")
        print("https://www.kaggle.com/datasets/patrickfleith/nasa-battery-dataset")
        print("or")
        print("https://ti.arc.nasa.gov/tech/dash/groups/pcoe/prognostic-data-repository/")
        print(f"\nPlace .mat files in: {output_path.absolute()}")
    
    return success_count > 0

if __name__ == "__main__":
    success = download_nasa_batteries()
    
    if not success:
        print("\n" + "="*60)
        print("MANUAL DOWNLOAD INSTRUCTIONS")
        print("="*60)
        print("1. Visit: https://www.kaggle.com/datasets/patrickfleith/nasa-battery-dataset")
        print("2. Download the dataset ZIP")
        print("3. Extract files: B0005.mat, B0006.mat, B0007.mat, B0018.mat")
        print("4. Place in: data/nasa_battery_raw/")
        print("5. Run: python notebooks/01_battery_dataset_cleaning.ipynb")
        print("="*60)
