from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
import time
from midi_manager import MidiDriver

class SequencerApp(App):
    def build(self):
        self.midi = MidiDriver()
        self.midi.setup()

        # Main layout with dark background
        main_layout = BoxLayout(orientation='vertical', canvas_color=(0.067, 0.067, 0.067, 1))  # #111111
        
        # Create 4x4 Grid for the Matrix
        matrix_layout = GridLayout(cols=4, size_hint_y=0.7)
        self.matrix_steps = []
        
        for i in range(16):  # 4x4
            btn = ToggleButton(
                text='',
                background_normal='', 
                background_color=(0.2, 0.2, 0.2, 1),  # Dark gray
                color=(0.5, 0.8, 0.8, 1)  # Cyan text highlight
            )
            matrix_layout.add_widget(btn)
            self.matrix_steps.append(btn)

        # Driver controls layout (X and Y)
        drivers_layout = BoxLayout(orientation='horizontal', size_hint_y=0.2)
        
        self.x_driver_btn = Button(
            text='X-Driver: Forward, 1/16',
            background_normal='',
            background_color=(0.8, 0.6, 0.2, 1)  # Amber
            )
        self.y_driver_btn = Button(
            text='Y-Driver: Forward, 1/16',
            background_normal='',
            background_color=(0.2, 0.8, 0.8, 1)  # Cyan
            )
        
        drivers_layout.add_widget(self.x_driver_btn)
        drivers_layout.add_widget(self.y_driver_btn)

        # Status label
        self.status_label = Label(
            text='Isogrid Sequencer Ready',
            size_hint_y=0.1,
            color=(0.5, 0.8, 0.8, 1)  # Cyan
        )

        # Add layouts to main layout
        main_layout.add_widget(matrix_layout)
        main_layout.add_widget(drivers_layout)
        main_layout.add_widget(self.status_label)

        # Initialize sequencer variables
        self.current_x = 0
        self.current_y = 0
        
        # Start Sequencer Loop (e.g., every 125ms for 120BPM)
        Clock.schedule_interval(self.tick, 0.125)
        
        return main_layout

    def tick(self, dt):
        # Update X position based on X driver logic
        self.update_x_position()
        
        # Update Y position based on Y driver logic
        self.update_y_position()
        
        # Calculate the active step index
        active_step_index = (self.current_y * 4) + self.current_x
        
        # Visual feedback for active position
        self.visualize_active_position()
        
        # Play the note at the intersection
        self.play_note_at_intersection(active_step_index)

    def update_x_position(self):
        # Simple forward movement for now - will expand to include all modes
        self.current_x = (self.current_x + 1) % 4

    def update_y_position(self):
        # Simple forward movement for now - will expand to include all modes
        self.current_y = (self.current_y + 1) % 4

    def visualize_active_position(self):
        # Reset all buttons to inactive state
        for btn in self.matrix_steps:
            btn.background_color = (0.2, 0.2, 0.2, 1)  # Dark gray
        
        # Highlight current position
        active_idx = (self.current_y * 4) + self.current_x
        self.matrix_steps[active_idx].background_color = (0.8, 0.6, 0.2, 1)  # Amber

        # Highlight row (Y axis)
        for x in range(4):
            idx = (self.current_y * 4) + x
            if self.matrix_steps[idx].background_color == (0.2, 0.2, 0.2, 1):
                self.matrix_steps[idx].background_color = (0.2, 0.5, 0.8, 1)  # Lighter blue

        # Highlight column (X axis)  
        for y in range(4):
            idx = (y * 4) + self.current_x
            if self.matrix_steps[idx].background_color == (0.2, 0.2, 0.2, 1):
                self.matrix_steps[idx].background_color = (0.2, 0.5, 0.8, 1)  # Lighter blue

        # Ensure intersection is amber
        self.matrix_steps[active_idx].background_color = (0.8, 0.6, 0.2, 1)  # Amber

    def play_note_at_intersection(self, step_index):
        # For now, play a simple note - this will connect to the MIDI manager
        note_value = 60 + step_index  # Starting from middle C
        self.midi.send_note_on(note_value)
        # Schedule note off after a short duration
        Clock.schedule_once(lambda dt: self.midi.send_note_off(note_value), 0.1)
        
if __name__ == '__main__':
    SequencerApp().run()