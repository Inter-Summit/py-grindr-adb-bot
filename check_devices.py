from appium import webdriver
from appium.options.android import UiAutomator2Options
from devices import DEVICES
import time

def check_device_connection(device_info):
    """Test if a device can connect successfully"""
    device_id = device_info["id"]
    port = device_info["port"]
    base_path = device_info["base_path"]
    
    opts = UiAutomator2Options()
    opts.set_capability("platformName", "Android")
    opts.set_capability("appium:deviceName", device_id)
    opts.set_capability("appium:udid", device_id)
    opts.set_capability("appium:automationName", "UiAutomator2")
    opts.set_capability("appium:appPackage", "com.grindrapp.android")
    opts.set_capability("appium:appActivity", ".HomeActivityOriginal")
    opts.set_capability("appium:noReset", True)

    try:
        print(f"Testing connection to {device_id}...")
        driver = webdriver.Remote(f"http://localhost:{port}{base_path}", options=opts)
        driver.implicitly_wait(5)
        time.sleep(2)
        
        # Test if we can activate app
        driver.activate_app("com.grindrapp.android")
        time.sleep(3)
        
        # Test if we can find Inbox
        try:
            driver.find_element("xpath", '//*[@text="Inbox"]')
            print(f"✅ {device_id} - WORKING (can access Inbox)")
            driver.quit()
            return True
        except:
            print(f"⚠️ {device_id} - CONNECTS but cannot access Inbox")
            driver.quit()
            return False
            
    except Exception as e:
        print(f"❌ {device_id} - FAILED: {str(e)[:100]}")
        return False

print("🔍 Checking device connections...")
working_devices = []
failed_devices = []

for device in DEVICES:
    if check_device_connection(device):
        working_devices.append(device)
    else:
        failed_devices.append(device)
    time.sleep(1)  # Short delay between tests

print(f"\n📊 RESULTS:")
print(f"✅ Working devices: {len(working_devices)}")
for device in working_devices:
    print(f"   - {device['id']}")

print(f"❌ Failed devices: {len(failed_devices)}")
for device in failed_devices:
    print(f"   - {device['id']}")

# Save working devices for use
if working_devices:
    print(f"\n💾 Creating working_devices.py with {len(working_devices)} devices...")
    with open('working_devices.py', 'w') as f:
        f.write("WORKING_DEVICES = [\n")
        for device in working_devices:
            f.write(f"    {device},\n")
        f.write("]\n")
    print("✅ working_devices.py created")