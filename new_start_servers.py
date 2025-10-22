#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import time
import os
import sys
from devices import DEVICES

# Set UTF-8 encoding for Windows
if sys.platform == "win32":
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except:
        pass

def get_appium_port(adb_port):
    """Generate Appium port by adding 44 prefix to ADB port"""
    # Extract port number from device ID (e.g., "100.64.100.6:5565" -> "5565")
    if ":" in adb_port:
        port_str = adb_port.split(":")[-1]
    else:
        port_str = str(adb_port)
    
    # Add 44 prefix (e.g., "5565" -> "445565")
    appium_port = f"4{port_str}"
    return int(appium_port)

def start_appium_servers():
    """Launch Appium servers for all devices with auto-generated ports"""
    
    print(f"[LAUNCHER] Starting {len(DEVICES)} Appium servers with auto-generated ports...")
    
    processes = []
    
    for i, device in enumerate(DEVICES):
        device_id = device["id"]
        
        # Generate Appium port from ADB port
        appium_port = get_appium_port(device_id)
        
        print(f"[{i+1}/{len(DEVICES)}] Processing device {device_id}...")
        print(f"  Auto-generated Appium port: {appium_port}")
        
        # First, connect via ADB
        print(f"  [ADB] Connecting via ADB: {device_id}")
        try:
            adb_result = subprocess.run([
                "adb", "connect", device_id
            ], capture_output=True, text=True, timeout=10)
            
            if adb_result.returncode == 0:
                print(f"  [OK] ADB connected: {device_id}")
            else:
                print(f"  [WARN] ADB connection warning: {adb_result.stderr.strip()}")
        except Exception as e:
            print(f"  [ERROR] ADB connection failed: {e}")
            continue
        
        # Wait a moment for ADB to stabilize
        time.sleep(2)
        
        # Create the Appium command
        appium_cmd = [
            "appium",
            "--port", str(appium_port),
            "--base-path", "/wd/hub",
            "--default-capabilities", f'{{"udid": "{device_id}"}}',
            "--allow-insecure", "adb_shell",
            "--relaxed-security"
        ]
        
        print(f"  [START] Starting Appium server on port {appium_port}...")
        
        try:
            # Start Appium server in a new window
            if os.name == 'nt':  # Windows
                # Use start command to open new cmd window
                full_cmd = ['start', 'cmd', '/k'] + appium_cmd
                process = subprocess.Popen(
                    full_cmd,
                    shell=True,
                    cwd=os.getcwd()
                )
            else:  # macOS/Linux
                # Use terminal to open new window
                full_cmd = ['osascript', '-e', f'tell app "Terminal" to do script "{" ".join(appium_cmd)}"']
                process = subprocess.Popen(full_cmd)
            
            processes.append({
                'process': process,
                'device_id': device_id,
                'port': appium_port
            })
            
            print(f"  [OK] Appium server started on port {appium_port}")
            
        except Exception as e:
            print(f"[ERROR] [{device_id}] Failed to start Appium server: {e}")
            continue
        
        # Small delay between starting servers
        time.sleep(1)
    
    print(f"\n[WARN] Keep these terminal windows open while running the bot!")
    print(f"[INFO] Started {len(processes)} Appium servers")
    
    return processes

def connect_all_devices():
    """Connect all devices via ADB first"""
    print(f"[ADB] Connecting {len(DEVICES)} devices via ADB...")
    
    connected = []
    failed = []
    
    for device in DEVICES:
        device_id = device["id"]
        
        try:
            result = subprocess.run([
                "adb", "connect", device_id
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                print(f"  [OK] Connected: {device_id}")
                connected.append(device_id)
            else:
                print(f"  [ERROR] Failed: {device_id} - {result.stderr.strip()}")
                failed.append(device_id)
                
        except subprocess.TimeoutExpired:
            print(f"  [ERROR] Timeout connecting to {device_id}")
            failed.append(device_id)
        except Exception as e:
            print(f"  [ERROR] Error connecting {device_id}: {e}")
            failed.append(device_id)
        
        time.sleep(1)  # Brief delay between connections
    
    print(f"\n[SUMMARY]:")
    print(f"  [OK] Connected: {len(connected)} devices")
    for device_id in connected:
        adb_port = device_id.split(":")[-1]
        appium_port = f"44{adb_port}"
        print(f"    - {device_id} -> Appium port {appium_port}")
    
    if failed:
        print(f"  [ERROR] Failed: {len(failed)} devices")
        for device_id in failed:
            print(f"    - {device_id}")

def stop_all_servers():
    """Stop all running Appium servers"""
    print("[INFO] Stopping all Appium servers...")
    
    for device in DEVICES:
        device_id = device["id"]
        appium_port = get_appium_port(device_id)
        
        try:
            # Kill process on specific port
            if os.name == 'nt':  # Windows
                subprocess.run([
                    "taskkill", "/F", "/FI", f"WINDOWTITLE eq *{appium_port}*"
                ], capture_output=True)
            else:  # macOS/Linux
                subprocess.run([
                    "lsof", "-ti", f":{appium_port}", "|", "xargs", "kill", "-9"
                ], shell=True, capture_output=True)
                
            print(f"[OK] [{device_id}] Server on port {appium_port} stopped")
        except Exception as e:
            print(f"[WARN] [{device_id}] Could not stop server on port {appium_port}: {e}")

def main():
    """Main function"""
    print("=" * 60)
    print("GRINDR BOT - NEW AUTO-PORT APPIUM SERVER STARTER")
    print("=" * 60)
    print(f"Total devices configured: {len(DEVICES)}")
    print("Port generation: ADB port with '44' prefix")
    print("Example: 100.64.100.6:5565 -> Appium port 445565")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == "stop":
        stop_all_servers()
        return
    
    if len(sys.argv) > 1 and sys.argv[1] == "connect":
        connect_all_devices()
        return
    
    # Show port mapping
    print("\nPort mapping preview:")
    for i, device in enumerate(DEVICES[:5]):  # Show first 5
        device_id = device["id"]
        appium_port = get_appium_port(device_id)
        print(f"  {device_id} -> Appium port {appium_port}")
    
    if len(DEVICES) > 5:
        print(f"  ... and {len(DEVICES) - 5} more devices")
    
    print("\nOptions:")
    print("  python new_start_servers.py         - Start all servers")
    print("  python new_start_servers.py connect - Connect ADB only")
    print("  python new_start_servers.py stop    - Stop all servers")
    
    input("\nPress Enter to start all Appium servers...")
    
    start_appium_servers()

if __name__ == "__main__":
    main()