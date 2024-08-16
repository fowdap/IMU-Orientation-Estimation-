import zmq
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Initialize ZMQ context and subscribe to the data
context = zmq.Context()
subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://localhost:5555")  # Connect to the publisher's address
subscriber.setsockopt_string(zmq.SUBSCRIBE, '')  # Subscribe to all messages

# Functions to calculate roll, pitch, and yaw
def calculate_roll_pitch_yaw(accelero, mag):
    ax, ay, az = accelero
    mx, my, mz = mag

    # Roll and pitch from accelerometer
    roll = np.arctan2(ay, az) * 180 / np.pi
    pitch = np.arctan2(-ax, np.sqrt(ay**2 + az**2)) * 180 / np.pi

    # Yaw from magnetometer (and considering pitch and roll for tilt compensation)
    yaw = np.arctan2(my * np.cos(roll) - mz * np.sin(roll),
                     mx * np.cos(pitch) + my * np.sin(roll) * np.sin(pitch) + mz * np.cos(roll) * np.sin(pitch)) * 180 / np.pi

    return roll, pitch, yaw

# Dynamic Plotting setup
fig, (ax_roll, ax_pitch, ax_yaw) = plt.subplots(3, 1)
roll_data, pitch_data, yaw_data, timestamps = [], [], [], []

ax_roll.set_title("Roll")
ax_pitch.set_title("Pitch")
ax_yaw.set_title("Yaw")

def animate(i):
    try:
        # Receive and process the message from the publisher
        message = subscriber.recv_string()
        data = list(map(float, message.split(',')))
        
        timestamp = data[0]
        accelero = data[1:4]
        mag = data[7:10]
        
        # Calculate orientation
        roll, pitch, yaw = calculate_roll_pitch_yaw(accelero, mag)

        # Update the data lists
        timestamps.append(timestamp)
        roll_data.append(roll)
        pitch_data.append(pitch)
        yaw_data.append(yaw)
        
        # Plot the data
        ax_roll.clear()
        ax_pitch.clear()
        ax_yaw.clear()

        ax_roll.plot(timestamps, roll_data, label="Roll")
        ax_pitch.plot(timestamps, pitch_data, label="Pitch")
        ax_yaw.plot(timestamps, yaw_data, label="Yaw")

        ax_roll.legend()
        ax_pitch.legend()
        ax_yaw.legend()

    except Exception as e:
        print(f"Error: {e}")

# Set up the animation
ani = animation.FuncAnimation(fig, animate, interval=100)  # Update every 100 ms
plt.show()
