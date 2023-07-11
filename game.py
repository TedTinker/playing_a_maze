import pygame
from pygame.locals import RESIZABLE, VIDEOEXPOSE

from time import time

import pyautogui
w, h = pyautogui.size()



class Object:
    
    def __init__(
            self, ID, name = None, color = (0,0,0), alpha = 255, text_color = None, pos = (0, 0), size = (1, 1), text = "", 
            fade_time = None, typeable = False, draggable = False, 
            constant = None, click = lambda : print("CLICKED"), 
            double_click = lambda : print("DOUBLE CLICKED"), right_click = lambda : print("RIGHT CLICKED")):
        
        self.ID = ID ; self.name = name if name != None else ID
        self.color = color ; self.alpha = alpha ; self.text_color = text_color if text_color != None else color
        self.obj = pygame.Surface((1,1), pygame.SRCALPHA) ; self.obj.fill(self.color)
        
        self.pos = pos ; self.size = size
        if(self.pos[0] == "center"): self.pos = ((w/h - self.size[0])/2, self.pos[1])
        if(self.pos[1] == "center"): self.pos = (self.pos[0], (1 - self.size[1])/2)
        
        self.text = text ; self.curser_pos = None ; self.fade_time = fade_time ; self.fade_start = None
        self.typeable = typeable ; self.text_box = None ; self.show_text() ; self.draggable = draggable
        self.constant = constant; self.click = click ; self.double_click = double_click ; self.right_click = right_click
        self.clicked_on = False ; self.last_time_clicked = None ; self.right_clicked_on = False
        self.being_dragged = False ; self.being_typed = False
        
    def get_text(self):
        name_empty = self.name.replace(" ", "") == ""
        text_empty = self.text == ""
        if(self.curser_pos != None):
            self_text = self.text[:self.curser_pos] + "|" + self.text[self.curser_pos:]
        else: self_text = self.text
        if(name_empty and text_empty): text = " "
        elif(name_empty): text = self_text 
        elif(text_empty and self.curser_pos == None): text = self.name 
        else:             text = self.name + " : " + self_text
        return(text)
        
    def show_text(self, font = "arial"):
        text = self.get_text()
        font = pygame.font.SysFont(font, 100)
        self.text_box = font.render(text, True, self.text_color)
        self.text_box.set_alpha(self.alpha)
        
    def copy(self):
        obj_copy = Object(
            ID = self.ID, name = self.name, color = self.color, text_color = self.text_color, 
            pos = self.pos, size = self.size, text = self.text, draggable = self.draggable, 
            typeable = self.typeable, click = self.click, double_click = self.double_click)
        return(obj_copy)
    
    def __str__(self):
        return("{}: {}".format(self.name, self.text))
        


