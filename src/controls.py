import pygame as pg
import traceback


# TODO move Button mapping to settings?

class KeyGetter():
    def __init__(self, game):
        self.game = game
        # mapping is a dict with 'name': pg.Key
        # default settings:
        self.keyboard_mapping = {
                'RIGHT': pg.K_RIGHT,
                'DOWN': pg.K_DOWN,
                'LEFT': pg.K_LEFT,
                'UP': pg.K_UP,
                'A': pg.K_a,
                'B': pg.K_b,
                'X': pg.K_x,
                'Y': pg.K_y,
                'L': pg.K_l,
                'R': pg.K_r,
                'START': pg.K_RETURN,
                'SELECT': pg.K_BACKSPACE
                }
    
    
    def get_input(self, pad, events):
        '''
        Processes the inputs from a gamepad and the keyboard and combines them
        into dictionaries as properties of the game object
        Args:
            pad: GamepadController instance
            events: event list from pygame.event.get()
        '''
        # process key status
        # create empty dict with key status
        self.game.keys_pressed = {key: 0 for key in self.keyboard_mapping.keys()}
        
        key_presses = pg.key.get_pressed()
        for key, value in self.keyboard_mapping.items():
            if not pad.inputs:
                if key_presses[value]:
                    self.game.keys_pressed[key] = 1
            else:
                if (pad.inputs[0][pad.button_mapping[key]] or 
                    key_presses[value]):
                    self.game.keys_pressed[key] = 1
        
        # process keydown and keyup events
        self.game.keydown = {key: 0 for key in self.keyboard_mapping.keys()}
        self.game.keyup = {key: 0 for key in self.keyboard_mapping.keys()}  
        for event in events:
            if event.type == pg.KEYDOWN:
                for key, value in self.keyboard_mapping.items():
                    if event.key == value:
                        self.game.keydown[key] = 1
            elif event.type == pg.KEYUP:
                for key, value in self.keyboard_mapping.items():
                    if event.key == value:
                        self.game.keyup[key] = 1
                        
        for key, value in pad.button_mapping.items():
            if pad.inputs_down and pad.inputs_down[0][value]:
                self.game.keydown[key] = 1
            elif pad.inputs_up and pad.inputs_up[0][value]:
                self.game.keyup[key] = 1
                  
    
    def test_inputs(self, inputs):
        '''
        Test the player inputs and return a string of all keys in the input dict
        Args:
            inputs: dict with key: status. Either self.game.keys_pressed, self.
            game.keydown or self.game.keyup
        '''
        input_string = ''
        try:
            for key, value in inputs.items():
                if value:
                    input_string += pg.key.name(key)
                    input_string += ','
            if input_string:
                print(input_string)
        except:
            traceback.print_exc()



class GamepadController():
    def __init__(self):
        # buttons held down
        self.inputs = []
        # button press events
        self.inputs_down = []
        self.inputs_up = []
        self.inputs_down_prev = []
        self.inputs_up_prev = []
        
        self.deadzones = {
                'stick_l': 0.2,
                'stick_r': 0.2,
                'trigger_l': 0.01,
                'trigger_r': 0.01
                }
        
        self.button_mapping = {
                    'A': 0,
                    'B': 1,
                    'X': 2, 
                    'Y': 3, 
                    'L': 4, 
                    'R': 5, 
                    'SELECT': 6, 
                    'START': 7,
                    'STICK_L': 8, 
                    'STICK_R': 9, 
                    'DPAD_X': 10, 
                    'DPAD_Y': 11, 
                    'STICK_L_X': 12,
                    'STICK_L_Y': 13, 
                    'STICK_R_X': 14, 
                    'STICK_R_Y': 15, 
                    'TRIGGER_L': 16, 
                    'TRIGGER_R': 17,
                    'RIGHT': 18,
                    'DOWN': 19,
                    'LEFT': 20,
                    'UP': 21,
                    }

        pg.joystick.init()
        
    
    def test_inputs(self, inputs):
        input_string = ''
        try:
            for controller_input in getattr(self, inputs):
                for i, inp in enumerate(controller_input):
                    if inp:
                        for key, value in self.button_mapping.items():
                            if value == i:
                                input_string += key
                                input_string += ','
            if input_string:
                print(input_string)
        except:
            traceback.print_exc()
            
    
    def any_key(self):
        '''returns if any of the buttons from any gamepad is pressed at this frame
        '''
        return any([any(i) for i in self.inputs])

    
    def update(self):
        self.gamepads = [pg.joystick.Joystick(x) for x in range(
                         pg.joystick.get_count())]
    
        self.inputs = []
        self.inputs_down = []
        self.inputs_up = []
        
        if len(self.gamepads) > 0:
            for n, pad in enumerate(self.gamepads):
                self.inputs.append([0 for i in range(len(self.button_mapping))])
                pad.init()
                
                # get button values
                for i in range(pad.get_numbuttons()):
                    if pad.get_button(i):
                        self.inputs[n][i] = 1
                            
                # get axes values
                for i in range(pad.get_numaxes()):
                    axis = pad.get_axis(i)
                    # compare each axis to deadzone
                    if i == 0:
                        # X axis left stick
                        if abs(axis) > self.deadzones['stick_l']:
                            self.inputs[n][12] = axis
                    elif i == 1:
                        # Y axis left stick
                        if abs(axis) > self.deadzones['stick_l']:
                            self.inputs[n][13] = axis
                    elif i == 2:
                        if axis > self.deadzones['trigger_l']:
                            self.inputs[n][16] = axis
                            self.inputs[n][17] = 0
                        elif abs(axis) > self.deadzones['trigger_r']:
                            self.inputs[n][17] = abs(axis)
                            self.inputs[n][16] = 0
                    elif i == 3:
                        # y axis right stick
                        if abs(axis) > self.deadzones['stick_r']:
                            self.inputs[n][15] = axis
                    elif i == 4:
                        # X axis right stick
                        if abs(axis) > self.deadzones['stick_r']:
                            self.inputs[n][14] = axis
                        
                # get dpad values
                for i in range(pad.get_numhats()):
                    self.inputs[n][10], self.inputs[n][11] = pad.get_hat(i)
                    X = self.inputs[n][10]
                    Y = self.inputs[n][11]
                    self.inputs[n][18] = 1 if X > 0 else 0
                    self.inputs[n][19] = 1 if Y < 0 else 0
                    self.inputs[n][20] = 1 if X < 0 else 0
                    self.inputs[n][21] = 1 if Y > 0 else 0
                
                # save button_pressed events by comparing to previous presses
                if len(self.inputs_down_prev) == n:
                    # if this gamepad has no previous inputs
                    self.inputs_down_prev.append([0 for _ in self.inputs[n]])
                else:
                    # compare current input to prev input
                    diff = [1 if elem and not self.inputs_down_prev[n][i] 
                            else 0 for i, elem in enumerate(self.inputs[n])]
                    self.inputs_down.append(diff)
                    # set prev input to current input
                    self.inputs_down_prev[n] = [inp for inp in self.inputs[n]]
                
                # do the same for release events
                if len(self.inputs_up_prev) == n:
                    # if this gamepad has no previous inputs
                    self.inputs_up_prev.append([0 for _ in self.inputs[n]])
                else:
                    # compare current input to prev input
                    diff = [1 if not elem and self.inputs_up_prev[n][i] 
                            else 0 for i, elem in enumerate(self.inputs[n])]
                    self.inputs_up.append(diff)
                    # set prev input to current input
                    self.inputs_up_prev[n] = [inp for inp in self.inputs[n]]  


                    
                    
                    