#!/usr/bin/env python3
"""
Cron scheduler for Grindr bot automation
Executes app.py at regular intervals
"""

import subprocess
import time
import sys
from datetime import datetime
import os
import urllib.request
import json
import zipfile
import shutil

# CONFIGURACIÓN
INTERVAL_MINUTES = 5  # Cambiar aquí para modificar el intervalo
SCRIPT_TO_RUN = "app.py"  # Script a ejecutar
GITHUB_REPO_OWNER = "Inter-Summit"  # Usuario/organización de GitHub
GITHUB_REPO_NAME = "py-grindr-adb-bot"  # Nombre del repositorio

def get_timestamp():
    """Get current timestamp for logging"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(message):
    """Log with timestamp"""
    print(f"[{get_timestamp()}] [CRON] {message}")

def sync_with_github():
    """Check for updates from GitHub using API and download if needed"""
    try:
        log("🔄 Checking for updates from GitHub...")
        
        # Get current directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Get latest commit hash from GitHub API
        api_url = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/commits/main"
        
        log("📡 Fetching latest commit info from GitHub API...")
        try:
            with urllib.request.urlopen(api_url) as response:
                commit_data = json.loads(response.read().decode())
                latest_commit = commit_data['sha'][:7]  # Short hash
                commit_message = commit_data['commit']['message'].split('\n')[0]
                
            log(f"🔍 Latest commit: {latest_commit} - {commit_message}")
        except Exception as e:
            log(f"❌ Failed to fetch commit info: {e}")
            return False
        
        # Check if we have a local commit hash stored
        commit_file = os.path.join(script_dir, '.last_commit')
        local_commit = None
        
        if os.path.exists(commit_file):
            try:
                with open(commit_file, 'r') as f:
                    local_commit = f.read().strip()
                log(f"📂 Local commit: {local_commit}")
            except:
                log("⚠️  Could not read local commit file")
        
        # Check if update is needed
        if local_commit == latest_commit:
            log("✅ Already up to date with GitHub")
            return True
        
        log(f"📥 New version available - downloading...")
        
        # Download the latest code as ZIP
        download_url = f"https://github.com/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/archive/refs/heads/main.zip"
        zip_path = os.path.join(script_dir, 'temp_update.zip')
        temp_dir = os.path.join(script_dir, 'temp_update')
        
        try:
            log("⬇️  Downloading latest code...")
            urllib.request.urlretrieve(download_url, zip_path)
            
            # Extract ZIP
            log("📦 Extracting files...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Find extracted folder (will be repo-name-main)
            extracted_folder = os.path.join(temp_dir, f"{GITHUB_REPO_NAME}-main")
            
            if not os.path.exists(extracted_folder):
                log(f"❌ Extracted folder not found: {extracted_folder}")
                return False
            
            # Backup current files that might be overwritten
            backup_files = ['app.py', 'devices.py', 'cron.py']
            backup_dir = os.path.join(script_dir, '.backup')
            
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
            os.makedirs(backup_dir)
            
            for file in backup_files:
                src = os.path.join(script_dir, file)
                if os.path.exists(src):
                    shutil.copy2(src, backup_dir)
                    log(f"💾 Backed up: {file}")
            
            # Copy new files (backup cron.py config before updating)
            log("📁 Updating files...")
            for item in os.listdir(extracted_folder):
                if item == 'cron.py':
                    # Special handling for cron.py - preserve config but update code
                    src_cron = os.path.join(extracted_folder, 'cron.py')
                    dst_cron = os.path.join(script_dir, 'cron.py')
                    
                    # Read current config values
                    current_interval = INTERVAL_MINUTES
                    current_script = SCRIPT_TO_RUN
                    current_owner = GITHUB_REPO_OWNER
                    current_name = GITHUB_REPO_NAME
                    
                    # Copy new cron.py
                    shutil.copy2(src_cron, dst_cron)
                    log(f"📄 Updated: {item} (config preserved)")
                    
                    # Restore config in the new file
                    with open(dst_cron, 'r') as f:
                        content = f.read()
                    
                    # Replace config values with current ones
                    content = content.replace('INTERVAL_MINUTES = 5', f'INTERVAL_MINUTES = {current_interval}')
                    content = content.replace('GITHUB_REPO_OWNER = "Inter-Summit"', f'GITHUB_REPO_OWNER = "{current_owner}"')
                    content = content.replace('GITHUB_REPO_NAME = "py-grindr-adb-bot"', f'GITHUB_REPO_NAME = "{current_name}"')
                    
                    with open(dst_cron, 'w') as f:
                        f.write(content)
                    
                    continue
                    
                src = os.path.join(extracted_folder, item)
                dst = os.path.join(script_dir, item)
                
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
                    log(f"📄 Updated: {item}")
                elif os.path.isdir(src):
                    if os.path.exists(dst):
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                    log(f"📁 Updated directory: {item}")
            
            # Save the new commit hash
            with open(commit_file, 'w') as f:
                f.write(latest_commit)
            
            log(f"✅ Successfully updated to commit {latest_commit}")
            
            # Cleanup
            os.remove(zip_path)
            shutil.rmtree(temp_dir)
            
            return True
            
        except Exception as e:
            log(f"❌ Error during file update: {e}")
            # Cleanup on error
            if os.path.exists(zip_path):
                os.remove(zip_path)
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            return False
            
    except Exception as e:
        log(f"❌ Error during GitHub sync: {e}")
        return False

def run_bot_script():
    """Execute the main bot script"""
    try:
        log(f"Starting execution of {SCRIPT_TO_RUN}...")
        
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(script_dir, SCRIPT_TO_RUN)
        
        log(f"Looking for script at: {script_path}")
        log(f"Current working directory: {os.getcwd()}")
        log(f"Script directory: {script_dir}")
        
        # Check if script exists
        if not os.path.exists(script_path):
            log(f"Script not found: {script_path}")
            
            # Try in current working directory as fallback
            fallback_path = os.path.join(os.getcwd(), SCRIPT_TO_RUN)
            log(f"Trying fallback path: {fallback_path}")
            
            if os.path.exists(fallback_path):
                log(f"Found script at fallback location")
                script_path = fallback_path
            else:
                log(f"Script not found in fallback location either")
                log(f"Files in current directory:")
                for file in os.listdir(os.getcwd()):
                    log(f"   - {file}")
                return False
        
        # Execute the script WITHOUT capturing output to avoid emoji issues
        start_time = datetime.now()
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=script_dir,
            capture_output=False,  # Don't capture output
            timeout=7200  # 2 hour timeout for complete execution
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        if result.returncode == 0:
            log(f"Script completed successfully in {duration:.1f} seconds")
            return True
        else:
            log(f"Script failed with return code {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        log("Script execution timed out after 2 hours")
        return False
    except Exception as e:
        log(f"Error executing script: {e}")
        return False

def check_required_files():
    """Check if all required files exist before starting"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    required_files = [
        'username.py',
        'devices.py', 
        'app.py'
    ]
    
    missing_files = []
    for file in required_files:
        file_path = os.path.join(script_dir, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
    
    if missing_files:
        log("❌ CRITICAL ERROR: Required files are missing!")
        for file in missing_files:
            log(f"   Missing: {file}")
        log("")
        log("Please ensure all required files exist before running the bot:")
        log("   - username.py: Contains your telegram username")
        log("   - devices.py: Contains device configuration")
        log("   - app.py: Main bot script")
        log("")
        log("Exiting...")
        return False
    
    log("✅ All required files found")
    return True

def main():
    """Main cron loop"""
    log("Grindr Bot Cron Scheduler Starting...")
    
    # Check required files first
    if not check_required_files():
        sys.exit(1)
    
    log(f"Will execute {SCRIPT_TO_RUN} every {INTERVAL_MINUTES} minutes")
    log(f"Working directory: {os.getcwd()}")
    log("Press Ctrl+C to stop the scheduler")
    
    execution_count = 0
    successful_runs = 0
    failed_runs = 0
    
    try:
        while True:
            execution_count += 1
            log(f"\n{'='*60}")
            log(f"EXECUTION #{execution_count}")
            log(f"Stats: {successful_runs} successful, {failed_runs} failed")
            log(f"{'='*60}")
            
            # First sync with GitHub (this might download missing files)
            log("🔄 Starting GitHub sync...")
            sync_success = sync_with_github()
            
            if sync_success:
                log("✅ GitHub sync completed")
            else:
                log("⚠️  GitHub sync had issues")
            
            # Check required files after sync (some might have been downloaded)
            log("🔍 Checking required files...")
            if not check_required_files():
                log("❌ Required files still missing after sync - skipping this execution")
                log("💡 Make sure these files exist in the GitHub repository")
                failed_runs += 1
                continue
            
            # Run the bot script
            log("🤖 Starting bot execution...")
            if run_bot_script():
                successful_runs += 1
            else:
                failed_runs += 1
            
            # Calculate next execution time
            current_time = datetime.now()
            next_run = current_time.replace(second=0, microsecond=0)
            
            # Add interval minutes
            total_minutes = next_run.minute + INTERVAL_MINUTES
            new_hour = next_run.hour
            new_minute = total_minutes % 60
            
            # If minutes overflow, add to hour
            if total_minutes >= 60:
                new_hour = (new_hour + total_minutes // 60) % 24
            
            next_run = next_run.replace(hour=new_hour, minute=new_minute)
            
            log(f"\nWaiting {INTERVAL_MINUTES} minutes until next execution...")
            log(f"Next run scheduled for: {next_run.strftime('%H:%M:%S')}")
            log(f"Sleeping for {INTERVAL_MINUTES * 60} seconds...")
            
            time.sleep(INTERVAL_MINUTES * 60)  # Convert minutes to seconds
            
    except KeyboardInterrupt:
        log("\nScheduler stopped by user (Ctrl+C)")
        log(f"Final Stats:")
        log(f"    Total executions: {execution_count}")
        log(f"    Successful runs: {successful_runs}")
        log(f"    Failed runs: {failed_runs}")
        log(f"    Success rate: {(successful_runs/execution_count*100):.1f}%" if execution_count > 0 else "N/A")
        log("Goodbye!")
        sys.exit(0)
    except Exception as e:
        log(f"Unexpected error in scheduler: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()