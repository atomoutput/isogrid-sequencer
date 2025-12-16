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
from kivy.clock import Clock
from kivy.graphics import Color, Line
import time
from midi_manager import MidiDriver

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
            # Bind long press to show step settings popup
            btn.bind(
                on_press=lambda btn, idx=i: self.on_step_press(idx),
                on_release=lambda btn, idx=i: self.on_step_release(idx)
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

        right_panel.add_widget(Label(text='X-Driver Mode:', color=(0.8, 0.6, 0.2, 1)))
        right_panel.add_widget(self.x_driver_spinner)
        right_panel.add_widget(Label(text='X-Speed:', color=(0.8, 0.6, 0.2, 1)))
        right_panel.add_widget(self.x_speed_spinner)
        right_panel.add_widget(self.cc_mapping_label)
        right_panel.add_widget(Label(text='X to CC:', color=(0.5, 0.8, 0.8, 1)))
        right_panel.add_widget(self.x_cc_spinner)
        right_panel.add_widget(Label(text='Y to CC:', color=(0.5, 0.8, 0.8, 1)))
        right_panel.add_widget(self.y_cc_spinner)

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

        # Start Sequencer Loop
        Clock.schedule_interval(self.tick, 0.125)  # 120 BPM default

        return main_layout

    def on_step_press(self, step_idx):
        # Handle step press for toggling activation
        self.step_states[step_idx] = not self.step_states[step_idx]
        if self.step_states[step_idx]:
            self.matrix_steps[step_idx].background_color = (0.5, 0.8, 0.5, 1)  # Green for active
        else:
            self.matrix_steps[step_idx].background_color = (0.2, 0.2, 0.2, 1)  # Back to dark gray

    def on_step_release(self, step_idx):
        # Could implement long press detection here to show settings
        pass

    def tick(self, dt):
        # Update X position based on X driver logic
        self.update_x_position()

        # Update Y position based on Y driver logic
        self.update_y_position()

        # Calculate the active step index
        active_step_index = (self.current_y * 4) + self.current_x

        # Visual feedback for active position
        self.visualize_active_position()

        # Send CC messages based on X/Y positions
        self.send_cc_messages()

        # Play the note at the intersection if step is enabled
        if self.step_states[active_step_index]:
            self.play_note_at_intersection(active_step_index)

    def update_x_position(self):
        speed_map = {'1/32': 0.25, '1/16': 0.5, '1/8': 1, '1/4': 2}
        speed_factor = speed_map[self.x_speed_spinner.text]

        # Simple forward movement for now - will expand to include all modes
        if self.x_driver_spinner.text == 'Forward':
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
        speed_map = {'1/32': 0.25, '1/16': 0.5, '1/8': 1, '1/4': 2}
        speed_factor = speed_map[self.y_speed_spinner.text]

        # Simple forward movement for now - will expand to include all modes
        if self.y_driver_spinner.text == 'Forward':
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

    def play_note_at_intersection(self, step_index):
        # Extract note value from button text (which shows note value)
        note_value = int(self.matrix_steps[step_index].text)

        # Use velocity based on X or Y position
        velocity = int(80 + (self.current_x * 15))  # Range from 80-125

        self.midi.send_note_on(note_value, velocity)
        # Schedule note off after a short duration
        Clock.schedule_once(lambda dt: self.midi.send_note_off(note_value), 0.1)

if __name__ == '__main__':
    SequencerApp().run()