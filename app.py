from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from devices import DEVICES
from username import USERNAME
from datetime import datetime


FIRST_MESSAGE = "HHello! how’s life lately? 🤭"
SECOND_MESSAGE = f"Btw I’m struggling to catch you up here since I don’t use this often. I prefer chatting in telegram if you’re interested you can chat me here {USERNAME} let’s talk and have some fun xd 😏" 

def get_timestamp():
    """Get current timestamp for logging"""
    return datetime.now().strftime("%H:%M:%S")

def log(device_id, message):
    """Log with timestamp"""
    print(f"[{get_timestamp()}] [{device_id}] {message}")

def run_bot(device_id, port, base_path):
    
    opts = UiAutomator2Options()
    opts.set_capability("platformName", "Android")
    opts.set_capability("appium:deviceName", device_id)
    opts.set_capability("appium:udid", device_id)
    opts.set_capability("appium:automationName", "UiAutomator2")
    opts.set_capability("appium:appPackage", "com.grindrapp.android")
    opts.set_capability("appium:appActivity", ".HomeActivityOriginal")
    opts.set_capability("appium:noReset", True)

    log(device_id, "🔌 Connecting to device...")
    
    # Retry connection up to 3 times
    connection_attempts = 0
    max_attempts = 3
    driver = None
    
    while connection_attempts < max_attempts:
        try:
            connection_attempts += 1
            log(device_id, f"🔄 Connection attempt {connection_attempts}/{max_attempts}...")
            
            driver = webdriver.Remote(f"http://localhost:{port}{base_path}", options=opts)
            driver.implicitly_wait(10)
            time.sleep(2)
            
            # Test the connection by getting current package
            current_package = driver.current_package
            log(device_id, f"✅ Connected successfully - current app: {current_package}")
            break
            
        except Exception as e:
            log(device_id, f"❌ Connection attempt {connection_attempts} failed: {str(e)[:100]}")
            if driver:
                try:
                    driver.quit()
                except:
                    pass
                driver = None
            
            if connection_attempts < max_attempts:
                log(device_id, f"⏳ Waiting 5 seconds before retry...")
                time.sleep(5)
            else:
                log(device_id, f"❌ All connection attempts failed")
                raise Exception(f"Connection failed after {max_attempts} attempts: {e}")
    
    if not driver:
        raise Exception("Driver is None after connection attempts")

    # STEP 1: Ensure clean state - close Grindr if it's open
    log(device_id, "🧹 Ensuring clean state - closing Grindr if open...")
    try:
        driver.terminate_app("com.grindrapp.android")
        log(device_id, "✅ Grindr closed successfully")
        time.sleep(2)  # Short wait after closing
    except Exception as close_error:
        log(device_id, f"⚠️ App close attempt: {str(close_error)[:50]} (may not have been open)")

    # STEP 2: Open Grindr fresh
    log(device_id, "📱 Opening Grindr fresh...")
    driver.activate_app("com.grindrapp.android")
    
    # STEP 3: Wait 20 seconds for full app initialization
    log(device_id, "⏳ Waiting 20 seconds for full app initialization...")
    time.sleep(20)
    
    # STEP 4: Verify Grindr is ready with Inbox visible AND navigate to Inbox
    log(device_id, "🔍 Verifying Grindr interface is ready...")
    
    inbox_ready_attempts = 0
    max_inbox_attempts = 3
    
    while inbox_ready_attempts < max_inbox_attempts:
        try:
            inbox_ready_attempts += 1
            log(device_id, f"🔍 Inbox verification attempt {inbox_ready_attempts}/{max_inbox_attempts}...")
            
            # Check current app state first
            current_package = driver.current_package
            log(device_id, f"📱 Current app: {current_package}")
            
            if "grindr" not in current_package.lower():
                log(device_id, "⚠️ Grindr not active, reactivating...")
                driver.activate_app("com.grindrapp.android")
                log(device_id, "⏳ Waiting for Grindr to fully load after reactivation...")
                time.sleep(8)  # Más tiempo para carga completa
                
                # Verificar de nuevo que Grindr está activo
                current_package = driver.current_package
                log(device_id, f"📱 After reactivation: {current_package}")
            
            # VERIFICACIÓN ADICIONAL: Esperar a que aparezcan elementos básicos de la UI
            log(device_id, "🔍 Waiting for basic UI elements to load...")
            try:
                # Esperar a que aparezcan elementos TextView (indicativo de UI cargada)
                WebDriverWait(driver, 10).until(
                    lambda d: len(d.find_elements("class name", "android.widget.TextView")) > 5
                )
                log(device_id, "✅ Basic UI elements loaded successfully")
            except:
                log(device_id, "⚠️ UI elements taking longer to load, continuing anyway...")
            
            inbox_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, '//*[@text="Inbox"]'))
            )
            log(device_id, "✅ Grindr is ready - Inbox button found")
            
            # STEP 5: Navigate to Inbox immediately
            log(device_id, "📥 Clicking Inbox to navigate to inbox screen...")
            inbox_button.click()
            
            # STEP 6: Verify we're in Inbox screen
            log(device_id, "🔍 Verifying we're in Inbox screen...")
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((AppiumBy.CLASS_NAME, "android.widget.TextView"))
            )
            log(device_id, "✅ Successfully navigated to Inbox screen")
            break
            
        except Exception as inbox_error:
            error_msg = str(inbox_error)
            log(device_id, f"❌ Inbox attempt {inbox_ready_attempts} failed: {error_msg[:100]}")
            
            # Detectar si es un error de sesión perdida
            if "session" in error_msg.lower() and "not known" in error_msg.lower():
                log(device_id, "⚠️ Session lost detected - need to reconnect to device")
                try:
                    # Cerrar driver actual
                    if driver:
                        driver.quit()
                    
                    # Recrear conexión
                    log(device_id, "🔄 Recreating Appium connection...")
                    driver = webdriver.Remote(f"http://localhost:{port}{base_path}", options=opts)
                    driver.implicitly_wait(10)
                    time.sleep(2)
                    
                    # Verificar nueva conexión
                    current_package = driver.current_package
                    log(device_id, f"✅ Reconnected successfully - current app: {current_package}")
                    
                except Exception as reconnect_error:
                    log(device_id, f"❌ Reconnection failed: {str(reconnect_error)[:50]}")
                    return
            
            if inbox_ready_attempts < max_inbox_attempts:
                log(device_id, f"🔄 Retrying Grindr setup in 3 seconds...")
                try:
                    # Try to restart Grindr
                    driver.terminate_app("com.grindrapp.android")
                    time.sleep(3)  # Wait for complete termination
                    log(device_id, "📱 Reactivating Grindr after restart...")
                    driver.activate_app("com.grindrapp.android")
                    
                    # ESPERA MÁS LARGA DESPUÉS DEL RESTART - como mencionaste
                    log(device_id, "⏳ Waiting 25 seconds for app to fully load after restart...")
                    time.sleep(25)  # Mucho más tiempo para carga completa
                    
                    # Verificar que la sesión sigue activa
                    current_package = driver.current_package
                    log(device_id, f"📱 App loaded, current package: {current_package}")
                    
                except Exception as restart_error:
                    log(device_id, f"⚠️ App restart failed during retry: {str(restart_error)[:50]}")
            else:
                log(device_id, f"❌ Could not navigate to Inbox after {max_inbox_attempts} attempts")
                return

    # We're already in Inbox from initialization, wait for chats to load
    log(device_id, "📋 Ready to search for chats - already in Inbox screen")
    log(device_id, "⏳ Waiting 5 seconds for chats to load in Inbox...")
    time.sleep(5)

    def get_chats():
        chats, seen_ids = [], set()
        interface_exclude = ["Inbox", "Albums", "Unread", "Distance", "Online", "Position", "Browse", "Faves", "Store", "Interest"]
        
        log(device_id, "🔍 Looking for chats with unread message badges...")
        
        # Buscar específicamente badges/círculos con números (mensajes sin leer)
        unread_badges = []
        
        try:
            log(device_id, "⏱️ Starting badge search...")
            # Optimized badge search - solo usar el selector más efectivo
            badge_selectors = [
                "//android.widget.TextView[@text='1' or @text='2' or @text='3' or @text='4' or @text='5' or @text='6' or @text='7' or @text='8' or @text='9']",  # Más rápido
                "//android.widget.TextView[@text and string-length(@text)<=2 and number(@text)]"  # Backup
            ]
            
            # Múltiples estrategias de búsqueda de badges
            try:
                log(device_id, f"⏱️ Multi-strategy badge search...")
                driver.implicitly_wait(3)  # Timeout corto
                
                # Estrategia 1: Números específicos
                badges = driver.find_elements("xpath", "//android.widget.TextView[@text='1' or @text='2' or @text='3' or @text='4' or @text='5' or @text='6' or @text='7' or @text='8' or @text='9']")
                unread_badges.extend(badges)
                log(device_id, f"⏱️ Strategy 1: Found {len(badges)} numeric badges")
                
                # Estrategia 2: Elementos con text numérico
                if not badges:
                    log(device_id, "⏱️ Strategy 2: Mathematical selector...")
                    badges = driver.find_elements("xpath", "//android.widget.TextView[@text and string-length(@text)<=2 and number(@text)]")
                    unread_badges.extend(badges)
                    log(device_id, f"⏱️ Strategy 2: Found {len(badges)} mathematical badges")
                
                # Estrategia 3: Buscar por atributos de badge
                if not badges:
                    log(device_id, "⏱️ Strategy 3: Badge attributes...")
                    badges = driver.find_elements("xpath", "//*[contains(@resource-id, 'badge') or contains(@content-desc, 'unread')]")
                    unread_badges.extend(badges)
                    log(device_id, f"⏱️ Strategy 3: Found {len(badges)} attribute badges")
                
                # Estrategia 4: Cualquier TextView pequeño con números
                if not badges:
                    log(device_id, "⏱️ Strategy 4: Small numeric text...")
                    all_small_text = driver.find_elements("xpath", "//android.widget.TextView[string-length(@text)<=3]")
                    for el in all_small_text:
                        try:
                            text = el.text.strip()
                            if text.isdigit() and 1 <= int(text) <= 99:
                                badges.append(el)
                                unread_badges.append(el)
                        except:
                            continue
                    log(device_id, f"⏱️ Strategy 4: Found {len(badges)} small numeric badges")
                
                driver.implicitly_wait(10)  # Restaurar timeout
                
                if unread_badges:
                    log(device_id, f"✅ Total badges found: {len(unread_badges)}")
                else:
                    log(device_id, "❌ No badges found with any strategy")
                
            except Exception as e:
                log(device_id, f"⚠️ Badge search failed: {str(e)[:50]}")
                driver.implicitly_wait(10)
                    
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
        
        log(device_id, f"🔍 Found {len(unread_badges)} potential badges")
        log(device_id, f"🔴 Found {len(unique_badges)} unique unread badges")
        
        # Procesar TODOS los badges visibles en la primera pasada, limitar solo en scrolls posteriores
        if not hasattr(get_chats, '_scroll_count'):
            get_chats._scroll_count = 0
        
        if get_chats._scroll_count == 0:
            # Primera pasada: procesar todos los badges visibles
            max_badges_to_process = len(unique_badges)
            log(device_id, f"⚡ First pass: processing ALL {max_badges_to_process} visible badges")
        else:
            # Pasadas posteriores (después de scroll): limitar para velocidad
            max_badges_to_process = min(3, len(unique_badges))
            log(device_id, f"⚡ Post-scroll pass: processing {max_badges_to_process} badges max")
        
        # Para cada badge único, buscar el chat asociado
        for i, badge in enumerate(unique_badges[:max_badges_to_process]):
            try:
                badge_text = badge.text.strip()
                log(device_id, f"🔴 Badge {i+1}/{max_badges_to_process}: '{badge_text}'")
                
                # SOLUCIÓN CORRECTA: El área del chat completa es clickeable
                # No necesito buscar elementos específicos - solo usar el badge o su padre
                
                try:
                    # Opción 1: Intentar encontrar el elemento padre clickeable del badge
                    chat_element = None
                    chat_name = f"Chat_{badge_text}"  # Nombre temporal
                    
                    # Buscar el elemento padre que sea clickeable
                    parent = badge
                    for attempt in range(3):  # Intentar hasta 3 niveles hacia arriba
                        try:
                            parent = parent.find_element("xpath", "..")
                            if parent.get_attribute("clickable") == "true":
                                chat_element = parent
                                log(device_id, f"⚡ Found clickable parent at level {attempt+1}")
                                break
                        except:
                            break
                    
                    # Opción 2: Si no encuentra padre clickeable, usar el badge mismo
                    if not chat_element:
                        chat_element = badge
                        log(device_id, f"⚡ Using badge as clickable element")
                    
                    # Opción 3: Buscar cualquier texto cercano para el nombre
                    try:
                        # Buscar rápidamente un texto para usar como nombre
                        nearby_texts = driver.find_elements("xpath", "//android.widget.TextView[string-length(@text) > 2 and string-length(@text) < 20]")[:5]
                        for text_el in nearby_texts:
                            txt = text_el.text.strip()
                            if txt and txt != badge_text and not txt.isdigit():
                                chat_name = txt
                                log(device_id, f"⚡ Found chat name: '{txt}'")
                                break
                    except:
                        pass
                    
                    # Crear el chat con el elemento clickeable correcto
                    pos_id = f"pos_{i}_{badge_text}"
                    contact = {
                        "name": chat_name,
                        "element": chat_element,  # Elemento realmente clickeable
                        "unread_count": badge_text,
                        "has_unread": True,
                        "position_id": pos_id
                    }
                    
                    if chat_name not in seen_ids:
                        chats.append(contact)
                        seen_ids.add(chat_name)
                        log(device_id, f"📬 CHAT READY: '{chat_name}' ({badge_text} msgs)")
                    else:
                        log(device_id, f"⚠️ Chat already processed: '{chat_name}'")
                        
                except Exception as parent_error:
                    log(device_id, f"⚠️ Parent search failed: {str(parent_error)[:50]}")
                    # Fallback: usar el badge directamente
                    pos_id = f"pos_{i}_{badge_text}"
                    contact = {
                        "name": f"Chat_{badge_text}",
                        "element": badge,
                        "unread_count": badge_text,
                        "has_unread": True,
                        "position_id": pos_id
                    }
                    chats.append(contact)
                    log(device_id, f"📬 FALLBACK CHAT: Chat_{badge_text} ({badge_text} msgs)")
                        
            except Exception as e:
                print(f"[{device_id}] ⚠️ Error procesando badge: {e}")
                continue
        
        if not chats:
            print(f"[{device_id}] ❌ No unread chats found (no badges detected)")
        
        return chats

    def find_next_unread_chat():
        """Encuentra el primer chat sin leer en la vista actual"""
        try:
            log(device_id, "🔍 Scanning for next unread chat...")
            
            # Buscar badges de mensajes sin leer
            badges = driver.find_elements("xpath", "//android.widget.TextView[@text='1' or @text='2' or @text='3' or @text='4' or @text='5' or @text='6' or @text='7' or @text='8' or @text='9']")
            
            if not badges:
                log(device_id, "❌ No unread badges found")
                return None
                
            # Tomar el primer badge encontrado
            first_badge = badges[0]
            badge_text = first_badge.text.strip()
            log(device_id, f"🎯 Found first unread badge: '{badge_text}'")
            
            # Buscar el elemento clickeable (el badge o su padre)
            chat_element = first_badge
            try:
                parent = first_badge.find_element("xpath", "..")
                if parent.get_attribute("clickable") == "true":
                    chat_element = parent
                    log(device_id, "✅ Using clickable parent element")
            except:
                log(device_id, "✅ Using badge element itself")
            
            return {
                "element": chat_element,
                "unread_count": badge_text,
                "position": first_badge.location
            }
            
        except Exception as e:
            log(device_id, f"⚠️ Error finding unread chat: {str(e)[:100]}")
            return None

    def process_single_chat(chat):
        """Procesa un solo chat"""
        try:
            log(device_id, f"📱 Opening chat with {chat['unread_count']} unread messages...")
            
            # Verificar que estamos en Inbox
            try:
                driver.find_element("xpath", '//*[@text="Inbox"]')
            except:
                log(device_id, "⚠️ Not in Inbox, returning...")
                return False
            
            # Abrir el chat
            chat["element"].click()
            
            # Esperar a que aparezca el campo de texto
            WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((AppiumBy.CLASS_NAME, "android.widget.EditText"))
            )
            time.sleep(2)
            log(device_id, "✅ Chat opened successfully")
            
            # Verificar si ya enviamos mensajes buscando nuestro username
            already_responded = False
            try:
                # Buscar elementos de mensaje por resource ID específico
                message_elements = driver.find_elements("id", "com.grindrapp.android:id/message")
                log(device_id, f"🔍 Found {len(message_elements)} message elements to check")
                
                for msg_element in message_elements:
                    try:
                        msg_text = msg_element.get_attribute("text") or msg_element.text
                        if msg_text and USERNAME in msg_text:
                            already_responded = True
                            log(device_id, f"✅ Found our username {USERNAME} in message - already sent")
                            break
                    except:
                        continue
                        
                if not already_responded:
                    log(device_id, f"❌ Username {USERNAME} not found - proceeding to send")
                        
            except Exception as e:
                log(device_id, f"⚠️ Error checking messages: {str(e)[:50]} - proceeding to send")
            
            if not already_responded:
                log(device_id, "🆕 New chat - sending messages...")
                
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
                    
                    log(device_id, "✅ First message sent")
                    time.sleep(1)
                
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
                    
                    log(device_id, "✅ Second message sent")
                
                log(device_id, "✅ All messages sent successfully")
            
            # Regresar al Inbox
            try:
                driver.press_keycode(4)
                WebDriverWait(driver, 8).until(
                    EC.presence_of_element_located((AppiumBy.XPATH, '//*[@text="Inbox"]'))
                )
                log(device_id, "✅ Returned to Inbox")
                time.sleep(1)
                return True
            except:
                log(device_id, "⚠️ Could not return to Inbox properly")
                return False
                
        except Exception as e:
            log(device_id, f"❌ Error processing chat: {str(e)[:100]}")
            return False

    # NUEVA ESTRATEGIA: Procesar uno por uno en tiempo real
    scroll_attempts = 0
    max_scroll_attempts = 4
    total_processed = 0
    
    log(device_id, f"🚀 Starting one-by-one chat processing strategy...")
    
    while scroll_attempts <= max_scroll_attempts:
        log(device_id, f"🔄 Scan cycle {scroll_attempts + 1}/{max_scroll_attempts + 1}")
        
        # Buscar un solo chat sin leer en la vista actual
        single_chat = find_next_unread_chat()
        
        if single_chat:
            log(device_id, f"✅ Found unread chat: processing immediately...")
            
            # Procesar este chat inmediatamente
            success = process_single_chat(single_chat)
            if success:
                total_processed += 1
                log(device_id, f"✅ Chat processed successfully (total: {total_processed})")
            else:
                log(device_id, f"⚠️ Chat processing failed, continuing...")
            
            # Después de procesar, continuar buscando sin hacer scroll todavía
            continue
            
        else:
            log(device_id, f"❌ No unread chats found in current view")
        
        # Si no encuentra más chats, hacer scroll
        if scroll_attempts < max_scroll_attempts:
            log(device_id, f"🔽 No more chats visible. Scrolling down (attempt {scroll_attempts + 1})...")
            
            # Intentar múltiples métodos de scroll
            scroll_success = False
            
            # Método 1: swipe tradicional
            try:
                driver.swipe(500, 1200, 500, 200, 1200)
                scroll_success = True
                log(device_id, f"✅ Scroll method 1 (swipe) successful")
            except Exception as e:
                log(device_id, f"⚠️ Scroll method 1 failed: {str(e)[:50]}")
            
            # Método 2: TouchAction (si el anterior falla)
            if not scroll_success:
                try:
                    from appium.webdriver.common.touch_action import TouchAction
                    action = TouchAction(driver)
                    action.press(x=500, y=1200).move_to(x=500, y=200).release().perform()
                    scroll_success = True
                    log(device_id, f"✅ Scroll method 2 (TouchAction) successful")
                except Exception as e:
                    log(device_id, f"⚠️ Scroll method 2 failed: {str(e)[:50]}")
            
            # Método 3: Scroll usando elemento específico
            if not scroll_success:
                try:
                    # Buscar un elemento scrolleable en el inbox
                    scrollable_elements = driver.find_elements("xpath", "//*[@scrollable='true']")
                    if scrollable_elements:
                        driver.execute_script("mobile: scroll", {"element": scrollable_elements[0], "direction": "down"})
                        scroll_success = True
                        log(device_id, f"✅ Scroll method 3 (element scroll) successful")
                    else:
                        log(device_id, f"⚠️ No scrollable elements found")
                except Exception as e:
                    log(device_id, f"⚠️ Scroll method 3 failed: {str(e)[:50]}")
            
            # Método 4: Scroll usando coordenadas alternativas
            if not scroll_success:
                try:
                    # Usar coordenadas más centradas y conservadoras
                    driver.swipe(400, 800, 400, 300, 800)
                    scroll_success = True
                    log(device_id, f"✅ Scroll method 4 (alternative coords) successful")
                except Exception as e:
                    log(device_id, f"⚠️ Scroll method 4 failed: {str(e)[:50]}")
            
            if scroll_success:
                time.sleep(3)
                log(device_id, f"📱 Scroll {scroll_attempts + 1} completed successfully")
            else:
                log(device_id, f"❌ All scroll methods failed - continuing without scroll")
        
        scroll_attempts += 1
        
        # Si ha hecho todos los scrolls y no encuentra más, terminar
        if scroll_attempts > max_scroll_attempts:
            log(device_id, f"🏁 All scroll attempts completed. Ending processing.")
            break
    
    print(f"\n[{device_id}] 📊 FINAL SUMMARY:")
    print(f"[{device_id}] ✅ Successfully processed {total_processed} chats")
    print(f"[{device_id}] 🏁 Chat processing completed - bot ready for next cycle")


