from helpers import database

db = database('finance.db')

userid = 10
row = db.execute('SELECT * FROM users WHERE id=?', userid)

print(row)