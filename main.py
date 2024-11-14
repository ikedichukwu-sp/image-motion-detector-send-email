import glob
import os
import cv2
import time
from emailing import send_email
from threading import Thread

# Initialize video capture from the default camera
video = cv2.VideoCapture(0)
time.sleep(1)  # Allow the camera to initialize

# Variables for storing the first frame, movement status, and image count
first_frame = None
status_list = []
count = 1


# Function to clean up the 'images' folder by deleting all .png files
def clean_folder():
    print("clean folder function started")
    images = glob.glob("images/*.png")  # List all images in the folder
    for image in images:
        try:
            os.remove(image)  # Attempt to delete each image
        except PermissionError:
            print(f"Could not delete {image} as it is still in use.")
    print("clean folder function ended")


# Main loop for video processing
while True:
    status = 0  # Status to check if motion is detected
    check, frame = video.read()  # Capture a frame from the video

    # Convert the frame to grayscale and apply Gaussian blur for motion detection
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_frame_gau = cv2.GaussianBlur(gray_frame, (21, 21), 0)

    # Set the first frame as a reference for detecting motion
    if first_frame is None:
        first_frame = gray_frame_gau

    # Compute the difference between the current frame and the first frame
    delta_frame = cv2.absdiff(first_frame, gray_frame_gau)
    # Apply thresholding to the delta frame to highlight motion areas
    thresh_frame = cv2.threshold(delta_frame, 60, 255, cv2.THRESH_BINARY)[1]
    # Dilate the thresholded frame to fill in gaps
    dil_frame = cv2.dilate(thresh_frame, None, iterations=2)
    cv2.imshow("my video", dil_frame)  # Display the processed frame for debugging

    # Find contours (boundaries) in the dilated frame
    contours, _ = cv2.findContours(dil_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv2.contourArea(contour) < 5000:  # Ignore small contours
            continue
        # Draw a rectangle around the detected motion
        x, y, w, h = cv2.boundingRect(contour)
        rectangle = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

        if rectangle.any():
            status = 1  # Set status to indicate motion detection
            # Save the current frame to the 'images' folder
            cv2.imwrite(f"images/{count}.png", frame)
            count += 1
            all_images = glob.glob("images/*.png")  # List all saved images

            # Select the middle image for emailing
            if all_images:  # Ensure there are images
                index = int(len(all_images) / 2)
                image_with_object = all_images[index]
            else:
                image_with_object = None  # No images to process

    # Update status list to track recent motion states
    status_list.append(status)
    status_list = status_list[-2:]

    # If motion stopped (status 1 -> 0) and an image was captured, send email and clean up
    if status_list[0] == 1 and status_list[1] == 0 and image_with_object:
        # Start a thread for sending the email with the selected image
        email_thread = Thread(target=send_email, args=(image_with_object,))
        email_thread.daemon = True
        email_thread.start()

        # Delay to ensure image saving is complete before cleaning
        time.sleep(2)  # Delay for system processing

        # Start a thread for cleaning the images folder
        clean_thread = Thread(target=clean_folder)
        clean_thread.daemon = True
        clean_thread.start()

    print(status_list)  # Print the status list for debugging
    cv2.imshow("video", frame)  # Display the original frame
    key = cv2.waitKey(1)

    # Break the loop if 'q' key is pressed
    if key == ord("q"):
        break

video.release()  # Release the video capture object
