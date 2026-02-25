[app]
# (str) Title of your application
title = VisuallyImpairedAssistant

# (str) Package name
package.name = viapp

# (str) Package domain (needed for android/ios packaging)
package.domain = org.assistance

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (empty string includes all standard files)
source.include_exts = py,png,jpg,kv,atlas,pt

# (str) Application versioning
version = 0.2

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
# We exclude desktop-only like pyttsx3. PyTorch requires specific flags.
requirements = python3,kivy,opencv,plyer,ultralytics,jnius,torch,torchvision,numpy

# (str) Supported orientation (landscape, portrait or all)
orientation = portrait

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (list) Permissions (ADDED RECORD_AUDIO as requested)
android.permissions = CAMERA, RECORD_AUDIO, INTERNET, VIBRATE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (str) Android architecture to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a

# (bool) enables Android auto backups (Android API >=23)
android.allow_backup = True

# Ensure Cython handles opencv/torch properly
p4a.branch = master

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
