from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from devices import DEVICES

# Variables para las frases de respuesta
FIRST_MESSAGE = "Hey how are you?"  # Rellena aquí la primera frase
SECOND_MESSAGE = "Damn, I think there's something wrong with my Grindr i send multiple chat but it's didn't go through. If you're interested let's chat on telegram instead here's my username @Alejandra_xo"  # Rellena aquí la segunda frase

def run_bot(device_id, port, base_path):
    # Tracking system para evitar duplicados
    processed_chats = set()
    opts = UiAutomator2Options()
    opts.set_capability("platformName", "Android")
    opts.set_capability("appium:deviceName", device_id)
    opts.set_capability("appium:udid", device_id)
    opts.set_capability("appium:automationName", "UiAutomator2")
    opts.set_capability("appium:appPackage", "com.grindrapp.android")
    opts.set_capability("appium:appActivity", ".HomeActivityOriginal")
    opts.set_capability("appium:noReset", True)

    print(f"[{device_id}] Connecting to device...")
    driver = webdriver.Remote(f"http://localhost:{port}{base_path}", options=opts)
    driver.implicitly_wait(15)
    time.sleep(5)  # Give device time to stabilize

    # Check if Grindr is open, if not, open it
    try:
        driver.find_element("xpath", '//*[@text="Inbox"]')
        print(f"[{device_id}] Grindr is already open")
    except:
        print(f"[{device_id}] Grindr is not open, opening it...")
        driver.activate_app("com.grindrapp.android")
        time.sleep(10)  # Wait for complete loading
        
        # Check again if it opened correctly
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((AppiumBy.XPATH, '//*[@text="Inbox"]'))
            )
            print(f"[{device_id}] Grindr opened correctly")
        except:
            print(f"[{device_id}] ❌ Could not open Grindr or load interface")
            return

    # Try to access Inbox with retry logic
    inbox_attempts = 0
    max_inbox_attempts = 2
    
    while inbox_attempts < max_inbox_attempts:
        try:
            driver.find_element("xpath", '//*[@text="Inbox"]').click()
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((AppiumBy.CLASS_NAME, "android.widget.TextView"))
            )
            print(f"[{device_id}] ✅ Inbox access successful")
            break
        except:
            inbox_attempts += 1
            print(f"[{device_id}] ❌ Could not access Inbox (attempt {inbox_attempts}/{max_inbox_attempts})")
            
            if inbox_attempts < max_inbox_attempts:
                print(f"[{device_id}] 🔄 Restarting Grindr app...")
                # Close and restart the app
                try:
                    driver.terminate_app("com.grindrapp.android")
                    time.sleep(3)
                    driver.activate_app("com.grindrapp.android")
                    time.sleep(8)  # Wait longer for complete app reload
                    
                    # Check if Inbox is available after restart
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((AppiumBy.XPATH, '//*[@text="Inbox"]'))
                    )
                    print(f"[{device_id}] ✅ Grindr restarted successfully")
                except Exception as restart_error:
                    print(f"[{device_id}] ⚠️ Error restarting app: {restart_error}")
            else:
                print(f"[{device_id}] ❌ Failed to access Inbox after {max_inbox_attempts} attempts")
                return

    def get_chats():
        chats, seen_ids = [], set()
        interface_exclude = ["Inbox", "Albums", "Unread", "Distance", "Online", "Position", "Browse", "Faves", "Store", "Interest"]
        
        print(f"[{device_id}] 🔍 Looking for chats with unread message badges...")
        
        # Buscar específicamente badges/círculos con números (mensajes sin leer)
        unread_badges = []
        
        try:
            # Buscar por diferentes posibles selectores de badges
            badge_selectors = [
                "//android.widget.TextView[@text and string-length(@text)<=2 and number(@text)]",  # Números de 1-2 dígitos
                "//android.view.View[contains(@content-desc, 'unread')]",
                "//android.widget.ImageView[contains(@content-desc, 'unread')]", 
                "//*[contains(@resource-id, 'badge') or contains(@resource-id, 'unread')]",
                "//android.widget.TextView[@text='1' or @text='2' or @text='3' or @text='4' or @text='5' or @text='6' or @text='7' or @text='8' or @text='9']"
            ]
            
            for selector in badge_selectors:
                try:
                    badges = driver.find_elements("xpath", selector)
                    unread_badges.extend(badges)
                except:
                    continue
                    
        except Exception as e:
            print(f"[{device_id}] ⚠️ Error buscando badges: {e}")
        
        # Eliminar duplicados de badges basándose en posición
        unique_badges = []
        seen_positions = set()
        
        for badge in unread_badges:
            try:
                pos = (badge.location['x'], badge.location['y'])
                if pos not in seen_positions:
                    unique_badges.append(badge)
                    seen_positions.add(pos)
            except:
                continue
        
        print(f"[{device_id}] 🔴 Found {len(unique_badges)} unique unread badges")
        
        # Para cada badge único, buscar el chat asociado
        for badge in unique_badges:
            try:
                badge_text = badge.text.strip()
                print(f"[{device_id}] 🔴 Processing badge: '{badge_text}'")
                
                # Obtener la posición del badge
                badge_location = badge.location
                badge_x, badge_y = badge_location['x'], badge_location['y']
                
                # Buscar elementos de texto cerca del badge que podrían ser nombres de usuario
                all_text_elements = driver.find_elements("class name", "android.widget.TextView")
                
                closest_candidates = []
                
                for text_el in all_text_elements:
                    try:
                        txt = text_el.text.strip()
                        
                        # Verificar proximidad al badge primero
                        text_location = text_el.location
                        text_x, text_y = text_location['x'], text_location['y']
                        distance = abs(text_x - badge_x) + abs(text_y - badge_y)
                        
                        if distance < 500:  # Aumentar mucho más el rango de búsqueda
                            closest_candidates.append({
                                "text": txt,
                                "element": text_el,
                                "distance": distance,
                                "clickable": text_el.get_attribute("clickable") == "true"
                            })
                    except:
                        continue
                
                # Sort by proximity but remove debug logging
                closest_candidates.sort(key=lambda x: x["distance"])
                
                # Buscar nombres válidos entre los candidatos (SIN filtrar por clickable)
                for candidate in closest_candidates:
                    txt = candidate["text"]
                    text_el = candidate["element"]
                    
                    # Filtrar nombres de usuario válidos con criterios más amplios
                    exclude_words = ["yesterday", "sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "new", "store", "inbox", "albums", "unread", "distance", "online", "position"]
                    
                    if (txt and 
                        txt != badge_text and  # No el badge mismo
                        txt not in interface_exclude and
                        len(txt) >= 2 and len(txt) <= 50 and  # Rango más amplio
                        not txt.isdigit() and
                        txt.lower() not in exclude_words and
                        not any(word in txt.lower() for word in exclude_words)):
                        
                        # Crear ID único basado en posición
                        pos_id = f"pos_{text_el.location['x']}_{text_el.location['y']}"
                        
                        contact = {
                            "name": txt,
                            "element": text_el,
                            "unread_count": badge_text,
                            "has_unread": True,
                            "badge_x": badge_x,
                            "badge_y": badge_y,
                            "position_id": pos_id
                        }
                        
                        if txt not in seen_ids:
                            chats.append(contact)
                            seen_ids.add(txt)
                            print(f"[{device_id}] 📬 UNREAD CHAT FOUND: '{txt}' ({badge_text} messages)")
                            break  # Solo tomar el primero válido por badge
                        
            except Exception as e:
                print(f"[{device_id}] ⚠️ Error procesando badge: {e}")
                continue
        
        if not chats:
            print(f"[{device_id}] ❌ No unread chats found (no badges detected)")
        
        return chats

    chats = get_chats()
    print(f"\n[{device_id}] 🔍 Total chats found: {len(chats)}")

    for chat in chats:
        # Verificar si ya procesamos este chat específico
        if chat['position_id'] in processed_chats:
            print(f"[{device_id}] ⏭️ Chat '{chat['name']}' already processed, skipping...")
            continue
            
        print(f"\n[{device_id}] 🔔 Attempting to open chat with: {chat['name']}")
        print(f"[{device_id}] 📍 USANDO POSICIÓN COMO ID: '{chat['position_id']}'")
        
        # Verificar que estamos en Inbox antes de continuar con retry
        inbox_retry_attempts = 0
        max_inbox_retry = 2
        
        while inbox_retry_attempts < max_inbox_retry:
            try:
                driver.find_element("xpath", '//*[@text="Inbox"]')
                break  # Found Inbox, continue
            except:
                inbox_retry_attempts += 1
                print(f"[{device_id}] Not in Inbox, attempt {inbox_retry_attempts}/{max_inbox_retry}")
                
                if inbox_retry_attempts < max_inbox_retry:
                    print(f"[{device_id}] 🔄 Restarting Grindr to return to Inbox...")
                    try:
                        driver.terminate_app("com.grindrapp.android")
                        time.sleep(3)
                        driver.activate_app("com.grindrapp.android")
                        time.sleep(8)
                        
                        # Navigate back to Inbox
                        WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located((AppiumBy.XPATH, '//*[@text="Inbox"]'))
                        )
                        driver.find_element("xpath", '//*[@text="Inbox"]').click()
                        time.sleep(2)
                        print(f"[{device_id}] ✅ Successfully returned to Inbox")
                    except Exception as return_error:
                        print(f"[{device_id}] ⚠️ Error returning to Inbox: {return_error}")
                else:
                    print(f"[{device_id}] ❌ Could not return to Inbox after {max_inbox_retry} attempts")
                    continue

        try:
            # Intentar hacer clic en el elemento del chat
            print(f"[{device_id}] Clicking on chat...")
            chat["element"].click()
            
            # Esperar a que aparezca el campo de texto del chat
            print(f"[{device_id}] Waiting for chat to load...")
            WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((AppiumBy.CLASS_NAME, "android.widget.EditText"))
            )
            time.sleep(2)
            print(f"[{device_id}] ✅ Chat '{chat['name']}' opened successfully")
            
        except Exception as e:
            print(f"[{device_id}] ⚠️ Could not open chat '{chat['name']}': {str(e)[:100]}")
            continue

        # Verificar si ya hemos enviado nuestro mensaje buscando SECOND_MESSAGE en el chat
        print(f"[{device_id}] 🔍 Checking if we already sent our message...")
        already_responded = False
        
        try:
            # Buscar todos los mensajes en el chat con diferentes selectores
            message_selectors = [
                "//android.widget.TextView[@resource-id='com.grindrapp.android:id/message']",
                "//android.widget.TextView[contains(@resource-id, 'message')]",
                "//android.widget.TextView[contains(text(), 'telegram')]",
                f"//android.widget.TextView[contains(text(), '{FIRST_MESSAGE[:20]}')]"
            ]
            
            for selector in message_selectors:
                try:
                    message_elements = driver.find_elements("xpath", selector)
                    for msg_element in message_elements:
                        try:
                            msg_text = msg_element.get_attribute("text") or msg_element.text
                            if msg_text and (SECOND_MESSAGE in msg_text or FIRST_MESSAGE in msg_text):
                                already_responded = True
                                print(f"[{device_id}] ✅ Already sent message to '{chat['name']}', skipping...")
                                break
                        except:
                            continue
                    if already_responded:
                        break
                except:
                    continue
                    
        except Exception as e:
            print(f"[{device_id}] ⚠️ Error checking messages: {e}")
        
        if not already_responded:
            print(f"[{device_id}] 🆕 New chat detected: '{chat['name']}', sending messages...")
            try:
                # Enviar primera frase
                if FIRST_MESSAGE:
                    input_box = driver.find_elements("class name", "android.widget.EditText")[0]
                    input_box.click()
                    input_box.clear()
                    input_box.send_keys(FIRST_MESSAGE)
                    time.sleep(1)

                    for b in driver.find_elements("class name", "android.widget.ImageView"):
                        rid = b.get_attribute("resource-id")
                        if rid and "send" in rid:
                            b.click()
                            break
                    
                    print(f"[{device_id}] First message sent, waiting 3 seconds...")
                    time.sleep(3)
                
                # Enviar segunda frase
                if SECOND_MESSAGE:
                    input_box = driver.find_elements("class name", "android.widget.EditText")[0]
                    input_box.click()
                    input_box.clear()
                    input_box.send_keys(SECOND_MESSAGE)
                    time.sleep(1)

                    for b in driver.find_elements("class name", "android.widget.ImageView"):
                        rid = b.get_attribute("resource-id")
                        if rid and "send" in rid:
                            b.click()
                            break
                    
                    print(f"[{device_id}] Second message sent")
                
                print(f"[{device_id}] ✅ Messages sent successfully to '{chat['name']}'")
                # Marcar este chat como procesado
                processed_chats.add(chat['position_id'])
                
            except Exception as e:
                print(f"[{device_id}] ❌ Error responding: {e}")
        else:
            print(f"[{device_id}] ⏭️ Skipping chat with '{chat['name']}' - already responded")
            # También marcar como procesado si ya respondimos
            processed_chats.add(chat['position_id'])

        try:
            # Hacer clic en la flecha de retroceso en la esquina superior izquierda
            back_button = driver.find_element(AppiumBy.XPATH, "//android.widget.ImageButton[@content-desc='Navigate up']")
            back_button.click()
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((AppiumBy.XPATH, '//*[@text="Inbox"]'))
            )
            time.sleep(1)
        except:
            print(f"[{device_id}] ⚠️ Could not find back button in UI")
            try:
                driver.press_keycode(4)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((AppiumBy.XPATH, '//*[@text="Inbox"]'))
                )
                time.sleep(1)
            except:
                print(f"[{device_id}] ⚠️ Could not go back with keycode")
        time.sleep(1)
    
    print(f"\n[{device_id}] 📊 FINAL SUMMARY:")
    print(f"[{device_id}] Chat processing completed")


