from ctypes import wintypes
from ctypes import windll, CFUNCTYPE, POINTER, c_int, c_void_p, byref
import atexit


def create_pointer(handler):
    cmp_func = CFUNCTYPE(c_int, c_int, c_int, POINTER(c_void_p))
    return cmp_func(handler)


class KeyboardEvent:
    def __init__(self, current_key=None, event_type=None, pressed_key=[]):
        self.current_key = current_key
        self.event_type = event_type
        self.pressed_key = pressed_key


class MouseEvent:
    def __init__(self, current_key=None, event_type=None):
        self.current_key = current_key
        self.event_type = event_type


class Hook:
    MouseId2Key = {513: 'LButton',
                   514: 'LButton',
                   516: 'RButton',
                   517: 'RButton',
                   519: 'WheelButton',
                   520: 'WheelButton',
                   522: 'Wheel'}

    MouseId2EventType = {513: 'key down',
                         514: 'key up',
                         516: 'key down',
                         517: 'key up',
                         519: 'key down',
                         520: 'key up',
                         522: None}

    ID2Key = {8: 'Back',
              9: 'Tab',
              13: 'Return',
              20: 'Capital',
              27: 'Escape',
              32: 'Space',
              33: 'Prior',
              34: 'Next',
              35: 'End',
              36: 'Home',
              37: 'Left',
              38: 'Up',
              39: 'Right',
              40: 'Down',
              44: 'Snapshot',
              46: 'Delete',
              48: '0',
              49: '1',
              50: '2',
              51: '3',
              52: '4',
              53: '5',
              54: '6',
              55: '7',
              56: '8',
              57: '9',
              65: 'A',
              66: 'B',
              67: 'C',
              68: 'D',
              69: 'E',
              70: 'F',
              71: 'G',
              72: 'H',
              73: 'I',
              74: 'J',
              75: 'K',
              76: 'L',
              77: 'M',
              78: 'N',
              79: 'O',
              80: 'P',
              81: 'Q',
              82: 'R',
              83: 'S',
              84: 'T',
              85: 'U',
              86: 'V',
              87: 'W',
              88: 'X',
              89: 'Y',
              90: 'Z',
              91: 'Lwin',
              92: 'Rwin',
              93: 'App',
              95: 'Sleep',
              96: 'Numpad0',
              97: 'Numpad1',
              98: 'Numpad2',
              99: 'Numpad3',
              100: 'Numpad4',
              101: 'Numpad5',
              102: 'Numpad6',
              103: 'Numpad7',
              104: 'Numpad8',
              105: 'Numpad9',
              106: 'Multiply',
              107: 'Add',
              109: 'Subtract',
              110: 'Decimal',
              111: 'Divide',
              112: 'F1',
              113: 'F2',
              114: 'F3',
              115: 'F4',
              116: 'F5',
              117: 'F6',
              118: 'F7',
              119: 'F8',
              120: 'F9',
              121: 'F10',
              122: 'F11',
              123: 'F12',
              144: 'Numlock',
              160: 'Lshift',
              161: 'Rshift',
              162: 'Lcontrol',
              163: 'Rcontrol',
              164: 'Lmenu',
              165: 'Rmenu',
              186: 'Oem_1',
              187: 'Oem_Plus',
              188: 'Oem_Comma',
              189: 'Oem_Minus',
              190: 'Oem_Period',
              191: 'Oem_2',
              192: 'Oem_3',
              219: 'Oem_4',
              220: 'Oem_5',
              221: 'Oem_6',
              222: 'Oem_7',
              1001: 'mouse left',  # mouse hotkeys
              1002: 'mouse right',
              1003: 'mouse middle',
              1000: 'mouse move',  # single event hotkeys
              1004: 'mouse wheel up',
              1005: 'mouse wheel down',
              1010: 'Ctrl',  # merged hotkeys
              1011: 'Alt',
              1012: 'Shift',
              1013: 'Win'}

    event_types = {0x100: 'key down',  # WM_KeyDown for normal keys
                   0x101: 'key up',  # WM_KeyUp for normal keys
                   0x104: 'key down',  # WM_SYSKEYDOWN, used for Alt key.
                   0x105: 'key up',  # WM_SYSKEYUP, used for Alt key.
                   }

    def __init__(self):
        self.handler = 0
        self.pressed_keys = []
        self.id = None

    def hook(self, keyboard=True, mouse=False):
        if not mouse and not keyboard:
            return;

        if keyboard:
            def low_level_handler(code, event_code, kb_data_ptr):
                key_code = kb_data_ptr[0];
                current_key = self.ID2Key[key_code];

                event_code = self.event_types[event_code];

                if event_code == 'key down':
                    self.pressed_keys.append(current_key)

                if event_code == 'key up':
                    self.pressed_keys.remove(current_key)

                event = KeyboardEvent(current_key, event_code, self.pressed_keys)

                if self.handler != 0:
                    self.handler(event);

                return windll.user32.CallNextHookEx(self.id, code, event_code, kb_data_ptr)

            keyboard_pointer = create_pointer(low_level_handler);
            windll.kernel32.GetModuleHandleW.restype = wintypes.HMODULE
            windll.kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
            self.id = windll.user32.SetWindowsHookExA(0x00D, keyboard_pointer, windll.kernel32.GetModuleHandleW(None),
                                                      0)

        if mouse:
            def mouse_low_level_handler(code, event_code, kb_data_ptr):
                if event_code != 512:
                    current_key = self.MouseId2Key[event_code]
                    event_code = self.MouseId2EventType[event_code]

                    event = MouseEvent(current_key, event_code)
                    if self.handler != 0:
                        self.handler(event);

                return windll.user32.CallNextHookEx(self.id, code, event_code, kb_data_ptr)

            mouse_pointer = create_pointer(mouse_low_level_handler);
            self.id = windll.user32.SetWindowsHookExA(0x0E, mouse_pointer, windll.kernel32.GetModuleHandleW(None), 0)

        atexit.register(windll.user32.UnhookWindowsHookEx, self.id)
        while True:
            msg = windll.user32.GetMessageW(None, 0, 0, 0)
            windll.user32.TranslateMessage(byref(msg))
            windll.user32.DispatchMessageW(byref(msg))


def on_event(args):
    if isinstance(args, KeyboardEvent):
        if args.current_key == 'A' and args.event_type == 'key down' and args.pressed_key.__contains__('Lcontrol'):
            print("Ctrl + A was pressed");

        if args.current_key == 'K' and args.event_type == 'key down':
            print("Lwin was pressed");

    if isinstance(args, MouseEvent):
        if args.current_key == 'RButton' and args.event_type == 'key down':
            print ("Right button pressed")

if __name__ == '__main__':
    hk = Hook()
    hk.handler = on_event
    hk.hook(keyboard=True, mouse=True)