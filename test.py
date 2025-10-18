#!/usr/bin/env python3
"""
Test script para analizar mensajes en un chat de Grindr
Ejecutar cuando ya tengas un chat abierto con mensajes enviados
"""

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
import time
from datetime import datetime

# Configuración del dispositivo
DEVICE_CONFIG = {"id": "100.64.100.6:5595", "port": 4707, "base_path": "/wd/hub"}
USERNAME = "@Alejandra_xo"

def get_timestamp():
    """Get current timestamp for logging"""
    return datetime.now().strftime("%H:%M:%S")

def log(message):
    """Log with timestamp"""
    print(f"[{get_timestamp()}] [TEST] {message}")

def main():
    log("🧪 Starting Grindr message analysis test...")
    log(f"📱 Connecting to device: {DEVICE_CONFIG['id']}")
    
    # Configurar Appium
    opts = UiAutomator2Options()
    opts.set_capability("platformName", "Android")
    opts.set_capability("appium:deviceName", DEVICE_CONFIG["id"])
    opts.set_capability("appium:udid", DEVICE_CONFIG["id"])
    opts.set_capability("appium:automationName", "UiAutomator2")
    opts.set_capability("appium:appPackage", "com.grindrapp.android")
    opts.set_capability("appium:appActivity", ".HomeActivityOriginal")
    opts.set_capability("appium:noReset", True)

    try:
        # Conectar al dispositivo
        driver = webdriver.Remote(f"http://localhost:{DEVICE_CONFIG['port']}{DEVICE_CONFIG['base_path']}", options=opts)
        driver.implicitly_wait(5)
        
        log("✅ Connected successfully!")
        log("📋 Analyzing current chat screen...")
        
        # Verificar que estamos en un chat (debe tener campo de texto)
        try:
            input_elements = driver.find_elements("class name", "android.widget.EditText")
            if input_elements:
                log(f"✅ Found {len(input_elements)} input field(s) - we're in a chat")
            else:
                log("❌ No input fields found - make sure you're in an open chat")
                return
        except:
            log("❌ Error finding input fields")
            return
        
        print(f"\n{'='*60}")
        print("📱 ANALYZING ALL TEXT ELEMENTS IN CHAT")
        print(f"{'='*60}")
        
        # Buscar todos los elementos de texto
        try:
            all_text_elements = driver.find_elements("class name", "android.widget.TextView")
            log(f"🔍 Found {len(all_text_elements)} TextView elements total")
            
            message_count = 0
            username_found = False
            
            for i, element in enumerate(all_text_elements):
                try:
                    text = element.get_attribute("text") or element.text
                    if text and len(text.strip()) > 0:
                        text = text.strip()
                        
                        # Skip very short texts (likely UI elements)
                        if len(text) < 3:
                            continue
                            
                        message_count += 1
                        
                        # Check if this looks like a message
                        is_message = len(text) > 10 or any(word in text.lower() for word in ['hey', 'hello', 'hi', 'how', 'telegram', 'chat', '@'])
                        
                        # Check if contains our username
                        contains_username = USERNAME in text
                        if contains_username:
                            username_found = True
                        
                        # Print detailed info
                        print(f"\n--- Element {i+1} (Message #{message_count}) ---")
                        print(f"Text: '{text}'")
                        print(f"Length: {len(text)} chars")
                        print(f"Contains username: {contains_username}")
                        print(f"Looks like message: {is_message}")
                        
                        # Get element properties
                        try:
                            location = element.location
                            size = element.size
                            print(f"Position: x={location['x']}, y={location['y']}")
                            print(f"Size: {size['width']}x{size['height']}")
                            print(f"Resource ID: {element.get_attribute('resource-id')}")
                            print(f"Class: {element.get_attribute('class')}")
                        except:
                            print("Could not get element properties")
                        
                except Exception as e:
                    continue
            
            print(f"\n{'='*60}")
            print(f"📊 SUMMARY")
            print(f"{'='*60}")
            print(f"Total TextView elements: {len(all_text_elements)}")
            print(f"Text elements with content: {message_count}")
            print(f"Username '{USERNAME}' found: {username_found}")
            
            # Test specific searches
            print(f"\n{'='*60}")
            print(f"🔍 TESTING SPECIFIC SEARCHES")
            print(f"{'='*60}")
            
            # Test 1: Search for username
            username_elements = driver.find_elements("xpath", f"//android.widget.TextView[contains(text(), '{USERNAME}')]")
            print(f"XPath search for '{USERNAME}': {len(username_elements)} elements found")
            
            # Test 2: Search for telegram
            telegram_elements = driver.find_elements("xpath", "//android.widget.TextView[contains(text(), 'telegram')]")
            print(f"XPath search for 'telegram': {len(telegram_elements)} elements found")
            
            # Test 3: Search for Hey
            hey_elements = driver.find_elements("xpath", "//android.widget.TextView[contains(text(), 'Hey')]")
            print(f"XPath search for 'Hey': {len(hey_elements)} elements found")
            
            # Test 4: Search case insensitive
            telegram_elements_ci = driver.find_elements("xpath", "//android.widget.TextView[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'telegram')]")
            print(f"XPath search for 'telegram' (case insensitive): {len(telegram_elements_ci)} elements found")
            
        except Exception as e:
            log(f"❌ Error analyzing text elements: {e}")
        
        driver.quit()
        log("🏁 Analysis completed!")
        
    except Exception as e:
        log(f"❌ Connection error: {e}")

if __name__ == "__main__":
    main()