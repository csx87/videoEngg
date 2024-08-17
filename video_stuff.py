import ffmpeg
import os
from fractions import Fraction
import time
import math
from config import CONSTANT_RATE_FACTOR as CRF, PRESET, SEGMENT_DURATION, HDR2SDR_FILTER, TEMP_DIR
from utils import create_a_circle, is_valid_video 

HDR_CIRCLE_COLOR = "blue"
SDR_CIRCLE_COLOR = "white"
HDR_PERCENT = 0.07
SDR_PERCENT = 0.05

class VideoFile:
    def __init__(self, name):
        self._path = name
        self._width = 0
        self._height = 0
        self._frame_rate = 0
        self._aspect_ratio = Fraction(0, 1)
        self._isHDR = False 
        self.__initialize()

    @property
    def path(self):
        return self._path
    @property
    def width(self):
        return self._width
    @property
    def height(self):
        return self._height
    @property
    def frame_rate(self):
        return self._frame_rate
    @property
    def aspect_ratio(self):
        return self._aspect_ratio
    @property
    def isHDR(self):
        return self._isHDR

    def __initialize(self):
        try:
            self._width, self._height, self._aspect_ratio,self._frame_rate, self._isHDR = self.__get_metadata_from_video()
        except Exception as e:
            print(f"Failed to initialize video resolution: {e}","Pleas check if the video file is proper")
            self._width, self._height, self._aspect_ratio,self._frame_rate, self._isHDR = 0,0,0,0,False

    def __get_metadata_from_video(self):
        try:
            width = 0
            height = 0
            aspect_ratio = Fraction(0, 1) 
            isHDR = False
            frame_rate = 0

            probe = ffmpeg.probe(
                self.path, v='error', 
                select_streams='v:0', 
                show_entries='stream=height,width,color_space,color_transfer,color_primaries,r_frame_rate',
                )

            if "streams" in probe.keys():
                stream_data = probe["streams"][0]
                if "width" in stream_data and "height" in stream_data and "r_frame_rate" in stream_data:
                    width = stream_data["width"]
                    height = stream_data["height"]
                    aspect_ratio = Fraction(width, height)
                    frame_rate = eval(stream_data["r_frame_rate"])

                if "color_space" in stream_data and "color_transfer" in stream_data and "color_primaries" in stream_data:
                    if stream_data["color_primaries"] == 'bt2020' and stream_data["color_transfer"] in ['smpte2084', 'arib-std-b67'] and stream_data["color_space"] == 'bt2020nc':
                        isHDR = True

        except ffmpeg.Error as e:
            error_message = e.stderr.decode()
            if "Invalid argument" in error_message:
                print("Invalid argument error")
            elif "File not found" in error_message:
                print("File not found error")
            else:
                print("General FFmpeg error")
            print("Error output:", error_message)
            print("Error message:", e.stdout.decode())
            raise

        return width, height, aspect_ratio,frame_rate, isHDR, 



def transcode_to_h265_with_circle_overlay(videoFile: VideoFile, output_height: int):
    if output_height <= 0:
        print("Invalid Resolution")
        return None

    if not is_valid_video(videoFile):
        print("Invalid Video File")
        return None

    try:
        output_width = math.ceil((videoFile.aspect_ratio.numerator * output_height) / videoFile.aspect_ratio.denominator)
        print(f"Transcoding video to {output_width}x{output_height}")
        
        start_time = time.time()

        circle_color = HDR_CIRCLE_COLOR if videoFile.isHDR else SDR_CIRCLE_COLOR
        y_position = "0" if videoFile.isHDR else "H-h"
        perc = HDR_PERCENT if videoFile.isHDR else SDR_PERCENT
        x_position = "W-w"

        circle_path = create_a_circle(int(perc * output_height), circle_color)
        start_time = time.time()

        output_path = os.path.join(TEMP_DIR,f"output_{output_height}.mp4")
        segment_size = int((SEGMENT_DURATION / 1000) * videoFile.frame_rate)

        # Base ffmpeg input
        inv = ffmpeg.input(videoFile.path)
        ini = ffmpeg.input(circle_path)

        # Create main output
        ffmpeg.output(
            inv, ini,
            str(output_path),
            filter_complex=f"[0:v]scale={output_width}:{output_height}[scaled];[scaled][1:v]overlay={x_position}:{y_position}",
            vcodec='libx265',
            preset=PRESET,
            crf=CRF,
            force_key_frames=f"expr:eq(mod(n,{segment_size}),0)"
        ).run(overwrite_output=True, capture_stdout=False, capture_stderr=True)

        # HDR to SDR conversion
        if videoFile.isHDR:
            sdr_circle_path = create_a_circle(int(SDR_PERCENT * output_height), SDR_CIRCLE_COLOR)
            sdr_output_path = os.path.join(TEMP_DIR,f"output_{output_height}_sdr.mp4")

            ffmpeg.output(
                inv, ffmpeg.input(sdr_circle_path),
                str(sdr_output_path),
                filter_complex=f"[0:v]scale={output_width}:{output_height},{HDR2SDR_FILTER}[scaled][1:v]overlay=W-w:H-h",
                vcodec='libx265',
                preset=PRESET,
                crf=CRF,
                force_key_frames=f"expr:eq(mod(n,{segment_size}),0)"
            ).run(overwrite_output=True, capture_stdout=False, capture_stderr=True)
            
            end_time = time.time()
            print(f"Transcoded video to {output_width}x{output_height} completed in {round(end_time-start_time,2)}")
            return VideoFile(str(output_path)), VideoFile(str(sdr_output_path))
            
        end_time = time.time()
        print(f"Transcoding video to {output_width}x{output_height} completed in {round(end_time-start_time,2)}")
        return VideoFile(str(output_path))

    except ffmpeg.Error as e:
        stderr = e.stderr.decode()
        stdout = e.stdout.decode()
        if "Invalid argument" in stderr:
            print("Invalid argument error")
        elif "File not found" in stderr:
            print("File not found error")
        else:
            print("General FFmpeg error")
        print("Error output:", stderr)
        print("Error message:", stdout)
        return None
    



if __name__ == "__main__":

    start_time = time.time()
    video = VideoFile('./input.mp4')
    #video = VideoFile('./tmp/output_720.mp4')
    print(f"Width: {video.width}, Height: {video.height}, Aspect Ratio: {video.aspect_ratio}, frame_rate:{round(video.frame_rate,2)} ,HDR video:{'yes' if video.isHDR else 'no'}")

    video_720 = transcode_to_h265_with_circle_overlay(video,360)


    end_time = time.time()

    print(f"Total Time take = {round(end_time -start_time)} sec", video_720.path)






