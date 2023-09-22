#!/usr/bin/python3
import cv2
import numpy as np
from os import path
import sys


AR_HEIGHT = 525
AR_WIDTH = 405 
# PTS1 = np.float32([[0, 0], [1, 0], [0, 1], [1, 1]])
PTS2 = np.float32([[0, 0], [AR_WIDTH, 0], [0, AR_HEIGHT], [AR_WIDTH, AR_HEIGHT]])


def draw_grid(image, pixel_per_unit=40, color=(255, 255, 255)):
    """Draw grid lines in 2D view"""
    row = int(AR_HEIGHT / pixel_per_unit)
    column = int(AR_WIDTH / pixel_per_unit)
    for r in range(row + 1):
        y = r * pixel_per_unit
        cv2.line(image, (0, y), (AR_WIDTH, y), color, 1)
    for c in range(column + 1):
        x = c * pixel_per_unit
        cv2.line(image, (x, 0), (x, AR_HEIGHT), color, 1)
    return image


def draw_grid_in_cam(name, image, pixel_per_unit=40):
    """Draw dot grid in camera view"""
    row = int(AR_HEIGHT / pixel_per_unit)
    column = int(AR_HEIGHT / pixel_per_unit)
    # get intersection points of grid
    for r in range(row + 1):
        y = r * pixel_per_unit
        for c in range(column + 1):
            x = c * pixel_per_unit
            color = (int(x*0.8), int(y*0.8), 0)
            # draw the intersection dot in 2d view
            cv2.circle(name, (x,y), 3, color, -1)
            # transform the intersection dot
            if PTS1 is not None and PTS2 is not None:
                cam_x, cam_y = get_2d_point((x, y), PTS2, PTS1)
                # draw the intersection dot in camera view
                cv2.circle(image, (cam_x, cam_y), 2, color, -1)
    return image


def get_2d_point(centroid, points1, points2):
    """Get x and y coordinates that will be used in tracker module"""
    #################################################
    # compute point in 2D map
    # calculate matrix Homo
    homo, status = cv2.findHomography(points1, points2)
    axis = np.array([centroid], dtype='float32') # provide a point you wish to map
    axis = np.array([axis])
    points_out = cv2.perspectiveTransform(axis, homo) # finally, get the mapping
    new_x = int(points_out[0][0][0]) #points at the warped image
    new_y = int(points_out[0][0][1]) #points at the warped image
    return new_x, new_y


def get_loc(cx, cy, pixel_per_unit=40):
    """Convert raw to grid position"""
    cx_2d, cy_2d = get_2d_point((cx, cy), PTS1, PTS2)
    grid_coor_trans = get_grid_position((cx_2d, cy_2d), pixel_per_unit)
    return (cx, cy), grid_coor_trans


def get_grid_position(position, pixel_per_unit):
    """Get grid coordinate"""
    grid_x = int((position[0] / pixel_per_unit) + 0.50)
    grid_y = int((position[1] / pixel_per_unit) + 0.50)
    return grid_x, grid_y