def run_bot_with_timeout(device_info):
    """Wrapper function to run bot with timeout and error isolation"""
    device_id = device_info["id"]
    port = device_info["port"]
    base_path = device_info["base_path"]
    
    log(device_id, f"🚀 Bot thread STARTED on port {port}")
    start_time = datetime.now()
    
    try:
        log(device_id, f"▶️ Calling run_bot function...")
        run_bot(device_id, port, base_path)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        log(device_id, f"✅ Bot thread COMPLETED - Total time: {duration:.1f}s")
        return f"[{device_id}] SUCCESS"
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        log(device_id, f"❌ Bot thread FAILED after {duration:.1f}s: {str(e)[:200]}")
        return f"[{device_id}] FAILED: {str(e)[:100]}"

# Process ALL devices with continuous pool of workers
MAX_CONCURRENT_DEVICES = 3
all_devices = DEVICES  # Process ALL devices from devices.py

print(f"[{get_timestamp()}] 🚀 Starting processing of {len(all_devices)} total devices...")
print(f"[{get_timestamp()}] 🔄 Will maintain {MAX_CONCURRENT_DEVICES} concurrent workers")

total_processed = 0
total_successful = 0
total_failed = 0

# Use continuous ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_DEVICES, thread_name_prefix="GrindrBot") as executor:
    # Submit all devices at once
    futures = {executor.submit(run_bot_with_timeout, device): device for device in all_devices}
    
    print(f"[{get_timestamp()}] 📋 All {len(futures)} devices submitted - processing with {MAX_CONCURRENT_DEVICES} workers...")
    
    # Process results as they complete
    for future in concurrent.futures.as_completed(futures, timeout=3600):  # 1 hour total timeout
        device = futures[future]
        total_processed += 1
        
        try:
            result = future.result()
            print(f"[{get_timestamp()}] ✅ ({total_processed}/{len(all_devices)}) {result}")
            total_successful += 1
        except concurrent.futures.TimeoutError:
            print(f"[{get_timestamp()}] ⏰ ({total_processed}/{len(all_devices)}) [{device['id']}] Timed out")
            total_failed += 1
        except Exception as e:
            print(f"[{get_timestamp()}] ❌ ({total_processed}/{len(all_devices)}) [{device['id']}] Error: {e}")
            total_failed += 1

print(f"\n[{get_timestamp()}] 🏁 ALL DEVICE PROCESSING COMPLETED!")
print(f"[{get_timestamp()}] 📊 FINAL SUMMARY:")
print(f"[{get_timestamp()}]    🎯 Total devices: {len(all_devices)}")
print(f"[{get_timestamp()}]    ✅ Successful: {total_successful}")
print(f"[{get_timestamp()}]    ❌ Failed: {total_failed}")
print(f"[{get_timestamp()}]    📦 Batches processed: {len(batches)}")
print(f"[{get_timestamp()}] 🎉 Bot execution completed!")