import sys
import os
import shutil

TEMP_DIR = "tmp"
os.makedirs(TEMP_DIR, exist_ok=True)

OUTPUT_DIR = "output"
if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)

SEGMENT_DURATION = 7500  # ms
CONSTANT_RATE_FACTOR = 28
PRESET = "medium"
SEGMENT_DURATION = 7500  # 7.5 sec
HDR2SDR_FILTER = "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0.0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p[scaled];"
BENTO4_SDK_MACOS = "Bento4-SDK-1-6-0-641.universal-apple-macosx"
BENTO4_SDK_WIN = "Bento4-SDK-1-6-0-641.x86_64-microsoft-win32"
BENTO4_SDK_LINUX = "Bento4-SDK-1-6-0-641.x86_64-unknown-linux"

if os.name == 'nt':  # 'nt' for Windows
    BENTO4_SDK_PATH = BENTO4_SDK_WIN
elif sys.platform == 'darwin':  # macOS
    BENTO4_SDK_PATH = BENTO4_SDK_MACOS
else:  # Assume Linux
    BENTO4_SDK_PATH = BENTO4_SDK_LINUX

