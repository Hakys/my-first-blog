#!"C:\salvar\xampp\python\python.exe"

import mysql.connector

cnx = mysql.connector.connect(
    user='operadorweb', 
    password='48933206Gloria',                          
    host='diablaroja.es',
    database='wordpress_60'
    )
cnx.close()

print("Content-type: text/html\n")
print("<html><head>")
print("</head><body>")
print("Hola.")
print("</body></html>")