"""Example usage of the EcoWitt API client."""

import asyncio
import logging
from aiohttp import ClientSession

from aioecowitt import EcoWittApi

# Configure logging
logging.basicConfig(level=logging.DEBUG)


async def main():
    """Example usage of the EcoWitt API."""
    # Replace with your weather station's IP address
    host = "192.168.1.100"
    
    async with ClientSession() as session:
        # Create API client
        api = EcoWittApi(host, session=session)
        
        try:
            # Get basic device info
            print("Getting device info...")
            device_info = await api.get_device_info()
            print(f"Device: {device_info.dev_name} (Version: {device_info.version})")
            print(f"MAC: {device_info.mac}")
            print()
            
            # Get all device data grouped for Home Assistant
            print("Getting all device data...")
            data = await api.get_all_data()
            
            # Display weather data
            print("=== Weather Data ===")
            if data.weather_data.tempf:
                print(f"Outdoor Temperature: {data.weather_data.tempf}°F")
            if data.weather_data.humidity:
                print(f"Outdoor Humidity: {data.weather_data.humidity}%")
            if data.weather_data.tempinf:
                print(f"Indoor Temperature: {data.weather_data.tempinf}°F")
            if data.weather_data.humidityin:
                print(f"Indoor Humidity: {data.weather_data.humidityin}%")
            if data.weather_data.windspeedmph:
                print(f"Wind Speed: {data.weather_data.windspeedmph} mph")
            if data.weather_data.winddir:
                print(f"Wind Direction: {data.weather_data.winddir}°")
            if data.weather_data.rainratein:
                print(f"Rain Rate: {data.weather_data.rainratein} in/hr")
            if data.weather_data.dailyrainin:
                print(f"Daily Rain: {data.weather_data.dailyrainin} in")
            print()
            
            # Display channel sensors
            print("=== Channel Sensors ===")
            for i in range(1, 5):
                pm25_attr = f"pm25_ch{i}"
                if hasattr(data.channel_sensors, pm25_attr):
                    pm25_val = getattr(data.channel_sensors, pm25_attr)
                    if pm25_val:
                        print(f"PM2.5 Channel {i}: {pm25_val} μg/m³")
                
                leak_attr = f"leak_ch{i}"
                if hasattr(data.channel_sensors, leak_attr):
                    leak_val = getattr(data.channel_sensors, leak_attr)
                    if leak_val:
                        print(f"Leak Sensor Channel {i}: {leak_val}")
                
                temp_attr = f"temp_ch{i}"
                humi_attr = f"humidity_ch{i}"
                if hasattr(data.channel_sensors, temp_attr) and hasattr(data.channel_sensors, humi_attr):
                    temp_val = getattr(data.channel_sensors, temp_attr)
                    humi_val = getattr(data.channel_sensors, humi_attr)
                    if temp_val or humi_val:
                        print(f"T&H Channel {i}: {temp_val}°F, {humi_val}% RH")
            print()
            
            # Display sensor diagnostics
            print("=== Sensor Diagnostics ===")
            for attr_name in dir(data.sensor_diagnostics):
                if not attr_name.startswith('_') and attr_name.endswith('_batt'):
                    battery_level = getattr(data.sensor_diagnostics, attr_name)
                    if battery_level and battery_level not in ("--", ""):
                        sensor_name = attr_name.replace('_batt', '').upper()
                        print(f"{sensor_name} Battery: {battery_level}")
            print()
            
            # Display IoT devices
            print("=== IoT Devices ===")
            if data.iot_devices:
                for device in data.iot_devices:
                    print(f"Device: {device.nickname} (ID: {device.id}, Model: {device.model})")
                    if device.iot_running:
                        print(f"  Status: {device.iot_running}")
                    if device.rssi:
                        print(f"  RSSI: {device.rssi}")
                    if device.iotbatt:
                        print(f"  Battery: {device.iotbatt}")
                    print()
            else:
                print("No IoT devices found")
            
            # Example: Control an IoT device (uncomment to test)
            # if data.iot_devices:
            #     device = data.iot_devices[0]
            #     print(f"Turning on device: {device.nickname}")
            #     result = await api.control_iot_device(device.id, device.model, True)
            #     print(f"Control result: {result}")
            
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())