# FOQA Flight Data Analysis Dashboard

A Streamlit-based web application for analyzing FOQA (Flight Operational Quality Assurance) Flight Data records (FDR). It automatically detects anomalies, temperature exceedances (e.g., TGT limits), and monitors pilot performance through rule-based and Machine Learning techniques.

## Prerequisites
- Python 3.12 (recommended)

## Installation

### Online Installation
If your PC has internet access, you can install the dependencies via pip:
```bash
pip install -r requirements.txt
```

### Offline Installation
If you are deploying this on an offline PC, you can download the packages on an internet-connected PC and transfer them:
1. On an internet-connected PC, run `download_for_offline_pc.bat` to download the packages into the `offline_packages` folder.
2. Copy the entire project folder (including `offline_packages`) to a USB drive and move it to your offline PC.
3. On the offline PC, open a command prompt in the project folder and run:
   ```bash
   pip install --no-index --find-links=./offline_packages -r requirements.txt
   ```

## Running the Application

To start the dashboard, you can simply run the provided batch script:
```bash
run_dashboard.bat
```

Alternatively, you can start the application manually via command line:
```bash
python -m streamlit run app.py
```

### Accessing the Dashboard on the Local Network
If you start the dashboard using `run_dashboard.bat`, it binds to `0.0.0.0`, meaning it will be accessible from other computers on your local network.
- Look at the console output of the batch script to find your local IPv4 address.
- On any other computer on the network, open a web browser and go to `http://[YOUR_IPV4_ADDRESS]:8501`.
