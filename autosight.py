from moviepy.editor import VideoFileClip


def process_video_image(image):
    return image


if __name__ == "__main__":
    print("Hello World")
    clip = VideoFileClip("loftus_street.mp4")
    out_clip = clip.fl_image(process_video_image)  # NOTE: this function expects color images!!
    out_clip.write_videofile("output.mp4", audio=True)
