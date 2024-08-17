import time
import os
import concurrent.futures
import video_stuff as videoLib
import packaging_stuff as streamLib

import argparse

from utils import is_valid_video,clean_and_exit
from config import OUTPUT_DIR,SEGMENT_DURATION

RESOLUTION_TO_TRANSCODE = [360, 480, 720, 1080]

def process_resolution(resolution): 
    """
    Transcodes and fragments a video based on its resolution and HDR status.

    Args:
        resolution (str): The resolution(height) to which the input video should be transcoded

    Returns:
        list: A list of fragmented video files.
    """
    try:
        fragmented_videos = []
        if inputVideo.isHDR:
            transcoded_video, transcoded_video_sdr = videoLib.transcode_to_h265_with_circle_overlay(inputVideo, resolution)
            fragmented_videos.append(streamLib.fragment_the_video_file(transcoded_video, SEGMENT_DURATION))
            fragmented_videos.append(streamLib.fragment_the_video_file(transcoded_video_sdr, SEGMENT_DURATION))
        else:
            transcoded_video = videoLib.transcode_to_h265_with_circle_overlay(inputVideo, resolution)
            fragmented_videos.append(streamLib.fragment_the_video_file(transcoded_video, SEGMENT_DURATION))
        return fragmented_videos
    except Exception as e:
        print(f"Failed to process resolution {resolution}: {e}")
        return []

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('input_file', type=str, help='The input file to be processed')

    args = parser.parse_args()

    input_path = args.input_file

    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        exit(1)

    inputVideo = videoLib.VideoFile(input_path)
    
    if is_valid_video(inputVideo,True):
        print(f"{input_path} is of resolution {inputVideo.width}x{inputVideo.height} "
              f"and aspect ratio {inputVideo.aspect_ratio} "
              f"HDR video: {'yes' if inputVideo.isHDR else 'no'}")
        
        fragmented_videos = []
        start_time = time.time()

        #Each resolution is transcoded in a seperate thread
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(process_resolution, res): res for res in RESOLUTION_TO_TRANSCODE}

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    fragmented_videos.extend(result)

        end_time = time.time()
        
        try: 
            streamLib.package_the_video_files_to_dash(fragmented_videos, OUTPUT_DIR)
            print(f"Total time taken: {round(end_time - start_time, 2)} seconds",flush=True)
            clean_and_exit()

        except Exception as e:
            print(f"Failed to pack {e}")
            clean_and_exit()
        
    else:
        print("Invalid Input Video File", flush=True)
        clean_and_exit()
