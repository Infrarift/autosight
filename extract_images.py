from moviepy.editor import VideoFileClip
import cv2
import os


class ImageExtractor:

    def __init__(self):
        self.current_frame = 0
        self.frames_max = 15
        self.frame_index = 1
        self.output_dir = "./extracted_images/"
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)

    def is_valid_frame(self):
        self.current_frame -= 1
        if self.current_frame <= 0:
            self.current_frame = self.frames_max
            return True
        return False

    def extract_image(self, image):
        if self.is_valid_frame():
            cv_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(self.output_dir + "image{}.jpg".format(self.frame_index), cv_image)
            self.frame_index += 1
        return image


if __name__ == "__main__":
    print("Hello World")
    image_extractor = ImageExtractor()
    clip = VideoFileClip("loftus_street.mp4")
    out_clip = clip.fl_image(image_extractor.extract_image)  # NOTE: this function expects color images!!
    out_clip.write_videofile("output.mp4", audio=True)
