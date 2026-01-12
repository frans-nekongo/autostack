#!/usr/bin/env python3
import os
import sys
import platform
import subprocess
import time

# --- Colors and Constants ---
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
BLUE = "\033[0;34m"
NC = "\033[0m"

APP_NAME = "AUTOSTACK"
VERSION = "1.0.0"

# --- ASCII Art ---
ASCII_ART = f"""
{BLUE}
   _         _         ____  _             _    
  / \  _   _| |_ ___  / ___|| |_ __ _  ___| | __
 / _ \| | | | __/ _ \ \___ \| __/ _` |/ __| |/ /
/ ___ \ |_| | || (_) | ___) | || (_| | (__|   < 
/_/   \_\__,_|\__\___/ |____/ \__\__,_|\___|_|\_\\
{NC}
{YELLOW}   [ Unified Management Interface v{VERSION} ]{NC}
"""

def clear_screen():
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def get_status_icon(success):
    return f"{GREEN}✓{NC}" if success else f"{RED}✗{NC}"

def check_docker():
    try:
        subprocess.check_output(["docker", "info"], stderr=subprocess.STDOUT)
        return True
    except:
        return False

def check_env():
    env_path = os.path.join("autostack-engine", ".env")
    if not os.path.exists(env_path):
        return False, "Missing .env"
    
    with open(env_path, "r") as f:
        content = f.read()
        if "GEMINI_API_KEY=$" in content or "GEMINI_API_KEY=\n" in content or "GEMINI_API_KEY= " in content:
            return True, "GEMINI_API_KEY not set"
    return True, "OK"

def print_summary():
    print(f"\n{BLUE}--- System Status ---{NC}")
    docker_ok = check_docker()
    env_exists, env_msg = check_env()
    
    print(f"  Docker Status:   [{get_status_icon(docker_ok)}] {'Running' if docker_ok else 'Not Running'}")
    print(f"  Environment:     [{get_status_icon(env_exists)}] {env_msg}")
    print(f"  Operating System: {platform.system()} ({platform.release()})")
    print(f"{BLUE}----------------------{NC}\n")

def run_setup():
    print(f"\n{GREEN}>>> Starting Setup...{NC}")
    if platform.system() == "Windows":
        # Check if running in a shell that can handle .sh or use a ps1 equivalent
        subprocess.run(["powershell.exe", "-File", "scripts/run.ps1"]) # Assuming setup is part of this or similar
        # For full setup on windows we'd need a separate ps1
        print(f"{YELLOW}Windows setup detected. Please ensure you have Git Bash or similar to run .sh scripts if needed.{NC}")
    else:
        subprocess.run(["bash", "scripts/setup_autostack.sh"])

def run_app():
    print(f"\n{GREEN}>>> Launching Application...{NC}")
    if platform.system() == "Windows":
        subprocess.run(["powershell.exe", "-File", "scripts/run.ps1"])
    else:
        subprocess.run(["bash", "scripts/run.sh"])

def run_cleanup():
    print(f"\n{RED}>>> Cleaning up Docker resources...{NC}")
    subprocess.run(["docker", "system", "prune", "-af", "--volumes"])
    print(f"{GREEN}Cleanup complete.{NC}")

def main_menu():
    while True:
        clear_screen()
        print(ASCII_ART)
        print_summary()
        
        print(f"{BLUE}Commands:{NC}")
        print(f"  {YELLOW}1.{NC} Full Project Setup")
        print(f"  {YELLOW}2.{NC} Run Application (Backend + Frontend)")
        print(f"  {YELLOW}3.{NC} System Cleanup (Prune Docker)")
        print(f"  {YELLOW}0.{NC} Exit")
        
        choice = input(f"\n{BLUE}Select an option (0-3): {NC}")
        
        if choice == '1':
            run_setup()
            input("\nPress Enter to return to menu...")
        elif choice == '2':
            run_app()
            # Since run scripts usually stay open, we don't need input() here unless it crashes
        elif choice == '3':
            confirm = input(f"{RED}This will delete all unused Docker data. Continue? (y/n): {NC}")
            if confirm.lower() == 'y':
                run_cleanup()
            input("\nPress Enter to return to menu...")
        elif choice == '0':
            print(f"\n{GREEN}Goodbye!{NC}")
            break
        else:
            print(f"{RED}Invalid choice.{NC}")
            time.sleep(1)

if __name__ == "__main__":
    main_menu()
