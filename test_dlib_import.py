import os
import sys

# Print Python version
print(f"Python version: {sys.version}")

# Add dll_files directory to PATH if it exists
dll_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dll_files')
if os.path.exists(dll_path):
    os.environ['PATH'] = dll_path + os.pathsep + os.environ['PATH']
    print(f"Added {dll_path} to PATH environment variable")

# Try importing dlib
try:
    import dlib
    print(f"Successfully imported dlib version {dlib.__version__}")
    print(f"DLIB_USE_CUDA: {dlib.DLIB_USE_CUDA if hasattr(dlib, 'DLIB_USE_CUDA') else 'Not available'}")
    
    # Check if we can access the predictor
    try:
        predictor_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shape_predictor_68_face_landmarks.dat')
        if os.path.exists(predictor_path):
            predictor = dlib.shape_predictor(predictor_path)
            print("Successfully loaded shape predictor")
        else:
            print(f"Shape predictor file not found at {predictor_path}")
    except Exception as e:
        print(f"Error loading shape predictor: {e}")
        
except ImportError as e:
    print(f"Error importing dlib: {e}")
    
    # Check if _dlib_pybind11 can be imported directly
    try:
        import _dlib_pybind11
        print("Successfully imported _dlib_pybind11 directly")
    except ImportError as e:
        print(f"Error importing _dlib_pybind11: {e}")
        
        # List all files in dll_files directory
        if os.path.exists(dll_path):
            print("\nFiles in dll_files directory:")
            for file in os.listdir(dll_path):
                print(f"  - {file}")
        else:
            print("\ndll_files directory does not exist. Run extract_dlib_dlls.py first.")

input("\nPress Enter to exit...")