import subprocess
import sys
import os

def run_script(script_name):
    print(f"--- Running {script_name} ---")
    SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))

    script_path = os.path.join(SCRIPTS_DIR, script_name)
    result = subprocess.run([sys.executable, script_path], capture_output=False)
    if result.returncode != 0:
        print(f"Error running {script_name}")
    return result.returncode

def main():
    # 0. Discover new sources (Brave Search + Eventbrite API)
    run_script("discovery_stage.py")
    
    # 1. Fetch new content
    run_script("fetcher.py")
    
    # 2. Process content and score events
    run_script("processor.py")
    
    # 2b. Conference scoring phase: aggregate speaker info from related pages
    run_script("conference_scorer.py")
    
    # 3. Send notifications
    run_script("notifier.py")

if __name__ == "__main__":
    main()