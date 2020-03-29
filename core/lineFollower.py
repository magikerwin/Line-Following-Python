import os
import cv2
import numpy as np
import matplotlib as mpl
import logging

from core.process import searchObject, getWindow, getPerimeterInfos, getEdgePoints, getPointers, getSkeletonPoint, updateData, connectPoints
from core.utils import plotPoint, plotWindow

class LineFollower():
    def __init__(self, d=2, black_text=True):
        self.d = d
        self.black_text = black_text
        
        self._history = {
            "img_src"  : None,
            "img_dst"  : None,
            "pointers" : [],
            "skeleton" : [],
        }
        
    def process(self, img_src):
        if not self.black_text: img_src = 255 - img_src
        
        img_dst = self._pipeline(img_src)
        
        if not self.black_text: img_dst = 255 - img_dst
        
        return img_dst
    
    def _pipeline(self, img_src):
        input_h, input_w = img_src.shape[:2]

        img_dst = np.ones_like(img_src, np.uint8) * 255
        data = cv2.cvtColor(img_src, cv2.COLOR_BGR2GRAY)
        data = np.clip(255 - data, 0, 1)        
                
        pointers_total   = []
        skeleton_total   = []
        pointers_pending = []
        skeleton_pending = []
        
        process = False
        while True:

            if not process:
                point_encounter = searchObject(data)
                if point_encounter is None:
                    logging.info('No object found! [Done]')
                    break
                else:
                    logging.info('Encounter object!')
                    process = True
                    pointers = [np.array(point_encounter), np.array(point_encounter)]
                    pointers_total.append(pointers)
                    skeleton_total.append(point_encounter)

            else:
                W = getWindow(pointers_total[-1][:2], input_w, input_h, self.d)
                points_edge = getEdgePoints(data, W)
                pointers = getPointers(points_edge)
                updateData(data, W)
                skeleton_total.append(getSkeletonPoint(W))

                ## check
                if pointers is None:
                    logging.info('End-of-Line!')
                    pointers_total.append([])
                    if len(pointers_pending) == 0:
                        logging.info('This object done!')
                        process = False
                    else:
                        logging.info("Back to pending branch")
                        pointers_total.append(pointers_pending.pop())
                        skeleton_total.append(skeleton_pending.pop())
                        continue

                elif len(pointers) == 2:
                    logging.info('Single-Branch')
                    pointers_total.append(pointers)
                else:
                    logging.info('Multi-Branch')
                    pointers_total.append(pointers)
                    pointers_pending.append(pointers[2:])
                    skeleton_pending.append(skeleton_total[-1])

                # export skeleton
                connectPoints(img_dst, skeleton_total[-2], skeleton_total[-1])
           
        # update history
        self._history["img_src"]  = img_src
        self._history["img_dst"]  = img_dst
        self._history["pointers"] = pointers_total
        self._history["skeleton"] = skeleton_total
        
        return img_dst
    
    def display_history(self, limit_steps=5, export_directory_path=None):
        if len(self._history["skeleton"]) == 0:
            print("No history found!")
            return
        
        img_process = self._history["img_src"].copy()
        img_skeleton = np.ones_like(img_process, np.uint8) * 255
        input_h, input_w = img_process.shape[:2]

        cols = 2
        rows = len(self._history["pointers"])
        fig = plt.figure(figsize=(cols*3, rows*3))

        for time_id, pointers in enumerate(self._history["pointers"]):
            
            if time_id == limit_steps: break
            
            # 1. display processing 
            ax1 = plt.subplot(rows, cols, cols * time_id + 1)
            ax1.set_xticklabels([])
            ax1.set_yticklabels([])

            if len(pointers) > 0:
                # plot current pointers
                plotPoint(pointers[0], 'red')
                plotPoint(pointers[1], 'red')

                # plot window
                W = getWindow(pointers[:2], input_w, input_h, self.d)
                plotWindow(W)

                # plot next pointers
                if time_id != (len(self._history["pointers"]) - 1):
                    for point_id, point in enumerate(self._history["pointers"][time_id+1]):
                        if point_id < 2:
                            plotPoint(point, 'green')
                        else:
                            plotPoint(point, 'blue')

                # clear window
                img_process[W[1]:W[3]+1, W[0]:W[2]+1] = 255


            plt.imshow((img_process*0.7 + img.copy()*0.3).astype(np.uint8), cmap='gray')
            plt.grid()
            plt.xticks(np.arange(0.5, input_w, step=1))
            plt.yticks(np.arange(0.5, input_h, step=1))
            plt.title("Processing")
            plt.text(-input_w/2, input_h/2, f"T={time_id}", fontsize=15)

            # display output skeleton
            ax2 = plt.subplot(rows, cols, cols * time_id + 2)
            ax2.set_xticklabels([])
            ax2.set_yticklabels([])
            if len(pointers) > 0:
                connectPoints(img_skeleton, self._history["skeleton"][time_id], self._history["skeleton"][time_id+1])

            plt.imshow(img_skeleton, cmap='gray')
            plt.grid()
            plt.xticks(np.arange(0.5, input_w, step=1))
            plt.yticks(np.arange(0.5, input_h, step=1))
            plt.title("Skeleton")
            
            # Save display image in specified directory
            if export_directory_path is not None:
                if os.path.exists(export_directory_path):
                    assert(0), f"the export directory already exists! \"{export_directory_path}\""
                else:
                    os.makedirs(export_directory_path)
                
                extent1 = ax1.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
                extent2 = ax2.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
                extent  = mpl.transforms.Bbox(np.array([extent1.get_points()[0],
                                                        extent2.get_points()[1]]))
                plt.savefig(os.path.join(export_directory_path, f'{time_id:05d}.png'),
                            bbox_inches=extent.expanded(1.4, 1.3))
            
        