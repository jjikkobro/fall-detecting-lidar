from utils.rplidar_utils import libLIDAR as LiDAR
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time
import pymysql
from dotenv import dotenv_values
from ast import literal_eval
import serial

# Preset
env = LiDAR('/dev/ttyUSB0', baudrate=256000)
ardu = serial.Serial('/dev/ttyACM0', baudrate=9600, timeout=.1)
env.init()
env.getState()
config = dotenv_values()
db_config = literal_eval(config['db_config'])

def waiting_for_lightup():
    global last_value
    print('waiting for lightup...')
    while True:
        if ardu.readline():
            last_value = 1
            return True
        else:
            print(ardu.readline())

def is_turnoff():
    global last_value
    data = ardu.readlines()
    if data:
        last_value = data[-1].decode('utf-8').strip() 
        print(last_value)
        
    if  int(last_value) == 0:
        return True
    else:
        return False

def connect_to_database():
    return pymysql.connect(**db_config)

def map_angle(angle):
    if 0 <= angle <= 50:
        return 50 - angle
    elif 310 <= angle <= 360:
        return 100 - (angle - 310)  # Map 310-360 to 50-100
    else:
        return angle
    
def db_update(cursor, status):
    cursor.execute(f'UPDATE home_status set status={status} where user=1')

conn = connect_to_database()
cursor = conn.cursor()   
waiting_for_lightup()
db_update(cursor, 1)
print("Status updated as 'Using'")
# Initial scanning to set up the boundary
count = 1
for scan in env.scanning():
    initial_scan1, initial_scan2 = env.getAngleand(scan, 0, 50, 310, 360)
    if count == 10:
        env.lidar.stop()
        env.lidar.stop_motor()
        break
    count += 1
    
if (initial_scan1 is not None and initial_scan1.size > 0) or (initial_scan2 is not None and initial_scan2.size > 0):
    # Combine the scans if both are valid
    initial_combined_scan = np.vstack((initial_scan1, initial_scan2)) if initial_scan1.size > 0 and initial_scan2.size > 0 else initial_scan1 if initial_scan1.size > 0 else initial_scan2
    
    initial_combined_scan[:, 0] = np.vectorize(map_angle)(initial_combined_scan[:, 0])
    initial_combined_scan[:, 0] = np.round(initial_combined_scan[:, 0]).astype(int)
    df_initial = pd.DataFrame(initial_combined_scan, columns=['angle', 'distance'])
    df_initial_grouped = df_initial.groupby('angle', as_index=False).mean()

    angles = np.deg2rad(initial_combined_scan[:, 0])  # Convert angles to radians for polar plotting
    distances = initial_combined_scan[:, 1]  # Extract distances

    # Plotting the initial scan data
    plt.figure(figsize=(10, 10))
    ax = plt.subplot(111, polar=True)  # Polar plot for angle-distance data
    ax.set_facecolor('black')  # Axes background
    plt.gcf().set_facecolor('black')
    
    ax.scatter(angles, distances, c='b', s=6)  # Scatter plot with red dots
    ax.set_title('Initial Boundary Scan Visualization', color='white')
    initial_round = max(distances) + 1
    ax.set_rmax(initial_round)  # Set maximum radius slightly larger than max distance

    # Save the plot as an image file
    plt.savefig('/home/matthew/project/initial_scan_visualization.png')  # Save the plot as a PNG file
    plt.close()  # Close the plot to free memory
    print("Plot saved as 'initial_scan_visualization.png'")
else:
    print("Initial scan data not available or is empty.")

print(initial_combined_scan)
time.sleep(1)


unslip = True
while unslip:
    try:
        count = 1
        for scan in env.scanning():
            current_scan1, current_scan2 = env.getAngleand(scan, 0, 50, 310, 360)
            if count == 10:
                env.lidar.stop()
                break
            count += 1
        
        if (current_scan1 is not None and current_scan1.size > 0) or (current_scan2 is not None and current_scan2.size > 0):
            current_combined_scan = np.vstack((current_scan1, current_scan2)) if current_scan1.size > 0 and current_scan2.size > 0 else current_scan1 if current_scan1.size > 0 else current_scan2
            
            current_combined_scan[:, 0] = np.vectorize(map_angle)(current_combined_scan[:, 0])
            current_combined_scan[:, 0] = np.round(current_combined_scan[:, 0]).astype(int)
            df_current = pd.DataFrame(current_combined_scan, columns=['angle', 'distance'])
            df_current_grouped = df_current.groupby('angle', as_index=False).mean()
            
            # Find matching angles and compare distances
            shorter_distances = []
            for current_point in current_combined_scan:
                # Find the corresponding initial distance for the same angle
                matching_initial = initial_combined_scan[initial_combined_scan[:, 0] == current_point[0]]
                if len(matching_initial) > 0:
                    initial_distance = matching_initial[0, 1]
                    if current_point[1] < (initial_distance - 5):
                        # Store angle and distance if the current distance is shorter
                        shorter_distances.append(current_point)

            # Convert to numpy array for plotting
            shorter_distances = np.array(shorter_distances)
            if shorter_distances.size > 0:
                angles = np.deg2rad(shorter_distances[:, 0])
                distances = shorter_distances[:, 1]

                # Plot the shorter distances
                plt.figure(figsize=(10, 10))
                ax = plt.subplot(111, polar=True)
                ax.set_facecolor('black')  # Axes background
                plt.gcf().set_facecolor('black')
                
                ax.scatter(angles, distances, c='r', s=6)  # Scatter plot with blue dots for shorter distances
                ax.set_title('Current Status Scan Visualization', color='white')
                ax.set_rmax(initial_round)
                plt.savefig('/home/matthew/project/manikin_scan_visualization.png')
                plt.close()
                print("Plot saved as 'manikin_scan_visualization.png'")
                
                # Check for continuity of shorter points
                sorted_angles = np.sort(shorter_distances[:, 0])
                consecutive_count = 1
                print("shorted_angles : ", sorted_angles)
                print("number of sorted_angles : ", len(sorted_angles))
                if is_turnoff():
                    print('Went out')
                    db_update(cursor, 0)
                    env.stop()
                    break

                for i in range(1, len(sorted_angles)):
                    if sorted_angles[i] - sorted_angles[i - 1] <= 5:
                        consecutive_count += 1
                        if consecutive_count >= 10:
                            print("Continuous Fallen points detected. Stopping the scan.")  
                            
                            print('Send status number : 2')
                            ardu.write(b'2')                      
                            db_update(cursor, 2)
                            unslip = False
                            env.stop()
                            break
                    else:
                        consecutive_count = 1  

                if not unslip:
                    break
            else:
                if is_turnoff():
                    print("Went out from toilet.")
                    db_update(cursor, 0)
                    env.stop()
                    break
                else:
                    print("No shorter distances found in current scans.")
        else:
            print("Current scan data not available or is empty.")
        
    except KeyboardInterrupt:
        env.stop()
        db_update(cursor, 0)
        break
    
    except Exception as e:
        print(e)
        env.stop()
        db_update(cursor, 0)
        break

while True: 
    if is_turnoff():
        db_update(cursor, 0)
        break
    else:
        continue
