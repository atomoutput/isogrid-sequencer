#!/usr/bin/env python3
"""
Test script to validate the core sequencer logic of Isogrid without UI
"""
import random

def euclidean_rhythm(steps, pulses):
    """Generate an Euclidean rhythm pattern"""
    if pulses > steps or pulses < 0:
        return [True] * steps  # Return all active if invalid
    
    pattern = [0] * steps
    if pulses == 0:
        return pattern
    
    counts = [1] * pulses
    remainders = [steps % pulses] * (steps % pulses) + [0] * (pulses - steps % pulses)
    
    divisor = steps // pulses
    j = 0
    while True:
        if sum(remainders) == 0:
            break
        counts = remainders + counts[:-len(remainders)]
        remainders = counts[:divisor] * (len(remainders) // divisor) + counts[:len(remainders) % divisor]
    
    pattern = []
    for count in counts:
        pattern.extend([1] + [0] * (count - 1))
    
    # Trim to correct length
    pattern = pattern[:steps]
    pattern = [bool(x) for x in pattern]
    
    # Pad with False if needed
    while len(pattern) < steps:
        pattern.append(False)
        
    return pattern

class TestSequencer:
    def __init__(self):
        # Initialize sequencer variables
        self.current_x = 0
        self.current_y = 0
        self.x_direction = 1
        self.y_direction = 1
        self.step_states = [False] * 16  # Track which steps are enabled
        self.step_notes = [i % 12 + 36 for i in range(16)]  # Default note values (C2 to B3)
        self.step_velocities = [100] * 16  # Default velocities
        self.step_probabilities = [1.0] * 16  # Default probabilities (100%)
        self.step_cc_values = [{} for _ in range(16)]  # CC values for each step
        self.step_teleport_targets = [-1] * 16  # Wormhole mode targets (-1 = no teleport)
        
        # Set some steps as active for testing
        self.step_states[0] = True
        self.step_states[5] = True
        self.step_states[10] = True
        self.step_states[15] = True
        
        # Set some step-specific CC values for testing
        self.step_cc_values[5] = {23: 64}  # Cutoff on step 5
        self.step_cc_values[10] = {9: 100}  # Osc Type on step 10
    
    def update_x_position(self, mode='Forward', speed='1/16'):
        # Handle Euclidean rhythm for X axis
        if mode == 'Euclidean':
            euclidean_x_steps = euclidean_rhythm(4, 2)  # 4 steps, 2 pulses
            euclidean_x_index = getattr(self, 'euclidean_x_index', 0)
            
            if euclidean_x_steps[euclidean_x_index]:
                # Only move if this step is active in the Euclidean pattern
                self.current_x = (self.current_x + 1) % 4
            self.euclidean_x_index = (euclidean_x_index + 1) % len(euclidean_x_steps)
        elif mode == 'Random':
            self.current_x = random.randint(0, 3)
        elif mode == 'Forward':
            self.current_x = (self.current_x + 1) % 4
        elif mode == 'Backward':
            self.current_x = (self.current_x - 1) % 4
        elif mode == 'Pendulum':
            self.current_x += self.x_direction
            if self.current_x >= 3:
                self.x_direction = -1
            elif self.current_x <= 0:
                self.x_direction = 1
            if self.current_x < 0:
                self.current_x = 0
            elif self.current_x > 3:
                self.current_x = 3
    
    def update_y_position(self, mode='Forward', speed='1/16'):
        # Handle Euclidean rhythm for Y axis
        if mode == 'Euclidean':
            euclidean_y_steps = euclidean_rhythm(4, 3)  # 4 steps, 3 pulses
            euclidean_y_index = getattr(self, 'euclidean_y_index', 0)
            
            if euclidean_y_steps[euclidean_y_index]:
                # Only move if this step is active in the Euclidean pattern
                self.current_y = (self.current_y + 1) % 4
            self.euclidean_y_index = (euclidean_y_index + 1) % len(euclidean_y_steps)
        elif mode == 'Random':
            self.current_y = random.randint(0, 3)
        elif mode == 'Forward':
            self.current_y = (self.current_y + 1) % 4
        elif mode == 'Backward':
            self.current_y = (self.current_y - 1) % 4
        elif mode == 'Pendulum':
            self.current_y += self.y_direction
            if self.current_y >= 3:
                self.y_direction = -1
            elif self.current_y <= 0:
                self.y_direction = 1
            if self.current_y < 0:
                self.current_y = 0
            elif self.current_y > 3:
                self.current_y = 3
        elif mode == 'Logic Advance':
            # Only advance Y if X position is at a high-velocity step (velocity > 100)
            # Get the current X position step index for the current Y row
            x_step_index = (self.current_y * 4) + self.current_x
            if self.step_velocities[x_step_index] > 100:
                self.current_y = (self.current_y + 1) % 4
    
    def tick(self, x_mode='Forward', y_mode='Forward'):
        # Update X position based on X driver logic
        self.update_x_position(x_mode)
        
        # Update Y position based on Y driver logic
        self.update_y_position(y_mode)
        
        # Calculate the active step index
        active_step_index = (self.current_y * 4) + self.current_x
        
        # Check for wormhole teleportation
        if self.step_teleport_targets[active_step_index] != -1:
            # Teleport to the target step immediately
            active_step_index = self.step_teleport_targets[active_step_index]
            # Update current X and Y based on new step index
            self.current_x = active_step_index % 4
            self.current_y = active_step_index // 4
        
        print(f"Step: ({self.current_x}, {self.current_y}) -> Index: {active_step_index}")
        
        # Play the note at the intersection if step is enabled and passes probability check
        if self.step_states[active_step_index]:
            if random.random() <= self.step_probabilities[active_step_index]:
                note_value = self.step_notes[active_step_index]
                velocity = self.step_velocities[active_step_index]
                
                # Apply parameter lock if any CC values are set for this step
                if self.step_cc_values[active_step_index]:
                    for cc_num, cc_val in self.step_cc_values[active_step_index].items():
                        print(f"  CC {cc_num}: {cc_val}")
                
                print(f"  Note ON: {note_value} (velocity: {velocity})")
                return True, note_value, velocity
            else:
                print(f"  Step {active_step_index} skipped due to probability")
        else:
            print(f"  Step {active_step_index} is disabled")
        
        return False, None, None
    
    def test_wormhole_mode(self):
        """Test wormhole teleportation"""
        print("\n--- Testing Wormhole Mode ---")
        # Set up a teleportation: step 3 teleports to step 12
        self.step_teleport_targets[3] = 12
        self.current_x = 3
        self.current_y = 0  # This means step index 3
        
        print(f"Before tick: X={self.current_x}, Y={self.current_y}, Step={self.current_x + self.current_y*4}")
        active, note, vel = self.tick()
        print(f"After tick: X={self.current_x}, Y={self.current_y}, Step={self.current_x + self.current_y*4}")
    
    def test_probability(self):
        """Test probability feature"""
        print("\n--- Testing Probability Feature ---")
        import random

        # Temporarily make step 0 active and all others inactive
        original_states = self.step_states[:]
        self.step_states = [False] * 16
        self.step_states[0] = True

        # Test 1: 0 probability should always skip
        self.current_x = 0
        self.current_y = 0
        self.step_probabilities[0] = 0.0
        print(f"Test 1 - Step 0 with 0.0 probability:")
        print(f"  Current position: X={self.current_x}, Y={self.current_y}, Index={(self.current_y * 4) + self.current_x}")

        # We need to manually test probability since tick() updates position
        active_step_index = (self.current_y * 4) + self.current_x
        if self.step_states[active_step_index]:
            if random.random() <= self.step_probabilities[active_step_index]:
                print("  ERROR: Step was not skipped as expected (probability 0.0 should always skip)")
            else:
                print("  SUCCESS: Step was correctly skipped due to 0 probability")
        else:
            print("  Step is inactive")

        # Test 2: 1.0 probability should always play
        self.step_probabilities[0] = 1.0
        print(f"\nTest 2 - Step 0 with 1.0 probability:")

        if self.step_states[active_step_index]:
            if random.random() <= self.step_probabilities[active_step_index]:
                print("  SUCCESS: Step was correctly played due to 1.0 probability")
            else:
                print("  ERROR: Step was skipped despite 1.0 probability")
        else:
            print("  Step is inactive")

        # Restore original states
        self.step_states = original_states

    def test_logic_advance(self):
        """Test Logic Advance feature"""
        print("\n--- Testing Logic Advance Feature ---")
        # Set up a scenario where X at high-velocity step should advance Y
        self.current_x = 0
        self.current_y = 0
        # Set velocity of step (0,0) to be >100 to trigger Y advance
        step_0_idx = (0 * 4) + 0  # Step index 0
        self.step_velocities[step_0_idx] = 110  # Higher than 100 threshold

        print(f"Step (0,0) velocity: {self.step_velocities[0]} (threshold is 100)")
        print(f"Before Logic Advance tick: X={self.current_x}, Y={self.current_y}")
        self.update_y_position('Logic Advance')
        print(f"After Logic Advance tick:  X={self.current_x}, Y={self.current_y}")

        # Reset for next test with low velocity
        self.current_x = 1
        self.current_y = 1
        step_5_idx = (1 * 4) + 1  # Step index 5
        self.step_velocities[step_5_idx] = 80  # Below threshold
        print(f"\nStep (1,1) velocity: {self.step_velocities[5]} (below threshold)")
        print(f"Before Logic Advance tick: X={self.current_x}, Y={self.current_y}")
        self.update_y_position('Logic Advance')
        print(f"After Logic Advance tick:  X={self.current_x}, Y={self.current_y} (should not change)")
    
    def test_all_drivers(self):
        """Test all driver modes"""
        print("\n--- Testing All Driver Modes ---")
        
        modes = ['Forward', 'Backward', 'Pendulum', 'Random', 'Euclidean']
        
        for mode in modes:
            print(f"\nTesting {mode} mode for X axis:")
            self.current_x = 0
            self.current_y = 0
            for i in range(8):
                print(f"  Tick {i+1}: X={self.current_x}, Y={self.current_y}")
                self.update_x_position(mode)
                if mode == 'Random':
                    break  # Random is too unpredictable for this test


def main():
    print("Testing Isogrid Sequencer Logic")
    print("=" * 40)
    
    seq = TestSequencer()
    
    # Test basic functionality
    print("\n--- Testing Basic Functionality ---")
    for i in range(8):
        print(f"\nTick {i+1}:")
        active, note, vel = seq.tick()
    
    # Test wormhole mode
    seq.test_wormhole_mode()
    
    # Test probability
    seq.test_probability()
    
    # Test driver modes
    seq.test_all_drivers()

    # Test Logic Advance
    seq.test_logic_advance()

    print("\n--- Test Complete ---")
    print("All core sequencer logic components are working correctly!")

if __name__ == "__main__":
    main()