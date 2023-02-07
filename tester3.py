def getfirstword(string):
    result = ""
    for char in string:
        if char != " ":
            result += char
        else:
            return result.upper()
        
line = "select * from shit lol lol shit;"

line1 = "insert foo into username;"

print(getfirstword(line))
print(getfirstword(line1))