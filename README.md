# VRCWeatherOSC
An OSC implementation to pull weather and time data to affect avatars

Dependencies:
Python 3.5+ (Personally using 3.10)

From cmd prompt

1. For OSC Support - pip install python-osc
2. For request handling - pip install requests


Credit to https://openweathermap.org/ for API support

Note it is best to make your own api key and modify the the code to accept it instead

Lines 14, 15, and 16 you can change your APIKey, zip code, and country code. To come: Window where these can be entered.

Eventually when I get more time, I will be adjusting this to have a window where the avatar param names can be entered to your liking as well as the temperature and time thresholds. For now they are not that difficult to change in the code manually.
