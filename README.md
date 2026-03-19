# Study Diary App

A local web app to organize study notes by course and section.
Built with Python and Streamlit. Data stored locally in CSV files.

## Features

- Create and manage courses and sections
- Add, edit and delete notes with Markdown support
- Attach files to notes (images, PDF, Python scripts, CSV, Jupyter notebooks)
- All data stored locally — no internet required

## Requirements

- Python 3.8+
- pip

## How to Run

1. Clone this repository:
   git clone https://github.com/Adolfds/study-diary-app.git
   cd study-diary-app

2. Create and activate a virtual environment:
   python -m venv venv
   venv\Scripts\activate       # Windows
   source venv/bin/activate    # Linux/macOS

3. Install dependencies:
   pip install -r requirements.txt

4. Start the app:
   streamlit run app.py

The app opens automatically at http://localhost:8501

## Tech Stack

- Python
- Streamlit
- Pandas
- nbconvert
