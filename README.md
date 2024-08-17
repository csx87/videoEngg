Here’s a polished version of your instructions formatted for a `README.md` file:

---

## Setup Instructions

### Step 1: Installation

1. Install the necessary Python packages:

   ```bash
   pip3 install opencv-python
   pip3 install ffmpeg-python
   ```

2. If you are using Linux, make the Bento4 SDK binaries executable:

   ```bash
   chmod +x ./Bento4-SDK-1-6-0-641.x86_64-unknown-linux/bin/*
   ```

### Step 2: Running the Script

Run the following command to start processing your input files:

```bash
python3 main.py <path_to_input_files>
```

- The `stream.mpd` file will be generated in the ```./output``` directory.

### Troubleshooting

- If the provided Bento4 SDK does not work, you can download the appropriate version for your system from the [Bento4 GitHub repository](https://github.com/axiomatic-systems/Bento4).
- Update the `BENTO4_SDK_PATH` in the `config.py` file with the path to your Bento4 SDK installation:

  ```python
  BENTO4_SDK_PATH = "<path_to_bento4_sdk>"
  ```

### Compatibility

- The script has been tested on **Linux** and **Windows**. It should work on both operating systems.
- **macOS** compatibility is untested, as I do not have access to a Mac.

---

