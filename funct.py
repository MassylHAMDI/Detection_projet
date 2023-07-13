# Our Setup, Import Libaries, Create Function and Download our videos
import cv2
import numpy as np
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from time import strftime
from time import gmtime
import math
 

counter = 0
indice_pixels  = [ ] 

def get_info(cap):
    """
    Get information about a video capture to display it in the terminal.

    Parameters:
    ----------
        cap: VideoCapture object for reading of video.

    """
    # Get the frame width.
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    # Get the frame height.
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # Get the fps.
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    # Get the number of frames in the video.
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    # Ger the time duration. 
    time_duration = frames/fps

    # Print the informations.
    print('________________________ INFO : _________________________')
    print('')
    print('  Time Duration      : ',strftime("%H:%M:%S", gmtime(time_duration)))
    print('  Total Frames       : ',frames)
    print('  Video Height       : ',height)
    print('  Video Width        : ',width)
    print('  Video Fps          : ',fps)  
    print('_________________________________________________________')
    print('')  



def get_shape(image, target_size):
    """
    Calculate the shape information and scaling factors for an image.

    Parameters:
    ----------
        image (numpy.ndarray): The input image as a NumPy array.
        target_size (tuple): The target size (width, height) for the image.

    Returns:
    -------
        tuple: A tuple containing image width, height, width scaling factor,
               and height scaling factor.
    """
    image_width, image_height, _ = image.shape
    newsize_w, newsize_h = target_size
    w_factor = image_width / newsize_w
    h_factor =  image_height / newsize_h

    return image_width, image_height, \
                w_factor, h_factor


def get_center(cap,target_size):
    _, frame = cap.read()
    newsize_w, newsize_h = target_size
    image_width, image_height, w_factor, h_factor = get_shape(frame, (newsize_w, newsize_h))
    first_frame = cv2.resize(frame, (newsize_w, newsize_h))
    cv2.imshow("frame", first_frame)
    cv2.setMouseCallback('frame', click_center)
    # wait for a key to be pressed to exit
    cv2.waitKey(0)
    # close the window
    cv2.destroyAllWindows()
    # Get the center of the cercle
    center = (int(indice_pixels [0][0]*h_factor),int(indice_pixels [0][1]*w_factor))
    return center


def get_coordinate(frame,target_size):
    """
    Get the coordinates and radius of a selected region in a video frame.

    Parameters:
    ----------
        cap: VideoCapture object for reading first frame of video.

    Returns:
    -------
        tuple: A tuple containing the center coordinates (x, y) and the radius of the selected region.
    """
     
    # _, frame = cap.read()
    newsize_w, newsize_h = target_size
    image_width, image_height, w_factor, h_factor = get_shape(frame, (newsize_w, newsize_h))
    first_frame = cv2.resize(frame, (newsize_w, newsize_h))
    cv2.putText(first_frame,'select the center & the point axis(x)',(20,40),cv2.FONT_HERSHEY_COMPLEX_SMALL,1,(255,255,255,2))
    cv2.imshow("frame", first_frame)
    cv2.setMouseCallback('frame', click_event)
    # wait for a key to be pressed to exit
    cv2.waitKey(0)
    # close the window
    cv2.destroyAllWindows()

    # # Pythagorean theorem to get the radius 
    # radius = np.sqrt( int((abs(indice_pixels [0][0]*h_factor-indice_pixels [1][0]*h_factor)**2)) + \
    #                         int((abs(indice_pixels [0][1]*w_factor-indice_pixels [1][1]*w_factor)**2)))
    # # Get the center of the cercle
    # center = (int(indice_pixels [0][0]*h_factor),int(indice_pixels [0][1]*w_factor))
    # return center, radius
    point1 = (int(indice_pixels [0][0]*h_factor),int(indice_pixels [0][1]*w_factor))
    point2 = (int(indice_pixels [1][0]*h_factor),int(indice_pixels [1][1]*w_factor))
    return point1, point2


def click_center(event,x_clic, y_clic, flags, params,numberclick = 1):
    
    """
    Mouse click center for pixel selection.

    Parameters:
    ----------
        event: The type of mouse event.
        x: The x-coordinate of the mouse click.
        y: The y-coordinate of the mouse click.
        flags: Additional flags for the mouse event.
        params: Additional parameters for the mouse event.
        numberclick: The number of clicks required to trigger the event. By default it's 1.
    """

    # Global variables: counter and indice_pixels.
    global counter
    global indice_pixels 
    
    # When the L mouse is cliced the (x, y) coordinates are appended to list and inc counter.
    if event == cv2.EVENT_LBUTTONDOWN:
        counter += 1 
        indice_pixels.append([x_clic,y_clic])

        # If the counter reaches 2, it means that two mouse clicks have been registered.
        if counter == numberclick:
            cv2.destroyAllWindows()



def click_event(event,x_clic, y_clic, flags, params,numberclick = 2):
    
    """
    Mouse click events for pixel selection.

    Parameters:
    ----------
        event: The type of mouse event.
        x: The x-coordinate of the mouse click.
        y: The y-coordinate of the mouse click.
        flags: Additional flags for the mouse event.
        params: Additional parameters for the mouse event.
        numberclick: The number of clicks required to trigger the event. By default it's 2.
    """

    # Global variables: counter and indice_pixels.
    global counter
    global indice_pixels 
    
    # When the L mouse is cliced the (x, y) coordinates are appended to list and inc counter.
    if event == cv2.EVENT_LBUTTONDOWN:
        counter += 1 
        indice_pixels.append([x_clic,y_clic])

        # If the counter reaches 2, it means that two mouse clicks have been registered.
        if counter == numberclick:
            cv2.destroyAllWindows()



def is_video_file(filename):
    """
    Check if the given filename corresponds to a video file.

    Parameters:
    ----------
        filename (str): The name of the file to be checked.


    Returns:
    -------
        (bool): True if the file is a video file (has extension .mp4 or .avi), False otherwise.


    """

    # Extracts the file extension.
    _, extension = os.path.splitext(filename) 

    return extension.lower() == '.mp4' \
            or extension.lower() == '.avi'



def select_file():
    """ 
    This function creates a file dialog box using Tkinter for selecting a file. 

    Returns the selected file path.

    Returns:
    -------
        filename(str) : The name of the file path

    """
    # Create a Tkinter root window
    root = Tk()
    root.withdraw()

    while True:
        # Select a file using the filedialog module
        file_path = askopenfilename()   

        # If the file path is a video file
        if is_video_file(file_path):
            print("Selected file:", file_path)
            break
        
        # Cancel the dialog
        elif isinstance(file_path,str):
            print("No file slected")
            exit()

        # If the file is not a video file
        else:
            print("Please select a valid file")

    return file_path



def get_angle(center, point):
    A = center
    B = point
    C = (B[0],A[1])
    AB = np.sqrt((B[0]-A[0])**2+(B[1]-A[1])**2)
    AC = np.sqrt((C[0]-A[0])**2+(C[1]-A[1])**2)
    ratio = AC/AB
    if point[0] >= center[0] and  point[1] < center[1]:
        alpha = math.degrees(math.acos(ratio))

    elif point[0] < center[0] and  point[1] <= center[1]:
        alpha = 180 - math.degrees(math.acos(ratio)) 

    elif point[0] <= center[0] and  point[1] > center[1]:
        alpha = 180 + math.degrees(math.acos(ratio)) 
    else:
        alpha = 360 - math.degrees(math.acos(ratio)) 
    return alpha