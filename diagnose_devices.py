from appium import webdriver
from appium.options.android import UiAutomator2Options
from devices import DEVICES
import time
from datetime import datetime

def get_timestamp():
    return datetime.now().strftime("%H:%M:%S")

def diagnose_device(device_info):
    """Diagnose a single device comprehensively"""
    device_id = device_info["id"]
    port = device_info["port"]
    base_path = device_info["base_path"]
    
    print(f"\n[{get_timestamp()}] 🔍 DIAGNOSING DEVICE: {device_id}")
    print(f"[{get_timestamp()}] Port: {port}, Base Path: {base_path}")
    
    # Test 1: Basic connection
    print(f"[{get_timestamp()}] ⚡ Test 1: Basic Appium connection...")
    try:
        opts = UiAutomator2Options()
        opts.set_capability("platformName", "Android")
        opts.set_capability("appium:deviceName", device_id)
        opts.set_capability("appium:udid", device_id)
        opts.set_capability("appium:automationName", "UiAutomator2")
        opts.set_capability("appium:noReset", True)
        
        driver = webdriver.Remote(f"http://localhost:{port}{base_path}", options=opts)
        driver.implicitly_wait(5)
        print(f"[{get_timestamp()}] ✅ Basic connection successful")
        
        # Test 2: Check current app state
        print(f"[{get_timestamp()}] ⚡ Test 2: Checking current app state...")
        try:
            current_package = driver.current_package
            current_activity = driver.current_activity
            print(f"[{get_timestamp()}] 📱 Current package: {current_package}")
            print(f"[{get_timestamp()}] 📱 Current activity: {current_activity}")
            
            if "grindr" in current_package.lower():
                print(f"[{get_timestamp()}] ✅ Grindr is currently active")
            else:
                print(f"[{get_timestamp()}] ⚠️ Grindr is NOT active - current app: {current_package}")
        except Exception as e:
            print(f"[{get_timestamp()}] ❌ Could not get current app: {e}")
        
        # Test 3: Try to activate Grindr
        print(f"[{get_timestamp()}] ⚡ Test 3: Attempting to activate Grindr...")
        try:
            driver.activate_app("com.grindrapp.android")
            time.sleep(3)
            print(f"[{get_timestamp()}] ✅ Grindr activation attempted")
            
            # Check if it worked
            current_package = driver.current_package
            if "grindr" in current_package.lower():
                print(f"[{get_timestamp()}] ✅ Grindr activation successful")
            else:
                print(f"[{get_timestamp()}] ❌ Grindr activation failed - still on: {current_package}")
        except Exception as e:
            print(f"[{get_timestamp()}] ❌ Grindr activation error: {e}")
        
        # Test 4: Look for UI elements
        print(f"[{get_timestamp()}] ⚡ Test 4: Checking for basic UI elements...")
        try:
            elements = driver.find_elements("class name", "android.widget.TextView")
            print(f"[{get_timestamp()}] 📱 Found {len(elements)} TextView elements")
            
            # Look for common UI text
            common_texts = ["Inbox", "Browse", "Messages", "Profile", "Settings"]
            found_texts = []
            
            for element in elements[:20]:  # Check first 20 elements
                try:
                    text = element.text
                    if text and text in common_texts:
                        found_texts.append(text)
                except:
                    continue
            
            if found_texts:
                print(f"[{get_timestamp()}] ✅ Found UI elements: {found_texts}")
            else:
                print(f"[{get_timestamp()}] ⚠️ No familiar UI elements found")
                
        except Exception as e:
            print(f"[{get_timestamp()}] ❌ UI check error: {e}")
        
        # Test 5: Check for Inbox specifically
        print(f"[{get_timestamp()}] ⚡ Test 5: Looking for Inbox button...")
        try:
            inbox_elements = driver.find_elements("xpath", '//*[@text="Inbox"]')
            if inbox_elements:
                print(f"[{get_timestamp()}] ✅ Inbox button found - Grindr UI is ready")
            else:
                print(f"[{get_timestamp()}] ❌ Inbox button NOT found - Grindr may not be loaded")
        except Exception as e:
            print(f"[{get_timestamp()}] ❌ Inbox check error: {e}")
        
        driver.quit()
        print(f"[{get_timestamp()}] ✅ Device {device_id} diagnosis completed")
        return True
        
    except Exception as e:
        print(f"[{get_timestamp()}] ❌ Connection failed for {device_id}: {e}")
        return False

# Test all active devices
active_devices = [d for d in DEVICES if d["id"] in ["100.64.100.6:5575", "100.64.100.6:5585", "100.64.100.6:5565"]]

print(f"[{get_timestamp()}] 🚀 Starting device diagnosis for {len(active_devices)} devices...")
print(f"[{get_timestamp()}] 📋 This will check connection, app state, and UI readiness")

successful_devices = []
failed_devices = []

for device in active_devices:
    if diagnose_device(device):
        successful_devices.append(device["id"])
    else:
        failed_devices.append(device["id"])
    
    time.sleep(2)  # Brief pause between devices

print(f"\n[{get_timestamp()}] 📊 DIAGNOSIS SUMMARY:")
print(f"[{get_timestamp()}] ✅ Working devices ({len(successful_devices)}): {successful_devices}")
print(f"[{get_timestamp()}] ❌ Failed devices ({len(failed_devices)}): {failed_devices}")

if failed_devices:
    print(f"\n[{get_timestamp()}] 💡 RECOMMENDATIONS for failed devices:")
    print(f"[{get_timestamp()}] 1. Check if Appium servers are running on the correct ports")
    print(f"[{get_timestamp()}] 2. Restart the failed device emulators")
    print(f"[{get_timestamp()}] 3. Manually open Grindr app on failed devices")
    print(f"[{get_timestamp()}] 4. Check if devices are properly connected to adb")