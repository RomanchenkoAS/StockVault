

line = "select * from users where username = ?, ? = ?"

# Tuple
arguments = (10, "cash", 10000)

print(len(arguments))
print(line.count("?"))
index = 0
for item in arguments:
    substitution = str(item)
    line = line.replace("?", substitution, 1)
        
print(line)


# Count ?
# If not equal to len(arguments) - throw error
# Substitute each with argument