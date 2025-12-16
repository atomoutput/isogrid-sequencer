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

class SequencerApp(App):
    def build(self):
        self.midi = MidiDriver()
        self.midi.setup()

        # Main layout with dark background
        main_layout = BoxLayout(orientation='horizontal', canvas_color=(0.067, 0.067, 0.067, 1))  # #111111

        # Left panel - Y Driver controls
        left_panel = BoxLayout(orientation='vertical', size_hint_x=0.2)
        self.y_driver_spinner = Spinner(
            text='Forward',
            values=['Forward', 'Backward', 'Pendulum', 'Random', 'Euclidean'],
            background_normal='',
            background_color=(0.2, 0.8, 0.8, 1)  # Cyan
        )
        self.y_speed_spinner = Spinner(
            text='1/16',
            values=['1/32', '1/16', '1/8', '1/4'],
            background_normal='',
            background_color=(0.2, 0.8, 0.8, 1)  # Cyan
        )
        left_panel.add_widget(Label(text='Y-Driver Mode:', color=(0.2, 0.8, 0.8, 1)))
        left_panel.add_widget(self.y_driver_spinner)
        left_panel.add_widget(Label(text='Y-Speed:', color=(0.2, 0.8, 0.8, 1)))
        left_panel.add_widget(self.y_speed_spinner)

        # Center panel - 4x4 Matrix
        center_panel = FloatLayout(size_hint_x=0.6)
        matrix_layout = GridLayout(
            cols=4,
            size_hint=(None, None),
            width=400,
            height=400,
            pos_hint={'center_x': 0.5, 'center_y': 0.6}
        )
        self.matrix_steps = []

        for i in range(16):  # 4x4
            btn = ToggleButton(
                text=str(i%12 + 36),  # Show note value (starting from C2)
                background_normal='',
                background_color=(0.2, 0.2, 0.2, 1),  # Dark gray
                color=(0.5, 0.8, 0.8, 1),  # Cyan text highlight
                font_size=14
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
            Color(0.2, 0.5, 0.8, 1)  # Cyan for X-axis
            self.h_line = Line(points=[], width=2)

        # Vertical line for Y-axis visualization
        with center_panel.canvas:
            Color(0.8, 0.5, 0.2, 1)  # Amber for Y-axis
            self.v_line = Line(points=[], width=2)

        # Right panel - X Driver controls and MicroFreak mapping
        right_panel = BoxLayout(orientation='vertical', size_hint_x=0.2)
        self.x_driver_spinner = Spinner(
            text='Forward',
            values=['Forward', 'Backward', 'Pendulum', 'Random', 'Euclidean'],
            background_normal='',
            background_color=(0.8, 0.6, 0.2, 1)  # Amber
        )
        self.x_speed_spinner = Spinner(
            text='1/16',
            values=['1/32', '1/16', '1/8', '1/4'],
            background_normal='',
            background_color=(0.8, 0.6, 0.2, 1)  # Amber
        )

        # Y Driver with Logic Advance option
        self.y_driver_spinner = Spinner(
            text='Forward',
            values=['Forward', 'Backward', 'Pendulum', 'Random', 'Euclidean', 'Logic Advance'],
            background_normal='',
            background_color=(0.2, 0.8, 0.8, 1)  # Cyan
        )
        self.y_speed_spinner = Spinner(
            text='1/16',
            values=['1/32', '1/16', '1/8', '1/4'],
            background_normal='',
            background_color=(0.2, 0.8, 0.8, 1)  # Cyan
        )

        # MicroFreak CC mapping controls
        self.cc_mapping_label = Label(text='CC Mapping', color=(0.5, 0.8, 0.8, 1))
        self.x_cc_spinner = Spinner(
            text='None',
            values=['None', 'Cutoff (23)', 'Resonance (83)', 'Osc Type (9)', 'Wave (10)', 'Timbre (12)', 'Shape (13)', 'Glide (5)'],
            background_normal='',
            background_color=(0.2, 0.8, 0.8, 1)  # Cyan
        )
        self.y_cc_spinner = Spinner(
            text='None',
            values=['None', 'Cutoff (23)', 'Resonance (83)', 'Osc Type (9)', 'Wave (10)', 'Timbre (12)', 'Shape (13)', 'Glide (5)'],
            background_normal='',
            background_color=(0.2, 0.8, 0.8, 1)  # Cyan
        )

        # Performance controls
        self.tempo_label = Label(text='Tempo: 120 BPM', color=(0.5, 0.8, 0.8, 1))
        self.tempo_slider = Slider(min=40, max=240, value=120, step=1)
        self.tempo_slider.bind(value=self.on_tempo_change)

        # Play controls
        self.play_button = Button(text='PLAY', background_normal='', background_color=(0.2, 0.8, 0.2, 1))
        self.play_button.bind(on_press=self.toggle_play_state)
        self.is_playing = True  # Start playing by default

        right_panel.add_widget(Label(text='X-Driver Mode:', color=(0.8, 0.6, 0.2, 1)))
        right_panel.add_widget(self.x_driver_spinner)
        right_panel.add_widget(Label(text='X-Speed:', color=(0.8, 0.6, 0.2, 1)))
        right_panel.add_widget(self.x_speed_spinner)
        right_panel.add_widget(Label(text='Y-Driver Mode:', color=(0.2, 0.8, 0.8, 1)))
        right_panel.add_widget(self.y_driver_spinner)
        right_panel.add_widget(Label(text='Y-Speed:', color=(0.2, 0.8, 0.8, 1)))
        right_panel.add_widget(self.y_speed_spinner)
        right_panel.add_widget(self.cc_mapping_label)
        right_panel.add_widget(Label(text='X to CC:', color=(0.5, 0.8, 0.8, 1)))
        right_panel.add_widget(self.x_cc_spinner)
        right_panel.add_widget(Label(text='Y to CC:', color=(0.5, 0.8, 0.8, 1)))
        right_panel.add_widget(self.y_cc_spinner)
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

        return main_layout

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
        layout = GridLayout(cols=2, padding=10, spacing=10)

        # Note selection
        layout.add_widget(Label(text='Note:', color=(0.5, 0.8, 0.8, 1)))
        note_spinner = Spinner(
            text=str(self.step_notes[step_idx]),
            values=[str(i) for i in range(12, 120)],  # MIDI note range
            background_normal='',
            background_color=(0.2, 0.8, 0.8, 1)
        )
        layout.add_widget(note_spinner)

        # Velocity slider
        layout.add_widget(Label(text='Velocity:', color=(0.5, 0.8, 0.8, 1)))
        velocity_slider = Slider(min=1, max=127, value=self.step_velocities[step_idx])
        layout.add_widget(velocity_slider)

        # Probability slider
        layout.add_widget(Label(text='Probability:', color=(0.5, 0.8, 0.8, 1)))
        prob_slider = Slider(min=0, max=1, value=self.step_probabilities[step_idx], step=0.01)
        layout.add_widget(prob_slider)

        # CC Lock controls
        layout.add_widget(Label(text='CC Lock:', color=(0.5, 0.8, 0.8, 1)))
        cc_lock_layout = BoxLayout(orientation='vertical')

        # CC number input
        cc_num_spinner = Spinner(
            text=str(list(self.step_cc_values[step_idx].keys())[0]) if self.step_cc_values[step_idx] else "None",
            values=["None"] + [str(i) for i in range(128)],  # MIDI CC range
            background_normal='',
            background_color=(0.2, 0.8, 0.8, 1)
        )
        cc_lock_layout.add_widget(cc_num_spinner)

        # CC value slider
        cc_val_slider = Slider(min=0, max=127, value=list(self.step_cc_values[step_idx].values())[0] if self.step_cc_values[step_idx] else 64)
        cc_lock_layout.add_widget(cc_val_slider)

        layout.add_widget(cc_lock_layout)

        # Teleport target (for wormhole mode)
        layout.add_widget(Label(text='Teleport to:', color=(0.5, 0.8, 0.8, 1)))
        teleport_spinner = Spinner(
            text=str(self.step_teleport_targets[step_idx]) if self.step_teleport_targets[step_idx] != -1 else "None",
            values=["-1 (None)"] + [str(i) for i in range(16)],
            background_normal='',
            background_color=(0.2, 0.8, 0.8, 1)
        )
        layout.add_widget(teleport_spinner)

        # Save button
        def save_and_close(instance):
            self.step_notes[step_idx] = int(note_spinner.text)
            self.step_velocities[step_idx] = int(velocity_slider.value)
            self.step_probabilities[step_idx] = prob_slider.value

            # Handle CC lock values
            if cc_num_spinner.text != "None":
                cc_num = int(cc_num_spinner.text)
                cc_val = int(cc_val_slider.value)
                self.step_cc_values[step_idx] = {cc_num: cc_val}
            else:
                self.step_cc_values[step_idx] = {}

            # Handle teleport target
            if teleport_spinner.text == "None" or teleport_spinner.text == "-1 (None)":
                self.step_teleport_targets[step_idx] = -1
            else:
                self.step_teleport_targets[step_idx] = int(teleport_spinner.text)

            # Update button text to show note value
            self.matrix_steps[step_idx].text = str(self.step_notes[step_idx])
            popup.dismiss()

        save_btn = Button(text='Save', background_normal='', background_color=(0.8, 0.6, 0.2, 1))
        save_btn.bind(on_press=save_and_close)
        layout.add_widget(save_btn)

        # Cancel button
        cancel_btn = Button(text='Cancel', background_normal='', background_color=(0.8, 0.2, 0.2, 1))
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        layout.add_widget(cancel_btn)

        popup = Popup(title=f'Step {step_idx} Configuration', content=layout, size_hint=(0.8, 0.8))
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

        # Check for wormhole teleportation
        if self.step_teleport_targets[active_step_index] != -1:
            # Teleport to the target step immediately
            active_step_index = self.step_teleport_targets[active_step_index]
            # Update current X and Y based on new step index
            self.current_x = active_step_index % 4
            self.current_y = active_step_index // 4

        # Visual feedback for active position
        self.visualize_active_position()

        # Send CC messages based on X/Y positions
        self.send_cc_messages()

        # Play the note at the intersection if step is enabled
        if self.step_states[active_step_index]:
            # Check probability - if random value is higher than step probability, skip
            if random.random() <= self.step_probabilities[active_step_index]:
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
            if self.step_velocities[x_step_index] > 100:
                self.current_y = (self.current_y + 1) % 4

    def visualize_active_position(self):
        # Reset all buttons to inactive state
        for i, btn in enumerate(self.matrix_steps):
            if self.step_states[i]:
                btn.background_color = (0.5, 0.8, 0.5, 1)  # Green for active steps
            else:
                btn.background_color = (0.2, 0.2, 0.2, 1)  # Dark gray for inactive

        # Highlight current position with amber
        active_idx = (self.current_y * 4) + self.current_x
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

        x_cc = x_cc_map[self.x_cc_spinner.text]
        if x_cc is not None:
            cc_value = int((self.current_x / 3) * 127)  # Scale to 0-127
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

        y_cc = y_cc_map[self.y_cc_spinner.text]
        if y_cc is not None:
            cc_value = int((self.current_y / 3) * 127)  # Scale to 0-127
            self.midi.send_cc(y_cc, cc_value)

    def on_tempo_change(self, slider, value):
        """Handle tempo change"""
        tempo = int(value)
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
        # Use the step-specific note value, velocity and CC values
        note_value = self.step_notes[step_index]
        velocity = self.step_velocities[step_index]

        # Apply parameter lock if any CC values are set for this step
        if self.step_cc_values[step_index]:
            for cc_num, cc_val in self.step_cc_values[step_index].items():
                self.midi.send_cc(cc_num, cc_val)

        self.midi.send_note_on(note_value, velocity)
        # Schedule note off after a short duration
        Clock.schedule_once(lambda dt: self.midi.send_note_off(note_value), 0.1)

if __name__ == '__main__':
    SequencerApp().run()