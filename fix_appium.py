import subprocess
import sys

def fix_appium_installation():
    """Fix Appium Python client installation"""
    
    print("🔧 Fixing Appium Python client installation...")
    
    # Uninstall current appium-python-client
    print("1. Uninstalling current Appium-Python-Client...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "Appium-Python-Client", "-y"])
        print("✅ Uninstalled successfully")
    except:
        print("⚠️  Nothing to uninstall")
    
    # Install specific working version
    print("2. Installing compatible Appium-Python-Client...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Appium-Python-Client==2.11.1"])
        print("✅ Installed Appium-Python-Client 2.11.1")
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        return False
    
    # Test the import
    print("3. Testing import...")
    try:
        from appium import webdriver
        from appium.options.android import UiAutomator2Options
        print("✅ Import test successful!")
        return True
    except ImportError as e:
        print(f"❌ Import still failing: {e}")
        
        # Try alternative installation
        print("4. Trying alternative installation...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "Appium-Python-Client==3.1.1"])
            from appium import webdriver
            print("✅ Alternative version works!")
            return True
        except:
            print("❌ Alternative version also failed")
            return False

if __name__ == "__main__":
    success = fix_appium_installation()
    
    if success:
        print("\n🎉 Appium installation fixed!")
        print("You can now run: python app.py")
    else:
        print("\n❌ Could not fix Appium installation")
        print("Try manually:")
        print("  pip uninstall Appium-Python-Client")
        print("  pip install Appium-Python-Client==2.11.1")