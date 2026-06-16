Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\appointmenthome"
WshShell.Run "python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501 --server.headless true", 0, False