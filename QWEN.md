
**Environment:** Termux (Local Dev) + GitHub Actions (Cloud Build)
**Stack:** Python 3, Kivy, Pyjnius, Buildozer

## Phase 1: Termux Environment Setup
*Goal: Configure Termux for coding and local UI testing (without compiling the APK).*

1.  **Update & Install Core Tools:**
    ```bash
    pkg update && pkg upgrade
    pkg install -y python git libtool pkg-config clang binutils
    ```

2.  **Install Graphical Environment (Termux-X11):**
    This allows you to run the app window on your phone screen to test the UI logic before building the APK.
    *   Install the **Termux-X11** app (from GitHub Releases).
    *   In Termux terminal:
    ```bash
    pkg install x11-repo
    pkg install termux-x11-nightly
    ```

3.  **Install Kivy & Buildozer (Python Libraries):**
    ```bash
    # Install dependencies for Kivy compilation
    pkg install libjpeg-turbo freetype
    
    # Install Kivy
    LDFLAGS="-lm -lcompiler_rt" pip install kivy
    
    # Install Buildozer (used only to generate config, not to build)
    pip install buildozer
    ```

## Phase 2: Project Architecture
*Goal: Separate the logic so the app runs in Termux (Mock Mode) and as an APK (Real Mode).*

**Directory Structure:**
```text
midi_sequencer/
├── .github/
│   └── workflows/
│       └── build.yml      # CI/CD Configuration
├── main.py                # UI & Sequencer Loop
├── midi_manager.py        # Handles Android Native MIDI vs Mock
├── buildozer.spec         # App Packaging Config
└── icon.png               # App Icon
```

## Phase 3: Development & Logic

### 1. The MIDI Backend (`midi_manager.py`)
Since Termux cannot access `android.media.midi` directly, we write a wrapper.

```python
from kivy.utils import platform

class MidiDriver:
    def __init__(self):
        self.device = None
        self.input_port = None
        
    def setup(self):
        if platform == 'android':
            self._setup_android()
        else:
            print("[MOCK] MIDI Setup Complete (Simulation Mode)")

    def _setup_android(self):
        from jnius import autoclass
        # Get Android Context & MIDI Service
        Context = autoclass('android.content.Context')
        activity = autoclass('org.kivy.android.PythonActivity').mActivity
        midi_service = activity.getSystemService(Context.MIDI_SERVICE)
        
        # Simplified: Open first available device
        devices = midi_service.getDevices()
        if devices.length > 0:
            midi_service.openDevice(devices[0], self._on_device_open, None)

    def _on_device_open(self, device):
        self.device = device
        self.input_port = device.openInputPort(0)

    def send_note_on(self, note, velocity=127):
        if self.input_port:
            # 0x90 = Note On, Channel 1
            data = [0x90, note, velocity]
            self.input_port.send(bytearray(data), 0, 3)
        else:
            print(f"[MOCK] Note ON: {note}")

    def send_note_off(self, note):
        if self.input_port:
            # 0x80 = Note Off, Channel 1
            data = [0x80, note, 0]
            self.input_port.send(bytearray(data), 0, 3)
        else:
            print(f"[MOCK] Note OFF: {note}")
```

### 2. The User Interface (`main.py`)
Use `time.perf_counter` for tighter timing control than `Clock.schedule_interval`.

```python
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.clock import Clock
import time
from midi_manager import MidiDriver

class SequencerApp(App):
    def build(self):
        self.midi = MidiDriver()
        self.midi.setup()
        
        # Create 16x16 Grid
        layout = GridLayout(cols=16)
        self.steps = []
        for i in range(256): # 16x16
            btn = ToggleButton(text='')
            layout.add_widget(btn)
            self.steps.append(btn)
            
        # Start Sequencer Loop (e.g., every 125ms for 120BPM)
        Clock.schedule_interval(self.tick, 0.125)
        return layout

    def tick(self, dt):
        # Sequencer logic here
        pass

if __name__ == '__main__':
    SequencerApp().run()
```

## Phase 4: Cloud Build Configuration (GitHub Actions)
*Goal: Compile the APK in the cloud.*

