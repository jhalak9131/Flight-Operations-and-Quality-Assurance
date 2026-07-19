@echo off
echo ===================================================
echo Starting FOQA Dashboard for Local Network (IP Based)
echo ===================================================
echo.
echo Please find your local IPv4 Address below:
ipconfig | findstr /i "IPv4"
echo.
echo You can access the dashboard from any PC on your offline network by typing:
echo http://[YOUR_IPV4_ADDRESS]:8501
echo.
echo For example: http://192.168.1.100:8501
echo.
echo Starting Server... (Do not close this window)
python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
