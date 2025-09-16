#!/usr/bin/env python3
"""Basic test of our new API implementation."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'aioecowitt'))

# Test models
print("Testing models...")
from models import DeviceInfo, WeatherData, ChannelSensors, SensorDiagnostics, EcoWittDeviceData, IoTDevice

# Test basic model creation
device_info = DeviceInfo("v1.0", "Test Station", "AA:BB:CC:DD:EE:FF")
print(f"DeviceInfo created: {device_info.dev_name}")

weather_data = WeatherData()
weather_data.tempf = "75.2"
weather_data.humidity = "60"
print(f"WeatherData created with temp: {weather_data.tempf}°F")

channel_sensors = ChannelSensors()
channel_sensors.pm25_ch1 = "12.5"
print(f"ChannelSensors created with PM2.5: {channel_sensors.pm25_ch1} μg/m³")

sensor_diagnostics = SensorDiagnostics()
sensor_diagnostics.wh68_batt = "80%"
print(f"SensorDiagnostics created with battery: {sensor_diagnostics.wh68_batt}")

iot_device = IoTDevice(id=1, model=1, nickname="Water Controller", rfnet_state=1)
print(f"IoTDevice created: {iot_device.nickname}")

# Test complete data structure
complete_data = EcoWittDeviceData(
    device_info=device_info,
    weather_data=weather_data,
    channel_sensors=channel_sensors,
    sensor_diagnostics=sensor_diagnostics,
    iot_devices=[iot_device]
)
print(f"Complete data structure created successfully")

# Test dict conversion
device_dict = device_info.to_dict()
print(f"Device as dict: {device_dict}")

recreated_device = DeviceInfo.from_dict(device_dict)
print(f"Recreated device: {recreated_device.dev_name}")

print("\n✅ All model tests passed!")

# Test core API functionality without network calls
print("\nTesting API core functions...")
from errors import EcoWittError, RequestError

try:
    raise RequestError("Test error")
except RequestError as e:
    print(f"RequestError caught: {e}")

print("✅ Error handling works!")

print("\nAll tests completed successfully! 🎉")