#%% 

from math import degrees, radians

from arena import Arena 
from game import Game

center = .88888

arena = Arena()



def begin_again():
    arena.begin()
    update_pic()
    
def update_pic():
    rgb = arena.obs()
    obs_plot.create_plot(rgb)
    
def wall_bump():
    game.add_object(
    " YOU BUMPED A WALL ", 
    size = (.4, .1), pos = (center - .2, "center"),
    color = (1, 1, 1), text_color = (255,255,255),
    fade_time = 1.5)
    
def ending(text):
    def begin_again_with_reward():
        game.remove_object(text)
        begin_again()
    game.add_object(
    text, 
    size = (.4, .1), pos = (center - .2, "center"),
    color = (1, 1, 1), text_color = (255,255,255),
    click = begin_again_with_reward)

def move_forward():
    pos, yaw = arena.get_pos_yaw()
    deg = round(degrees(yaw) % 360)
    if(deg == 0):   new_pos = (pos[0] - 1, pos[1],     pos[2])
    if(deg == 90):  new_pos = (pos[0],     pos[1] - 1, pos[2])
    if(deg == 180): new_pos = (pos[0] + 1, pos[1],     pos[2])
    if(deg == 270): new_pos = (pos[0],     pos[1] + 1, pos[2])
    if(not (new_pos[0], new_pos[1]) in arena.locs):
        arena.resetBasePositionAndOrientation(new_pos, yaw)
    else: wall_bump()
    update_pic() 
    end, which = arena.end_collisions()
    if(end):
        if(which == "LEFT"):  ending(" REWARD of 1 ")
        if(which == "RIGHT"): ending(" REWARD of 10 ")

def turn_left():
    pos, yaw = arena.get_pos_yaw()
    yaw = radians(round(degrees(yaw) + 90))
    arena.resetBasePositionAndOrientation(pos, yaw)
    update_pic() 

def turn_right():
    pos, yaw = arena.get_pos_yaw()
    yaw = radians(round(degrees(yaw) - 90))
    arena.resetBasePositionAndOrientation(pos, yaw)
    update_pic()
    
    

game = Game()
obs_plot = game.add_object(
    "obs_plot", 
    size = (.5, .5), pos = (center - .25, .25),
    color = (1, 1, 1), text_color = (1,1,1))
forward = game.add_object(
    " FORWARD ", 
    size = (.2, .1), pos = (center - .1, .85),
    color = (1, 1, 1), text_color = (255,255,255),
    click = move_forward)
left = game.add_object(
    " LEFT ", 
    size = (.2, .1), pos = (center - .5, .85),
    color = (1, 1, 1), text_color = (255,255,255),
    click = turn_left)
right = game.add_object(
    " RIGHT ", 
    size = (.2, .1), pos = (center + .3, .85),
    color = (1, 1, 1), text_color = (255,255,255),
    click = turn_right)
restart = game.add_object(
    " START ", 
    size = (.2, .1), pos = (center -.1, .05),
    color = (1, 1, 1), text_color = (255,255,255),
    click = begin_again)
game.run()



# %%
