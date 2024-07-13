from flask import Flask, render_template
import asyncio
import struct
from bleak import BleakClient, BleakError
import time

app = Flask(__name__)
app.debug = True  # Make this False if you are no longer debugging

device_address = "10:06:1C:17:A4:42"  # My ESP32's BLE address
temperature_uuid = "beb5483e-36e1-4688-b7f5-ea07361b26a8"
humidity_uuid = "beb5483e-36e1-4688-b7f5-ea07361b26a9"

def bytes_to_float(bytes_data):
    """Converts 4 bytes of little-endian binary data to a floating-point number."""
    return struct.unpack('<f', bytes_data)[0]

async def connect_device(device_address):
    """Connects to the BLE device and returns the client object."""
    client = BleakClient(device_address)
    try:
        await client.connect()
        print("Connected to the device!")
        return client
    except BleakError as e:
        print(f"BLE error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return None

async def read_temperature_and_humidity():
    """Attempts to connect to the BLE device and read temperature and humidity data."""
    # Connect to the device
    client = await connect_device(device_address)  # Await the coroutine here
    if client is None:
        return None, None
    try:
        # Read the characteristic data
        temperature_bytes = await client.read_gatt_char(temperature_uuid)
        humidity_bytes = await client.read_gatt_char(humidity_uuid)

        # Convert bytes to float
        temperature = bytes_to_float(temperature_bytes)
        humidity = bytes_to_float(humidity_bytes)

        await client.disconnect()
        return temperature, humidity
    except BleakError as e:
        print(f"BLE error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        await client.disconnect()
    return None, None  # Return None for both values if there was an error

@app.route("/")
def hello():
    return "Welcome to Smart Garden!"

@app.route("/lab_temp")
def lab_temp():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    temperature, humidity = loop.run_until_complete(read_temperature_and_humidity())
    loop.close()
    
    if humidity is None or temperature is None:
        time.sleep(3)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        temperature, humidity = loop.run_until_complete(read_temperature_and_humidity())
        loop.close()
    if humidity is not None and temperature is not None:
        return render_template("lab_temp.html", temp=temperature, hum=humidity)
    else:
        return render_template("no_sensor.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
