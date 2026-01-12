#!/usr/bin/env python3
import os
import sys
import platform
import subprocess
import time
import shutil

# --- Colors and Constants ---
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
BLUE = "\033[0;34m"
CYAN = "\033[0;36m"
NC = "\033[0m"

APP_NAME = "AUTOSTACK"
VERSION = "1.1.0"

# --- ASCII Art ---
ASCII_ART = f"""
{BLUE}
   _         _         ____  _             _    
  / \\  _   _| |_ ___  / ___|| |_ __ _  ___| | __
 / _ \\| | | | __/ _ \\ \\___ \\| __/ _` |/ __| |/ /
/ ___ \\ |_| | || (_) | ___) | || (_| | (__|   < 
/_/   \\_\\__,_|\\__\\___/ |____/ \\__\\__,_|\\___|_|\\_\\
{NC}
{YELLOW}   [ Smart Engineering Interface v{VERSION} ]{NC}
"""

def clear_screen():
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def get_status_label(status):
    if status == "OK" or status == "Installed" or status == "Running":
        return f"{GREEN}{status}{NC}"
    if status == "Missing" or status == "Not Running":
        return f"{RED}{status}{NC}"
    return f"{YELLOW}{status}{NC}"

def check_docker():
    try:
        subprocess.check_output(["docker", "info"], stderr=subprocess.STDOUT)
        return True
    except:
        return False

def check_env():
    env_path = os.path.join("autostack-engine", ".env")
    if not os.path.exists(env_path):
        return False, "Missing"
    
    with open(env_path, "r") as f:
        content = f.read()
        if "GEMINI_API_KEY=$" in content or "GEMINI_API_KEY=\n" in content or "GEMINI_API_KEY= " in content:
            return True, "API Key Missing"
    return True, "OK"

def check_backend():
    # Check for poetry lock and .venv
    engine_dir = "autostack-engine"
    lock_exists = os.path.exists(os.path.join(engine_dir, "poetry.lock"))
    # Check if a venv exists (common locations)
    venv_exists = os.path.exists(os.path.join(engine_dir, ".venv")) or \
                  subprocess.run(["python3", "-m", "poetry", "env", "info", "--path"], cwd=engine_dir, capture_output=True).returncode == 0
    
    if venv_exists and lock_exists:
        return "Installed"
    if lock_exists:
        return "Not Installed (Venv Missing)"
    return "Not Installed"

def check_frontend():
    frontend_dir = "autostack"
    node_modules = os.path.exists(os.path.join(frontend_dir, "node_modules"))
    lock_exists = os.path.exists(os.path.join(frontend_dir, "package-lock.json"))
    
    if node_modules and lock_exists:
        return "Installed"
    if lock_exists:
        return "Not Installed (Modules Missing)"
    return "Not Installed"

def print_dashboard():
    print(f"{CYAN}┌──────────────────────────────────────────────────────────┐{NC}")
    print(f"{CYAN}│{NC}  {BLUE}SYSTEM DASHBOARD{NC}                                       {CYAN}│{NC}")
    print(f"{CYAN}├──────────────────────────────────────────────────────────┤{NC}")
    
    docker_status = "Running" if check_docker() else "Not Running"
    env_exists, env_msg = check_env()
    backend_status = check_backend()
    frontend_status = check_frontend()
    
    print(f"{CYAN}│{NC}  Docker:          {get_status_label(docker_status):<40} {CYAN}│{NC}")
    print(f"{CYAN}│{NC}  Environment:     {get_status_label(env_msg):<40} {CYAN}│{NC}")
    print(f"{CYAN}│{NC}  Backend:         {get_status_label(backend_status):<40} {CYAN}│{NC}")
    print(f"{CYAN}│{NC}  Frontend:        {get_status_label(frontend_status):<40} {CYAN}│{NC}")
    print(f"{CYAN}└──────────────────────────────────────────────────────────┘{NC}")

def run_script(script_name):
    script_path = os.path.join("scripts", script_name)
    if platform.system() == "Windows":
        if script_name.endswith(".ps1"):
            subprocess.run(["powershell.exe", "-File", script_path])
        else:
            print(f"{RED}Error: Cannot run .sh script directly on Windows shell.{NC}")
    else:
        subprocess.run(["bash", script_path])

def run_setup():
    backend = check_backend()
    frontend = check_frontend()
    
    if backend == "Installed" and frontend == "Installed":
        print(f"\n{YELLOW}Project is already installed.{NC}")
        choice = input(f"Do you want to (U)pdate dependencies or (R)e-install completely? (u/r/cancel): ").lower()
        if choice == 'u':
            print(f"\n{GREEN}>>> Updating dependencies...{NC}")
            # Quick update logic
            subprocess.run(["python3", "-m", "poetry", "install"], cwd="autostack-engine")
            subprocess.run(["npm", "install"], cwd="autostack")
            print(f"{GREEN}Update complete.{NC}")
            return
        elif choice == 'cancel':
            return
    
    print(f"\n{GREEN}>>> Starting Full Setup...{NC}")
    run_script("setup_autostack.sh")

def main_menu():
    while True:
        clear_screen()
        print(ASCII_ART)
        print_dashboard()
        
        backend = check_backend()
        frontend = check_frontend()
        needs_setup = backend != "Installed" or frontend != "Installed"
        
        print(f"\n{BLUE}Available Actions:{NC}")
        setup_label = "Update/Reinstall" if not needs_setup else "Full Project Setup"
        print(f"  {YELLOW}1.{NC} {setup_label}")
        print(f"  {YELLOW}2.{NC} Run Application (Backend + Frontend)")
        print(f"  {YELLOW}3.{NC} Advanced: Cleanup Docker (Prune)")
        print(f"  {YELLOW}4.{NC} Check Environment Details")
        print(f"  {YELLOW}0.{NC} Exit")
        
        choice = input(f"\n{BLUE}Select an option (0-4): {NC}")
        
        if choice == '1':
            run_setup()
            input("\nPress Enter to return to menu...")
        elif choice == '2':
            if needs_setup:
                print(f"\n{RED}Warning: Project is not fully installed! Running setup first...{NC}")
                run_setup()
            run_script("run.sh" if platform.system() != "Windows" else "run.ps1")
        elif choice == '3':
            confirm = input(f"{RED}This will delete ALL unused Docker data. Continue? (y/n): {NC}")
            if confirm.lower() == 'y':
                print(f"\n{RED}>>> Cleaning up...{NC}")
                subprocess.run(["docker", "system", "prune", "-af", "--volumes"])
                input("\nCleanup finished. Press Enter to return...")
        elif choice == '4':
            clear_screen()
            print(f"\n{CYAN}--- Detailed System Check ---{NC}")
            print_dashboard()
            check_env() # More detailed env check could be added here
            input("\nPress Enter to return to menu...")
        elif choice == '0':
            print(f"\n{GREEN}Goodbye!{NC}")
            break
        else:
            print(f"{RED}Invalid choice.{NC}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n{GREEN}Exit signaled. Goodbye!{NC}")
        sys.exit(0)
