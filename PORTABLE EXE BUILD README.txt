EPOCH DOY CLOCK - PORTABLE EXE BUILD
====================================

QUICK BUILD
-----------

1. Extract this ZIP to a normal folder on your Windows PC.

2. Double-click:

       BUILD PORTABLE EXE.bat

3. The script will:
   - Find your installed Python 3
   - Install/update PyInstaller for your Windows user
   - Build a single-file, no-console Windows executable
   - Open the output folder automatically

4. Your finished program will be:

       dist\Epoch DOY Clock.exe

You can then copy just that EXE to another Windows computer.

The target computer DOES NOT need Python installed.


PORTABLE SETTINGS
-----------------

The EXE stores its settings beside itself, including:

    epoch_doy_clock.json
    epoch_doy_clock.<COMPUTERNAME>.json

This means one copy placed in Dropbox can still keep separate per-computer
layout/position settings.

If you want to distribute a completely clean copy to someone else, give them
ONLY:

    Epoch DOY Clock.exe

Their own JSON settings files will be created when they first run it.


WINDOWS SECURITY
----------------

Because this personal EXE is not digitally code-signed, Windows SmartScreen
may show an "unrecognized app" warning on another computer.

For trusted internal/personal use, the user may need to choose:

    More info -> Run anyway

Company-managed Windows computers may have policies that prevent unsigned
executables from running.


REBUILDING
----------

After changing epoch_doy_clock.py, simply run BUILD PORTABLE EXE.bat again.

For a completely clean PyInstaller rebuild, BUILD PORTABLE EXE already uses
the --clean option. You can also run CLEAN BUILD FILES.bat to remove the
build/dist folders and generated .spec file.


NOTES
-----

The build uses:

    --onefile
    --windowed

--onefile packages Python, Tkinter, and the application into one EXE.
--windowed prevents a console/command window from appearing when the clock runs.
