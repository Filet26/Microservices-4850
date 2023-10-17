import datetime
timestamp = "2023-09-26%2011:10:57.843920"
timestamp = timestamp.replace("%20", " ")
print(timestamp)
timestamp_converted = datetime.datetime.strptime(timestamp, "%Y-%m-%d%H:%M:%S.%f")
print(timestamp)