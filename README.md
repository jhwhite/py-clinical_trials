#Installation Instructions

Clone the repo `git clone git@github.com:jhwhite/py-clinical_trials.git`

Run the ingestor before running the Flask app. See the readme in the ingestor folder for instructions.

This was written with Python3.

Create a virtual environment and run `pip3 install -r requirements.txt`

You will also need to download elasticsearch.

Start an elasticsearch search process then in the main project directory run `python3 clinical_trials.py`
