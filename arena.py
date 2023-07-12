#%%
import pandas as pd
import numpy as np
import pybullet as p
import cv2
from math import pi, sin, cos

class Exit:
    def __init__(self, name, pos, rew):     # Position (Y, X)
        self.name = name ; self.pos = pos ; self.rew = rew
        
class Arena_Description:
    def __init__(self, start, exits):
        self.start = start 
        self.exit_list = exits
        self.exits = pd.DataFrame(
            data = [[exit.name, exit.pos, exit.rew] for exit in exits],
            columns = ["Name", "Position", "Reward"])
        
        
        
arena_dict = {
    "t.png" : Arena_Description(
        (3, 1),
        [Exit(  "LEFT",     (2,0), "default"),
        Exit(   "RIGHT",    (2,4), "better")]
        )}



def get_physics(GUI, w, h):
    if(GUI):
        physicsClient = p.connect(p.GUI)
        p.resetDebugVisualizerCamera(1,90,-89,(w/2,h/2,w), physicsClientId = physicsClient)
    else:   
        physicsClient = p.connect(p.DIRECT)
    p.setAdditionalSearchPath("pybullet_data/")
    return(physicsClient)



class Arena():
    def __init__(self, arena_name = "t"):
        if(not arena_name.endswith(".png")): arena_name += ".png"
        self.start = arena_dict[arena_name].start
        self.exits = arena_dict[arena_name].exits
        arena_map = cv2.imread("arenas/" + arena_name)
        w, h, _ = arena_map.shape
        self.physicsClient = get_physics(True, w, h)
        
        plane_positions = [[0, 0, 0], [10, 0, 0], [0, 10, 0], [10, 10, 0]]
        plane_ids = []
        for position in plane_positions:
            plane_id = p.loadURDF("plane.urdf", position, globalScaling=.5, useFixedBase=True, physicsClientId=self.physicsClient)
            plane_ids.append(plane_id)

        self.ends = {} ; self.colors = {} ; self.locs = []
        for loc in ((x, y) for x in range(w) for y in range(h)):
            pos = [loc[0], loc[1], .5]
            if ((arena_map[loc] == [255]).all()):
                if (not self.exits.loc[self.exits["Position"] == loc].empty):
                    row = self.exits.loc[self.exits["Position"] == loc]
                    end_pos = ((pos[0] - .5, pos[0] + .5), (pos[1] - .5, pos[1] + .5))
                    self.ends[row["Name"].values[0]] = (end_pos, row["Reward"].values[0])
            else:
                ors = p.getQuaternionFromEuler([0, 0, 0])
                color = arena_map[loc][::-1] / 255
                color = np.append(color, 1)
                cube = p.loadURDF("cube.urdf", (pos[0], pos[1], pos[2]), ors, 
                                  useFixedBase=True, physicsClientId=self.physicsClient)
                self.colors[cube] = color
                self.locs.append((pos[0], pos[1]))
        
        for cube, color in self.colors.items():
            p.changeVisualShape(cube, -1, rgbaColor = color, physicsClientId = self.physicsClient)

        inherent_roll = pi/2
        inherent_pitch = 0
        yaw = 0
        file = "ted_duck.urdf"
        pos = (self.start[0], self.start[1], .5)
        orn = p.getQuaternionFromEuler([inherent_roll, inherent_pitch, yaw])
        self.body_num = p.loadURDF(file, pos, orn,
                           globalScaling = 2, 
                           physicsClientId = self.physicsClient)
        p.changeDynamics(self.body_num, 0, maxJointVelocity=10000)
        p.changeVisualShape(self.body_num, -1, rgbaColor = [1,0,0,1], physicsClientId = self.physicsClient)
        
    def begin(self):
        yaw = 0
        spe = 0
        pos = (self.start[0], self.start[1], .5)
        self.resetBasePositionAndOrientation(pos, yaw)
        
    def get_pos_yaw(self):
        pos, ors = p.getBasePositionAndOrientation(self.body_num, physicsClientId = self.physicsClient)
        yaw = p.getEulerFromQuaternion(ors)[-1]
        return(pos, yaw)
    
    def resetBasePositionAndOrientation(self, pos, yaw):
        inherent_roll = pi/2
        inherent_pitch = 0
        orn = p.getQuaternionFromEuler([inherent_roll, inherent_pitch, yaw])
        p.resetBasePositionAndOrientation(self.body_num, pos, orn, physicsClientId = self.physicsClient)
        
    def obs(self):
        pos, yaw = self.get_pos_yaw()
        x, y = cos(yaw), sin(yaw)
        view_matrix = p.computeViewMatrix(
            cameraEyePosition = [pos[0], pos[1], .4], 
            cameraTargetPosition = [pos[0] - x, pos[1] - y, .4], 
            cameraUpVector = [0, 0, 1], physicsClientId = self.physicsClient)
        proj_matrix = p.computeProjectionMatrixFOV(
            fov = 90, aspect = 1, nearVal = .01, 
            farVal = 10, physicsClientId = self.physicsClient)
        _, _, rgba, _, _ = p.getCameraImage(
            width=512, height=512,
            projectionMatrix=proj_matrix, viewMatrix=view_matrix, shadow = 0,
            physicsClientId = self.physicsClient)
        rgb = np.divide(rgba[:,:,:-1], 255)
        return(rgb)
    
    def pos_in_box(self, box):
        (min_x, max_x), (min_y, max_y) = box 
        pos, _ = self.get_pos_yaw()
        in_x = pos[0] >= min_x and pos[0] <= max_x 
        in_y = pos[1] >= min_y and pos[1] <= max_y 
        return(in_x and in_y)
    
    def end_collisions(self):
        col = False
        which = None
        for end_name, (end, end_reward) in self.ends.items():
            if self.pos_in_box(end):
                col = True
                which = end_name
        return(col, which)
        
                

if __name__ == "__main__":
    arena = Arena()
# %%