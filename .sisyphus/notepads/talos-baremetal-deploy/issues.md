## Notepad: Issues
 - `python3 -c "from platforms.types import PlatformProfile; print('OK')"` failed because `platforms/__init__.py` eagerly imports `platforms.resolver`, which requires the external `pulumi` package that is not installed in this environment.
