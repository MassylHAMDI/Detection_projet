# Our Setup, Import Libaries, Create Function and Download our videos
import cv2
import numpy as np
import os
import sys
from tqdm import tqdm
from funct import get_coordinate, get_info, select_file, get_angle
import argparse
from image_processing import BackgroundSubtraction, ImageProcessing
from file_formatting import FileFormatting

def on_track(val):
     return val

def run ():      

    chemin_fichier = 'fichier01.xlsx'
    file = FileFormatting(chemin_fichier)
    file_name = select_file()
    file.load_file()


    cap = cv2.VideoCapture(file_name)

    # Reads the first frame of the video
    _, first_frame = cap.read()

    # get infis of the video
    get_info(cap)

    # Get the coordinates of the center and a reference point in the first frame.
    center,point_ref = get_coordinate(first_frame, (900, 900))

    # Calculate the angle between the old axis and reference point.
    deg = get_angle(center, point_ref) 

    Frame_traitment = ImageProcessing()
    # Rotate the video by the calculated angle around the center to get the new axis.
    # rotated_img = rotate_image(first_frame,-deg,center)
    rotated_img =Frame_traitment.rotate_image(first_frame, -deg, center) 
 

    # Create a presettings and settings windeows
    cv2.namedWindow('Presettings',cv2.WINDOW_NORMAL) #

    cv2.resizeWindow("Presettings", 640, 200) 

    cv2.createTrackbar('raduis'       ,'Presettings', 255, 1024, on_track  ) 
    while True :
        # Get the current trackbar position
        raduis = cv2.getTrackbarPos('raduis', 'Presettings'                   )
        frame__ = Frame_traitment.mask_image(rotated_img,center, raduis)
        frame__= Frame_traitment.draw_axes(frame__ ,center ,raduis)
        cv2.imshow('réglage', frame__)
        key = cv2.waitKey(1)
        if key == ord('q') or key == ord('Q'):
            break
    cv2.destroyAllWindows()
    
    Method = 'previous frame'
    frame1 = None

    cv2.namedWindow('Settings',cv2.WINDOW_FREERATIO) #
    cv2.resizeWindow("Settings", 640, 200) 
    cv2.createTrackbar("Seuil",'Settings', 30, 255, on_track)
    cv2.createTrackbar('minarea'  ,'Settings', 40, 200, on_track)
    cv2.createTrackbar('State','Settings', 0  , 1  ,on_track)      

    ligne_depart = 35  # Par exemple, commencer à partir de la ligne 35
    # feuille.insert_rows(ligne_depart)

    #initialisation des entéte 
    list_adjust = ['A','B','C','D']
    for i in list_adjust:
        file.width_adjustment(i, 20)
        
    
    entete_list = ['FRAME', 'Cordonnee (x,y)', 'Largeur', 'Hauteur']
    file.headers(entete_list, 34)

    # Get total number of frames for tqdm
    total_Frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) 
    # Progress Bar

    detect = 0
    crop = True
    if first_frame.shape[0]>2000:
        crop = False
    Fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    with tqdm(total=total_Frames,desc= "progress bar", bar_format='{l_bar}{bar:38}{r_bar:10}') as thebar:
        frame_count = 0
        frame_skip = 10
        while True:
            ret, frame = cap.read()
            vid = frame
            thebar.update(1)
            

            if ret == True:

                min_threshold  = cv2.getTrackbarPos('Seuil','Settings'  )
                min_sizearea   = cv2.getTrackbarPos('minarea' ,'Settings'  )
                Stat_detection = cv2.getTrackbarPos('State' ,'Settings')


                

                if Stat_detection == 1 :

                    if    Method == 'previous frame'   and frame1 is None:
                        frame1 = frame
                        continue 
                    elif  Method == 'Frame_diff_i' and frame1 is None:  
                        frame1 = first_frame
                        continue
                    elif Method == 'mean frame' and frame1 is None:
                        
                        frame1 = frame
                        continue

                    image_diff = BackgroundSubtraction()
                    
                    frame_thresh, contours  = image_diff.compute_frame_difference(first_frame, frame, center, raduis,-deg,min_threshold)
                    

                    for cnt in contours:
                        # print(len(cnt))
                        if cv2.contourArea(cnt) < min_sizearea:
                                continue
                        if detect == 0 :
                            detect += 1
                            frame_firstdetect = frame_count
                        (x,y,w,h) = cv2.boundingRect(cnt)
                        point = (x,y)
                        # if frame_count % frame_skip == 0:
                        nouvelle_ligne = [f"frame{frame_count}",str(point),w,h]
                        if frame_count % frame_skip == 0:
                            file.add_line(line = nouvelle_ligne, line_number= ligne_depart)
                            file.alignment_line(line_number=ligne_depart)
                            ligne_depart += 1
                        cv2.rectangle(vid,(x,y),(x+w,y+h),(0,255,10),3)
                        cv2.putText(vid,'crack Detected',(20,40),cv2.FONT_HERSHEY_COMPLEX_SMALL,1,(0,255,0,2))
                        
                    kernel = np.ones((3,3),np.uint8)
                    frame_thresh    = cv2.erode(frame_thresh,kernel,iterations =1)
                vid = cv2.resize(vid,(800,800)) 
                cv2.imshow('frame',vid)
                if Stat_detection == 1 :
                    frame_thresh = cv2.resize(frame_thresh,(800,800))
                    cv2.imshow('BGS',frame_thresh)
                frame_count += 1 
                key = cv2.waitKey(1)
                if key == ord('q') or key == ord('Q'):
                    break
            else :
                break
        
        

        cap.release()# release video file
        cv2.destroyAllWindows() # Closes all the frames

    file.merge_cells(start_line=3,number_of_lines=9)
    file.Resume_info(total_Frames, Fps, frame_firstdetect, crop, raduis)

    file.save_file()

run()     
