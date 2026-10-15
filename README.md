# aioEcoWitt

Simple python library for the EcoWitt Protocol

Inspired by pyecowit & ecowitt2mqtt

## Features

- **Async HTTP API Client**: Modern async/await support for EcoWitt weather stations
- **Structured Data Models**: Using mashumaro for type-safe data serialization
- **Device Grouping**: Data grouped by device type for easy Home Assistant integration
- **IoT Device Control**: Support for controlling water flow controllers and AC controllers
- **Comprehensive Sensor Support**: Temperature, humidity, PM2.5, rain, wind, lightning, and more
- **Battery Monitoring**: Detailed battery status for all wireless sensors
- **Unit Conversions**: Automatic conversion between metric and imperial units

## API Client Usage

```python
import asyncio
from aiohttp import ClientSession
from aioecowitt import EcoWittApi

async def main():
    async with ClientSession() as session:
        api = EcoWittApi("192.168.1.100", session=session)
        
        # Get device information
        device_info = await api.get_device_info()
        print(f"Device: {device_info.dev_name}")
        
        # Get all sensor data grouped by device
        data = await api.get_all_data()
        
        # Access weather data
        if data.weather_data.tempf:
            print(f"Temperature: {data.weather_data.tempf}°F")
            
        # Access channel sensors (PM2.5, leak, soil, etc.)
        if data.channel_sensors.pm25_ch1:
            print(f"PM2.5 CH1: {data.channel_sensors.pm25_ch1} μg/m³")
            
        # Access sensor diagnostics (battery, RSSI, signal)
        if data.sensor_diagnostics.wh68_batt:
            print(f"WH68 Battery: {data.sensor_diagnostics.wh68_batt}")
            
        # Control IoT devices
        for device in data.iot_devices:
            if device.nickname == "Water Controller":
                await api.control_iot_device(device.id, device.model, True)

asyncio.run(main())
```

## Data Structure

The API returns data grouped for easy device creation in Home Assistant:

- **DeviceInfo**: Basic device information (name, version, MAC)
- **WeatherData**: Main weather station data (temperature, humidity, wind, rain, etc.)
- **ChannelSensors**: Multi-channel sensors (PM2.5, leak, soil moisture, temperature/humidity)
- **SensorDiagnostics**: Battery levels, RSSI, and signal strength for all sensors
- **IoTDevices**: List of controllable IoT devices with current status

## Server Usage (Original Protocol Listener)

The original EcoWitt protocol listener is still available:
