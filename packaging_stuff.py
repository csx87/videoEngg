import subprocess
from video_stuff import VideoFile

SEGMENT_DURATION = 7500 #ms
TEMP_DIR = "./tmp"
BENTO_OUTPUT_DIR = "./bento_output"
BENTO4_SDK_PATH = "/home/csx87/lib/Bento4-SDK-1-6-0-641.x86_64-unknown-linux/bin"
    
def fragment_the_video_file(videoFile: VideoFile, segement_duration: int):
    if(videoFile is not None and videoFile.aspect_ratio > 0 and segement_duration > 0):
        try:
            output_file_path = f"{TEMP_DIR}/output_{videoFile.height}_frag.mp4"
            if(videoFile.isHDR):
                output_file_path = f"{TEMP_DIR}/output_{videoFile.height}_HDR_frag.mp4"
            command = [
                f'{BENTO4_SDK_PATH}/mp4fragment', 
                f'--fragment-duration',
                str(segement_duration),
                videoFile.path,
                output_file_path
            ]

            # Run the command
            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
            print(f"Fragmentation successful! Output file: " + output_file_path)
            return VideoFile(output_file_path)
        
        except subprocess.CalledProcessError as e:
            print(f"An error occurred: {e.stderr.decode('utf-8')}")
    else:
        pass 
        #TODO exception or Invalid parameters

def package_the_video_files_to_dash(videoFiles: list, output_dir: str,):
    try:
        input_video_files = []
        for videoFile in videoFiles:
            if(videoFile is None or videoFile.aspect_ratio <= 0):
                print(f"{videoFile.path} is invalid, not including in stream")
            else: 
                input_video_files.append(videoFile.path)
        if(len(output_dir) > 0 and len(input_video_files) > 0):
            command =[f"{BENTO4_SDK_PATH}/mp4dash",
                "--profile",
                "on-demand",
                "--output-dir",
                output_dir,
            ]

            command = command + input_video_files
            
            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            pass
            #TODO give proper output str

    except subprocess.CalledProcessError as e:
            print(f"An error occurred: {e.stderr.decode('utf-8')}")
    

if __name__ == "__main__":
    video_720 = VideoFile("./tmp/output_360.mp4")
    #print(video_720.isHDR)
    video_720_sdr = VideoFile("./tmp/output_360_sdr.mp4")
    video_720_frag = fragment_the_video_file(video_720,7500)
    video_720_frag_sdr = fragment_the_video_file(video_720_sdr,7500)

    package_the_video_files_to_dash([video_720_frag,video_720_frag_sdr],"./bento_output")
    #package_the_video_files_to_dash([video_720_frag_sdr],"./bento_output")