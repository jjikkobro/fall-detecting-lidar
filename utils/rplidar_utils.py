from rplidar import RPLidar
import numpy as np

SCAN_TYPE = "normal"
SAMPLE_RATE = 10
MAX_BUFFER_SIZE = 3000
MIN_DISTANCE = 0

class libLIDAR(object):
    def __init__(self, port, baudrate):
        self.rpm = 0
        self.lidar = RPLidar(port, baudrate)
        self.scan = []

    def init(self):
        info = self.lidar.get_info()
        print(info)

    def getState(self):
        health = self.lidar.get_health()
        print(health)

    def scanning(self):
        scan_list = []
        iterator = self.lidar.iter_measures(SCAN_TYPE, MAX_BUFFER_SIZE)
        for new_scan, quality, angle, distance in iterator:
            if new_scan:
                if len(scan_list) > SAMPLE_RATE:
                    np_data = np.array(list(scan_list))
                    yield np_data[:, 1:]
                scan_list = []
            if distance > MIN_DISTANCE:
                scan_list.append((quality, angle, distance))
   
    def minmaxdetection(self, scan):
        distance_list = []
        if len(scan) == 0:
            pass
        else:
            for i in range(len(scan)):
                distance_list.append(scan[i][1])
            
            return min(distance_list), max(distance_list)

    def stop(self):
        self.lidar.stop()
        self.lidar.stop_motor()
        self.lidar.disconnect()

    def setRPM(self, rpm):
        self.lidar.motor_speed = rpm

    def getRPM(self):
        return self.lidar.motor_speed

    def getAngleRange(self, scan, minAngle, maxAngle):
        data = np.array(scan)
        condition = np.where((data[:, 0] < maxAngle) & (data[:, 0] > minAngle))
        return data[condition]

    def getAngleand(self, scan, Angle1, Angle2, Angle3, Angle4):
        data = np.array(scan)
        condition1 = np.where((data[:,0] < Angle2 ) & (data[:,0] > Angle1))
        condition2 = np.where((data[:,0] > Angle3) & (data[:,0] < Angle4))
        return data[condition1], data[condition2]
    
    def getDistanceRange(self, scan, minDist, maxDist):
        data = np.array(scan)
        condition = np.where((data[:, 1] < maxDist) & (data[:, 1] > minDist))
        return data[condition]

    def getAngleDistanceRange(self, scan, minAngle, maxAngle, minDist, maxDist):
        data = np.array(scan)
        condition = np.where((data[:, 0] < maxAngle) & (data[:, 0] > minAngle) & (data[:, 1] < maxDist) & (data[:, 1] > minDist))
        return data[condition]