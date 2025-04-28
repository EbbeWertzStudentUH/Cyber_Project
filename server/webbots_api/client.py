import paho.mqtt.client as mqtt

broker = "localhost"  # This can be 'localhost' if Mosquitto is on the same machine or the broker's IP address
port = 1883  # Default MQTT port for Mosquitto
topic = "test/topic"


def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(topic)

def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()} on topic {msg.topic}")

# Create a new MQTT client instance
client = mqtt.Client()

# Assign the callback functions
client.on_connect = on_connect
client.on_message = on_message

# Connect to the broker
client.connect(broker, port, 60)

# Start a loop that continuously checks for new messages and handles the connection
client.loop_start()

# Publish a test message to the topic
client.publish(topic, "Hello from MQTT client!")

# Keep the client running (this ensures it remains active to handle incoming messages)
import time
time.sleep(5)  # Give the client some time to receive messages before exiting
client.loop_stop()
