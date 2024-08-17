import subprocess
from video_stuff import VideoFile
from utils import is_valid_video
import os
import sys
from config import BENTO4_SDK_PATH,SEGMENT_DURATION, TEMP_DIR
    
def fragment_the_video_file(videoFile: VideoFile, segement_duration: int):
    """
    Fragments a video file into segments of specified duration.

    Args:
        videoFile (VideoFile): The video file to be fragmented. 
        segment_duration (int): The duration of each segment in seconds. Must be a positive integer.

    Returns:
        VideoFile: An instance of the `VideoFile` class representing the path to the fragmented output file
        None: if the fragmentation fails or the input is invalid.

    Raises:
        ValueError: If `segment_duration` is less than or equal to zero.
        FileNotFoundError: If `videoFile` is not a valid video file."""

    if(segement_duration <= 0):
        print("Invalid Segment Duration")
        return None 
    if(not is_valid_video(videoFile)):
        print("Not a valid video file")
        return None
    else:
        try:
            output_file_name = f"output_{videoFile.height}_HDR_frag.mp4" if videoFile.isHDR else f"output_{videoFile.height}_frag.mp4"
            output_file_path = os.path.join(TEMP_DIR,output_file_name)
            mp4fragment = os.path.join(BENTO4_SDK_PATH,"bin","mp4fragment")
            command = [
                mp4fragment, 
                f'--fragment-duration',
                str(segement_duration),
                videoFile.path,
                output_file_path
            ]
            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
            print(f"Fragmentation of {videoFile.width}x{videoFile.height} {'HDR' if videoFile.isHDR else ''} successful!")
            return VideoFile(output_file_path)
        
        except subprocess.CalledProcessError as e:
            print(f"An error occurred: {e.stderr.decode('utf-8')}")

def package_the_video_files_to_dash(videoFiles: list, output_dir: str):
    """
    Packages a list of video files into DASH (Dynamic Adaptive Streaming over HTTP) format.

    This function uses the `mp4dash` tool to package multiple video files into a DASH-compliant streaming format.

    Args:
        videoFiles (list): A list of `VideoFile` instances to be packaged into DASH format. Each `VideoFile` should have properties like `path` and `aspect_ratio`.
        output_dir (str): The directory where the packaged DASH files will be saved.

    Returns:
        None: The function does not return a value but prints status messages indicating success or failure.

    Raises:
        ValueError: If no valid video files are provided.
        subprocess.CalledProcessError: If the `mp4dash` command fails, an error message is printed detailing the issue.
    
    Notes:
        The final output will be in OUTPUT_DIR specified in config.py (./output by default)
    """
    try:
        print("Trying to package the files into DASH stramble format",flush = True)
        input_video_files = []
        for videoFile in videoFiles:
            if(videoFile is None or videoFile.aspect_ratio <= 0):
                print(f"{videoFile.path} is invalid, not including in stream")
            else: 
                input_video_files.append(videoFile.path)
        
        if(len(input_video_files)  == 0):
            print("Error: Give proper input files")

        else:
            mp4dash = os.path.join(BENTO4_SDK_PATH,"bin","mp4dash")

            if os.name == 'nt': #windows
                mp4dash = mp4dash + ".bat"

            command =[mp4dash,
                "--profile",
                "on-demand",
                "--output-dir",
                output_dir,
                "--force"
            ]

            command = command + input_video_files
            
            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"\n\n\n Packaging successful! Output file: " + output_dir)

    except subprocess.CalledProcessError as e:
            print(f"An error occurred: {e.stderr.decode('utf-8')}",flush=True)
    

if __name__ == "__main__":
    video_720 = VideoFile("./tmp/output_360.mp4")
    #print(video_720.isHDR)
    video_720_sdr = VideoFile("./tmp/output_360_sdr.mp4")
    video_720_frag = fragment_the_video_file(video_720,7500)
    video_720_frag_sdr = fragment_the_video_file(video_720_sdr,7500)

    package_the_video_files_to_dash([video_720_frag,video_720_frag_sdr],"./bento_output")
    package_the_video_files_to_dash([video_720_frag_sdr],"./bento_output")