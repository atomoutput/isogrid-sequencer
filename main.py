from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.graphics import Color, Line
import time
import random
from midi_manager import MidiDriver

def euclidean_rhythm(steps, pulses):
    """Generate an Euclidean rhythm pattern with improved algorithm"""
    if steps <= 0:
        return []
    if pulses >= steps:
        return [True] * steps
    if pulses <= 0:
        return [False] * steps

    # Bresenham algorithm approach for Euclidean rhythms
    pattern = []
    error = 0

    for i in range(steps):
        error += pulses
        if error >= steps:
            pattern.append(True)
            error -= steps
        else:
            pattern.append(False)

    return pattern

class SequencerApp(App):
    def build(self):
        self.midi = MidiDriver()
        self.midi.setup()

        # Main layout with dark background
        main_layout = BoxLayout(orientation='horizontal')
        # Set background color to dark (Eurorack style)
        with main_layout.canvas.before:
            Color(0.067, 0.067, 0.067, 1)  # #111111 dark background
            self.rect = Rectangle(size=main_layout.size, pos=main_layout.pos)
            main_layout.bind(size=self._update_rect, pos=self._update_rect)

        # Left panel - Y Driver controls (The "Drivers" module)
        left_panel = BoxLayout(orientation='vertical', size_hint_x=0.2, padding=10, spacing=5)
        left_panel.add_widget(Label(text='Y-DRIVER', color=(0.2, 0.8, 0.8, 1), font_size=18, bold=True,
                                  canvas_color=(0.15, 0.15, 0.15, 1)))

        self.y_driver_spinner = Spinner(
            text='Forward',
            values=['Forward', 'Backward', 'Pendulum', 'Random', 'Euclidean', 'Logic Advance'],
            background_normal='',
            background_color=(0.2, 0.6, 0.8, 1),  # Cyan blue
            color=(0, 0, 0, 1)  # Black text for contrast
        )
        self.y_speed_spinner = Spinner(
            text='1/16',
            values=['1/32', '1/16', '1/8', '1/4'],
            background_normal='',
            background_color=(0.2, 0.6, 0.8, 1),  # Cyan blue
            color=(0, 0, 0, 1)  # Black text for contrast
        )

        left_panel.add_widget(Label(text='Mode:', color=(0.5, 0.8, 0.8, 1)))
        left_panel.add_widget(self.y_driver_spinner)
        left_panel.add_widget(Label(text='Speed:', color=(0.5, 0.8, 0.8, 1)))
        left_panel.add_widget(self.y_speed_spinner)

        # Center panel - 4x4 Matrix (The "Matrix" module)
        center_panel = FloatLayout(size_hint_x=0.6)
        matrix_layout = GridLayout(
            cols=4,
            size_hint=(None, None),
            width=min(center_panel.size[0]*0.8, 400),
            height=min(center_panel.size[1]*0.7, 400),
            pos_hint={'center_x': 0.5, 'center_y': 0.6}
        )
        self.matrix_steps = []

        for i in range(16):  # 4x4
            btn = ToggleButton(
                text=str(self.step_notes[i]),  # Show note value (starting from C2)
                background_normal='',
                background_color=(0.1, 0.1, 0.1, 1),  # Darker gray for inactive
                color=(0.5, 0.8, 0.8, 1),  # Cyan text highlight
                font_size=16,
                border=(2, 2, 2, 2)  # Add border for Eurorack style
            )
            # Store the step index in the button for later use
            btn.step_idx = i
            # Bind press events to track timing for long press
            btn.bind(
                on_press=self.on_step_press_with_timing,
                on_release=self.on_step_release_with_timing
            )
            matrix_layout.add_widget(btn)
            self.matrix_steps.append(btn)

        center_panel.add_widget(matrix_layout)

        # Horizontal line for X-axis visualization
        with center_panel.canvas:
            Color(0.8, 0.6, 0.2, 1)  # Amber for X-axis
            self.h_line = Line(points=[], width=3)

        # Vertical line for Y-axis visualization
        with center_panel.canvas:
            Color(0.2, 0.8, 0.8, 1)  # Cyan for Y-axis
            self.v_line = Line(points=[], width=3)

        # Right panel - X Driver controls and MicroFreak control center
        right_panel = BoxLayout(orientation='vertical', size_hint_x=0.2, padding=10, spacing=5)

        # X Driver controls
        right_panel.add_widget(Label(text='X-DRIVER', color=(0.8, 0.6, 0.2, 1), font_size=18, bold=True))
        self.x_driver_spinner = Spinner(
            text='Forward',
            values=['Forward', 'Backward', 'Pendulum', 'Random', 'Euclidean'],
            background_normal='',
            background_color=(0.8, 0.6, 0.2, 1),  # Amber
            color=(0, 0, 0, 1)  # Black text for contrast
        )
        self.x_speed_spinner = Spinner(
            text='1/16',
            values=['1/32', '1/16', '1/8', '1/4'],
            background_normal='',
            background_color=(0.8, 0.6, 0.2, 1),  # Amber
            color=(0, 0, 0, 1)  # Black text for contrast
        )

        right_panel.add_widget(Label(text='Mode:', color=(0.8, 0.6, 0.2, 1)))
        right_panel.add_widget(self.x_driver_spinner)
        right_panel.add_widget(Label(text='Speed:', color=(0.8, 0.6, 0.2, 1)))
        right_panel.add_widget(self.x_speed_spinner)

        # MicroFreak Control Center
        right_panel.add_widget(Label(text='MICROFREAK CTRL', color=(0.5, 0.8, 0.8, 1), font_size=18, bold=True))

        # CC mapping controls
        self.x_cc_spinner = Spinner(
            text='None',
            values=['None', 'Cutoff (23)', 'Resonance (83)', 'Osc Type (9)', 'Wave (10)', 'Timbre (12)', 'Shape (13)', 'Glide (5)'],
            background_normal='',
            background_color=(0.2, 0.8, 0.8, 1),  # Cyan
            color=(0, 0, 0, 1)  # Black text for contrast
        )
        self.y_cc_spinner = Spinner(
            text='None',
            values=['None', 'Cutoff (23)', 'Resonance (83)', 'Osc Type (9)', 'Wave (10)', 'Timbre (12)', 'Shape (13)', 'Glide (5)'],
            background_normal='',
            background_color=(0.2, 0.8, 0.8, 1),  # Cyan
            color=(0, 0, 0, 1)  # Black text for contrast
        )

        right_panel.add_widget(Label(text='X to CC:', color=(0.5, 0.8, 0.8, 1)))
        right_panel.add_widget(self.x_cc_spinner)
        right_panel.add_widget(Label(text='Y to CC:', color=(0.5, 0.8, 0.8, 1)))
        right_panel.add_widget(self.y_cc_spinner)

        # Performance controls
        self.tempo_label = Label(text='Tempo: 120 BPM', color=(0.5, 0.8, 0.8, 1))
        self.tempo_slider = Slider(min=40, max=240, value=120, step=1)
        self.tempo_slider.bind(value=self.on_tempo_change)

        # Play controls
        self.play_button = Button(text='PLAY', background_normal='', background_color=(0.2, 0.8, 0.2, 1), color=(0, 0, 0, 1))
        self.play_button.bind(on_press=self.toggle_play_state)
        self.is_playing = True  # Start playing by default

        right_panel.add_widget(self.tempo_label)
        right_panel.add_widget(self.tempo_slider)
        right_panel.add_widget(self.play_button)

        # Add panels to main layout
        main_layout.add_widget(left_panel)
        main_layout.add_widget(center_panel)
        main_layout.add_widget(right_panel)

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

        # Start Sequencer Loop at 120 BPM (16th notes = 480 BPM, so interval = 60/480 = 0.125s)
        interval = 60.0 / 120.0 / 4.0  # 120 BPM, 16th note interval
        Clock.schedule_interval(self.tick, interval)

        # Add callback to update the rectangle when the layout size changes
        main_layout.bind(size=self._update_rect, pos=self._update_rect)
        return main_layout

    def _update_rect(self, *args):
        """Update the background rectangle when layout changes"""
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_step_press_with_timing(self, button):
        # Record the time when button was pressed
        button.press_time = time.time()
        # Use the button's stored index
        step_idx = button.step_idx
        # Temporarily store the button reference to check in release
        self.current_pressed_button = button

    def on_step_release_with_timing(self, button):
        # Calculate press duration
        press_duration = time.time() - button.press_time
        step_idx = button.step_idx

        # If press duration was long enough, show config popup
        if press_duration > 0.5:  # 0.5 seconds for long press
            self.show_step_config(step_idx)
        else:
            # Regular press: toggle activation
            self.step_states[step_idx] = not self.step_states[step_idx]
            if self.step_states[step_idx]:
                self.matrix_steps[step_idx].background_color = (0.5, 0.8, 0.5, 1)  # Green for active
            else:
                self.matrix_steps[step_idx].background_color = (0.2, 0.2, 0.2, 1)  # Back to dark gray

    def show_step_config(self, step_idx):
        """Show the step configuration popup"""
        # Create a base layout with dark background
        base_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        with base_layout.canvas.before:
            Color(0.067, 0.067, 0.067, 1)  # Dark background
            base_rect = Rectangle(size=base_layout.size, pos=base_layout.pos)
            base_layout.bind(size=lambda *args: setattr(base_rect, 'size', base_layout.size),
                           pos=lambda *args: setattr(base_rect, 'pos', base_layout.pos))

        # Inner grid layout for controls
        layout = GridLayout(cols=2, padding=10, spacing=10)

        # Note selection
        layout.add_widget(Label(text='Note:', color=(0.5, 0.8, 0.8, 1), size_hint_y=None, height=40))
        note_spinner = Spinner(
            text=str(self.step_notes[step_idx]),
            values=[str(i) for i in range(12, 120)],  # MIDI note range
            background_normal='',
            background_color=(0.2, 0.6, 0.8, 1),  # Cyan blue
            color=(0, 0, 0, 1),  # Black text for contrast
            size_hint_y=None,
            height=40
        )
        layout.add_widget(note_spinner)

        # Velocity slider
        layout.add_widget(Label(text='Velocity:', color=(0.5, 0.8, 0.8, 1), size_hint_y=None, height=40))
        velocity_slider = Slider(min=1, max=127, value=self.step_velocities[step_idx], size_hint_y=None, height=40)
        layout.add_widget(velocity_slider)

        # Probability slider
        layout.add_widget(Label(text='Probability:', color=(0.5, 0.8, 0.8, 1), size_hint_y=None, height=40))
        prob_slider = Slider(min=0, max=1, value=self.step_probabilities[step_idx], step=0.01, size_hint_y=None, height=40)
        layout.add_widget(prob_slider)

        # CC Lock controls
        layout.add_widget(Label(text='CC Lock:', color=(0.5, 0.8, 0.8, 1), size_hint_y=None, height=40))
        cc_lock_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=80)

        # CC number input
        cc_num_spinner = Spinner(
            text=str(list(self.step_cc_values[step_idx].keys())[0]) if self.step_cc_values[step_idx] else "None",
            values=["None"] + [str(i) for i in range(128)],  # MIDI CC range
            background_normal='',
            background_color=(0.2, 0.8, 0.8, 1),  # Cyan
            color=(0, 0, 0, 1),  # Black text for contrast
            size_hint_y=None,
            height=40
        )
        cc_lock_layout.add_widget(cc_num_spinner)

        # CC value slider
        cc_val_slider = Slider(min=0, max=127, value=list(self.step_cc_values[step_idx].values())[0] if self.step_cc_values[step_idx] else 64, size_hint_y=None, height=40)
        cc_lock_layout.add_widget(cc_val_slider)

        layout.add_widget(cc_lock_layout)

        # Teleport target (for wormhole mode)
        layout.add_widget(Label(text='Teleport to:', color=(0.5, 0.8, 0.8, 1), size_hint_y=None, height=40))
        teleport_spinner = Spinner(
            text=str(self.step_teleport_targets[step_idx]) if self.step_teleport_targets[step_idx] != -1 else "None",
            values=["-1 (None)"] + [str(i) for i in range(16)],
            background_normal='',
            background_color=(0.2, 0.8, 0.8, 1),  # Cyan
            color=(0, 0, 0, 1),  # Black text for contrast
            size_hint_y=None,
            height=40
        )
        layout.add_widget(teleport_spinner)

        # Button layout
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)

        # Save button
        def save_and_close(instance):
            try:
                # Bounds checking before updating
                if 0 <= step_idx < len(self.step_notes):
                    self.step_notes[step_idx] = int(note_spinner.text)
                if 0 <= step_idx < len(self.step_velocities):
                    self.step_velocities[step_idx] = int(velocity_slider.value)
                if 0 <= step_idx < len(self.step_probabilities):
                    self.step_probabilities[step_idx] = prob_slider.value

                # Handle CC lock values
                if cc_num_spinner.text != "None":
                    cc_num = int(cc_num_spinner.text)
                    cc_val = int(cc_val_slider.value)
                    if 0 <= step_idx < len(self.step_cc_values):
                        self.step_cc_values[step_idx] = {cc_num: cc_val}
                else:
                    if 0 <= step_idx < len(self.step_cc_values):
                        self.step_cc_values[step_idx] = {}

                # Handle teleport target
                if teleport_spinner.text == "None" or teleport_spinner.text == "-1 (None)":
                    if 0 <= step_idx < len(self.step_teleport_targets):
                        self.step_teleport_targets[step_idx] = -1
                else:
                    teleport_target = int(teleport_spinner.text)
                    # Validate teleport target is within valid range
                    if 0 <= teleport_target < 16 and 0 <= step_idx < len(self.step_teleport_targets):
                        self.step_teleport_targets[step_idx] = teleport_target
                    elif 0 <= step_idx < len(self.step_teleport_targets):
                        self.step_teleport_targets[step_idx] = -1  # Default to no teleport if invalid

                # Update button text to show note value
                if 0 <= step_idx < len(self.matrix_steps):
                    self.matrix_steps[step_idx].text = str(self.step_notes[step_idx])
                popup.dismiss()
            except ValueError as e:
                print(f"[ERROR] Invalid value in step configuration: {str(e)}")
                # Could show an error popup here
            except Exception as e:
                print(f"[ERROR] Unexpected error saving step configuration: {str(e)}")

        save_btn = Button(text='Save', background_normal='', background_color=(0.2, 0.8, 0.2, 1), color=(0, 0, 0, 1), size_hint_x=0.5)
        save_btn.bind(on_press=save_and_close)

        # Cancel button
        cancel_btn = Button(text='Cancel', background_normal='', background_color=(0.8, 0.2, 0.2, 1), color=(0, 0, 0, 1), size_hint_x=0.5)
        cancel_btn.bind(on_press=lambda x: popup.dismiss())

        button_layout.add_widget(save_btn)
        button_layout.add_widget(cancel_btn)

        # Add the grid layout and button layout to the base layout
        base_layout.add_widget(layout)
        base_layout.add_widget(button_layout)

        popup = Popup(title=f'STEP {step_idx} CONFIGURATION',
                     content=base_layout,
                     size_hint=(0.8, 0.8),
                     background_color=(0.067, 0.067, 0.067, 1))
        popup.open()

    def tick(self, dt):
        # Only update if playing
        if not self.is_playing:
            return

        # Update X position based on X driver logic
        self.update_x_position()

        # Update Y position based on Y driver logic
        self.update_y_position()

        # Calculate the active step index
        active_step_index = (self.current_y * 4) + self.current_x

        # Bounds checking for step index
        if active_step_index < 0 or active_step_index >= len(self.step_teleport_targets):
            print(f"[ERROR] Active step index out of bounds: {active_step_index}")
            return

        # Check for wormhole teleportation
        if self.step_teleport_targets[active_step_index] != -1:
            # Teleport to the target step immediately
            teleport_target = self.step_teleport_targets[active_step_index]
            if 0 <= teleport_target < 16:  # Validate teleport target
                active_step_index = teleport_target
                # Update current X and Y based on new step index
                self.current_x = active_step_index % 4
                self.current_y = active_step_index // 4
            else:
                print(f"[WARNING] Invalid teleport target: {teleport_target}")

        # Visual feedback for active position
        self.visualize_active_position()

        # Send CC messages based on X/Y positions
        self.send_cc_messages()

        # Bounds checking for step states
        if active_step_index < len(self.step_states) and self.step_states[active_step_index]:
            # Check probability - if random value is higher than step probability, skip
            if active_step_index < len(self.step_probabilities) and random.random() <= self.step_probabilities[active_step_index]:
                self.play_note_at_intersection(active_step_index)

    def update_x_position(self):
        # Handle Euclidean rhythm for X axis
        if self.x_driver_spinner.text == 'Euclidean':
            # Generate Euclidean rhythm pattern based on current settings
            self.euclidean_x_steps = getattr(self, 'euclidean_x_steps', euclidean_rhythm(4, 2))  # Default 4 steps, 2 pulses
            self.euclidean_x_index = getattr(self, 'euclidean_x_index', 0)

            if self.euclidean_x_steps[self.euclidean_x_index]:
                # Only move if this step is active in the Euclidean pattern
                self.current_x = (self.current_x + 1) % 4
            self.euclidean_x_index = (self.euclidean_x_index + 1) % len(self.euclidean_x_steps)
        elif self.x_driver_spinner.text == 'Random':
            self.current_x = random.randint(0, 3)
        elif self.x_driver_spinner.text == 'Forward':
            self.current_x = (self.current_x + 1) % 4
        elif self.x_driver_spinner.text == 'Backward':
            self.current_x = (self.current_x - 1) % 4
        elif self.x_driver_spinner.text == 'Pendulum':
            self.current_x += self.x_direction
            if self.current_x >= 3:
                self.x_direction = -1
            elif self.current_x <= 0:
                self.x_direction = 1
            if self.current_x < 0:
                self.current_x = 0
            elif self.current_x > 3:
                self.current_x = 3

    def update_y_position(self):
        # Handle Euclidean rhythm for Y axis
        if self.y_driver_spinner.text == 'Euclidean':
            # Generate Euclidean rhythm pattern based on current settings
            self.euclidean_y_steps = getattr(self, 'euclidean_y_steps', euclidean_rhythm(4, 3))  # Default 4 steps, 3 pulses
            self.euclidean_y_index = getattr(self, 'euclidean_y_index', 0)

            if self.euclidean_y_steps[self.euclidean_y_index]:
                # Only move if this step is active in the Euclidean pattern
                self.current_y = (self.current_y + 1) % 4
            self.euclidean_y_index = (self.euclidean_y_index + 1) % len(self.euclidean_y_steps)
        elif self.y_driver_spinner.text == 'Random':
            self.current_y = random.randint(0, 3)
        elif self.y_driver_spinner.text == 'Forward':
            self.current_y = (self.current_y + 1) % 4
        elif self.y_driver_spinner.text == 'Backward':
            self.current_y = (self.current_y - 1) % 4
        elif self.y_driver_spinner.text == 'Pendulum':
            self.current_y += self.y_direction
            if self.current_y >= 3:
                self.y_direction = -1
            elif self.current_y <= 0:
                self.y_direction = 1
            if self.current_y < 0:
                self.current_y = 0
            elif self.current_y > 3:
                self.current_y = 3
        elif self.y_driver_spinner.text == 'Logic Advance':
            # Only advance Y if X position is at a high-velocity step (velocity > 100)
            # Get the current X position step index for the current Y row
            x_step_index = (self.current_y * 4) + self.current_x
            # Add bounds checking
            if 0 <= x_step_index < len(self.step_velocities) and self.step_velocities[x_step_index] > 100:
                self.current_y = (self.current_y + 1) % 4

    def visualize_active_position(self):
        # Ensure we have the right number of matrix steps
        if len(self.matrix_steps) != 16 or len(self.step_states) != 16:
            print("[ERROR] Matrix steps and step states have incorrect lengths")
            return

        # Reset all buttons to inactive state
        for i, btn in enumerate(self.matrix_steps):
            if 0 <= i < len(self.step_states):
                if self.step_states[i]:
                    btn.background_color = (0.15, 0.15, 0.15, 1)  # Dark gray for inactive steps that are enabled
                else:
                    btn.background_color = (0.1, 0.1, 0.1, 1)  # Even darker for inactive steps

        # Calculate and validate active position
        active_idx = (self.current_y * 4) + self.current_x
        if not (0 <= active_idx < len(self.matrix_steps)):
            print(f"[ERROR] Active index out of bounds: {active_idx}")
            return

        # Highlight current position with amber
        self.matrix_steps[active_idx].background_color = (0.8, 0.6, 0.2, 1)  # Amber

        # Highlight current row (Y axis) with cyan
        for x in range(4):
            idx = (self.current_y * 4) + x
            if 0 <= idx < len(self.matrix_steps) and 0 <= idx < len(self.step_states):
                if self.step_states[idx]:
                    if idx != active_idx:  # Don't override the active position color
                        self.matrix_steps[idx].background_color = (0.2, 0.8, 0.8, 0.7)  # Cyan for active row
                else:
                    if idx != active_idx:
                        self.matrix_steps[idx].background_color = (0.1, 0.1, 0.1, 0.5)  # Partially highlighted for row

        # Highlight current column (X axis) with cyan
        for y in range(4):
            idx = (y * 4) + self.current_x
            if 0 <= idx < len(self.matrix_steps) and 0 <= idx < len(self.step_states):
                if self.step_states[idx]:
                    if idx != active_idx and self.matrix_steps[idx].background_color != (0.2, 0.8, 0.8, 0.7):  # Don't override row highlight
                        self.matrix_steps[idx].background_color = (0.2, 0.8, 0.8, 0.7)  # Cyan for active column
                else:
                    if idx != active_idx and self.matrix_steps[idx].background_color != (0.1, 0.1, 0.1, 0.5):
                        self.matrix_steps[idx].background_color = (0.1, 0.1, 0.1, 0.5)  # Partially highlighted for column

        # Ensure intersection is amber
        if 0 <= active_idx < len(self.matrix_steps):
            self.matrix_steps[active_idx].background_color = (0.8, 0.6, 0.2, 1)  # Amber

    def send_cc_messages(self):
        # Map X position to selected CC
        x_cc_map = {
            'None': None,
            'Cutoff (23)': 23,
            'Resonance (83)': 83,
            'Osc Type (9)': 9,
            'Wave (10)': 10,
            'Timbre (12)': 12,
            'Shape (13)': 13,
            'Glide (5)': 5
        }

        # Add bounds checking for spinner text
        if hasattr(self, 'x_cc_spinner') and self.x_cc_spinner.text in x_cc_map:
            x_cc = x_cc_map[self.x_cc_spinner.text]
            if x_cc is not None:
                # Ensure current_x is not 0 to avoid division by zero when denominator is 3
                cc_value = int((self.current_x / 3) * 127) if 3 != 0 else 0  # Scale to 0-127
                self.midi.send_cc(x_cc, cc_value)

        # Map Y position to selected CC
        y_cc_map = {
            'None': None,
            'Cutoff (23)': 23,
            'Resonance (83)': 83,
            'Osc Type (9)': 9,
            'Wave (10)': 10,
            'Timbre (12)': 12,
            'Shape (13)': 13,
            'Glide (5)': 5
        }

        # Add bounds checking for spinner text
        if hasattr(self, 'y_cc_spinner') and self.y_cc_spinner.text in y_cc_map:
            y_cc = y_cc_map[self.y_cc_spinner.text]
            if y_cc is not None:
                # Ensure current_y is not 0 to avoid division by zero when denominator is 3
                cc_value = int((self.current_y / 3) * 127) if 3 != 0 else 0  # Scale to 0-127
                self.midi.send_cc(y_cc, cc_value)

    def on_tempo_change(self, slider, value):
        """Handle tempo change"""
        tempo = max(1, int(value))  # Ensure tempo is at least 1 to avoid division by zero
        self.tempo_label.text = f'Tempo: {tempo} BPM'

        # Update the clock interval based on tempo
        # For 16th notes: interval = 60 / BPM / 4
        interval = 60.0 / tempo / 4.0
        Clock.unschedule(self.tick)
        Clock.schedule_interval(self.tick, interval)

    def toggle_play_state(self, instance):
        """Toggle play/pause state"""
        self.is_playing = not self.is_playing
        if self.is_playing:
            instance.text = 'PLAY'
            instance.background_color = (0.2, 0.8, 0.2, 1)  # Green
        else:
            instance.text = 'PAUSE'
            instance.background_color = (0.8, 0.2, 0.2, 1)  # Red

    def play_note_at_intersection(self, step_index):
        # Bounds checking for step index
        if step_index < 0 or step_index >= len(self.step_notes):
            print(f"[ERROR] Step index out of bounds in play_note_at_intersection: {step_index}")
            return

        # Use the step-specific note value, velocity and CC values
        note_value = self.step_notes[step_index]
        velocity = self.step_velocities[step_index]

        # Apply parameter lock if any CC values are set for this step
        if 0 <= step_index < len(self.step_cc_values) and self.step_cc_values[step_index]:
            for cc_num, cc_val in self.step_cc_values[step_index].items():
                self.midi.send_cc(cc_num, cc_val)

        self.midi.send_note_on(note_value, velocity)
        # Schedule note off after a short duration
        Clock.schedule_once(lambda dt: self.midi.send_note_off(note_value), 0.1)

if __name__ == '__main__':
    SequencerApp().run()