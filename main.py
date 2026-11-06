import sys
import threading
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from core.shortcut_listener import ShortcutCommunicator, ShortcutListener
from ui.overlay_window import OverlayWindow
from ui.menu_window import MenuWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 1. Creamos la ventana overlay del personaje
    overlay = OverlayWindow()
    overlay.show()

    # 2. Creamos el menú desplegable pasándole la referencia del overlay
    menu = MenuWindow(overlay)

    # 3. Configuramos el comunicador para escuchar el atajo global (Ctrl + Shift + A)
    communicator = ShortcutCommunicator()
    communicator.senal_atajo.connect(menu.alternar)

    # Arrancamos el hilo secundario del atajo de teclado
    listener = ShortcutListener(communicator)
    listener.start()

    # Notificación de prueba inicial
    QTimer.singleShot(1500, lambda: overlay.mostrar_notificacion("¡Aplicación modular con persistencia JSON activa!"))

    sys.exit(app.exec())