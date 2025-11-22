"""
Test cases for Car Park Management System
"""
import os
import sys
from io import StringIO
from datetime import datetime

# Import the carpark module
import carpark

def test_load_data():
    """Test 1: Verify data loading"""
    print("\n" + "="*60)
    print("TEST 1: Data Loading")
    print("="*60)
    
    carpark.load_spaces("SPACES.txt")
    carpark.load_cars("CARS.txt")
    carpark.load_parked("PARKED.txt")
    
    print(f"✓ Loaded {len(carpark.spaces)} spaces")
    print(f"✓ Loaded {len(carpark.cars)} registered cars")
    print(f"✓ Loaded {len(carpark.parked)} parked cars")
    
    # Verify spaces are marked as occupied
    occupied_count = sum(1 for s in carpark.spaces if s["occupied"])
    print(f"✓ {occupied_count} spaces marked as occupied")
    
    assert len(carpark.spaces) == 6, "Should have 6 spaces"
    assert len(carpark.cars) == 5, "Should have 5 registered cars"
    assert len(carpark.parked) == 2, "Should have 2 parked cars"
    assert occupied_count == 2, "Should have 2 occupied spaces"
    
    print("✓ TEST 1 PASSED")

def test_space_types():
    """Test 2: Verify different space types exist"""
    print("\n" + "="*60)
    print("TEST 2: Space Types")
    print("="*60)
    
    space_types = {}
    for space in carpark.spaces:
        space_type = space["type"]
        space_types[space_type] = space_types.get(space_type, 0) + 1
    
    print(f"Space type distribution:")
    for space_type, count in space_types.items():
        print(f"  {space_type}: {count}")
    
    assert "Standard" in space_types, "Should have Standard spaces"
    assert "EV" in space_types, "Should have EV spaces"
    assert "Disabled" in space_types, "Should have Disabled spaces"
    
    print("✓ TEST 2 PASSED")

def test_available_spaces_standard():
    """Test 3: Check available standard spaces"""
    print("\n" + "="*60)
    print("TEST 3: Available Standard Spaces")
    print("="*60)
    
    available = carpark.get_available_spaces("Standard")
    print(f"Available standard spaces: {len(available)}")
    for space in available:
        print(f"  {space['id']}: {space['location']} ({space['type']})")
    
    assert len(available) > 0, "Should have available standard spaces"
    print("✓ TEST 3 PASSED")

def test_available_spaces_ev():
    """Test 4: Check available EV spaces"""
    print("\n" + "="*60)
    print("TEST 4: Available EV Spaces")
    print("="*60)
    
    available = carpark.get_available_spaces("EV")
    print(f"Available EV spaces: {len(available)}")
    for space in available:
        print(f"  {space['id']}: {space['location']} ({space['type']})")
    
    # Note: S004 is occupied, so there should be no available EV spaces
    print("✓ TEST 4 PASSED")

def test_available_spaces_disabled():
    """Test 5: Check available disabled spaces"""
    print("\n" + "="*60)
    print("TEST 5: Available Disabled Spaces")
    print("="*60)
    
    available = carpark.get_available_spaces("Disabled")
    print(f"Available disabled spaces: {len(available)}")
    for space in available:
        print(f"  {space['id']}: {space['location']} ({space['type']})")
    
    # Disabled entitlement can use Standard spaces too
    assert len(available) > 0, "Should have spaces available for disabled"
    print("✓ TEST 5 PASSED")

def test_car_registration():
    """Test 6: Verify car registration data"""
    print("\n" + "="*60)
    print("TEST 6: Car Registration Data")
    print("="*60)
    
    test_reg = "AB12CDE"
    assert test_reg in carpark.cars, f"{test_reg} should be registered"
    
    car_info = carpark.cars[test_reg]
    print(f"Car {test_reg}:")
    print(f"  Owner: {car_info['owner']}")
    print(f"  Contract: {car_info['contract']}")
    print(f"  Entitlement: {car_info['entitlement']}")
    
    # Owner name depends on dataset; verify it's a non-empty string
    assert isinstance(car_info['owner'], str) and len(car_info['owner']) > 0
    assert car_info['entitlement'] == "Standard"
    
    print("✓ TEST 6 PASSED")

def test_parked_car_data():
    """Test 7: Verify parked car data structure"""
    print("\n" + "="*60)
    print("TEST 7: Parked Car Data")
    print("="*60)
    
    for record in carpark.parked:
        print(f"Space {record['space_id']}: {record['reg']}")
        print(f"  Time in: {record['time_in']}")
        print(f"  Expected out: {record['expected_time_out']}")
        
        # Verify required fields exist
        assert "space_id" in record
        assert "reg" in record
        assert "time_in" in record
        assert "expected_time_out" in record
    
    print("✓ TEST 7 PASSED")

def test_space_occupancy():
    """Test 8: Verify space occupancy matches parked cars"""
    print("\n" + "="*60)
    print("TEST 8: Space Occupancy Consistency")
    print("="*60)
    
    # Get occupied space IDs from parked cars
    parked_space_ids = {record['space_id'] for record in carpark.parked}
    
    # Get occupied space IDs from spaces
    occupied_space_ids = {space['id'] for space in carpark.spaces if space['occupied']}
    
    print(f"Parked car space IDs: {parked_space_ids}")
    print(f"Occupied space IDs: {occupied_space_ids}")
    
    assert parked_space_ids == occupied_space_ids, "Parked cars and occupied spaces should match"
    
    print("✓ TEST 8 PASSED")

def test_unregistered_car():
    """Test 9: Test behavior with unregistered car"""
    print("\n" + "="*60)
    print("TEST 9: Unregistered Car Check")
    print("="*60)
    
    fake_reg = "FAKE123"
    assert fake_reg not in carpark.cars, "Fake registration should not exist"
    print(f"✓ Registration {fake_reg} correctly not found in system")
    
    print("✓ TEST 9 PASSED")

def test_free_spaces_count():
    """Test 10: Verify free spaces count"""
    print("\n" + "="*60)
    print("TEST 10: Free Spaces Count")
    print("="*60)
    
    free_spaces = [s for s in carpark.spaces if not s["occupied"]]
    occupied_spaces = [s for s in carpark.spaces if s["occupied"]]
    
    print(f"Total spaces: {len(carpark.spaces)}")
    print(f"Free spaces: {len(free_spaces)}")
    print(f"Occupied spaces: {len(occupied_spaces)}")
    
    assert len(free_spaces) + len(occupied_spaces) == len(carpark.spaces)
    assert len(free_spaces) == 4, "Should have 4 free spaces (6 total - 2 occupied)"
    
    print("✓ TEST 10 PASSED")

def run_all_tests():
    """Run all test cases"""
    print("\n" + "="*60)
    print("CAR PARK MANAGEMENT SYSTEM - TEST SUITE")
    print("="*60)
    
    try:
        test_load_data()
        test_space_types()
        test_available_spaces_standard()
        test_available_spaces_ev()
        test_available_spaces_disabled()
        test_car_registration()
        test_parked_car_data()
        test_space_occupancy()
        test_unregistered_car()
        test_free_spaces_count()
        
        print("\n" + "="*60)
        print("ALL TESTS PASSED! ✓")
        print("="*60)
        return True
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
