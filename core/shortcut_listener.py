import ctypes
import ctypes.wintypes
import threading
from PyQt6.QtCore import QObject, pyqtSignal

# Constantes de Windows para el atajo global (Ctrl + Shift + A)
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_NOREPEAT = 0x4000
WM_HOTKEY = 0x0312
VK_A = 0x41
ID_ATAJO = 1

class ShortcutCommunicator(QObject):
    """Puente de señales para comunicar el hilo de Windows con la UI de PyQt de forma segura."""
    senal_atajo = pyqtSignal()

class ShortcutListener(threading.Thread):
    """Hilo secundario que monitoriza las pulsaciones globales de teclado en Windows."""
    def __init__(self, communicator: ShortcutCommunicator):
        super().__init__()
        self.communicator = communicator
        self.daemon = True # Se cierra automáticamente al cerrar la app principal

    def run(self):
        user32 = ctypes.windll.user32
        # Registramos el atajo global Ctrl + Shift + A
        if user32.RegisterHotKey(None, ID_ATAJO, MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT, VK_A):
            mensaje = ctypes.wintypes.MSG()
            while user32.GetMessageW(ctypes.byref(mensaje), None, 0, 0) != 0:
                if mensaje.message == WM_HOTKEY:
                    self.communicator.senal_atajo.emit()
        else:
            print("Aviso: No se pudo registrar el atajo global (¿otro programa lo está usando?).")