def run_bot_with_timeout(device_info):
    """Wrapper function to run bot with timeout and error isolation"""
    device_id, port, base_path = device_info["id"], device_info["port"], device_info["base_path"]
    try:
        run_bot(device_id, port, base_path)
        return f"[{device_id}] SUCCESS"
    except Exception as e:
        print(f"[{device_id}] ❌ Bot failed with error: {str(e)[:200]}")
        return f"[{device_id}] FAILED: {str(e)[:100]}"

# Use ThreadPoolExecutor with limited concurrent connections
MAX_CONCURRENT_DEVICES = 3  # Process 3 devices at once
print(f"🚀 Starting device bots (max {MAX_CONCURRENT_DEVICES} concurrent)...")
with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_DEVICES, thread_name_prefix="GrindrBot") as executor:
    # Submit all tasks
    futures = {executor.submit(run_bot_with_timeout, device): device for device in DEVICES}
    
    # Process results as they complete
    for future in concurrent.futures.as_completed(futures, timeout=300):  # 5 minute timeout
        device = futures[future]
        try:
            result = future.result()
            print(f"✅ {result}")
        except concurrent.futures.TimeoutError:
            print(f"⏰ [{device['id']}] Timed out after 5 minutes")
        except Exception as e:
            print(f"❌ [{device['id']}] Unexpected error: {e}")

print("🏁 All device processing completed")