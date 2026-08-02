EPOCH DOY CLOCK — V1
====================

A small always-on-top Windows UTC clock focused on NASA-style Day of Year display.

START
-----
Double-click:

    Start Epoch DOY Clock.bat

Python 3 with Tkinter is required. Standard Windows Python installations normally include Tkinter.

CONTROLS
--------
Left Arrow            Previous day
Right Arrow           Next day
Shift + Left/Right    Move 7 days
0                     Return to current UTC day
Escape                Return to current UTC day
Mouse Wheel           Move backward/forward one day
Ctrl+C                Copy the displayed Epoch DOY
Ctrl+Q                Close the widget
Alt+F4                Close the widget
Left-click Epoch      Copy the displayed Epoch DOY
Left-drag anywhere    Move the widget
Right-click           Open menu

RIGHT-CLICK MENU
----------------
Now
Copy Epoch
Copy Full Timestamp
Layout > Horizontal / Vertical
Opacity
Always on Top
Edit Settings JSON
Reload Settings
Restore Defaults
Help
Close

SETTINGS
--------
Edit epoch_doy_clock.json to change colors, fonts, opacity, layout, formats, and spacing.

Useful epoch_format examples:

    GMT {doy:03d}
    GMT {doy:03d}/{hour:02d}:{minute:02d}:{second:02d}
    {year}-{doy:03d}
    {year}/{doy:03d}
    {year}{doy:03d}
    {doy:03d}

The default horizontal layout has:
- Epoch DOY on the left
- UTC time and date centered in the middle zone
- Day offset on the right

NOTES
-----
The selected date is always calculated as a live UTC clock plus the chosen day offset.
The current UTC day is green, future days are yellow, and past days are red.
The widget position and settings are saved automatically.


LAYOUT SWITCHING
----------------
Changing between Horizontal and Vertical saves the setting and launches a fresh
widget instance before closing the current one. This avoids a Windows/Tkinter issue where rebuilding a
borderless window from a popup menu can disable later right-clicks.


HELP OVERLAY
------------
Choose Help from the right-click menu to display all keyboard and mouse controls.
Dismiss it by clicking anywhere on the overlay or pressing Enter, Space, or Escape.


V1.6 DEVICE-SPECIFIC SETTINGS
-----------------------------
The shared file is:

    epoch_doy_clock.json

Use it for settings you want shared through Dropbox, such as colors, fonts,
opacity, date formats, and other common defaults.

Each computer automatically creates its own settings file using its Windows
computer name, for example:

    epoch_doy_clock.DESKTOP-PC.json
    epoch_doy_clock.LAPTOP.json

The device-specific file stores that computer's effective settings, including
its layout and screen position. This prevents a desktop position or layout
from being imposed on the laptop.

The right-click menu now includes:

    Edit This Device Settings
    Edit Shared Defaults
    Reload Settings

OFF-SCREEN RECOVERY
-------------------
At startup, V1.6 checks whether the saved position is visible on the current
display. If it is outside the available screen area, the widget resets itself
to position 100,100.
