from appium import webdriver
from appium.options.android import UiAutomator2Options
from devices import DEVICES

def debug_screen(device_id, port, base_path):
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
    
    print(f"[{device_id}] Getting all text elements...")
    all_text = driver.find_elements("class name", "android.widget.TextView")
    visible_texts = []
    
    for elem in all_text:
        try:
            text = elem.text
            if text and len(text.strip()) > 0:
                visible_texts.append(text.strip())
        except:
            continue
    
    print(f"[{device_id}] === ALL VISIBLE TEXT ===")
    for i, text in enumerate(visible_texts[:20]):  # Show first 20
        print(f"[{device_id}] {i+1}: '{text}'")
    
    print(f"[{device_id}] === LOOKING FOR 'Inbox' ===")
    inbox_found = False
    for text in visible_texts:
        if "inbox" in text.lower():
            print(f"[{device_id}] FOUND SIMILAR: '{text}'")
            inbox_found = True
    
    if not inbox_found:
        print(f"[{device_id}] ❌ NO 'Inbox' text found at all!")
    
    # Try to find Inbox element directly
    try:
        inbox_elem = driver.find_element("xpath", '//*[@text="Inbox"]')
        print(f"[{device_id}] ✅ Found Inbox element directly!")
    except:
        print(f"[{device_id}] ❌ Could not find Inbox element")
    
    driver.quit()

# Test with first device only
device = DEVICES[0]
debug_screen(device["id"], device["port"], device["base_path"])