class Game:
    
    def __init__(self, size = [w//2, h//2]):
        pygame.init()
        self.paras = {"size" : size} 
        self.objects = [] 
        self.bg = self.add_object("bg", "bg", color = (255, 255, 255), size = (w/h, 1), pos = (0, 0))
        self.screen = pygame.display.set_mode(self.paras["size"], RESIZABLE)
        
    def add_object(self, *args, **kwargs):
        obj = Object(*args, **kwargs)
        self.objects.append(obj)
        return(obj)
    
    def remove_object(self, ID):
        pop_these = []
        for i, obj in enumerate(self.objects):
            if obj.ID == ID:
                pop_these.append(i)
        for i in reversed(pop_these): self.objects.pop(i) 
        
    def obj_size(self, obj):
        ww, wh = self.paras["size"]
        wider = wh/ww < h/w
        w_size = wh if wider else ww*h/w
        size = [s*w_size for s in obj.size]
        return(size)
    
    def obj_pos(self, obj):
        ww, wh = self.paras["size"]
        wider = wh/ww < h/w
        w_size = wh if wider else ww*h/w
        sw, sh = self.obj_size(self.bg)
        pos  = [p*w_size for p in obj.pos]
        if(wider): pos[0] += (ww - sw)/2
        else:      pos[1] += (wh - sh)/2
        return(pos)
    
    def obj_click(self, obj, pos):
        size = self.obj_size(obj) ; obj_pos  = self.obj_pos(obj)
        if(pos[0] > obj_pos[0] and pos[0] < obj_pos[0] + size[0]):
            if(pos[1] > obj_pos[1] and pos[1] < obj_pos[1] + size[1]):
                return(True)
        return(False)
    
    def where_in_text(self, obj, pos):
        if(not obj.typeable): return 
        text = obj.get_text()
        text_pos, text_size = self.get_text_pos_size(obj)
        curser_pos = obj.curser_pos
        curser_pos = int(len(text) * (pos[0] - text_pos[0]) / text_size[0])
        curser_pos -= len(text) - len(obj.text) - 1
        if(curser_pos < 0):             curser_pos = 0 
        if(curser_pos > len(obj.text)): curser_pos = len(obj.text)
        obj.curser_pos = curser_pos
        
    def get_text_pos_size(self, obj):
        size = self.obj_size(obj) ; pos = self.obj_pos(obj)
        x_1, y_1, x_2, y_2 = obj.text_box.get_rect()
        x = x_2 - x_1 ; y = y_2 - y_1 ; text_ratio = x / y
        x_change = size[0] / x ; y_change = size[1] / y ; change = max([x_change, y_change])
        if(change == x_change): 
            text_size = (size[1] * text_ratio, size[1]) 
            text_pos = (pos[0] + size[0]/2 - text_size[0]/2, pos[1])
        else:                   
            text_size = (size[0], size[0] / text_ratio) 
            text_pos = (pos[0], pos[1] + size[1]/2 - text_size[1]/2)
            # If possible, add /n to make new lines
        return(text_pos, text_size)
        
    def render(self, obj):
        size = self.obj_size(obj) ; pos = self.obj_pos(obj)
        obj.color = obj.color[:3] + (int(obj.alpha),)
        obj.obj.set_alpha(obj.alpha)
        OBJ = pygame.transform.scale(obj.obj, size)
        self.screen.blit(OBJ, pos)
        obj.show_text()
        if(obj.text_box != None):
            text_pos, text_size = self.get_text_pos_size(obj)
            text = pygame.transform.scale(obj.text_box, text_size)
            self.screen.blit(text, text_pos)
        
    def run(self):
        running = True ; frames = 0
        old_pos = pygame.mouse.get_pos()
        while running:
            frames += 1 ; pos = pygame.mouse.get_pos()
            for obj in reversed(self.objects):
                if(obj.constant != None):
                    obj.constant()
                if(obj.fade_time != None):
                    if(obj.fade_start == None): obj.fade_start = time()
                    time_fading = time() - obj.fade_start
                    alpha = 255 * (1 - (time_fading / obj.fade_time))
                    obj.alpha = alpha
                    if(time_fading >= obj.fade_time):
                        self.remove_object(obj.ID)
            
            for obj in self.objects: 
                self.render(obj)
            
            events = pygame.event.get()
            for event in events:
                
                if event.type == pygame.QUIT: running = False
                if event.type == VIDEOEXPOSE: 
                    pygame.display.update()
                    self.paras["size"] = self.screen.get_size()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for obj in reversed(self.objects):
                        obj.being_typed = False ; obj.curser_pos = None
                    for obj in reversed(self.objects):
                        if(self.obj_click(obj, pos)):
                            if(event.button == 1): # Left click
                                obj.clicked_on = True
                                if(obj.typeable): 
                                    obj.being_typed = True
                                    self.where_in_text(obj, pos)
                            if(event.button == 3): # Right click
                                obj.right_clicked_on = True
                            break
                    
                if event.type == pygame.MOUSEBUTTONUP:
                    if(event.button == 1):     
                        for obj in reversed(self.objects):
                            if(self.obj_click(obj, pos)):
                                clicked_this = obj
                                if(not obj.being_dragged):
                                    obj.click()
                                    if(obj.last_time_clicked != None and time() - obj.last_time_clicked <= .5): 
                                        obj.double_click()
                                    obj.last_time_clicked = time()
                                break
                        for obj in reversed(self.objects): 
                            obj.clicked_on = False ; obj.being_dragged = False
                            if(clicked_this != obj): obj.last_time_clicked = None
                    if(event.button == 3):
                        for obj in reversed(self.objects):
                            if(self.obj_click(obj, pos) and not obj.being_dragged):
                                obj.right_click()
                                break
                        
                if event.type == pygame.KEYDOWN:
                    key = event.unicode
                    for obj in reversed(self.objects):
                        if(obj.being_typed):
                            if(event.key == pygame.K_RETURN): 
                                obj.being_typed = False ; obj.curser_pos = None ; break
                            elif(event.key == pygame.K_BACKSPACE):
                                obj.text = obj.text[:obj.curser_pos-1] + obj.text[obj.curser_pos:]
                                obj.curser_pos -= 1
                            elif(event.key == pygame.K_LEFT):
                                if(obj.curser_pos != 0): obj.curser_pos -= 1 
                            elif(event.key == pygame.K_RIGHT):
                                if(obj.curser_pos < len(obj.text)): obj.curser_pos += 1 
                            else:
                                obj.text = obj.text[:obj.curser_pos] + key + obj.text[obj.curser_pos:]
                                obj.curser_pos += 1
                            break
                
            for obj in reversed(self.objects):
                if(obj.draggable and obj.clicked_on):
                    change_x = pos[0] - old_pos[0] ; change_y = pos[1] - old_pos[1]
                    bg_size = self.obj_size(self.bg)
                    change_x /= bg_size[1] ; change_y /= bg_size[1]
                    obj.pos = (obj.pos[0] + change_x, obj.pos[1] + change_y)
                    if(change_x > 0 or change_y > 0): obj.being_dragged = True
                                     
            old_pos = pos
            pygame.display.flip()
        pygame.quit()
        
        
        
if __name__ == "__main__":
    
    def new_button():
        new_button = Object("FADING", color = (255, 1, 1), alpha = 100, fade_time = 2, text_color = (0,0,0), size = (.1, .1), pos = (.5, .5),
                     click = lambda: print("CLICKED"), double_click = lambda: print("DOUBLE CLICKED"))
        new_button.double_click = get_remove_button("REMOVE")
        game.objects.append(new_button)
    
    def get_remove_button(name):
        def remove_button():
            game.remove_object(name)
        return(remove_button)

    game = Game()
    typing = game.add_object("TYPE", color = (1, 1, 255), size = (1, .1), pos = (.3, .3), text_color = (0,0,0), typeable = True, draggable = True)
    new = game.add_object("NEW", color = (255, 1, 255), size = (.1, .1), pos = (.4, .4),  text_color = (0,0,0), double_click = new_button)
    game.run()