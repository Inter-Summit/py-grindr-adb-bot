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

# CONFIGURACIÓN
INTERVAL_MINUTES = 15  # Cambiar aquí para modificar el intervalo
SCRIPT_TO_RUN = "app.py"  # Script a ejecutar

def get_timestamp():
    """Get current timestamp for logging"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(message):
    """Log with timestamp"""
    print(f"[{get_timestamp()}] [CRON] {message}")

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

def main():
    """Main cron loop"""
    log("Grindr Bot Cron Scheduler Starting...")
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
            
            # Run the bot script
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