def draw_2d_points(image, cx_2d, cy_2d, pixel_per_unit=40):
    """Draw filled circle on detected object in black 2d space"""
    # grid_coor_raw, grid_coor_trans = get_loc(cx, cy, pixel_per_unit)
    # __id_grid_loc_buffer.append((tracked_id, grid_coor_raw, grid_coor_trans))
    
    # Compute bird's eye coordinates
    b_eye_x = int(cx_2d - (cx_2d % pixel_per_unit))
    b_eye_y = int(cy_2d - (cy_2d % pixel_per_unit))
    cv2.putText(image, 'test', (int(b_eye_x-10), int(b_eye_y-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Fill-in the bird's eye box where a detected person is currently located
    pt1 = b_eye_x, b_eye_y
    pt2 = (int(pt1[0] + pixel_per_unit), int(pt1[1] + pixel_per_unit))
    pt_color = (255, 255, 0)
    cv2.rectangle(image, pt1, pt2, pt_color, -1)

    # draw a circle indicates the location of a detected person in the bird's eye view
    cv2.circle(image, (cx_2d, cy_2d), 10, (255, 255, 255), -1)
    return image


def pt_in_roi(cx, cy, roi_xywh):
    if cx < roi_xywh[0]:
        return False
    elif cx > roi_xywh[0] + roi_xywh[2]:
        return False
    elif cy < roi_xywh[1]:
        return False
    elif cy > roi_xywh[1] + roi_xywh[3]:
        return False
    else:
        return True


class UIControl:
    def __init__(self):
        self.mode = 'init'  # init, select, track
        self.target_tl = (-1, -1)
        self.target_br = (-1, -1)
        self.new_init = True
        self.pt_pos = (-1, -1)

    def mouse_callback(self, event, x, y, flags, param):
        # print(f'inside mouse_callback, mode:{self.mode}')
        if event == cv2.EVENT_LBUTTONDOWN and self.mode == 'init':
            self.target_tl = (x, y)
            self.target_br = (x, y)
            self.mode = 'select'
        elif event == cv2.EVENT_MOUSEMOVE and self.mode == 'select':
            self.target_br = (x, y)
        elif event == cv2.EVENT_LBUTTONDOWN and self.mode == 'select':
            self.target_br = (x, y)
            self.mode = 'init'
            self.new_init = True
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.pt_pos = (x, y)

    def get_tl(self):
        return self.target_tl if self.target_tl[0] < self.target_br[0] else self.target_br

    def get_br(self):
        return self.target_br if self.target_tl[0] < self.target_br[0] else self.target_tl

    def get_bb(self):
        tl = self.get_tl()
        br = self.get_br()

        bb = [min(tl[0], br[0]), min(tl[1], br[1]), abs(br[0] - tl[0]), abs(br[1] - tl[1])]
        return bb

    def get_pt(self):
        return self.pt_pos


if __name__ == '__main__':
    # video_path = '/media/dit-test/UUI/temp_kelvin/People-Flow-Analysis-System/data/test.mp4'
    video_path = sys.argv[1]
    cam = cv2.VideoCapture(video_path)
    frame_rate = cam.get(cv2.CAP_PROP_FPS)  # cam.get(5)
    FPS_MS = int((1/frame_rate)*1000)
    ui_control = UIControl()
    # cv2 windows
    name = path.basename(video_path)
    rect_color = (0, 0, 255)
    play = 1
    selecting = False
    map_opened = False
    mapname = '2D Map'
    pixel_per_unit = 40
    PTS1 = np.float32([[0, 0], [cam.get(3), 0], [0, cam.get(4)], [cam.get(3), cam.get(4)]])
    mapimg = np.zeros((AR_HEIGHT, AR_WIDTH, 3), np.uint8)
    blackimg = np.zeros((AR_HEIGHT, AR_WIDTH, 3), np.uint8)

    cv2.namedWindow(name, cv2.WINDOW_KEEPRATIO)
    cv2.setMouseCallback(name, ui_control.mouse_callback)
    while cv2.getWindowProperty(name, cv2.WND_PROP_VISIBLE)>=1:
        if play:
            ret, img = cam.read()
            # vis = img.copy()
            # cv2.imshow(name, vis)
        vis = img.copy()
        key = cv2.waitKey(FPS_MS)
        if ui_control.mode == 'select' and play:
            play = play ^ 1
            selecting = True
            rect_color = (0, 255, 255)
        elif ui_control.mode == 'init' and selecting:
            play = play ^ 1
            selecting = selecting ^ 1
            rect_color = (0, 0, 255)
            map_opened = True
            cv2.namedWindow(mapname)
            map_control = UIControl()
            blackimg = draw_grid(blackimg, pixel_per_unit)
            cv2.imshow(mapname, blackimg)
    
        if map_opened or cv2.getWindowProperty(mapname, cv2.WND_PROP_VISIBLE)>=1:
            # mapimg =    (blackimg, track_id)
            pt = ui_control.get_pt()
            map_opened = True
            mapimg = blackimg.copy()
            if not pt == (-1, -1):
                inside = pt_in_roi(pt[0], pt[1], ui_control.get_bb())    
                if inside:
                    mapimg = draw_grid(mapimg, pixel_per_unit, (255, 0, 255))
                    cx_2d, cy_2d = get_2d_point(pt, PTS1, PTS2)
                    mapimg= draw_2d_points(mapimg, cx_2d, cy_2d, pixel_per_unit)
                    # print(pt, cx_2d, cy_2d)
            cv2.imshow(mapname, mapimg)
        if ui_control.new_init:
            state = ui_control.get_bb()
            PTS1 = np.float32([[state[0], state[1]], \
                               [state[2] + state[0], state[1]], \
                               [state[0], state[3] + state[1]], \
                               [state[2] + state[0], state[3] + state[1]]])
        cv2.rectangle(vis, (state[0], state[1]), (state[2] + state[0], state[3] + state[1]), rect_color, 5)
        cv2.imshow(name, vis)
        
        # key = cv2.waitKey(5)
        if 0xFF & key == 27 or key == ord('q'):  # Esc
            break
        elif 0xFF & key == 13 or 0xFF & key == 32 or key == ord('p'):  # Enter or Space
            play = play ^ 1
    cv2.destroyAllWindows()
