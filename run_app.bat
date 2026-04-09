cd C:\conference
:: run this command for getting the serving ip address as http://192.168.129.114:5000 
waitress-serve --host=0.0.0.0 --port=5000 app:app
pause