1.  **Initialize Config:**
    Run inside your project folder:
    ```bash
    buildozer init
    ```

2.  **Edit `buildozer.spec`:**
    Modify these specific lines:
    ```ini
    title = MyMidiSeq
    package.name = midiseq
    package.domain = org.test
    
    # Add pyjnius to requirements
    requirements = python3, kivy, pyjnius
    
    # Request MIDI permissions
    android.permissions = MIDI
    
    # Target modern Android
    android.api = 33
    android.minapi = 24
    ```

3.  **Create Workflow File:**
    Create directory `.github/workflows/` and file `build.yml`:
    ```yaml
    name: Build Android APK
    on: [push]
    jobs:
      build:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v2
          
          # Setup Buildozer
          - name: Build with Buildozer
            uses: ArtemSBulgakov/buildozer-action@v1
            id: buildozer
            with:
              workdir: .
              buildozer_version: master
          
          # Upload the APK to GitHub Actions page
          - name: Upload artifacts
            uses: actions/upload-artifact@v2
            with:
              name: package
              path: ${{ steps.buildozer.outputs.filename }}
    ```

## Phase 5: The Workflow Loop

1.  **Code & Test Locally:**
    Open Termux X11 app, then in Termux terminal:
    ```bash
    export DISPLAY=:0
    python main.py
    ```
    *Result:* You see the UI. You press buttons. The console prints `[MOCK] Note ON`.

2.  **Push to Build:**
    When the UI looks good:
    ```bash
    git add .
    git commit -m "Added sequencer grid"
    git push origin main
    ```

3.  **Deploy:**
    1.  Wait ~5-8 minutes.
    2.  Go to your GitHub Repository -> **Actions** tab.
    3.  Click the latest workflow run.
    4.  Scroll down to **Artifacts** and download `package`.
    5.  Install the APK on your phone.
    6.  Connect a MIDI keyboard/synth via USB OTG.
    7.  *Result:* The app now sends real MIDI signals instead of printing mock messages.

## Optimization Tips
*   **Garbage Collection:** MIDI needs low latency. In your `tick` loop, avoid creating new variables. Create them once in `__init__`.
*   **Permissions:** If the app crashes on launch, check App Info -> Permissions. You may need to manually allow "Connect to MIDI devices" depending on your Android version, though the manifest usually handles it.
*   



Let's call this project: **"The Isogrid"**.

---

# Design Specification: The "Isogrid" Sequencer

## 1. Core Philosophy: The Cartesian Split
Standard sequencers move linearly (1, 2, 3, 4). The Make Noise René is famous because it separates the **X-Axis** (horizontal movement) from the **Y-Axis** (vertical movement).

**The Isogrid Concept:**
We will treat the sequencers as two independent forces colliding on a 4x4 grid.
*   **Clock A** controls the Horizontal (X) position.
*   **Clock B** controls the Vertical (Y) position.
*   The **Result** is the note found at the intersection of X and Y.

## 2. Interface Design (Kivy UI Layout)

