import csv
import random

# Define possible values
times = ["morning", "afternoon", "evening", "night"]
locations = ["urban", "rural", "isolated"]
streetlights = ["yes", "no"]
police_patrol = ["high", "medium", "low"]
crowd_level = ["high", "medium", "low"]

def assign_risk(time, loc, inc, lights, patrol, crowd, dist):
    score = 0
    # Base on incidents
    if inc > 8:
        score += 3
    elif inc > 5:
        score += 2
    elif inc > 3:
        score += 1

    # Streetlights
    if lights == "no":
        score += 2
    # Patrol
    if patrol == "low":
        score += 2
    elif patrol == "medium":
        score += 1
    # Crowd
    if crowd == "low":
        score += 2
    elif crowd == "medium":
        score += 1
    # Time
    if time == "night":
        score += 3
    elif time == "evening":
        score += 1
    # Distance
    if dist > 3:
        score += 2
    elif dist > 2:
        score += 1

    if score >= 8:
        return "High"
    elif score >= 5:
        return "Medium"
    else:
        return "Low"

# Generate 4000 records
rows = []
for i in range(4000):
    t = random.choice(times)
    l = random.choice(locations)
    inc = random.randint(0, 10)
    s = random.choice(streetlights)
    p = random.choice(police_patrol)
    c = random.choice(crowd_level)
    d = round(random.uniform(0.2, 5.0), 2)
    risk = assign_risk(t, l, inc, s, p, c, d)
    rows.append([t, l, inc, s, p, c, d, risk])

# Write to CSV
with open("safety_data.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow([
        "time_of_day", "location_type", "incidents", 
        "streetlights", "police_patrol", "crowd_level", 
        "distance_from_home", "risk_level"
    ])
    writer.writerows(rows)

print("✅ safety_data.csv (4000 rows) generated successfully!")
