# =======================
# 1. Imports
# =======================
import random
import csv


# Dense traffic highway driving simulation - periods of slow and little movement
# coupled with stretches of high-pace driving
# Author: Andy Suri

# =======================
# 3. Variable Initialization
# =======================
header = ["Time", "Speed (m/s)"]
data = [header]  # To store {time, speed} pairs

# Acceleration ranges (m/s²)
startFast = 0.0   # Fast acceleration lower bound
endFast = 10      # Fast acceleration upper bound
startSlow = -10   # Slow acceleration lower bound (dense traffic)
endSlow = 5       # Slow acceleration upper bound

Speed = 0.0       # Current speed of the vehicle
maxSpeed = 30     # Maximum highway speed (m/s)

current_time = 0.00   # Start time
interval = 0.01       # Time step in seconds
generationRange = 700 # Total duration for simulation (seconds)

isDense = 0  # Flag for traffic density (0 = free, 1 = dense)

# =======================
# 4. Data Generation Loop
# =======================
while current_time < generationRange:
    # Update traffic density randomly every second
    if int(current_time) != int(current_time - interval):
        isDense = random.randint(0, 1)

    # Determine acceleration based on traffic density
    if isDense:
        acceleration = random.uniform(startSlow, endSlow)  # Dense traffic
    else:
        acceleration = random.uniform(startFast, endFast)  # Free-flow traffic

    # Integrate acceleration to compute speed change
    accel_integration = acceleration * interval

    # Update speed while keeping within 0 and maxSpeed limits
    if 0 <= Speed + accel_integration <= maxSpeed:
        Speed += accel_integration

    # Round values for better readability
    current_time = round(current_time, 3)
    Speed = round(Speed, 1)

    # Store the time-speed pair
    data.append([current_time, Speed])

    # Increment time
    current_time += interval

# =======================
# 5. Export Data to CSV
# =======================
with open("config\drive_cycle\highway_randomized_conditions.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(data)