Imagine the screen split into three "modular" sections. The aesthetic should be dark (Hex #111111) with neon highlights (Amber for Pulse, Cyan for Logic), mimicking a Eurorack setup.

### A. The "Matrix" (Center Stage)
A 4x4 Grid of 16 touchable cells.
*   **Visuals:** Each cell displays its Note Value and a small slider for a MicroFreak parameter (e.g., Timbre).
*   **Interaction:**
    *   *Tap:* Select/Active cell.
    *   *Long Press:* Open a popup to set Note, Octave, and Probability.
    *   *Visual Feedback:* The active step is not just a light; it is a crosshair. A horizontal line highlights the active Row, a vertical line highlights the active Column. The intersection is the Note playing.

### B. The "Drivers" (The René Influence)
Instead of just a "Play" button, you have two "Driver" modules on the left and bottom.

*   **X-Driver (Bottom):** Controls left/right movement.
    *   *Modes:* Forward, Backward, Pendulum, Random, **Euclidean**.
    *   *Speed:* 1/16, 1/8, 1/4, or "Polyrhythm 5:4".
*   **Y-Driver (Left):** Controls up/down movement.
    *   *Modes:* Same as X.
    *   *Innovation:* **"Logic Advance"**. Only move Y if the note played on X had a velocity > 100.

### C. The MicroFreak Control Center (Right Panel)
The MicroFreak comes alive when parameters are automated. This section converts grid data into MIDI CC (Control Change) messages.

*   **Axis Mapping:**
    *   **Map X-Position to CC:** As the sequencer moves Left->Right, it slowly opens the **Filter Cutoff** (CC 23).
    *   **Map Y-Position to CC:** As the sequencer moves Bottom->Top, it changes the **Oscillator Type** (CC 9).
*   **The "Freak" Slider:** A global chaos slider. When increased, it randomizes the **Spice/Dice** (CC 2) amount on every step.

---

## 3. Functionality & Logic (Python/Midi Logic)

### The "Cartesian" Loop Logic
In a standard sequencer, you have one index `i` going 0 to 15. In Isogrid, you have `x` (0-3) and `y` (0-3).

**Algorithm:**
1.  **Clock Tick:** The system clock fires.
2.  **Calculate X:**
    *   Is X-Driver ready to move? (Check Euclidean rhythm/clock division).
    *   If yes, update `current_x`.
3.  **Calculate Y:**
    *   Is Y-Driver ready to move?
    *   If yes, update `current_y`.
4.  **The Intersection:**
    *   The active step index = `(current_y * 4) + current_x`.
    *   *State Check:* Is this step "Active" (enabled)?
    *   *Logic Gate:* If active, Trigger MIDI Note ON.
5.  **MicroFreak Modulation:**
    *   Send CC Message: `Value = (current_x / 3) * 127` -> Mapped to Timbre.
    *   Send CC Message: `Value = (current_y / 3) * 127` -> Mapped to Wave.

### Experimental Feature: "Snake Mode" vs "Wormhole Mode"
*   **Snake Mode:** Standard linear movement wrapped into a grid.
*   **Wormhole Mode (The Innovation):**
    Each cell in the 4x4 grid has a "Teleporter" setting.
    *   *Example:* If the sequence lands on Cell 6, it immediately jumps to Cell 12 without waiting for the clock. This creates skittering, glitchy IDM rhythms perfect for the MicroFreak.

---

## 4. MicroFreak MIDI Implementation Plan

To make this work with your hardware, you need to hardcode (or make selectable) the specific CC map for the MicroFreak.

**MicroFreak CC Cheat Sheet (for your Python code):**
*   **Cutoff:** CC 23
*   **Resonance:** CC 83
*   **Type (Oscillator):** CC 9 (This creates drastic sound changes)
*   **Wave:** CC 10
*   **Timbre:** CC 12
*   **Shape:** CC 13
*   **Glide:** CC 5

**The "Parameter Lock" Feature:**
In your Kivy `long_press` menu for a step, allow the user to define a "Lock".
*   *Logic:* "When this specific Note plays, Force CC 9 (Type) to Value 50."
*   *Result:* Each step can sound like a completely different synthesizer.

---

## 5. Summary of the User Flow

1.  **Launch App:** You see a 4x4 Dark Grid.
2.  **Connect:** USB OTG cable to MicroFreak. App detects device.
3.  **Setup:**
    *   Set X-Driver to "Forward, 1/16th".
    *   Set Y-Driver to "Random, 1/4th".
4.  **Play:** The sequence creates a non-repeating pattern because the X and Y clocks are out of sync (Polyrhythm).
5.  **Modulate:** You toggle "Link X to Timbre". Now, as the playhead moves right, the MicroFreak sound gets brighter/harsher.
6.  **Perform:** You drag your finger across the grid. The "Touch" overrides the sequencer, momentarily holding notes (like the touch plates on the René).

## Next Step
This design is complex but achievable in Kivy.
**Do you want to start by coding the "Cartesian Logic" (the X/Y intersecting clock system) or the "UI Layout" (the Grid and visual style) first?**