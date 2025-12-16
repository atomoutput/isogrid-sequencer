from kivy.utils import platform

class MidiDriver:
    def __init__(self):
        self.device = None
        self.input_port = None
        self.is_mock_mode = platform != 'android'

    def setup(self):
        if platform == 'android':
            self._setup_android()
        else:
            print("[MOCK] MIDI Setup Complete (Simulation Mode)")

    def _setup_android(self):
        try:
            from jnius import autoclass
            # Get Android Context & MIDI Service
            Context = autoclass('android.content.Context')
            activity = autoclass('org.kivy.android.PythonActivity').mActivity
            midi_service = activity.getSystemService(Context.MIDI_SERVICE)

            # Simplified: Open first available device
            devices = midi_service.getDevices()
            if devices.length > 0:
                midi_service.openDevice(devices[0], self._on_device_open, None)
                print("[ANDROID] MIDI Device opened successfully")
            else:
                print("[ANDROID] No MIDI devices found, falling back to mock mode")
                self.is_mock_mode = True
        except Exception as e:
            print(f"[ERROR] Failed to setup Android MIDI: {str(e)}")
            self.is_mock_mode = True

    def _on_device_open(self, device):
        self.device = device
        self.input_port = device.openInputPort(0)

    def send_note_on(self, note, velocity=127):
        if not self.is_mock_mode and self.input_port:
            try:
                # 0x90 = Note On, Channel 1
                data = [0x90, note, velocity]
                self.input_port.send(bytearray(data), 0, 3)
            except Exception as e:
                print(f"[ERROR] Failed to send MIDI note ON: {str(e)}")
                self.is_mock_mode = True
        else:
            print(f"[MOCK] Note ON: {note} (velocity: {velocity})")

    def send_note_off(self, note):
        if not self.is_mock_mode and self.input_port:
            try:
                # 0x80 = Note Off, Channel 1
                data = [0x80, note, 0]
                self.input_port.send(bytearray(data), 0, 3)
            except Exception as e:
                print(f"[ERROR] Failed to send MIDI note OFF: {str(e)}")
                self.is_mock_mode = True
        else:
            print(f"[MOCK] Note OFF: {note}")

    def send_cc(self, controller, value):
        """Send a MIDI Control Change message"""
        if not self.is_mock_mode and self.input_port:
            try:
                # 0xB0 = Control Change, Channel 1
                data = [0xB0, controller, value]
                self.input_port.send(bytearray(data), 0, 3)
            except Exception as e:
                print(f"[ERROR] Failed to send MIDI CC: {str(e)}")
                self.is_mock_mode = True
        else:
            print(f"[MOCK] CC {controller}: {value}")