import ctypes
from ctypes import wintypes

MOD_CONTROL = 0x0002
VK_SPACE = 0x20
WM_HOTKEY = 0x0312
HOTKEY_ID_DEFAULT = 1001

class WindowsHotkeyManager:
    """Gestiona el registro y despacho de atajos globales usando user32.dll en Windows."""

    def __init__(self, hwnd: int, hotkey_id: int = HOTKEY_ID_DEFAULT):
        self.hwnd = hwnd
        self.hotkey_id = hotkey_id
        self.registrado = False
        self._user32 = ctypes.windll.user32

    def registrar(self, modificador: int = MOD_CONTROL, tecla_vk: int = VK_SPACE) -> bool:
        if self._user32.RegisterHotKey(self.hwnd, self.hotkey_id, modificador, tecla_vk):
            self.registrado = True
            return True
        return False

    def desregistrar(self) -> None:
        if self.registrado:
            self._user32.UnregisterHotKey(self.hwnd, self.hotkey_id)
            self.registrado = False

    def es_evento_hotkey(self, message_ptr: int) -> bool:
        """Determina si un mensaje nativo de Windows corresponde a nuestro hotkey."""
        msg = wintypes.MSG.from_address(message_ptr)
        return msg.message == WM_HOTKEY and msg.wParam == self.hotkey_id
