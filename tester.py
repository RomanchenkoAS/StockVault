from helpers import database

db = database('finance.db')

clause = 'insert into users '

userid = 10
row = db.execute(clause, userid)

print(row)

username = row[0]["username"]
print(username)
