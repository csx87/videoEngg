import ffmpeg
from fractions import Fraction
from utils import create_a_circle, is_valid_video
import time
import math
from config import CONSTANT_RATE_FACTOR as CRF, PRESET, SEGMENT_DURATION, HDR2SDR_filter  

TEMP_DIR="./tmp"

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
                print(stream_data) 
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



def transcode_to_h265_and_insert_a_circle(videoFile : VideoFile,output_height: int):
    
    if(output_height <=0):
        print("Invalid Resolution")
        return None

    if(not is_valid_video(videoFile)):
        print("Invalid Video File")
        return None
    else:
        try:
            output_width = math.ceil((videoFile.aspect_ratio.numerator)*output_height/(videoFile.aspect_ratio.denominator))

            print(f"Transcoding video to {output_width}x{output_height}")
            
            if(videoFile.isHDR):
                circle_color = "blue"
                y_position = "0"
                perc = 0.07
            
            else:
                circle_color = "white"
                y_position = "H-h"
                perc = 0.05

            x_position = "W-w"
            circle_path = create_a_circle(int(perc*output_height),circle_color)
            start_time = time.time()
        

            inv = ffmpeg.input(videoFile.path)
            ini = ffmpeg.input(circle_path)
            output_path = f"{TEMP_DIR}/output_{output_height}.mp4"
            segment_size = int((SEGMENT_DURATION/1000)*videoFile.frame_rate)

            ffmpeg.output(inv,ini,
                output_path, 
                filter_complex=f"[0:v]scale={output_width}:{output_height}[scaled];[scaled][1:v]overlay={x_position}:{y_position}",
                vcodec='libx265', 
                preset=PRESET, 
                crf= CRF,
                force_key_frames=f"expr:eq(mod(n,{segment_size}),0)"
            ).run(overwrite_output= True,capture_stdout=False, capture_stderr=True)
            
            if(videoFile.isHDR):
                #Creating an SDR file
                sdr_circle_path = create_a_circle(int(0.05*output_height),"white")
                ini = ffmpeg.input(sdr_circle_path)
                sdr_output_path = f"{TEMP_DIR}/output_{output_height}_sdr.mp4"
            
                ffmpeg.output(
                    inv,
                    ini,
                    sdr_output_path,
                    filter_complex=(
                        f"[0:v]scale={output_width}:{output_height}," + 
                        HDR2SDR_filter +
                        f"[scaled][1:v]overlay=W-w:H-h"
                    ),
                    vcodec='libx265',
                    preset=PRESET,
                    crf=CRF,
                    force_key_frames=f"expr:eq(mod(n,{segment_size}),0)"
                ).run(overwrite_output=True, capture_stdout=False, capture_stderr=True)


            end_time = time.time()

            print(f"Successfully Transcoded video to {output_width}x{output_height} in {round(end_time - start_time,2)} sec")
            if(videoFile.isHDR):
                return VideoFile(output_path), VideoFile(sdr_output_path)

            return VideoFile(output_path)
            
        except ffmpeg.Error as e:
            if "Invalid argument" in e.stderr.decode():
                print("Invalid argument error")
            elif "File not found" in e.stderr.decode():
                print("File not found error")
            else:
                print("General FFmpeg error")
            print("Error output:", e.stderr.decode())
            print("Error message:", e.stdout.decode())
            return None
    



if __name__ == "__main__":

    start_time = time.time()
    video = VideoFile('./input.mp4')
    #video = VideoFile('./tmp/output_720.mp4')
    print(f"Width: {video.width}, Height: {video.height}, Aspect Ratio: {video.aspect_ratio}, frame_rate:{round(video.frame_rate,2)} ,HDR video:{'yes' if video.isHDR else 'no'}")

    video_720 = transcode_to_h265_and_insert_a_circle(video,360)


    end_time = time.time()

    print(f"Total Time take = {round(end_time -start_time)} sec", video_720.path)






