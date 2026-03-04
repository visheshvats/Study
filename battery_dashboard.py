#!/usr/bin/env python3
import subprocess
import time
import os
import re

# ANSI Color Codes
CLR_RESET = "\033[0m"
CLR_BOLD = "\033[1m"
CLR_RED = "\033[31m"
CLR_GREEN = "\033[32m"
CLR_YELLOW = "\033[33m"
CLR_BLUE = "\033[34m"
CLR_CYAN = "\033[36m"
CLR_BG_BLUE = "\033[44m"

def get_upower_data():
    try:
        # Get primary battery
        res = subprocess.run(['upower', '-e'], capture_output=True, text=True)
        batt_path = next((line for line in res.stdout.splitlines() if 'battery_BAT' in line), None)
        
        if not batt_path:
            return None
        
        result = subprocess.run(['upower', '-i', batt_path], capture_output=True, text=True, check=True)
        return result.stdout
    except (subprocess.CalledProcessError, StopIteration):
        return None

def parse_stats(output):
    stats = {}
    if not output: return stats
    
    mapping = {
        'vendor': r'vendor:\s+(.*)',
        'model': r'model:\s+(.*)',
        'state': r'state:\s+(.*)',
        'percentage': r'percentage:\s+([\d.]+)',
        'energy_rate': r'energy-rate:\s+([\d.]+)',
        'voltage': r'voltage:\s+([\d.]+)',
        'energy_full': r'energy-full:\s+([\d.]+)',
        'energy_full_design': r'energy-full-design:\s+([\d.]+)',
        'time_to_empty': r'time to empty:\s+(.*)',
        'time_to_full': r'time to full:\s+(.*)',
        'technology': r'technology:\s+(.*)',
        'capacity': r'capacity:\s+([\d.]+)'
    }
    
    for key, pattern in mapping.items():
        match = re.search(pattern, output)
        if match:
            stats[key] = match.group(1).strip()
    
    return stats

def get_color_for_perc(perc):
    if perc > 70: return CLR_GREEN
    if perc > 30: return CLR_YELLOW
    return CLR_RED

def draw_bar(perc, length=30):
    filled = int(perc / 100 * length)
    color = get_color_for_perc(perc)
    bar = color + "█" * filled + CLR_RESET + "░" * (length - filled)
    return f"[{bar}]"

def clear_screen():
    print("\033[H\033[J", end="")

def main():
    try:
        while True:
            raw = get_upower_data()
            stats = parse_stats(raw)
            clear_screen()
            
            print(f"{CLR_BG_BLUE}{CLR_BOLD}       ⚡ BATTERY COMMAND CENTER ⚡       {CLR_RESET}\n")
            
            if not stats:
                print(f"{CLR_RED}Error: Battery hardware not detected.{CLR_RESET}")
            else:
                p_val = float(stats.get('percentage', 0))
                state = stats.get('state', 'Unknown').upper()
                
                # Header Section
                color = get_color_for_perc(p_val)
                print(f"{CLR_BOLD}STATUS:{CLR_RESET} {color}{state}{CLR_RESET}")
                print(f"{CLR_BOLD}CHARGE:{CLR_RESET} {draw_bar(p_val)} {color}{p_val}%{CLR_RESET}")
                
                # Efficiency Section
                print(f"\n{CLR_CYAN}{CLR_BOLD}--- REAL-TIME METRICS ---{CLR_RESET}")
                print(f"{CLR_BOLD}Power Draw: {CLR_RESET}{stats.get('energy_rate', '0')} W")
                print(f"{CLR_BOLD}Voltage:    {CLR_RESET}{stats.get('voltage', '0')} V")
                
                if 'time_to_empty' in stats and state == 'DISCHARGING':
                    print(f"{CLR_BOLD}Est. Life:  {CLR_YELLOW}{stats['time_to_empty']}{CLR_RESET}")
                elif 'time_to_full' in stats and state == 'CHARGING':
                    print(f"{CLR_BOLD}Est. Full:  {CLR_GREEN}{stats['time_to_full']}{CLR_RESET}")
                
                # Health Section
                print(f"\n{CLR_CYAN}{CLR_BOLD}--- HARDWARE HEALTH ---{CLR_RESET}")
                health = stats.get('capacity', 'N/A')
                print(f"{CLR_BOLD}Battery Health: {CLR_RESET}{health}%")
                print(f"{CLR_BOLD}Technology:     {CLR_RESET}{stats.get('technology', 'N/A')}")
                print(f"{CLR_BOLD}Manufacturer:   {CLR_RESET}{stats.get('vendor', 'N/A')} ({stats.get('model', 'N/A')})")
            
            print(f"\n{CLR_BLUE}Updating every 5s... Press Ctrl+C to quit.{CLR_RESET}")
            time.sleep(5)
            
    except KeyboardInterrupt:
        print(f"\n{CLR_BOLD}Dashboard closed.{CLR_RESET}")

if __name__ == "__main__":
    main()
