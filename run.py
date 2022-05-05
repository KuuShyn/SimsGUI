#King AJ magalona0 - Solo
from SIMS import App
import mysql.connector

makedb = mysql.connector.connect(
    host='localhost',
    user=f'{App.user}',
    password=f'{App.passwd}'
)

curdb = makedb.cursor()

curdb.execute("CREATE DATABASE IF NOT EXISTS sims")

curdb.close()

app = App()
app.run()
#King AJ magalona0 - Solo