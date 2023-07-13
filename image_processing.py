import cv2
import numpy as np


class ImageProcessing:
    def __init__(self):
        pass

    def resize_image(self, image, width, height):
        """Resizes the image.

        Args:
            image (numpy.ndarray): The image to resize.
            width (int): The desired width.
            height (int): The desired height.

        Returns:
            numpy.ndarray: The resized image.
        """
        return cv2.resize(image, (width, height))

    def save_image(self,image,image_name):
        """Resizes the image.

        Args:
            image (numpy.ndarray): The image to resize.
            image_name(str): The name of image.

        Returns:
            None
        """
        cv2.imwrite(f"{image_name}.png",image)
        

    def convert_to_grayscale(self, image):
        """Converts the image to grayscale.

        Args:
            image (numpy.ndarray): The image to convert.

        Returns:
            numpy.ndarray: The image converted to grayscale.
        """
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def rotate_image(self, image, deg, center):
        """Rotates the image around the given center.

        Args:
            image (numpy.ndarray): The image to rotate.
            deg (float): The rotation angle in degrees.
            center (tuple): The (x, y) coordinates of the rotation center.

        Returns:
            numpy.ndarray: The image after rotation.
        """
        if len(image.shape) == 3:
            rows, cols, c = image.shape
        else:
            rows, cols    = image.shape
        M = cv2.getRotationMatrix2D(center, deg, 1)
        return cv2.warpAffine(image, M, (cols, rows))

    def mask_image(self, image, center, radius):
        """Applies a circular mask to the image to keep only a region of interest.

        Args:
            image (numpy.ndarray): The image to mask.
            center (tuple): The (x, y) coordinates of the center of the circle.
            radius (int): The radius of the circle.

        Returns:
            numpy.ndarray: The masked image with the region of interest.
        """
        mask = np.zeros_like(image)
        mask = cv2.circle(mask, center, radius, (255, 255, 255), -1)
        return cv2.bitwise_and(image, mask)

    def draw_axes(self, image, center, radius):
        """Draws a horizontal and vertical axis on the image.

        Args:
            image (numpy.ndarray): The image on which to draw the axes.
            center (tuple): The (x, y) coordinates of the circle center.
            radius (int): The radius of the circle.

        Returns:
            numpy.ndarray: The image with the axes drawn.
        """
        x0    = center[0]
        y0    = center[1]
        y1    = center[1]
        x1    = int(np.sqrt(radius**2 - (y1 - y0)**2) + x0)
        image = cv2.arrowedLine(image, (x0 - radius, y0), (x1, y1), (250, 255, 0), 1, line_type=1, tipLength=0.02)

        x0    = center[0]
        y0    = center[1]
        x1    = center[0]
        y1    = int(np.sqrt(radius**2 - (x1 - x0)**2) + y0)
        image = cv2.arrowedLine(image, (x1, y1), (x0, y0 - radius), (250, 255, 0), 1, line_type=1, tipLength=0.02)

        return image

    
    def apply_threshold(self, framediff, min_threshold):
        """Applies a binary threshold to the difference image and finds the contours.

        Args:
            framediff (numpy.ndarray): The difference image.
            min_threshold (int): The threshold value.

        Returns:
            tuple: A pair containing the thresholded image and the contours.
        """
        _, frame_thresh = cv2.threshold(framediff.copy(), min_threshold, 255, cv2.THRESH_BINARY)
        contours, _     = cv2.findContours(frame_thresh, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_SIMPLE)
        contours        = sorted(contours, key=cv2.contourArea, reverse=True)
        return frame_thresh, contours
    

