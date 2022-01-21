# Auto-Restart Audio Engine on Device Reconnect

This script (python3) will check all selected and available devices every 5 seconds to see whether devices previously disconnect were connected. If so the audio engine of Voicemeeter will be restarted.

## Requirements

* [Voicemeeter](https://vb-audio.com/Voicemeeter/potato.htm) installed and running
* [python3](https://www.python.org/downloads/) and `py` available on the PATH

## Setup

Copy files into the Voicemeeter install folder OR copy the `VoicemeeterRemote64.dll` into this folder so that the dll can be found by the script.

### py

Running this as python directly will cause it to stop if Voicemeeter is not running or shutdown while it is running. As soon as it detects that, the script exits.

```py
py autorestart-audio-engine.py
```

### bat

You can chose to run the `.bat` file instead of the `.py`. This will then automatically restart the python script if it exits (5s later). Simply double click the .bat.

### vbs

The `.vbs` file will start the `.bat` file once, but without a terminal window. Like this you can start the process in the background. This is especially helpful if you want to run this on Windows start.

#### Autostart on Windows

To enable autostart for this, press `Win + R` and enter `shell:startup` to open the *Autostart* folder of Windows. Place a link file to the `.vbs` file in that folder. To deactivate the autostart simply remove the link.

## Stop the process

Stopping the process is not really included in the scripts at the moment. If you chose the run the `py` or `bat` you can simply stop the process directly in your cmd or in the task manager.

If you chose the `vbs` approach your `cmd` window is hidden. You will have to search the Task Manager for the correct `cmd.exe`, stop that process and afterwards stop the `python.exe` related to the script.

## Known Issues

### py script exits if voicemeeter is not available

The script needs Voicemeeter to be running (Login status 0), because otherwise the selected devices can not be determined. If that's not the case the python script will simply exit because logout and login again did not work correctly. The `.bat` file will automatically restart it because of this 5s after exit.
