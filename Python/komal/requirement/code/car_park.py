#!/usr/bin/env python3
"""
Car Park Management Program
Manages parking spaces, cars, and parking records
"""

import os
import datetime
from typing import Dict, List, Optional, Tuple


class CarPark:
    """Main class for managing the car park"""
    
    def __init__(self):
        """Initialize the car park system"""
        self.spaces: Dict[str, Dict] = {}  # {space_id: {location, type, available}}
        self.cars: Dict[str, Dict] = {}  # {registration: {owner, contact, type}}
        self.parked: Dict[str, Dict] = {}  # {registration: {space_id, time_in, expected_time_out}}
        self.space_to_reg: Dict[str, str] = {}  # {space_id: registration} for quick lookup
        
    def load_spaces(self, filename: str = "SPACES.txt") -> bool:
        """Load parking spaces from file"""
        try:
            if not os.path.exists(filename):
                print(f"Warning: {filename} not found. Creating empty file.")
                return False
                
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 3:
                        space_id, location, space_type = parts[0], parts[1], parts[2]
                        self.spaces[space_id] = {
                            'location': location,
                            'type': space_type,
                            'available': True
                        }
            return True
        except Exception as e:
            print(f"Error loading spaces: {e}")
            return False
    
    def load_cars(self, filename: str = "CARS.txt") -> bool:
        """Load car details from file"""
        try:
            if not os.path.exists(filename):
                print(f"Warning: {filename} not found. Creating empty file.")
                return False
                
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 3:
                        registration = parts[0]
                        owner = parts[1]
                        contact = parts[2]
                        # Read entitlement (4th field) if available, otherwise default to Standard
                        car_type = parts[3] if len(parts) >= 4 else "Standard"
                        # Ensure car_type is one of the valid types
                        if car_type not in ["Standard", "EV", "Disabled"]:
                            car_type = "Standard"
                        
                        self.cars[registration] = {
                            'owner': owner,
                            'contact': contact,
                            'type': car_type
                        }
            return True
        except Exception as e:
            print(f"Error loading cars: {e}")
            return False
    
    def load_parked(self, filename: str = "PARKED.txt") -> bool:
        """Load currently parked cars from file"""
        try:
            if not os.path.exists(filename):
                # Empty file is okay - no cars parked
                return True
                
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 4:
                        space_id, registration, time_in, expected_time_out = parts[0], parts[1], parts[2], parts[3]
                        if space_id in self.spaces:
                            self.parked[registration] = {
                                'space_id': space_id,
                                'time_in': time_in,
                                'expected_time_out': expected_time_out
                            }
                            self.space_to_reg[space_id] = registration
                            self.spaces[space_id]['available'] = False
            return True
        except Exception as e:
            print(f"Error loading parked cars: {e}")
            return False
    
    def save_parked(self, filename: str = "PARKED.txt") -> bool:
        """Save currently parked cars to file"""
        try:
            with open(filename, 'w') as f:
                # Write header comment
                f.write("#Space ID, Registration, Time In, Expected Time Out\n")
                for registration, details in self.parked.items():
                    f.write(f"{details['space_id']},{registration},{details['time_in']},{details['expected_time_out']}\n")
            return True
        except Exception as e:
            print(f"Error saving parked cars: {e}")
            return False
    
    def find_available_space(self, car_type: str = "Standard") -> Optional[str]:
        """Find an available space matching the car type"""
        for space_id, space_info in self.spaces.items():
            if space_info['available']:
                space_type = space_info['type']
                # EV cars can use EV spaces, Disabled cars can use Disabled spaces
                # Standard cars can use Standard spaces
                if car_type == "EV" and space_type == "EV":
                    return space_id
                elif car_type == "Disabled" and space_type == "Disabled":
                    return space_id
                elif car_type == "Standard" and space_type == "Standard":
                    return space_id
        
        # If no matching space found, return None
        return None
    
    def park_car(self, registration: str, duration_minutes: int) -> Tuple[bool, str]:
        """Park a car in an available space"""
        # Validate car exists
        registration = registration.upper()
        if registration not in self.cars:
            return False, f"Car {registration} not found in CARS.txt"
        
        # Check if car is already parked
        if registration in self.parked:
            return False, f"Car {registration} is already parked in space {self.parked[registration]['space_id']}"
        
        # Get car type
        car_type = self.cars[registration]['type']
        
        # Find available space
        space_id = self.find_available_space(car_type)
        if not space_id:
            return False, f"No available {car_type} space found"
        
        # Calculate times
        now = datetime.datetime.now()
        time_in = now.strftime("%Y-%m-%d %H:%M:%S")
        expected_time_out = (now + datetime.timedelta(minutes=duration_minutes)).strftime("%Y-%m-%d %H:%M:%S")
        
        # Create parking record
        self.parked[registration] = {
            'space_id': space_id,
            'time_in': time_in,
            'expected_time_out': expected_time_out
        }
        self.space_to_reg[space_id] = registration
        self.spaces[space_id]['available'] = False
        
        return True, f"Car {registration} parked successfully in {space_id} ({self.spaces[space_id]['location']})"
    
    def leave_carpark(self, identifier: str) -> Tuple[bool, str]:
        """Remove a car from the carpark by registration or space ID"""
        identifier = identifier.upper()
        
        # Try to find by registration
        if identifier in self.parked:
            registration = identifier
            space_id = self.parked[registration]['space_id']
        # Try to find by space ID
        elif identifier in self.space_to_reg:
            space_id = identifier
            registration = self.space_to_reg[space_id]
        else:
            return False, f"Car or space {identifier} not found in parked cars"
        
        # Remove parking record
        del self.parked[registration]
        del self.space_to_reg[space_id]
        self.spaces[space_id]['available'] = True
        
        return True, f"Car {registration} has left space {space_id}"
    
    def view_parked_cars(self) -> None:
        """Display all currently parked cars"""
        if not self.parked:
            print("\nNo cars currently parked.")
            return
        
        print("\n" + "="*80)
        print("CURRENTLY PARKED CARS")
        print("="*80)
        print(f"{'Space ID':<12} {'Registration':<15} {'Owner':<20} {'Time In':<20} {'Expected Out':<20}")
        print("-"*80)
        
        for registration, details in sorted(self.parked.items()):
            space_id = details['space_id']
            owner = self.cars[registration]['owner']
            time_in = details['time_in']
            expected_out = details['expected_time_out']
            print(f"{space_id:<12} {registration:<15} {owner:<20} {time_in:<20} {expected_out:<20}")
        
        print("="*80)
    
    def view_free_spaces(self) -> None:
        """Display all free spaces"""
        free_spaces = [space_id for space_id, info in self.spaces.items() if info['available']]
        
        if not free_spaces:
            print("\nNo free spaces available.")
            return
        
        print("\n" + "="*80)
        print("FREE SPACES")
        print("="*80)
        print(f"{'Space ID':<12} {'Location':<25} {'Type':<15}")
        print("-"*80)
        
        for space_id in sorted(free_spaces):
            location = self.spaces[space_id]['location']
            space_type = self.spaces[space_id]['type']
            print(f"{space_id:<12} {location:<25} {space_type:<15}")
        
        print("="*80)
    
    def initialize(self) -> bool:
        """Initialize the system by loading all data files"""
        print("Initializing Car Park Management System...")
        success = True
        success &= self.load_spaces()
        success &= self.load_cars()
        success &= self.load_parked()
        
        if success:
            print(f"Loaded {len(self.spaces)} spaces, {len(self.cars)} cars, {len(self.parked)} parked cars.")
        return success


