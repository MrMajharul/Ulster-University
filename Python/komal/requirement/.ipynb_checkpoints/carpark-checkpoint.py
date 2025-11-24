import datetime
import os
from typing import List, Dict, Optional

##data structures
spaces : List[Dict[str, str]] = []
cars : List[Dict[str, str]] = {}
parked: List[Dict[str, str]] = []

def load_spaces(filename: str) -> None:
    '''Load parking spaces from a spaces file.'''
    
    global spaces
    spaces = []
    if not os.path.exists(filename):
        print(f"Spaces file '{filename}' not found.")
        return
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith("#"):
                spaces_id, location, space_type = line.split(", ", 2)
                spaces.append({
                    "id": spaces_id,
                    "location": location,
                    "type": space_type,
                    "occupied": False
                })
                
def load_cars(filename: str) -> None:
    '''Load registration cars from CARS.txt file'''
    global cars
    cars = {}
    if not os.path.exists(filename):
        print(f"Cars file '{filename}' not found.")
        return
    
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith("#"):
                reg, name, contract, entitlement = line.split(", ", 3)
                cars[reg.upper()] = {
                    "owner": name,
                    "contract": contract,
                    "entitlement": entitlement
                }
                
def load_parked(filename: str) -> None:
    """ load current parked cars and mark spaces as occupied """
    
    global parked
    parked = []
    if not os.path.exists(filename):
        print(f"Parked file '{filename}' not found.")
        return
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith("#"):
                spaces_id, reg, time_in, expected_time_out = line.split(", ", 3)
                parked.append({
                    "space_id": spaces_id,
                    "reg": reg.upper(),
                    "time_in": time_in,
                    "expected_time_out": expected_time_out
                })
                # Mark space as occupied
                for space in spaces:
                    if space["id"] == spaces_id:
                        space["occupied"] = True
                        break
                    
def save_parked(filename: str = "PARKED.txt") -> None:
    """ Save current parked cars to PARKED.txt file """
    
    with open(filename, "w") as file:
        file.write("# SpaceID, Reg, TimeIn, ExpectedTimeOut\n")
        for record in parked:
            file.write(f"{record['space_id']}, {record['reg']}, {record['time_in']}, {record['expected_time_out']}\n")
            
    print(f" Parked cars saved successfully to '{filename}'")
    
    
def get_available_spaces(required_type: str = "Standard") -> List[Dict[str, str]]:
    """ Get a list of available parking spaces of a specific type """
    
    available = []
    for space in spaces:
        if not space["occupied"]:
            if space["type"] == required_type or \
                (required_type == "Disabled" and space["type"] == "Standard"):
                    available.append(space)
            elif required_type == "Standard" and space["type"] in ["Standard", "Disabled", "EV"]:
                if space["type"] == "Standard":
                    available.append(space)
            elif required_type == "EV" and space["type"] in ["EV" ]:
                available.append(space)
    return available
def park_car() -> None:
    """Main function to park a car"""
    try:
        reg = input("\nEnter car registration number: ").strip().upper()
        if reg not in cars:
            print(f" Car with registration '{reg}' is not registered in this car park.")
            return
        
        car = cars[reg]
        entitlement = car["entitlement"]
        duration_str = input("Enter expected parking duration in minutes (multiple of 15): ").strip()
        duration = int(duration_str)
        
        if duration <= 0 or duration % 15 != 0:
            print(" Invalid duration. Please enter a positive multiple of 15.")
            return
        
        # calculate expected time out
        now = datetime.datetime.now()
        time_in_str = now.strftime("%Y-%m-%d %H:%M")
        expected_time_out = now + datetime.timedelta(minutes=duration)
        expected_time_out_str = expected_time_out.strftime("%Y-%m-%d %H:%M")
        
        # find available space
        available_spaces = get_available_spaces(entitlement)
        if not available_spaces:
            print(f" No available parking spaces for entitlement '{entitlement}'.")
            return
        print("\nAvailable parking spaces:")
        for idx, space in enumerate(available_spaces, start=1):
            print(f" {idx}. ID: {space['id']}, Location: {space['location']}, Type: {space['type']}")
        
        choice = int(input("Select a parking space by number: ").strip())
        if choice < 1 or choice > len(available_spaces):
            print(" Invalid choice.")
            return
        
        chosen_space = available_spaces[choice - 1]
        
        #parking record
        parked.append({
            "space_id": chosen_space["id"],
            "reg": reg,
            "time_in": time_in_str,
            "expected_time_out": expected_time_out_str
        })
        # mark space as occupied
        for space in spaces:
            if space["id"] == chosen_space["id"]:
                space["occupied"] = True
                break
        print(f"\nCar '{reg}' parked in space '{chosen_space['id']}' until {expected_time_out_str}.")
    except ValueError:
        print(" Invalid input. Please try again.")
    except Exception as e:
        print(f" An error occurred: {e}")
        
def leave_car() -> None:
    '''remove a car from the car park'''
    identifier = input("\nEnter car registration number to leave: ").strip().upper()
    
    for record in parked:
        if record["reg"] == identifier or record["space_id"] == identifier:
            
            for space in spaces:
                if space["id"] == record["space_id"]:
                    space["occupied"] = False
                    break
            parked.remove(record)
            print(f"\nCar '{identifier}' has left the car park from space '{record['space_id']}'.")
            return
    print(f"\nCar '{identifier}' not found in the car park.")
    
def view_parked_cars() -> None:
    """Display all currently parked cars"""
    if not parked:
        print("\nThe car park is empty.")
        return

    print("\n" + "="*80)
    print(f"{'Space':<8} {'Registration':<12} {'Owner':<20} {'Time In':<16} {'Expected Out':<16}")
    print("="*80)
    for record in parked:
        reg = record["reg"]
        owner = cars.get(reg, {}).get("owner", "Unknown")
        print(f"{record['space_id']:<8} {reg:<12} {owner:<20} {record['time_in']:<16} {record['expected_time_out']:<16}")
    print("="*80)
    
def view_free_spaces() -> None:
    """Show all free parking spaces"""
    free = [s for s in spaces if not s["occupied"]]
    if not free:
        print("\nNo free spaces - car park is full!")
        return

    print("\nFree spaces:")
    print(f"{'Space ID':<8} {'Location':<25} {'Type'}")
    print("-" * 50)
    for space in free:
        print(f"{space['id']:<8} {space['location']:<25} {space['type']}")
        
def display_menu() -> None:
    print("\n" + "="*50)
    print("     Car park management system")
    print("="*50)
    print("1. Park a car")
    print("2. Car leaving")
    print("3. View currently parked cars")
    print("4. View free spaces")
    print("5. Exit")
    print("="*50)   
    
def main() -> None:
    print("Loading data...")
    load_spaces("SPACES.txt")
    load_cars("CARS.txt")
    load_parked("PARKED.txt")
    print(f"Loaded {len(spaces)} spaces, {len(cars)} registered cars, {len(parked)} currently parked.")

    while True:
        display_menu()
        choice = input("Enter your choice (1-5): ").strip()

        if choice == "1":
            park_car()
        elif choice == "2":
            leave_car()
        elif choice == "3":
            view_parked_cars()
        elif choice == "4":
            view_free_spaces()
        elif choice == "5":
            save_parked()
            print("Thank you for using the Car Park Management System. Goodbye!")
            break
        else:
            print("Invalid choice - please enter 1-5.")   
    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")