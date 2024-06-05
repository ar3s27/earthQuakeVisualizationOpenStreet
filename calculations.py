import random as rnd

def earthquake_percentage():
    percentage = rnd.uniform(20.0, 40.0)
    return percentage

def earthquake_location():
    latitude = rnd.uniform(36.0, 41.0)
    longitude = rnd.uniform(27.0, 40.0)
    location = [latitude, longitude]
    return location

print(earthquake_percentage())
print(earthquake_location())
