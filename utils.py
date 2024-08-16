import cv2
import numpy as np
from enum import Enum
from fractions import Fraction

class Color():
    def __init__(self,color):
        if(color == "white"):
            self.bgra = (255,255,255,255) #The 4th parameter is the alpha channel, basically indating transparency is 0%
        elif(color == "blue"):
            self.bgra = (255,0,0,255)
        else:
            self.bgra = (0,0,0,255)
        


def create_a_circle(radius: int,color: str) -> str:
    # Create an bgra image with a transparent background
    height, width = radius*2, radius*2
    image = np.zeros((height, width, 4), dtype="uint8")

    # Draw a white circle (centered at (250, 250) with a radius of 200)
    center = (int(height/2), int(width/2))
    cv2.circle(image, center, radius,Color(color).bgra, -1)  # (B, G, R, A) format

    # Save the image
    cv2.imwrite(f'./tmp/output_circle_{radius}.png', image)
    return f'./tmp/output_circle_{radius}.png'

if __name__ == "__main__":
    create_a_circle(200,"kuchbhi")


def is_valid_video(video, open_frame = False):
    if(video.width > 0 and video.height > 0 and video.aspect_ratio == Fraction(video.width,video.height)):
        cap = cv2.VideoCapture(video.path)
        if not cap.isOpened():
            return False
        if(open_frame):
            ret, frame = cap.read() 
            cap.release()
            return ret
        return True
    else:
        return False