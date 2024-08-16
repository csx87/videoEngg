import video_stuff as videoLib
import packaging_stuff as streamLib
import time
import os

RESOLUTION_TO_TRANSCODE = [360, 480, 720, 1080]
SEGMENT_DURATION = 7500  # ms
OUTPUT_DIR = "./output"

def process_resolution(resolution):
    try:
        if(inputVideo.isHDR):
            transcoded_video,transcoded_video_sdr = videoLib.transcode_to_h265_and_insert_a_circle(inputVideo, resolution)
            hdr_frag = streamLib.fragment_the_video_file(transcoded_video, SEGMENT_DURATION)
            sdr_frag = streamLib.fragment_the_video_file(transcoded_video_sdr, SEGMENT_DURATION)
            return hdr_frag,sdr_frag
        else:
            transcoded_video = videoLib.transcode_to_h265_and_insert_a_circle(inputVideo, resolution)
            return streamLib.fragment_the_video_file(transcoded_video, SEGMENT_DURATION)
    except Exception as e:
        print(f"Failed to process resolution {resolution}: {e}")

if __name__ == "__main__":
    input_path = input("Enter the video File path: ")

    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        exit(1)

    inputVideo = videoLib.VideoFile(input_path)
    
    if inputVideo.aspect_ratio > 0:
        print(f"{input_path} is of resolution {inputVideo.width}x{inputVideo.height} ",
              f"and aspect ratio {inputVideo.aspect_ratio}",
              f"HDR video:{'yes' if inputVideo.isHDR else 'no'}")
        
        fragmented_videos = []
        start_time = time.time()

        for resolution in RESOLUTION_TO_TRANSCODE:
            fragmented_videos.append(process_resolution(resolution))

        print([x.path for x in fragmented_videos])
        streamLib.package_the_video_files_to_dash(fragmented_videos, OUTPUT_DIR)
        
        end_time = time.time()
        print(f"Total time taken: {round(end_time - start_time, 2)} seconds")

    else:
        print("Invalid Input Video File")
