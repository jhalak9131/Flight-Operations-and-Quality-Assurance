# Flight-Operations-and-Quality-Assurance
This project performs automated analysis of Flight Data Recorder (FDR) data from helicopter operations as part of a Flight Operations and Quality Assurance (FOQA/FOCA) program. Raw FDR datasets are processed in Python to evaluate engine and flight parameters against ideal operating ranges, detect exceedances, and flag potential safety.
The output is a structured Excel report with parameter-wise evaluations, exceedance/accident flags, DGCA compliance status, and visual summaries (bar charts, pie charts) for quick review by flight safety and quality teams.
Key Features


Automated FDR data ingestion — reads raw flight data recorder exports and structures them for analysis.
Parameter grouping (Group 1–Group 9) — engine and flight parameters are organized into logical groups (e.g., engine temperature parameters, control parameters, flight attitude parameters) for structured evaluation.
Ideal range evaluation — checks each parameter against defined safe/ideal operating limits, including:

Engine temperature (TGT – Turbine Gas Temperature)
T45 (turbine inter-stage temperature)
Alpha, Beta, Theta (flight control / attitude angles)
Other engine and airframe health parameters



Exceedance & accident detection — automatically flags parameter values that exceed safe thresholds, along with severity classification.
DGCA compliance mapping — cross-references exceedances against DGCA (Directorate General of Civil Aviation) regulatory limits and generates a compliance status.
Recommended actions — generates suggested corrective/maintenance actions for each flagged exceedance.
Automated Excel reporting — consolidates all evaluated parameters, flags, and compliance results into a single, structured Excel workbook.
Data visualization — generates bar charts and pie charts summarizing exceedance frequency, parameter-wise distribution, and compliance status for quick management review.


Tech Stack

Python (pandas, NumPy) — data processing and rule-based evaluation
Matplotlib / Seaborn — bar charts and pie charts for visual summaries
openpyxl / xlsxwriter — Excel report generation with formatted output

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

