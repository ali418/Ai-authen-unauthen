import os
import zipfile
import shutil
import sys

# Get the Python version
python_version = f"{sys.version_info.major}{sys.version_info.minor}{sys.version_info.micro}"
print(f"Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

# Path to the wheel file based on Python version
wheel_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dlib-whl-20.0.0-alpha', 'dlib-whl-20.0.0-alpha')
wheel_file = None

# Find the appropriate wheel file
for file in os.listdir(wheel_dir):
    if file.endswith('.whl') and f'cp{sys.version_info.major}{sys.version_info.minor}' in file:
        wheel_file = os.path.join(wheel_dir, file)
        break

if not wheel_file:
    print(f"No matching wheel file found for Python {sys.version_info.major}.{sys.version_info.minor}")
    # Default to Python 3.13 if no match found
    wheel_file = os.path.join(wheel_dir, 'dlib-20.0.0-cp313-cp313-win_amd64.whl')
    print(f"Using default wheel file: {wheel_file}")

# Create dll_files directory if it doesn't exist
dll_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dll_files')
os.makedirs(dll_dir, exist_ok=True)

# Extract DLL files from the wheel
print(f"Extracting DLLs from {wheel_file}")
with zipfile.ZipFile(wheel_file, 'r') as zip_ref:
    # List all files in the wheel
    for file in zip_ref.namelist():
        # Extract only .pyd and .dll files
        if file.endswith('.pyd') or file.endswith('.dll'):
            print(f"Extracting {file}")
            zip_ref.extract(file, dll_dir)

# Add dll_files to PATH environment variable
dll_path = os.path.abspath(dll_dir)
if dll_path not in os.environ['PATH']:
    os.environ['PATH'] = dll_path + os.pathsep + os.environ['PATH']
    print(f"Added {dll_path} to PATH environment variable")

print("\nDLL files extracted successfully. You can now try importing dlib.")
print("To permanently add the DLL directory to your PATH, run the following command in PowerShell as administrator:")
print(f'[Environment]::SetEnvironmentVariable("PATH", "$env:PATH;{dll_path.replace(os.sep, "/")}", "Machine")')

print("\nAlternatively, add the following code at the beginning of your Python scripts:")
print("""import os
import sys

# Add DLL files directory to PATH
dll_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dll_files')
os.environ['PATH'] = dll_path + os.pathsep + os.environ['PATH']
""")