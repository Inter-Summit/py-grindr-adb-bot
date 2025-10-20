#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import time
import os
import sys
from devices import DEVICES

# Set UTF-8 encoding for Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def start_appium_servers():
    """Launch Appium servers for all devices in separate cmd windows"""
    
    print(f"[LAUNCHER] Starting {len(DEVICES)} Appium servers...")
    
    processes = []
    
    for i, device in enumerate(DEVICES):
        device_id = device["id"]
        port = device["port"]
        
        print(f"[{i+1}/{len(DEVICES)}] Processing device {device_id}...")
        
        # First, connect via ADB
        print(f"  [ADB] Connecting via ADB: {device_id}")
        try:
            adb_result = subprocess.run(
                ["adb", "connect", device_id],
                capture_output=True,
                text=True,
                timeout=10
            )
            if adb_result.returncode == 0:
                print(f"  [OK] ADB connected: {device_id}")
            else:
                print(f"  [WARN]  ADB connection warning: {adb_result.stderr.strip()}")
        except Exception as e:
            print(f"  [ERROR] ADB connection failed: {e}")
            continue  # Skip this device if ADB fails
        
        # Command to start Appium server (Appium 3.x compatible)
        appium_cmd = [
            "appium",
            "--port", str(port),
            "--allow-cors",
            "--default-capabilities", f'{{"udid":"{device_id}"}}'
        ]
        
        # Solo añadir base-path si existe en el dispositivo y no es "/"
        if "base_path" in device and device["base_path"] and device["base_path"] != "/":
            appium_cmd.extend(["--base-path", device["base_path"]])
        
        print(f"  [START] Starting Appium server on port {port}...")
        
        try:
            # Start in new cmd window (Windows)
            if os.name == 'nt':  # Windows
                process = subprocess.Popen(
                    ["cmd", "/c", "start", "cmd", "/k"] + appium_cmd,
                    shell=True
                )
            else:  # macOS/Linux
                # For macOS, open in new Terminal window
                terminal_cmd = f"osascript -e 'tell app \"Terminal\" to do script \"{' '.join(appium_cmd)}\"'"
                process = subprocess.Popen(terminal_cmd, shell=True)
            
            processes.append({
                "device_id": device_id,
                "port": port,
                "process": process
            })
            
            print(f"  [OK] Appium server started on port {port}")
            
            # Wait a bit between launches to avoid conflicts
            time.sleep(3)  # Increased to 3 seconds for stability
            
        except Exception as e:
            print(f"[ERROR] [{device_id}] Failed to start Appium server: {e}")
    
    print(f"\n🎉 All {len(processes)} Appium servers started!")
    print("\n📋 Server Summary:")
    for server in processes:
        print(f"  • {server['device_id']} → http://localhost:{server['port']}")
    
    print(f"\n[WARN]  Keep these terminal windows open while running the bot!")
    print(f"💡 To stop all servers, close the terminal windows or press Ctrl+C in each one.")
    
    return processes

def connect_all_adb():
    """Connect all devices via ADB only (without starting Appium)"""
    print(f"[ADB] Connecting {len(DEVICES)} devices via ADB...")
    
    connected = []
    failed = []
    
    for i, device in enumerate(DEVICES):
        device_id = device["id"]
        print(f"[{i+1}/{len(DEVICES)}] Connecting {device_id}...")
        
        try:
            result = subprocess.run(
                ["adb", "connect", device_id],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"  [OK] Connected: {device_id}")
                connected.append(device_id)
            else:
                print(f"  [ERROR] Failed: {device_id} - {result.stderr.strip()}")
                failed.append(device_id)
                
        except Exception as e:
            print(f"  [ERROR] Error connecting {device_id}: {e}")
            failed.append(device_id)
        
        time.sleep(1)
    
    print(f"\n📊 ADB Connection Summary:")
    print(f"  [OK] Connected: {len(connected)} devices")
    if connected:
        for device in connected:
            print(f"    • {device}")
    
    if failed:
        print(f"  [ERROR] Failed: {len(failed)} devices")
        for device in failed:
            print(f"    • {device}")

def stop_all_servers():
    """Stop all Appium servers (kills processes on specific ports)"""
    print("🛑 Stopping all Appium servers...")
    
    for device in DEVICES:
        port = device["port"]
        device_id = device["id"]
        
        try:
            if os.name == 'nt':  # Windows
                # Find and kill process using the port
                subprocess.run(f"netstat -ano | findstr :{port}", shell=True, capture_output=True)
                subprocess.run(f"taskkill /F /PID $(netstat -ano | findstr :{port} | awk '{{print $5}}' | head -1)", shell=True)
            else:  # macOS/Linux
                subprocess.run(f"lsof -ti tcp:{port} | xargs kill -9", shell=True)
            
            print(f"[OK] [{device_id}] Server on port {port} stopped")
        except Exception as e:
            print(f"[WARN]  [{device_id}] Could not stop server on port {port}: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "stop":
            stop_all_servers()
        elif sys.argv[1] == "adb":
            connect_all_adb()
        else:
            print("Usage:")
            print("  python appium.py          # Start all Appium servers (with ADB connect)")
            print("  python appium.py adb      # Connect all devices via ADB only")
            print("  python appium.py stop     # Stop all Appium servers")
    else:
        start_appium_servers()
        
        print(f"\n🔄 Servers are running. To stop them later, run:")
        print(f"   python appium.py stop")
        
        # Keep script running so user can see the output
        try:
            input("\nPress Enter to keep servers running (or Ctrl+C to exit)...")
        except KeyboardInterrupt:
            print(f"\n\n🛑 Stopping all servers...")
            stop_all_servers()