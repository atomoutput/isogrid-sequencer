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

The project is configured for automated APK building via GitHub Actions, however there's a special requirement for adding the workflow file:

1. After cloning this repository, you need to manually add the GitHub Actions workflow file to enable automated building
2. Go to your repository on GitHub: `https://github.com/atomoutput/isogrid-sequencer`
3. Navigate to `.github/workflows/` directory (create it if it doesn't exist)
4. Create a new file named `build.yml`
5. Copy the content from `github-actions-workflow.yml` in this repository into that file
6. Commit the file directly to your repository

Once the workflow file is added, GitHub Actions will automatically build the APK for each push to the repository.

## Building for Android

After setting up the GitHub Actions workflow, the project uses Buildozer to package the application for Android. The build process runs automatically via GitHub Actions when changes are pushed to the repository.

To build locally, install Buildozer and run:
```bash
buildozer android debug
```

## License

MIT License - See LICENSE file for details.