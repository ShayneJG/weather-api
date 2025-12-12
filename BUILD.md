# Build and Release Process

This document describes how to build and release the Weather Tray application.

## Prerequisites

- Python 3.8 or higher
- Virtual environment with dependencies installed
- Git access to the repository
- GitHub account with repository access

## Version Management

The application version is defined in `tray/version.py`:

```python
__version__ = "1.0.0"
```

Update this file when preparing a new release.

## Building the Executable

1. Navigate to the tray directory:

   ```bash
   cd tray
   ```

2. Ensure virtual environment is activated and dependencies are installed:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the build script:

   ```bash
   python build.py
   ```

4. The executable will be created in `dist/v{version}/WeatherTray.exe`

## Release Process

### 1. Prepare the Release

1. Update version in `tray/version.py`
2. Commit all changes to main:
   ```bash
   git add .
   git commit -m "Prepare release v{version}"
   git push origin main
   ```

### 2. Create Release Branch

```bash
git checkout -b release
git push origin release
```

### 3. Build the Executable

```bash
cd tray
python build.py
```

### 4. Create GitHub Release

1. Go to your GitHub repository
2. Click "Releases" → "Create a new release"
3. Tag: `v{version}` (e.g., `v1.0.0`)
4. Target: `release` branch
5. Title: `Weather Tray v{version}`
6. Description: List of changes and features
7. Upload the built executable: `dist/v{version}/WeatherTray.exe`
8. Click "Publish release"

### 5. Update Main Branch

After release, merge any release-specific changes back to main if needed.

## Auto-Update Feature

The application checks for updates when the user opens the tray menu. The update checker:

1. Queries the GitHub API for the latest release tag
2. Compares it with the current version
3. Shows "⚠ Update available: v{version}" if a newer version exists
4. Clicking the update message opens the GitHub release page in the browser

## Configuration

Before first release, update `tray/update_checker.py`:

```python
GITHUB_REPO = "your-username/weather-api"  # Replace with your GitHub username
```

## Testing the Build

To test the executable:

1. Close any running instances of the tray app
2. Navigate to `dist/v{version}/`
3. Run `WeatherTray.exe`
4. Verify all functionality works:
   - Tray icon displays UV
   - Right-click menu shows weather data
   - Window appears when clicking "Show"
   - Version is displayed in menu
   - Backend connection works

## Troubleshooting

**Build fails with import errors:**

- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that virtual environment is activated

**Executable crashes on startup:**

- Test in development mode first: `python main.py`
- Check that `config.json` is being bundled correctly
- Review PyInstaller logs in `build/WeatherTray/`

**Update checker doesn't work:**

- Verify GitHub repository is public
- Check that `GITHUB_REPO` is set correctly in `update_checker.py`
- Ensure release tags follow semantic versioning (v1.0.0)