def round_to_15_minutes(minutes: int) -> int:
    """Round duration to nearest 15 minutes"""
    return round(minutes / 15) * 15


def main():
    """Main program loop"""
    car_park = CarPark()
    
    if not car_park.initialize():
        print("Warning: Some data files could not be loaded. Program may not function correctly.")
    
    while True:
        print("\n" + "="*50)
        print("CAR PARK MANAGEMENT SYSTEM")
        print("="*50)
        print("1. Park a car")
        print("2. Leave carpark")
        print("3. View parked cars")
        print("4. View free spaces")
        print("5. Exit")
        print("="*50)
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            registration = input("Enter car registration: ").strip()
            try:
                duration = int(input("Enter parking duration in minutes: ").strip())
                duration = round_to_15_minutes(duration)
                if duration < 15:
                    duration = 15
                print(f"Rounded to nearest 15 minutes: {duration} minutes")
                
                success, message = car_park.park_car(registration, duration)
                print(message)
            except ValueError:
                print("Invalid duration. Please enter a number.")
        
        elif choice == "2":
            identifier = input("Enter car registration or space ID: ").strip()
            success, message = car_park.leave_carpark(identifier)
            print(message)
        
        elif choice == "3":
            car_park.view_parked_cars()
        
        elif choice == "4":
            car_park.view_free_spaces()
        
        elif choice == "5":
            print("\nSaving parked cars to PARKED.txt...")
            if car_park.save_parked():
                print("Data saved successfully.")
            else:
                print("Error saving data.")
            print("Exiting program. Goodbye!")
            break
        
        else:
            print("Invalid choice. Please enter 1-5.")


if __name__ == "__main__":
    main()

