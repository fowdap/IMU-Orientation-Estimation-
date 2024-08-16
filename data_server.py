import zmq
import depthai as dai
# import numpy as np
# import math

def main():
    context = zmq.Context()
    publisher = context.socket(zmq.PUB)
    
    try:
        publisher.bind("tcp://*:5555")
        print("Publisher bound to port 5555")
    except zmq.ZMQError as e:
        print(f"Failed to bind publisher to port: {e}")
        return

    pipeline = dai.Pipeline()
    imu = pipeline.create(dai.node.IMU)
    xlinkOut = pipeline.create(dai.node.XLinkOut)

    xlinkOut.setStreamName("imu")

    imu.enableIMUSensor(dai.IMUSensor.ACCELEROMETER, 100)
    imu.enableIMUSensor(dai.IMUSensor.GYROSCOPE_CALIBRATED, 100)
    imu.enableIMUSensor(dai.IMUSensor.MAGNETOMETER_CALIBRATED, 100)

    imu.setBatchReportThreshold(1)
    imu.setMaxBatchReports(10)


    imu.out.link(xlinkOut.input)

    try:
        with dai.Device(pipeline) as device:
            imuQueue = device.getOutputQueue(name="imu", maxSize=1, blocking=False)
            print("Device initialized successfully")

            while True:
                try:
                    imuData = imuQueue.get()
                    imuPackets = imuData.packets
                    for imuPacket in imuPackets:
                        acceleroValues = imuPacket.acceleroMeter
                        gyroValues = imuPacket.gyroscope
                        magValues = imuPacket.magneticField

                        gyroTs = gyroValues.getTimestampDevice().total_seconds() * 1000
                        gyroTs = round(gyroTs, 3)

                        accelero = [acceleroValues.x, acceleroValues.y, acceleroValues.z]
                        gyro = [gyroValues.x, gyroValues.y, gyroValues.z]
                        mag = [magValues.x, magValues.y, magValues.z]

                        data_to_publish = f"{gyroTs},{accelero[0]},{accelero[1]},{accelero[2]},{gyro[0]},{gyro[1]},{gyro[2]},{mag[0]},{mag[1]},{mag[2]}"
                        publisher.send_string(data_to_publish)
                        print("data sent")

                except Exception as e:
                    print(f"Error occurred while processing IMU data: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        publisher.close()
        context.term()

if __name__ == "__main__":
    main()
