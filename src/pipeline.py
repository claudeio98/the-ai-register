import subprocess
import sys
import os

def run_script(script_name):
    print(f"--- Running {script_name} ---")
    result = subprocess.run([sys.executable, f"/Users/claudio/.pi/workspace/ai-events-tracker/src/{script_name}"], capture_output=False)
    if result.returncode != 0:
        print(f"Error running {script_name}")
    return result.returncode

def main():
    # 0. Occasionally discover new sources
    # In a real production system, this could be based on a timestamp in the DB
    # For now, we'll make it a separate step or run it based on a simple logic.
    # Let's run it every time the pipeline is triggered for maximum discovery, 
    # or you can move this to a separate cron job.
    run_script("discovery.py")
    
    # 1. Fetch new content
    run_script("fetcher.py")
    
    # 2. Process content and score events
    run_script("processor.py")
    
    # 3. Send notifications
    run_script("notifier.py")

if __name__ == "__main__":
    main()
