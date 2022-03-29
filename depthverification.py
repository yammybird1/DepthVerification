import numpy as np
import pandas as pd
import cv2 as cv
from PIL import Image
import sys
import os
from plyfile import PlyData, PlyElement
import statistics
import csv

mouse_input = False

dir = sys.argv[1] 
input_csv_dir = sys.argv[2]
input_csv_filename = sys.argv[3]
newcsv_name = sys.argv[4]

# mouse callback function
# Create a black image, a window and bind the function to window
leftimg = cv.imread(os.path.join(dir, 'left_00.jpg'))

depthimg = Image.open(os.path.join(dir, 'depth1_00.tiff'))
deptharray = np.array(depthimg) 
  
leftR = cv.rotate(leftimg, cv.ROTATE_180)
imageL = cv.rotate(leftR, cv.ROTATE_90_CLOCKWISE)
depthR = cv.rotate(deptharray, cv.ROTATE_180)
imageD = cv.rotate(depthR, cv.ROTATE_90_CLOCKWISE)
points = np.zeros((10,2))
expdepth = np.zeros((250,2))
i = 0
j = 0
row1 = 0
row2 = 25

def get_depth_information(event,x, y, flags, param):
    if event == cv.EVENT_LBUTTONDBLCLK:
        # global i 
        global row1
        row1 = 0
        print(f"x: {x}, y: {y}, d: {imageD[y][x]}")
        #cv.putText(leftimg,str(depthimg[y][x]),(x,y),cv.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)
        cv.putText(imageL,str(imageD[y][x]),(x,y),cv.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)
        cv.rectangle(imageL, (x-2,y-2), (x+2,y+2), color=(0,0,255), thickness=10)

        points[row1, j] = x
        points[row1, j + 1] = y

        print(points)
        row1 += 1


def get_depth(csvpoints):
    point = 0
    table = np.zeros((250,1))
    global row1
    global row2
    row1 = 0
    row2 = 25
    for point in range(len(csvpoints)):
        x, y = int(csvpoints.x[point]), int(csvpoints.y[point])
        print(f"x: {x}, y: {y}, d: {imageD[y][x]}")

        depths = imageD[y-2:y+3, x-2:x+3]
        
        depths = depths.flatten()

        table[row1:row2, j] = depths

        row1 += 25
        row2 += 25
        
    print(table)
    return table

def main():
    global points
    global expdepth
    global row1
    global row2
    row1 = 0
    row2 = 25
    if mouse_input:
        cv.namedWindow('image', cv.WINDOW_NORMAL)
        cv.setMouseCallback('image',get_depth_information)
        while(1):                 
            cv.imshow("image", imageL) 
            cv.resizeWindow('image', 1000, 1000) 
            if cv.waitKey(20) & 0xFF == 27:
                break
    elif mouse_input == False:
        # read point coordinates from the csv
        csvreader = pd.read_csv(os.path.join(input_csv_dir, input_csv_filename))
        for element in range(10):
            expdepth[row1:row2 , 0] = csvreader.x[element]
            expdepth[row1: row2, 1] = csvreader.y[element]
            row1 += 25
            row2 += 25
            
        # use a loop to get depths for all the images of different exposure
        pic = 0
        global imageD
        for pic in range(8):
            depthimg = Image.open(os.path.join(dir, 'depth1_0' + str(pic) + '.tiff'))
            deptharray = np.array(depthimg) 
            depthR = cv.rotate(deptharray, cv.ROTATE_180)
            imageD = cv.rotate(depthR, cv.ROTATE_90_CLOCKWISE)
            depthpoints = get_depth(csvreader)
            expdepth = np.append(expdepth, depthpoints, axis = 1)
           
    if mouse_input:
        df = pd.DataFrame({'x': points[:, 0], # set x values in first column
                           'y': points[:, 1]}, # set y values in second column, # set depth values in third column} 
                         ) 
        
        df.to_csv(f'/mnt/sda1/zed_depth_camera/{input_csv_filename}.csv', index = False, header=True)
        print(points)
        print(df)
    elif mouse_input == False:
        df = pd.DataFrame({'x': expdepth[:, 0], # set x values in first column
        'y': expdepth[:, 1], # set y values in second column
        'd0': expdepth[:, 2],
        'd1': expdepth[:, 3],
        'd2': expdepth[:, 4], # set depth values in third column
        'd3': expdepth[:, 5],
        'd4': expdepth[:, 6],
        'd5': expdepth[:, 7],
        'd6': expdepth[:, 8],
        'd7': expdepth[:, 9],} 
            ) 
        df.to_csv(f'/mnt/sda1/zed_depth_camera/{newcsv_name}.csv', index = False, header=True)
        print(expdepth)
        print(df)

    cv.destroyAllWindows()


if __name__ == "__main__":
    main()


# from 1633