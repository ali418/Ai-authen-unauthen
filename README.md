# AI Face Authentication / Unauthorized Detection

This project is a face-recognition based access control system with:
- User management and admin dashboard
- Live camera view with authorized / unauthorized face highlighting
- Logging of access attempts

The instructions below explain how to run the project from scratch on a new machine.

## 1. Clone the repository

```bash
git clone https://github.com/ali418/Ai-authen-unauthen.git
cd Ai-authen-unauthen
```

## 2. Create and activate a virtual environment

### Windows (PowerShell)

```bash
python -m venv venv
venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install dependencies

With the virtual environment activated:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Download the dlib shape predictor model

You have two options.

### Option A: Use the environment setup script

This will create the virtual environment (if it does not exist), install dependencies, and download and extract the `shape_predictor_68_face_landmarks.dat` model file.

```bash
python setup_env.py
```

### Option B: Use the dedicated downloader

If you already created and activated the virtual environment and installed requirements:

```bash
python download_shape_predictor.py
```

The script will:
- Download `shape_predictor_68_face_landmarks.dat.bz2` from one of several mirrors
- Extract it to `shape_predictor_68_face_landmarks.dat` in the project root

## 5. Initialize the database (first time only)

The project uses SQLite by default. To create or rebuild the database schema:

```bash
python rebuild_db.py
```

This will create the database file and apply the initial schema.

## 6. Run the application

With the virtual environment activated and the model downloaded:

```bash
python run.py
```

By default, the application runs on:

```text
http://127.0.0.1:5000/
```

## 7. Notes

- Make sure your camera is connected and accessible by the operating system.
- On first runs you may need to add at least one user and capture a face image so that the system can distinguish between authorized and unauthorized faces.

