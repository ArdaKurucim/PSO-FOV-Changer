import pymem
import pymem.process
import time
import keyboard

def get_pointer_address(pm, base_address, offsets):
    address = pm.read_longlong(base_address)
    for offset in offsets[:-1]:
        address += offset
        address = pm.read_longlong(address)
    address += offsets[-1]
    return address

def main():
    game_name = "ProSoccerOnline-Win64-Shipping.exe"
    base_offset = 0x7A567D8

    offsets = [0x20, 0x68, 0x2D8, 0x98, 0xC8, 0x0, 0x230]

    try:
        pm = pymem.Pymem(game_name)
        print(f"Successfully attached to {game_name} (PID: {pm.process_id})")

        game_module = pymem.process.module_from_name(pm.process_handle, game_name)
        game_base_address = game_module.lpBaseOfDll
        print(f"Game base address: 0x{game_base_address:X}")

        initial_pointer_address = game_base_address + base_offset
        print(f"Initial pointer address (base + static offset): 0x{initial_pointer_address:X}")

        print("\nMonitoring FOV. Press UP_ARROW (+) or DOWN_ARROW (-). Press ESC to exit.")

        last_up_press_time = 0
        last_down_press_time = 0
        key_press_delay = 0.2

        while True:
            final_value_address = get_pointer_address(pm, initial_pointer_address, offsets)

            if final_value_address == 0:
                print("Error: Pointer chain invalid. Retrying... (Try joining a lobby if you're not in one!)")
                time.sleep(1)
                continue

            try:
                current_value = pm.read_float(final_value_address)
            except pymem.exception.MemoryReadError:
                print(f"Error reading memory at 0x{final_value_address:X}. Pointer might be invalid. Retrying... (Try joining a lobby if you're not in one!)")
                time.sleep(1)
                continue

            current_time = time.time()

            if keyboard.is_pressed('up') and (current_time - last_up_press_time > key_press_delay):
                current_value += 10.0
                pm.write_float(final_value_address, current_value)
                print(f"FOV increased to: {current_value:.2f}")
                last_up_press_time = current_time
                time.sleep(0.05)

            elif keyboard.is_pressed('down') and (current_time - last_down_press_time > key_press_delay):
                current_value -= 10.0
                pm.write_float(final_value_address, current_value)
                print(f"FOV decreased to: {current_value:.2f}")
                last_down_press_time = current_time
                time.sleep(0.05)

            elif keyboard.is_pressed('esc'):
                print("Exiting...")
                break

            time.sleep(0.01)

    except pymem.exception.PymemError as e:
        print(f"Pymem Error: {e}")
        if "Could not find process" in str(e):
            print(f"Make sure '{game_name}' is running.")
        elif "Could not open process" in str(e) or "Access is denied" in str(e):
            print("Access denied. Please run the script as an administrator.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()