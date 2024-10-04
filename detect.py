from utils.rplidar_utils import libLIDAR as LiDAR
import time

# Preset
env = LiDAR('COM9', baudrate=256000)
env.init()
env.getState()

# Initial scanning to set up the boundary
count = 1
for scan in env.scanning():
    initial_scan = env.getAngleRange(scan, 50, 340)
    if count == 3:
        env.stop()
        break
    count += 1

# Variables to track short distances and continuity
short_distance_list = []
is_continuous = 0
threshold_distance = 0.5  # Example threshold distance in meters
threshold_angle = 30  # Example threshold angle in degrees
start_time = None

# Begin monitoring
for scan in env.scanning():
    # Keep scan boundary distance; if someone has slipped, the distance to the boundary becomes short.
    current_scan = env.getAngleRange(scan, 50, 340)

    # Check if the angles of initial and current scan match
    if initial_scan['angle'] == current_scan['angle']:
        if short_distance_list:
            # If there's a previous short distance and continuity check is not set
            if is_continuous == 0:
                start_angle = min(short_distance_list)
                end_angle = max(short_distance_list)
                calculated_angle = end_angle - start_angle

                if calculated_angle > threshold_angle:
                    print("Slipped!")
                    # Start time checking
                    if start_time is None:
                        start_time = time.time()

                    # Check if the slip condition persists
                    if time.time() - start_time > 3:  # If more than 3 seconds
                        print("Dangerous!")
                        break
        else:
            # Reset time if short distance list is empty
            start_time = None

    # Check if the distance has significantly shortened from the initial distance
    if current_scan['distance'] < (initial_scan['distance'] - threshold_distance):
        short_distance_list.append(current_scan['angle'])
        is_continuous = 1
    else:
        is_continuous = 0
        short_distance_list.clear()
