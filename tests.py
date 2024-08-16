import video_stuff as videoLib
from utils import is_valid_video
import argparse
import os
import shutil
import packaging_stuff as streamLib

def video_stuff_test(onlySDR: bool):
    video_sdr = videoLib.VideoFile('./input.mp4')
    print("loading the SDR video.... ",end="")
    if(is_valid_video(video_sdr)):
        print("Passed")
    else:
        print("Failed")
        exit()

    if(not onlySDR):
        video_hdr = videoLib.VideoFile('./input_hdr.mkv')
        print("loading the HDR video.... ",end="")
        if(is_valid_video(video_hdr)):
            print("Passed")
        else:
            print("Failed")
            exit()


    video_720_sdr = videoLib.transcode_to_h265_with_circle_overlay(video_sdr,720)
    print("Transcoding of SDR video...",end="")
    if(is_valid_video(video_720_sdr,open_frame = True)):
        print("Passed")
    else:
        print("Failed")

    if(not onlySDR):
        video_720_hdr,video_720_sdr = videoLib.transcode_to_h265_with_circle_overlay(video_hdr,720)
        print("Transcoding of HDR video...",end="")
        if(is_valid_video(video_720_hdr,open_frame = True) and is_valid_video(video_720_sdr,open_frame = True)):
            print("Passed")
        else:
            print("Failed")

def packaging_stuff():
    video_1080 = videoLib.VideoFile("./test_sdr_inputs/output_1080.mp4")
    video_720 = videoLib.VideoFile("./test_sdr_inputs/output_720.mp4")
    video_480 = videoLib.VideoFile("./test_sdr_inputs/output_480.mp4")
    video_360 = videoLib.VideoFile("./test_sdr_inputs/output_360.mp4")

    video_1080_frag = streamLib.fragment_the_video_file(video_1080,7500)
    video_720_frag = streamLib.fragment_the_video_file(video_720,7500)
    video_480_frag = streamLib.fragment_the_video_file(video_480,7500)
    video_360_frag = streamLib.fragment_the_video_file(video_360,7500)

    directory = "./tmp/test_sdr_output"
    if os.path.exists(directory):
        shutil.rmtree(directory)

    streamLib.package_the_video_files_to_dash([video_1080_frag,video_720_frag,video_480_frag,video_360_frag],directory)
    print(f"packaging successfull find output in {directory}....Passed")

    
    video_1080 = videoLib.VideoFile("./test_hdr_inputs/output_1080.mp4")
    video_720 = videoLib.VideoFile("./test_hdr_inputs/output_720.mp4")
    video_480 = videoLib.VideoFile("./test_hdr_inputs/output_480.mp4")
    video_360 = videoLib.VideoFile("./test_hdr_inputs/output_360.mp4")

    video_1080_frag = streamLib.fragment_the_video_file(video_1080,7500)
    video_720_frag = streamLib.fragment_the_video_file(video_720,7500)
    video_480_frag = streamLib.fragment_the_video_file(video_480,7500)
    video_360_frag = streamLib.fragment_the_video_file(video_360,7500)

    video_1080_sdr = videoLib.VideoFile("./test_hdr_inputs/output_1080_sdr.mp4")
    video_720_sdr = videoLib.VideoFile("./test_hdr_inputs/output_720_sdr.mp4")
    video_480_sdr = videoLib.VideoFile("./test_hdr_inputs/output_480_sdr.mp4")
    video_360_sdr = videoLib.VideoFile("./test_hdr_inputs/output_360_sdr.mp4")

    video_1080_sdr_frag = streamLib.fragment_the_video_file(video_1080_sdr,7500)
    video_720_sdr_frag = streamLib.fragment_the_video_file(video_720_sdr,7500)
    video_480_sdr_frag = streamLib.fragment_the_video_file(video_480_sdr,7500)
    video_360_sdr_frag = streamLib.fragment_the_video_file(video_360_sdr,7500)

    videoList = [video_1080_frag,video_720_frag,video_480_frag,video_360_frag,video_1080_sdr_frag,video_720_sdr_frag,video_360_sdr_frag,video_480_sdr_frag]

    directory = "./tmp/test_hdr_output"
    if os.path.exists(directory):
        shutil.rmtree(directory)

    streamLib.package_the_video_files_to_dash(videoList,directory)
    print(f"packaging successfull find output in {directory}....Passed")
    

def main():
    parser = argparse.ArgumentParser(description="Process some video options.")
    parser.add_argument('--only-sdr', action='store_true', help="Only process SDR content")
    parser.add_argument('--only-video-stuff', action='store_true', help="Only process video stuff")
    parser.add_argument('--only-stream-stuff', action='store_true', help="Only process stream stuff")
    args = parser.parse_args()

    if args.only_video_stuff and not args.only_stream_stuff :
        video_stuff_test(args.only_sdr)
    elif args.only_stream_stuff and not args.only_video_stuff:
        packaging_stuff()
    else:
        video_stuff_test(args.only_sdr)
        packaging_stuff()

if __name__ == "__main__":
    main()




