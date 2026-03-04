import ctypes
import time
import random
import sys
import datetime

def move_mouse_relative(dx, dy):
    """
    Moves the mouse cursor relative to its current position.
    Uses the Windows user32.dll mouse_event function.
    """
    # MOUSEEVENTF_MOVE = 0x0001
    ctypes.windll.user32.mouse_event(0x0001, dx, dy, 0, 0)

def main():
    print("=== Mouse Jiggler for Windows ===")
    print("Prevents system idle by simulating micro mouse movements.")
    print("Press Ctrl+C to stop the script.\n")

    if sys.platform != 'win32':
        print("[WARNING] This script is designed to run on Windows.")
        print("It uses ctypes to access user32.dll, which is not available on Linux/macOS.")
        print("You can still see the logic below, but you must run this on a Windows machine.\n")

    try:
        while True:
            # Generate random small movements (pixels)
            delta_x = random.randint(-1, 1)
            delta_y = random.randint(-1, 1)

            # Ensure at least some movement occurs if both zero
            if delta_x == 0 and delta_y == 0:
                delta_x = 1

            # Perform the move
            try:
                move_mouse_relative(delta_x, delta_y)
                
                # Timestamp for logging
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] Activity simulated. (Delta: {delta_x}, {delta_y})")
                
            except AttributeError:
                # Fallback for non-Windows (testing)
                print(f"[Simulation] Would move mouse: {delta_x}, {delta_y}")
            except Exception as e:
                print(f"Error: {e}")

            # Random sleep interval (e.g., between 1 to 3 minutes)
            # This makes the pattern less predictable.
            sleep_time = random.randint(60, 180) 
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\nScript stopped by user.")

if __name__ == "__main__":
    main()
