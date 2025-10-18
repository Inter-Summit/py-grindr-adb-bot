import sys
import subprocess

def check_appium_status():
    """Diagnose what's wrong with Appium installation"""
    
    print("🔍 Diagnosing Appium installation...")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    # Check if appium package exists
    print("\n1. Checking if 'appium' package is installed...")
    try:
        import appium
        print(f"✅ appium package found at: {appium.__file__}")
        print(f"✅ appium version: {appium.__version__}")
    except ImportError:
        print("❌ 'appium' package not found!")
        return
    except AttributeError:
        print("⚠️  'appium' package found but no version info")
    
    # Check what's inside appium package
    print("\n2. Checking appium package contents...")
    try:
        import appium
        contents = dir(appium)
        print(f"Available in appium: {contents}")
        
        if 'webdriver' in contents:
            print("✅ webdriver found in appium")
        else:
            print("❌ webdriver NOT found in appium")
            
    except Exception as e:
        print(f"❌ Error checking contents: {e}")
    
    # Try different import methods
    print("\n3. Testing different import methods...")
    
    # Method 1: Original way
    try:
        from appium import webdriver
        print("✅ Method 1 works: from appium import webdriver")
    except ImportError as e:
        print(f"❌ Method 1 failed: {e}")
    
    # Method 2: Alternative way
    try:
        from appium.webdriver import Remote
        print("✅ Method 2 works: from appium.webdriver import Remote")
    except ImportError as e:
        print(f"❌ Method 2 failed: {e}")
    
    # Method 3: Check selenium webdriver
    try:
        from selenium import webdriver as selenium_webdriver
        print("✅ Method 3 works: selenium webdriver available")
    except ImportError as e:
        print(f"❌ Method 3 failed: {e}")
    
    # Check installed packages
    print("\n4. Checking installed Appium-related packages...")
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "list"], 
                              capture_output=True, text=True)
        lines = result.stdout.split('\n')
        appium_packages = [line for line in lines if 'appium' in line.lower()]
        
        if appium_packages:
            print("Found Appium packages:")
            for pkg in appium_packages:
                print(f"  • {pkg}")
        else:
            print("❌ No Appium packages found in pip list")
            
    except Exception as e:
        print(f"❌ Error checking packages: {e}")

if __name__ == "__main__":
    check_appium_status()