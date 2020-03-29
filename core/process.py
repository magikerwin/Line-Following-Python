import cv2
import numpy as np

# search object
def searchObject(data):
    """ 
    search object (black pixels) 
    """
    for j in range(data.shape[0]):
        for i in range(data.shape[1]):
            if data[j, i] == 1:
                return i, j
    
def getWindow(LP_RP_pair, image_width, image_height, d=2):
    """
    """
    x_LP, y_LP = LP_RP_pair[0]
    x_RP, y_RP = LP_RP_pair[1]
    xmin = min(x_LP, x_RP) - d
    xmax = max(x_LP, x_RP) + d
    ymin = min(y_LP, y_RP) - d
    ymax = max(y_LP, y_RP) + d
    xmin = np.clip(xmin, 0, image_width - 1)
    xmax = np.clip(xmax, 0, image_width - 1)
    ymin = np.clip(ymin, 0, image_height - 1)
    ymax = np.clip(ymax, 0, image_height - 1)
    return [xmin, ymin, xmax, ymax]
            
def getPerimeterInfos(data, W):
    xmin_W, ymin_W, xmax_W, ymax_W = W
    
    points = []
    values = []
    for x in range(xmin_W, xmax_W):
        points.append([x, ymin_W])
        values.append(data[ymin_W, x])
    for y in range(ymin_W, ymax_W):
        points.append([xmax_W, y])
        values.append(data[y, xmax_W])
    for x in range(xmax_W, xmin_W, -1):
        points.append([x, ymax_W])
        values.append(data[ymax_W, x])
    for y in range(ymax_W, ymin_W, -1):
        points.append([xmin_W, y])
        values.append(data[y, xmin_W])
    return np.array(points), np.array(values)

def getEdgePoints(data, W):
    # get perimeter
    points_perimeter, values_perimeter = getPerimeterInfos(data, W)

    # get edges in perimeter
    mask_left_edges  = 1 - np.roll(values_perimeter, -1)
    mask_right_edges = 1 - np.roll(values_perimeter,  1)
    _ = mask_left_edges * values_perimeter + mask_right_edges * values_perimeter
    indexs_edge = np.squeeze(np.argwhere(_ > 0))
    points_edge = points_perimeter[indexs_edge]    
    return points_edge

def getPointers(points_edge):
    if len(points_edge) == 0:
        return None
            
    elif len(points_edge) == 2:
        # if only one edge point founds, that means left edge and right edge are same.
        if np.ndim(points_edge) == 1: points_edge = np.stack([points_edge, points_edge])
        return [points_edge[0],  # LLP
                points_edge[1],] # RRP
        
    else:
        return [points_edge[0],   # LLP
                points_edge[1],   # LRP
                points_edge[2],   # RLP
                points_edge[-1],] # RRP 

def getSkeletonPoint(W):
    xmin_W, ymin_W, xmax_W, ymax_W = W
    x_keep = xmin_W + (xmax_W - xmin_W)//2
    y_keep = ymin_W + (ymax_W - ymin_W)//2
    return x_keep, y_keep

def updateData(data, W):
    """
    clear pixels exclusively in window
    """
    xmin, ymin, xmax, ymax = W
    data[ymin:ymax+1, xmin:xmax+1] = 0
    #cv2.rectangle(data, (xmin, ymin), (xmax, ymax), 0, cv2.FILLED)
    
def connectPoints(img, point_last, point):
    cv2.line(img, point_last, point, (0, 0, 0))