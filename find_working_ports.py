import requests
import time
from devices import DEVICES

def check_appium_server(port):
    """Check if an Appium server is running on the given port"""
    try:
        response = requests.get(f"http://localhost:{port}/wd/hub/status", timeout=2)
        if response.status_code == 200:
            return True
    except:
        pass
    return False

def scan_port_range(start_port, end_port):
    """Scan a range of ports for Appium servers"""
    working_ports = []
    print(f"Scanning ports {start_port}-{end_port}...")
    
    for port in range(start_port, end_port + 1):
        if check_appium_server(port):
            print(f"✅ Found Appium server on port {port}")
            working_ports.append(port)
        else:
            print(f"❌ No server on port {port}")
    
    return working_ports

# Check configured ports first
print("🔍 Checking configured ports from devices.py...")
configured_ports = [device["port"] for device in DEVICES]
for port in configured_ports:
    if check_appium_server(port):
        print(f"✅ Configured port {port} is working")
    else:
        print(f"❌ Configured port {port} is not working")

# Scan common Appium port ranges
print("\n🔍 Scanning common Appium port ranges...")
working_ports = []

# Common ranges
ranges = [
    (4723, 4750),  # Default Appium range
    (4700, 4730),  # Extended range
    (8000, 8050),  # Alternative range
]

for start, end in ranges:
    found_ports = scan_port_range(start, end)
    working_ports.extend(found_ports)

if working_ports:
    print(f"\n✅ Found {len(working_ports)} working Appium servers:")
    for port in working_ports:
        print(f"   - Port {port}")
        
    # Based on the logs, create a mapping
    device_ids_from_logs = [
        "100.64.100.6:5575",
        "100.64.100.6:5585", 
        "100.64.100.6:5565"
    ]
    
    print(f"\n💾 Creating corrected device configuration...")
    if len(working_ports) >= len(device_ids_from_logs):
        with open('corrected_devices.py', 'w') as f:
            f.write("CORRECTED_DEVICES = [\n")
            for i, device_id in enumerate(device_ids_from_logs):
                if i < len(working_ports):
                    f.write(f'    {{"id": "{device_id}", "port": {working_ports[i]}, "base_path": "/wd/hub"}},\n')
            f.write("]\n")
        print("✅ corrected_devices.py created")
else:
    print("❌ No working Appium servers found")
    print("Make sure Appium servers are running before testing devices")