import pygame

class InputFrame:
    def __init__(self):
        self.keys_held = set()
        self.keys_pressed = set()
        self.keys_released = set()

        self.mouse_buttons_held = set()
        self.mouse_buttons_pressed = set()
        self.mouse_buttons_released = set()

        self.mouse_pos = (0, 0)

class InputManager:
    def __init__(self):
        self.current_frame = InputFrame()
        # 上一帧状态
        self.prev_keys = set()
        self.prev_mouse = set()
    def update(self):
        frame = InputFrame()
        # 获取当前按住键
        keys = pygame.key.get_pressed()
        current_keys = {
            k for k in range(len(keys)) if keys[k]
        }
        # pressed
        frame.keys_pressed = current_keys - self.prev_keys
        # released
        frame.keys_released = self.prev_keys - current_keys
        # held
        frame.keys_held = current_keys
        # 鼠标
        mouse_buttons = pygame.mouse.get_pressed()
        current_mouse = {
            i + 1 for i, pressed in enumerate(mouse_buttons) if pressed
        }
        frame.mouse_buttons_pressed = current_mouse - self.prev_mouse
        frame.mouse_buttons_released = self.prev_mouse - current_mouse
        frame.mouse_buttons_held = current_mouse
        frame.mouse_pos = pygame.mouse.get_pos()
        self.prev_keys = current_keys
        self.prev_mouse = current_mouse
        self.current_frame = frame