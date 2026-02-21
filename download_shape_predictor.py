import os
import bz2
import urllib.request
import ssl
import sys
import time

def download_and_extract_shape_predictor():
    """
    Downloads and extracts the shape_predictor_68_face_landmarks.dat file
    required for dlib face alignment.
    """
    # URLs for the shape predictor file (multiple sources)
    urls = [
        "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2",
        "https://github.com/davisking/dlib-models/raw/master/shape_predictor_68_face_landmarks.dat.bz2",
        "https://sourceforge.net/projects/dclib/files/dlib/v18.10/shape_predictor_68_face_landmarks.dat.bz2/download"
    ]
    
    # Paths for downloaded and extracted files
    bz2_file_path = "shape_predictor_68_face_landmarks.dat.bz2"
    dat_file_path = "shape_predictor_68_face_landmarks.dat"
    
    # Check if the .dat file already exists
    if os.path.exists(dat_file_path):
        print(f"The file {dat_file_path} already exists.")
        return dat_file_path
    
    # Download the file if it doesn't exist
    if not os.path.exists(bz2_file_path):
        print(f"Attempting to download {bz2_file_path}...")
        
        # Try each URL until one works
        download_success = False
        for url in urls:
            try:
                print(f"Trying URL: {url}")
                # First try with proper SSL verification
                urllib.request.urlretrieve(url, bz2_file_path)
                download_success = True
                print("Download complete.")
                break
            except urllib.error.URLError as e:
                print(f"Error with URL {url}: {e}")
                try:
                    if 'CERTIFICATE_VERIFY_FAILED' in str(e):
                        print("SSL certificate verification failed. Trying with verification disabled...")
                        # Create a context that doesn't verify certificates
                        ssl_context = ssl._create_unverified_context()
                        # Download with the unverified context
                        with urllib.request.urlopen(url, context=ssl_context) as response, open(bz2_file_path, 'wb') as out_file:
                            data = response.read()
                            out_file.write(data)
                        download_success = True
                        print("Download complete with SSL verification disabled.")
                        break
                except Exception as inner_e:
                    print(f"Failed with SSL bypass too: {inner_e}")
                    # Continue to the next URL
                    continue
        
        if not download_success:
            print("\nAll download attempts failed. Please download the file manually from one of these URLs:")
            for url in urls:
                print(f"- {url}")
            print("\nAnd place it in the current directory as 'shape_predictor_68_face_landmarks.dat.bz2'")
            print("\nAlternatively, you can download the extracted .dat file directly and place it in the current directory.")
            sys.exit(1)
    
    # Extract the bz2 file
    print(f"Extracting {bz2_file_path}...")
    with bz2.BZ2File(bz2_file_path, 'rb') as f_in:
        with open(dat_file_path, 'wb') as f_out:
            data = f_in.read()
            f_out.write(data)
    print("Extraction complete.")
    
    # Optionally remove the bz2 file after extraction
    os.remove(bz2_file_path)
    print(f"Removed {bz2_file_path}")
    
    return dat_file_path

if __name__ == "__main__":
    file_path = download_and_extract_shape_predictor()
    print(f"Shape predictor file is available at: {file_path}")