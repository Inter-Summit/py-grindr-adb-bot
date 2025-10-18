from appium import webdriver
from appium.options.android import UiAutomator2Options
from devices import DEVICES
import time

def quick_debug(device_id, port, base_path):
    opts = UiAutomator2Options()
    opts.set_capability("platformName", "Android")
    opts.set_capability("appium:deviceName", device_id)
    opts.set_capability("appium:udid", device_id)
    opts.set_capability("appium:automationName", "UiAutomator2")
    opts.set_capability("appium:appPackage", "com.grindrapp.android")
    opts.set_capability("appium:appActivity", ".HomeActivityOriginal")
    opts.set_capability("appium:noReset", True)

    print(f"[{device_id}] Connecting...")
    driver = webdriver.Remote(f"http://localhost:{port}{base_path}", options=opts)
    driver.implicitly_wait(2)  # Very short timeout
    
    print(f"[{device_id}] Testing basic connection...")
    
    # Test 1: Can we get page source?
    try:
        source = driver.page_source
        if source:
            print(f"[{device_id}] ✅ Can get page source (length: {len(source)})")
            # Show first few lines
            lines = source.split('\n')[:5]
            for line in lines:
                print(f"[{device_id}] SOURCE: {line[:100]}")
        else:
            print(f"[{device_id}] ❌ Page source is empty")
    except Exception as e:
        print(f"[{device_id}] ❌ Cannot get page source: {e}")
    
    # Test 2: Can we find ANY elements?
    try:
        all_elements = driver.find_elements("xpath", "//*")
        print(f"[{device_id}] ✅ Found {len(all_elements)} total elements")
    except Exception as e:
        print(f"[{device_id}] ❌ Cannot find any elements: {e}")
    
    # Test 3: Look for Inbox specifically
    try:
        inbox = driver.find_element("xpath", '//*[@text="Inbox"]')
        print(f"[{device_id}] ✅ FOUND INBOX!")
    except:
        print(f"[{device_id}] ❌ No Inbox found")
    
    # Test 4: Look for any text containing "box"
    try:
        box_elements = driver.find_elements("xpath", '//*[contains(@text, "box")]')
        if box_elements:
            print(f"[{device_id}] Found {len(box_elements)} elements with 'box':")
            for elem in box_elements[:3]:  # Show first 3
                try:
                    print(f"[{device_id}] BOX TEXT: '{elem.text}'")
                except:
                    pass
        else:
            print(f"[{device_id}] No elements with 'box' found")
    except Exception as e:
        print(f"[{device_id}] Error searching for 'box': {e}")
    
    driver.quit()

# Test with first device only
device = DEVICES[0]
quick_debug(device["id"], device["port"], device["base_path"])