import zmq
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import math

# 1. Set up the ZMQ context and subscriber socket
context = zmq.Context()
subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://localhost:5555")  # Connect to the publisher
subscriber.setsockopt_string(zmq.SUBSCRIBE, "")  # Subscribe to all messages

# 2. Initialize lists to store timestamps and orientation data
timestamps = []
rolls = []
pitches = []
yaws = []

# 3. Initialize angles
roll = 0.0
pitch = 0.0
yaw = 0.0

# 4. Define the function to calculate roll, pitch, and yaw
def calculate_rpy(gyro_x, gyro_y, gyro_z, dt):
    global roll, pitch, yaw

    # Update roll, pitch, and yaw using gyroscope data
    roll += gyro_x * dt
    pitch += gyro_y * dt
    yaw += gyro_z * dt

    # Convert radians to degrees
    roll_deg = math.degrees(roll)
    pitch_deg = math.degrees(pitch)
    yaw_deg = math.degrees(yaw)

    return roll_deg, pitch_deg, yaw_deg

# 5. Set up real-time plotting using matplotlib
fig, (ax_roll, ax_pitch, ax_yaw) = plt.subplots(3, 1, figsize=(10, 8))

ax_roll.set_title("Roll")
ax_pitch.set_title("Pitch")
ax_yaw.set_title("Yaw")

def animate(i):
    global roll, pitch, yaw
    
    try:
        # Receive data from the publisher
        message = subscriber.recv_string()
        data = message.split(',')
        
        # Parse the data
        gyroTs = float(data[0])
        gyro_x = float(data[4])
        gyro_y = float(data[5])
        gyro_z = float(data[6])
        
        # Calculate time difference (dt) from previous timestamp
        if timestamps:
            dt = (gyroTs - timestamps[-1]) / 1000.0  # Convert ms to seconds
        else:
            dt = 0.01  # Assume initial dt as 10 ms

        # Calculate roll, pitch, and yaw in degrees
        roll_deg, pitch_deg, yaw_deg = calculate_rpy(gyro_x, gyro_y, gyro_z, dt)
        
        # Append the data to lists
        timestamps.append(gyroTs)
        rolls.append(roll_deg)
        pitches.append(pitch_deg)
        yaws.append(yaw_deg)

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

# 6. Start the animation
ani = FuncAnimation(fig, animate, interval=100)
plt.show()
