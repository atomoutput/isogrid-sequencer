# Isogrid Sequencer

The Isogrid Sequencer is an innovative MIDI sequencer application built with Kivy for Android. Inspired by the Make Noise René sequencer, it implements a unique "Cartesian Split" approach where X and Y axes operate independently to create complex rhythmic patterns.

## Features

- 4x4 grid sequencer with independent X and Y clock drivers
- Multiple playback modes: Forward, Backward, Pendulum, Random, Euclidean
- Real-time MIDI output for controlling external synthesizers (especially designed for Arturia MicroFreak)
- Visual feedback with crosshair highlighting active positions
- Support for Control Change (CC) automation
- Works natively on Android with USB MIDI support

## Technical Architecture

The application consists of:
- `main.py`: The Kivy UI and sequencer logic
- `midi_manager.py`: Handles MIDI communication with Android native MIDI or mock simulation
- `buildozer.spec`: Configuration for building Android APK
- `github-actions-workflow.yml`: GitHub Actions configuration (see Setup below)

## Setup for GitHub Actions (APK Building)

The project is configured for automated APK building via GitHub Actions. To enable this:

1. After cloning this repository, you need to manually add the GitHub Actions workflow file to enable automated building
2. Go to your repository on GitHub: `https://github.com/atomoutput/isogrid-sequencer`
3. Navigate to `.github/workflows/` directory (create it if it doesn't exist)
4. Create a new file named `build.yml`
5. Copy the following content into that file:

```yaml
name: Build Android APK
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    container:
      image: kivy/buildozer:latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.8'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          apt-get update
          apt-get install -y python3-pip

      - name: Build with Buildozer
        run: |
          cd /github/workspace
          buildozer android debug
        env:
          P4A_LOCAL_DIRECTORY: /github/workspace/.buildozer

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: isogrid-sequencer-apk
          path: bin/*.apk
```

6. Commit the file directly to your repository

Once the workflow file is added, GitHub Actions will automatically build the APK for each push to the repository.

## Building for Android

### Local Building
To build locally, you need to install Buildozer first:
```bash
pip install buildozer
```

Then run:
```bash
buildozer android debug
```

### Requirements
- Python 3.8+
- Buildozer
- Docker (for local testing)

## Local Development Setup

To run the Isogrid Sequencer locally in development mode:

1. Install dependencies:
```bash
pip install kivy pyjnius
```

2. Run the application:
```bash
python main.py
```

The application will run in mock mode, simulating MIDI output to the console without requiring actual MIDI hardware.

## License

MIT License - See LICENSE file for details.

_Last updated: December 2024_