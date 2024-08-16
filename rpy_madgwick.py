import zmq
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from ahrs.filters import Madgwick
from ahrs.common.orientation import q2euler

# 1. Set up the ZMQ context and subscriber socket
context = zmq.Context()
subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://localhost:5555")
subscriber.setsockopt_string(zmq.SUBSCRIBE, "")

# 2. Initialize lists to store timestamps and orientation data
timestamps = []
rolls = []
pitches = []
yaws = []

# Initialize the Madgwick filter
madgwick = Madgwick()

# 4. Set up real-time plotting using matplotlib
fig, (ax_roll, ax_pitch, ax_yaw) = plt.subplots(3, 1, figsize=(10, 8))

ax_roll.set_title("Roll")
ax_pitch.set_title("Pitch")
ax_yaw.set_title("Yaw")

def animate(i):
    try:
        # Receive data from the publisher
        message = subscriber.recv_string()
        data = list(map(float, message.split(',')))
        
        # Parse the data
        gyroTs = float(data[0])
        accel_data = np.array(data[1:4])
        gyro_data = np.array(data[4:7])
        mag_data = np.array(data[7:10])
        
        # Normalize accelerometer and magnetometer data
        accel_data /= np.linalg.norm(accel_data)
        mag_data /= np.linalg.norm(mag_data)

         # Calculate time difference (dt) from previous timestamp
        if timestamps:
            dt = (gyroTs - timestamps[-1]) / 1000.0  # Convert ms to seconds
        else:
            dt = 0.01  # Assume initial dt as 10 ms
        
        # Update the Madgwick filter with new sensor data
        orientation = madgwick.updateMARG(gyro=gyro_data, acc=accel_data, mag=mag_data, dt=dt)
        
        # Convert the quaternion to Euler angles (roll, pitch, yaw)
        roll, pitch, yaw = np.degrees(q2euler(orientation))
        
        # Append the data to lists
        timestamps.append(gyroTs)
        rolls.append(roll)
        pitches.append(pitch)
        yaws.append(yaw)

        # Clear and update the plots
        ax_roll.clear()
        ax_pitch.clear()
        ax_yaw.clear()
        
        ax_roll.plot(timestamps, rolls, label='Roll', color='r')
        ax_pitch.plot(timestamps, pitches, label='Pitch', color='g')
        ax_yaw.plot(timestamps, yaws, label='Yaw', color='b')
        
        ax_roll.set_ylabel('Roll (°)')
        ax_pitch.set_ylabel('Pitch (°)')
        ax_yaw.set_ylabel('Yaw (°)')
        ax_yaw.set_xlabel('Time (ms)')
        
        ax_roll.legend()
        ax_pitch.legend()
        ax_yaw.legend()
        
        plt.tight_layout()
        
    except Exception as e:
        print(f"Error: {e}")

# 5. Start the animation
ani = FuncAnimation(fig, animate, interval=100)
plt.show()

