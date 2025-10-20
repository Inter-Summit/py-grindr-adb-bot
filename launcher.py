#!/usr/bin/env python3
"""
Grindr Bot Launcher - GUI for managing servers and bot
Provides easy buttons to start Appium servers and bot scheduler
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import threading
import os
import sys
from datetime import datetime

class GrindrBotLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Grindr Bot Launcher")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Variables to track running processes
        self.server_process = None
        self.bot_process = None
        
        # Get script directory
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🤖 Grindr Bot Launcher", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Server section
        server_frame = ttk.LabelFrame(main_frame, text="📱 Mobile Servers", padding="10")
        server_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        server_frame.columnconfigure(1, weight=1)
        
        self.connect_btn = ttk.Button(server_frame, text="🔌 Connect Mobiles", 
                                     command=self.start_servers, width=20)
        self.connect_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.server_status = ttk.Label(server_frame, text="Status: Not connected", 
                                      foreground="red")
        self.server_status.grid(row=0, column=1, sticky=tk.W)
        
        self.stop_servers_btn = ttk.Button(server_frame, text="⏹️ Stop Servers", 
                                          command=self.stop_servers, width=20, 
                                          state="disabled")
        self.stop_servers_btn.grid(row=1, column=0, padx=(0, 10), pady=(5, 0))
        
        # Bot section
        bot_frame = ttk.LabelFrame(main_frame, text="🤖 Bot Scheduler", padding="10")
        bot_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        bot_frame.columnconfigure(1, weight=1)
        
        self.start_bot_btn = ttk.Button(bot_frame, text="🚀 Start Bot", 
                                       command=self.start_bot, width=20)
        self.start_bot_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.bot_status = ttk.Label(bot_frame, text="Status: Not running", 
                                   foreground="red")
        self.bot_status.grid(row=0, column=1, sticky=tk.W)
        
        self.stop_bot_btn = ttk.Button(bot_frame, text="⏹️ Stop Bot", 
                                      command=self.stop_bot, width=20, 
                                      state="disabled")
        self.stop_bot_btn.grid(row=1, column=0, padx=(0, 10), pady=(5, 0))
        
        # Log section
        log_frame = ttk.LabelFrame(main_frame, text="📋 Logs", padding="10")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=70)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Clear log button
        clear_btn = ttk.Button(log_frame, text="🗑️ Clear Logs", command=self.clear_logs)
        clear_btn.grid(row=1, column=0, pady=(5, 0))
        
        # Initial log message
        self.log("🚀 Grindr Bot Launcher started")
        self.log("💡 Click 'Connect Mobiles' first, then 'Start Bot'")
        
    def log(self, message):
        """Add message to log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
    def clear_logs(self):
        """Clear the log display"""
        self.log_text.delete(1.0, tk.END)
        
    def start_servers(self):
        """Start the Appium servers"""
        try:
            self.log("🔌 Starting mobile servers...")
            
            # Check if start_servers.py exists
            server_script = os.path.join(self.script_dir, "start_servers.py")
            if not os.path.exists(server_script):
                self.log("❌ start_servers.py not found!")
                return
                
            # Start the server process
            self.server_process = subprocess.Popen(
                [sys.executable, server_script],
                cwd=self.script_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=0,  # Unbuffered for real-time output
                universal_newlines=True,
                encoding='utf-8',  # Force UTF-8 encoding
                errors='replace',  # Replace problematic chars
                env=dict(os.environ, PYTHONUNBUFFERED="1")  # Force Python unbuffered
            )
            
            # Update UI
            self.connect_btn.config(state="disabled")
            self.stop_servers_btn.config(state="normal")
            self.server_status.config(text="Status: Starting...", foreground="orange")
            
            # Start thread to read output
            threading.Thread(target=self.read_server_output, daemon=True).start()
            
        except Exception as e:
            self.log(f"❌ Failed to start servers: {e}")
            
    def read_server_output(self):
        """Read output from server process"""
        try:
            while self.server_process and self.server_process.poll() is None:
                try:
                    line = self.server_process.stdout.readline()
                    if line:
                        # Clean line and replace problematic chars
                        clean_line = line.strip().encode('ascii', 'replace').decode('ascii')
                        self.log(f"[SERVERS] {clean_line}")
                        
                        # Update status based on output
                        if "successfully started" in line.lower() or "server started" in line.lower():
                            self.root.after(0, lambda: self.server_status.config(
                                text="Status: Connected [OK]", foreground="green"))
                except UnicodeDecodeError:
                    self.log("[SERVERS] [Output contains special characters]")
                except Exception as line_error:
                    self.log(f"[SERVERS] Error reading line: {line_error}")
                        
        except Exception as e:
            self.log(f"❌ Error reading server output: {e}")
            
    def stop_servers(self):
        """Stop the Appium servers"""
        try:
            if self.server_process:
                self.log("⏹️ Stopping mobile servers...")
                self.server_process.terminate()
                self.server_process.wait(timeout=10)
                self.server_process = None
                
            # Update UI
            self.connect_btn.config(state="normal")
            self.stop_servers_btn.config(state="disabled")
            self.server_status.config(text="Status: Disconnected", foreground="red")
            self.log("✅ Mobile servers stopped")
            
        except Exception as e:
            self.log(f"❌ Failed to stop servers: {e}")
            
    def start_bot(self):
        """Start the bot scheduler"""
        try:
            self.log("🤖 Starting bot scheduler...")
            
            # Check if cron.py exists
            cron_script = os.path.join(self.script_dir, "cron.py")
            if not os.path.exists(cron_script):
                self.log("❌ cron.py not found!")
                return
                
            # Start the bot process
            self.bot_process = subprocess.Popen(
                [sys.executable, cron_script],
                cwd=self.script_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=0,  # Unbuffered for real-time output
                universal_newlines=True,
                encoding='utf-8',  # Force UTF-8 encoding
                errors='replace',  # Replace problematic chars
                env=dict(os.environ, PYTHONUNBUFFERED="1")  # Force Python unbuffered
            )
            
            # Update UI
            self.start_bot_btn.config(state="disabled")
            self.stop_bot_btn.config(state="normal")
            self.bot_status.config(text="Status: Starting...", foreground="orange")
            
            # Start thread to read output
            threading.Thread(target=self.read_bot_output, daemon=True).start()
            
        except Exception as e:
            self.log(f"❌ Failed to start bot: {e}")
            
    def read_bot_output(self):
        """Read output from bot process"""
        try:
            while self.bot_process and self.bot_process.poll() is None:
                try:
                    line = self.bot_process.stdout.readline()
                    if line:
                        # Clean line and replace problematic chars
                        clean_line = line.strip().encode('ascii', 'replace').decode('ascii')
                        self.log(f"[BOT] {clean_line}")
                        
                        # Update status based on output
                        if "scheduler starting" in line.lower():
                            self.root.after(0, lambda: self.bot_status.config(
                                text="Status: Running [OK]", foreground="green"))
                        elif "stopping scheduler" in line.lower() or "goodbye" in line.lower():
                            self.root.after(0, lambda: self.bot_status.config(
                                text="Status: Stopped", foreground="red"))
                except UnicodeDecodeError:
                    self.log("[BOT] [Output contains special characters]")
                except Exception as line_error:
                    self.log(f"[BOT] Error reading line: {line_error}")
                        
        except Exception as e:
            self.log(f"❌ Error reading bot output: {e}")
            
    def stop_bot(self):
        """Stop the bot scheduler"""
        try:
            if self.bot_process:
                self.log("⏹️ Stopping bot scheduler...")
                self.bot_process.terminate()
                self.bot_process.wait(timeout=10)
                self.bot_process = None
                
            # Update UI
            self.start_bot_btn.config(state="normal")
            self.stop_bot_btn.config(state="disabled")
            self.bot_status.config(text="Status: Stopped", foreground="red")
            self.log("✅ Bot scheduler stopped")
            
        except Exception as e:
            self.log(f"❌ Failed to stop bot: {e}")
            
    def on_closing(self):
        """Handle window closing"""
        self.log("🔄 Shutting down launcher...")
        
        # Stop any running processes
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
            except:
                pass
                
        if self.bot_process:
            try:
                self.bot_process.terminate()
                self.bot_process.wait(timeout=5)
            except:
                pass
                
        self.root.destroy()

def main():
    """Main function"""
    root = tk.Tk()
    app = GrindrBotLauncher(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    main()