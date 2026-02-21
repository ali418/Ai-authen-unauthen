import os
import sys
import subprocess
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
VENV_DIR = BASE_DIR / "venv"


def run_command(args, cwd=None):
    print("Running:", " ".join(str(a) for a in args))
    subprocess.check_call(args, cwd=cwd)


def ensure_virtualenv():
    if VENV_DIR.exists():
        print(f"Virtual environment already exists at {VENV_DIR}")
        return
    print("Creating virtual environment...")
    run_command([sys.executable, "-m", "venv", str(VENV_DIR)])


def get_venv_python():
    if os.name == "nt":
        python_path = VENV_DIR / "Scripts" / "python.exe"
    else:
        python_path = VENV_DIR / "bin" / "python"
    if not python_path.exists():
        raise FileNotFoundError(f"Python executable not found in virtual environment at {python_path}")
    return str(python_path)


def install_requirements():
    requirements_file = BASE_DIR / "requirements.txt"
    if not requirements_file.exists():
        print("requirements.txt not found, skipping dependency installation.")
        return
    python_path = get_venv_python()
    print("Installing dependencies from requirements.txt...")
    run_command([python_path, "-m", "pip", "install", "--upgrade", "pip"])
    run_command([python_path, "-m", "pip", "install", "-r", str(requirements_file)])


def setup_shape_predictor():
    python_path = get_venv_python()
    script_path = BASE_DIR / "download_shape_predictor.py"
    if not script_path.exists():
        print("download_shape_predictor.py not found, skipping model download.")
        return
    print("Downloading and extracting shape_predictor_68_face_landmarks.dat...")
    run_command([python_path, str(script_path)])


def main():
    ensure_virtualenv()
    install_requirements()
    setup_shape_predictor()
    print("Environment setup completed successfully.")
    print("Next steps:")
    print("  1) Activate the virtual environment")
    if os.name == "nt":
        print("     venv\\Scripts\\Activate.ps1  (PowerShell)")
    else:
        print("     source venv/bin/activate")
    print("  2) Initialize the database (first time only):")
    print("     python rebuild_db.py")
    print("  3) Run the application:")
    print("     python run.py")


if __name__ == "__main__":
    main()

