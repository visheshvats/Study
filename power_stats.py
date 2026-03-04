#!/usr/bin/env python3
import subprocess
import time
import os
import re

def get_upower_output():
    try:
        result = subprocess.run(['upower', '-i', '/org/freedesktop/UPower/devices/battery_BAT0'], 
                               capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError:
        return None

def parse_upower(output):
    stats = {}
    if not output:
        return stats
    
    # Define regex patterns for keys we care about
    patterns = {
        'state': r'state:\s+(.*)',
        'energy_rate': r'energy-rate:\s+(.*)',
        'voltage': r'voltage:\s+(.*)',
        'percentage': r'percentage:\s+(.*)',
        'time_to_empty': r'time to empty:\s+(.*)',
        'time_to_full': r'time to full:\s+(.*)',
        'energy': r'energy:\s+(.*)',
        'energy_full': r'energy-full:\s+(.*)'
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, output)
        if match:
            stats[key] = match.group(1).strip()
    
    return stats

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    try:
        while True:
            output = get_upower_output()
            stats = parse_upower(output)
            
            clear_screen()
            print("="*40)
            print("      LIVE POWER DIAGNOSTICS      ")
            print("="*40)
            
            if not stats:
                print("Error: Could not retrieve battery data.")
            else:
                state = stats.get('state', 'Unknown').capitalize()
                rate = stats.get('energy_rate', 'N/A')
                voltage = stats.get('voltage', 'N/A')
                perc = stats.get('percentage', 'N/A')
                
                print(f"Status:         {state}")
                print(f"Charge Level:   {perc}")
                print(f"Energy Rate:    {rate}")
                print(f"Voltage:        {voltage}")
                
                if 'time_to_empty' in stats:
                    print(f"Time to Empty:  {stats['time_to_empty']}")
                if 'time_to_full' in stats:
                    print(f"Time to Full:   {stats['time_to_full']}")
                
                # Visual bar for percentage
                try:
                    p_val = int(perc.strip('%'))
                    bar_len = 20
                    filled = int(p_val / 100 * bar_len)
                    bar = "[" + "#" * filled + "-" * (bar_len - filled) + "]"
                    print(f"\nCapacity: {bar} {perc}")
                except:
                    pass
            
            print("\n" + "="*40)
            print("Press Ctrl+C to exit info...")
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()
