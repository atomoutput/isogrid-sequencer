from kivy.utils import platform

class MidiDriver:
    def __init__(self):
        self.device = None
        self.input_port = None
        self.output_port = None
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
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            midi_service = PythonActivity.mActivity.getSystemService(Context.MIDI_SERVICE)

            # Get available MIDI devices
            devices = midi_service.getDevices()
            if devices.length > 0:
                # Attempt to open the first device
                device_info = midi_service.getInfo(devices[0])
                print(f"[ANDROID] Found MIDI device: {device_info.getName()}")

                def on_device_opened(device):
                    if device is not None:
                        self.device = device
                        # Open input and output ports
                        # For sending MIDI data, we need input ports
                        for port_num in range(device.getNumInputPorts()):
                            self.input_port = device.openInputPort(port_num)
                            if self.input_port:
                                break

                        if self.input_port:
                            print("[ANDROID] MIDI Input Port opened successfully")
                        else:
                            print("[ANDROID] Failed to open MIDI Input Port")
                            self.is_mock_mode = True
                    else:
                        print("[ANDROID] Failed to open MIDI device")
                        self.is_mock_mode = True

                # Open the device asynchronously
                midi_service.openDevice(devices[0], on_device_opened, None)
            else:
                print("[ANDROID] No MIDI devices found, falling back to mock mode")
                self.is_mock_mode = True
        except Exception as e:
            print(f"[ERROR] Failed to setup Android MIDI: {str(e)}")
            print("[ERROR] Traceback:", __import__('traceback').format_exc())
            self.is_mock_mode = True

    def send_note_on(self, note, velocity=127, channel=0):
        """Send a MIDI Note ON message"""
        if not self.is_mock_mode and self.input_port:
            try:
                # 0x90 + channel = Note On for specified channel
                status_byte = 0x90 | (channel & 0x0F)
                data = [status_byte, note, velocity]
                self.input_port.send(bytearray(data), 0, len(data))
            except Exception as e:
                print(f"[ERROR] Failed to send MIDI note ON: {str(e)}")
                # Don't switch to mock mode here to prevent constant toggling
                # Just print the error and continue
                print(f"[MOCK] Note ON: {note} (velocity: {velocity}, channel: {channel}) - sent as mock due to error")
        else:
            print(f"[MOCK] Note ON: {note} (velocity: {velocity}, channel: {channel})")

    def send_note_off(self, note, channel=0):
        """Send a MIDI Note OFF message"""
        if not self.is_mock_mode and self.input_port:
            try:
                # 0x80 + channel = Note Off for specified channel
                status_byte = 0x80 | (channel & 0x0F)
                data = [status_byte, note, 0]
                self.input_port.send(bytearray(data), 0, len(data))
            except Exception as e:
                print(f"[ERROR] Failed to send MIDI note OFF: {str(e)}")
                print(f"[MOCK] Note OFF: {note}, channel: {channel} - sent as mock due to error")
        else:
            print(f"[MOCK] Note OFF: {note}, channel: {channel}")

    def send_cc(self, controller, value, channel=0):
        """Send a MIDI Control Change message"""
        if not self.is_mock_mode and self.input_port:
            try:
                # 0xB0 + channel = Control Change for specified channel
                status_byte = 0xB0 | (channel & 0x0F)
                data = [status_byte, controller, value]
                self.input_port.send(bytearray(data), 0, len(data))
            except Exception as e:
                print(f"[ERROR] Failed to send MIDI CC: {str(e)}")
                print(f"[MOCK] CC {controller} on ch.{channel}: {value} - sent as mock due to error")
        else:
            print(f"[MOCK] CC {controller} on ch.{channel}: {value}")

    def send_program_change(self, program, channel=0):
        """Send a MIDI Program Change message"""
        if not self.is_mock_mode and self.input_port:
            try:
                # 0xC0 + channel = Program Change for specified channel
                status_byte = 0xC0 | (channel & 0x0F)
                data = [status_byte, min(127, max(0, program))]
                self.input_port.send(bytearray(data), 0, len(data))
            except Exception as e:
                print(f"[ERROR] Failed to send MIDI PC: {str(e)}")
                print(f"[MOCK] PC {program} on ch.{channel} - sent as mock due to error")
        else:
            print(f"[MOCK] PC {program} on ch.{channel}")

    def send_pitch_bend(self, value, channel=0):
        """Send a MIDI Pitch Bend message (0-16383, centered at 8192)"""
        if not self.is_mock_mode and self.input_port:
            try:
                # 0xE0 + channel = Pitch Bend for specified channel
                status_byte = 0xE0 | (channel & 0x0F)
                # Convert 0-16383 value to LSB and MSB
                value = min(16383, max(0, value))
                lsb = value & 0x7F
                msb = (value >> 7) & 0x7F
                data = [status_byte, lsb, msb]
                self.input_port.send(bytearray(data), 0, len(data))
            except Exception as e:
                print(f"[ERROR] Failed to send MIDI Pitch Bend: {str(e)}")
                print(f"[MOCK] PB {value} on ch.{channel} - sent as mock due to error")
        else:
            print(f"[MOCK] PB {value} on ch.{channel}")