class BackgroundSubtraction(ImageProcessing):
    def __init__(self):
        super().__init__()
        pass

    #
    def compute_frame_difference(self,previous_frame, current_frame, center, radius, angle, threshold):
        """Computes the difference between two images and applies a binary threshold to find the contours.

        Args:
            image1 (numpy.ndarray): The i-th image.
            image2 (numpy.ndarray): The i+1-th image.
            center (tuple): The (x,y) coordinates of the center of the region of interest circle.
            radius (int): The radius of the region of interest circle.
            deg (float): The rotation angle in degrees.
            min_threshold (int): The threshold value.

        Returns:
            tuple: A pair containing the thresholded image and the contours.
        """
        previous_frame = self.convert_to_grayscale(previous_frame)
        current_frame  = self.convert_to_grayscale(current_frame)
        
        previous_frame = self.mask_image(previous_frame, center, radius)
        current_frame  = self.mask_image(current_frame, center, radius)

        previous_frame = self.rotate_image(previous_frame, angle, center)
        current_frame  = self.rotate_image(current_frame, angle, center)

        frame_diff = cv2.absdiff(previous_frame, current_frame)

        return self.apply_threshold(frame_diff, threshold)


    # TEST FUNCTION
    def compute_frame_difference2(self, image1, image2, center, radius, deg, min_threshold):
       frame1 = self.convert_to_grayscale(image1)
       frame2 = self.convert_to_grayscale(image2)

       frame1 = self.mask_image(frame1, center, radius)
       frame2 = self.mask_image(frame2, center, radius)

       frame1 = self.rotate_image(frame1, deg, center)
       frame2 = self.rotate_image(frame2, deg, center)

       img_diff0 = cv2.absdiff(frame2, frame1)
       img_diff1 = cv2.absdiff(frame1, frame2)

       frame_diff = cv2.bitwise_or(img_diff0,img_diff1)

       return self.apply_threshold(frame_diff,min_threshold)
    

    def temporal_frame_difference(self, reference_frame, current_frame, center, radius, angle, threshold):
        """Performs temporal frame differencing between the reference frame and a given frame,
        then applies binary thresholding and finds contours.

        Args:
            reference_frame (numpy.ndarray): The reference frame.
            current_frame (numpy.ndarray): The frame to compare.
            center (tuple): The (x, y) coordinates of the center of the circular region of interest.
            radius (int): The radius of the circular region of interest.
            angle (float): The rotation angle in degrees.
            threshold (int): The threshold value.

        Returns:
            tuple: A pair containing the thresholded image and the contours.
        """
        alpha = 0.01
        reference_frame = self.convert_to_grayscale(reference_frame)
        current_frame   = self.convert_to_grayscale(current_frame)
        
        reference_frame = self.mask_image(reference_frame, center, radius)
        current_frame   = self.mask_image(current_frame, center, radius)

        reference_frame = self.rotate_image(reference_frame, angle, center)
        current_frame   = self.rotate_image(current_frame, angle, center)

        background = ((1 - alpha) * reference_frame + alpha * current_frame).astype(np.uint8)
        
        frame_diff = cv2.absdiff(current_frame, background)

        return self.threshold(frame_diff, threshold)

    def mean_filter(self, image_sequence, current_image, center, radius, angle, threshold):
        """Applies a mean filter to a sequence of images,
        then applies binary thresholding and finds contours.

        Args:
            image_sequence (list): The sequence of images.
            current_image (numpy.ndarray): The i+1th image.
            center (tuple): The (x, y) coordinates of the center of the circular region of interest.
            radius (int): The radius of the circular region of interest.
            angle (float): The rotation angle in degrees.
            threshold (int): The threshold value.

        Returns:
            tuple: A pair containing the thresholded image and the contours.
        """
        frames        = self.convert_to_grayscale(image_sequence)
        current_image = self.convert_to_grayscale(current_image)

        frames        = self.mask_image(frames, center, radius)
        current_image = self.mask_image(current_image, center, radius)

        frames        = self.rotate_image(frames, angle, center)
        current_image = self.rotate_image(current_image, angle, center)
        
        mean_frame.append(frames)
        if len(mean_frame) == 30:
            mean_frame.pop(0)
        mean_frame = np.array(mean_frame)
        mean_frame = np.mean(mean_frame, axis=0).astype(dtype=np.uint8)
        frame_diff = cv2.absdiff(mean_frame, current_image).astype(np.uint8)
        return self.threshold(frame_diff, threshold)