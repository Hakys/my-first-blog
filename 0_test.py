#!"J:\salvar\ServidorWamp\python\Python37\python.exe"

import mysql.connector

cnx = mysql.connector.connect(user='root', password='',
                              host='127.0.0.1',
                              database='djangogirls')
cnx.close()

print("Content-type: text/html\n")
print("<html><head>")
print("</head><body>")
print("Hola.")
print("</body></html>")