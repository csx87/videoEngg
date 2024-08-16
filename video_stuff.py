import ffmpeg
from fractions import Fraction
from utils import create_a_circle
import time
import math
from config import CONSTANT_RATE_FACTOR as CRF, PRESET, SEGMENT_DURATION, HDR2SDR_filter  

TEMP_DIR="./tmp"

class VideoFile:
    def __init__(self, name):
        self.path = name
        self.width = 0
        self.height = 0
        self.aspect_ratio = Fraction(0, 1)
        self.isHDR = False #TODO: Get the info from probe 
        self.__initialize()

    def __initialize(self):
        try:
            self.width, self.height, self.aspect_ratio,self.isHDR = self.__get_metadata_from_video()
        except Exception as e:
            print(f"Failed to initialize video resolution: {e}")
            # Optional: Set to default values or handle error as needed
            self.width, self.height, self.aspect_ratio = 0, 0, Fraction(0, 1)

    def __get_metadata_from_video(self):
        width = 0
        height = 0
        aspect_ratio = Fraction(0, 1) 
        isHDR = False

        try:
            probe = ffmpeg.probe(self.path, v='error', select_streams='v:0', show_entries='stream=height,width,color_space,color_transfer,color_primaries')
            if "streams" in probe.keys():
               
                stream_data = probe["streams"][0]
                
                if "width" in stream_data and "height" in stream_data:
                    width = stream_data["width"]
                    height = stream_data["height"]
                    aspect_ratio = Fraction(width, height)
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
            # Raising an exception to be handled by the calling method
            raise

        return width, height, aspect_ratio, isHDR



def transcode_to_h265_and_insert_a_circle(videoFile : VideoFile,output_height: int, crf_op = CRF, preset_op = PRESET, segement_duration_op = SEGMENT_DURATION):
    if(len(videoFile.path) > 0 and videoFile.aspect_ratio != 0 and output_height > 0):
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
            print("circle_radius: ",int(perc*output_height))
            circle_path = create_a_circle(int(perc*output_height),circle_color)

            start_time = time.time()
            '''
            ffmpeg.input(videoFile.path).output(
                f'./tmp/output_{output_height}.mp4', 
                vf=f'scale={output_width}:{output_height}', 
                vcodec='libx265', preset='medium', 
                crf=28).run(overwrite_output= True,capture_stdout=False, capture_stderr=True)
            '''

            inv = ffmpeg.input(videoFile.path)
            ini = ffmpeg.input(circle_path)
            output_path = f"{TEMP_DIR}/output_{output_height}.mp4"
            #TODO get frames from videoFile
            segment_size = int((segement_duration_op/1000)*24)
            print("Segment size:",segment_size)

            ffmpeg.output(inv,ini,
                output_path, 
                filter_complex=f"[0:v]scale={output_width}:{output_height}[scaled];[scaled][1:v]overlay={x_position}:{y_position}",
                vcodec='libx265', 
                preset=preset_op, 
                crf= crf_op,
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
                        # Apply scaling and HDR-to-SDR conversion, and label the result as [scaled]
                        f"[0:v]scale={output_width}:{output_height}",
                        HDR2SDR_filter,
                        # Use the labeled output [scaled] and overlay it with the second video [1:v]
                        f"[scaled][1:v]overlay=W-w:H-h"
                    ),
                    vcodec='libx265',
                    preset=preset_op,
                    crf=crf_op,
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
    else:
        pass
        #raise an exception???
    return None



if __name__ == "__main__":

    start_time = time.time()
    video = VideoFile('./input_hdr.mkv')
    #video = VideoFile('./tmp/output_720.mp4')
    print(f"Width: {video.width}, Height: {video.height}, Aspect Ratio: {video.aspect_ratio} ,HDR video:{'yes' if video.isHDR else 'no'}")

    video_720,video_720_sdr = transcode_to_h265_and_insert_a_circle(video,360)


    end_time = time.time()

    print(f"Total Time take = {round(end_time -start_time)} sec", video_720.path,video_720_sdr.path)






