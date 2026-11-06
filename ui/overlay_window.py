import os
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QWidget
from core.storage import StorageManager

# Rutas de assets
CARPETA_CODE = os.path.dirname(os.path.abspath(__file__))
CARPETA_ASSETS = os.path.join(CARPETA_CODE, "..", "assets")
IMAGEN_ICONO = os.path.join(CARPETA_ASSETS, "imagen.png")

class OverlayWindow(QWidget):
    """Ventana flotante transparente que muestra el personaje y las notificaciones."""
    def __init__(self):
        super().__init__()
        self.storage = StorageManager()
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        # Cuadro de notificación flotante
        self.label_notificacion = QLabel("¡Logro desbloqueado!", self)
        self.label_notificacion.setWordWrap(True)
        self.label_notificacion.setStyleSheet("""
            background-color: #ffffff;
            color: #000000;
            border: 2px solid #ffb6c1;
            border-radius: 8px;
            padding: 10px 14px;
            font-family: 'Segoe UI';
            font-weight: bold;
            font-size: 13px;
        """)
        self.label_notificacion.hide()

        self.timer_notif = QTimer(self)
        self.timer_notif.setSingleShot(True)
        self.timer_notif.timeout.connect(self.label_notificacion.hide)

        # Carga de la imagen del personaje
        self.label_imagen = QLabel(self)

        # Aplicar configuración inicial
        self.actualizar_configuracion()

    def actualizar_configuracion(self):
        """Recarga las opciones, aplica la opacidad y reajusta la posición del overlay."""
        datos_completos = self.storage.cargar_datos()
        opciones = datos_completos.get("opciones", {})
        
        margen_izq = opciones.get("margen_izquierdo", 20)
        margen_inf = opciones.get("margen_inferior", -10)
        mostrar_img = opciones.get("mostrar_imagen", True)
        opacidad = opciones.get("opacidad_overlay", 1.0)

        # Aplicar opacidad general a toda la ventana flotante
        self.setWindowOpacity(max(0.1, min(1.0, opacidad)))

        ancho_img, alto_img = 0, 0
        if os.path.exists(IMAGEN_ICONO) and mostrar_img:
            pixmap = QPixmap(IMAGEN_ICONO)
            self.label_imagen.setPixmap(pixmap)
            ancho_img = pixmap.width()
            alto_img = pixmap.height()
            self.label_imagen.show()
        else:
            self.label_imagen.clear()
            self.label_imagen.hide()

        screen = self.screen().geometry()
        
        ancho_ventana = (ancho_img + 420) if mostrar_img else 410
        alto_ventana = (alto_img + 20) if mostrar_img else 90
        
        x = margen_izq
        y = screen.height() - alto_ventana - margen_inf
        self.setGeometry(x, y, ancho_ventana, alto_ventana)
        self.x_ventana = x
        self.y_ventana = y

        if mostrar_img:
            self.label_imagen.setGeometry(0, alto_ventana - alto_img, ancho_img, alto_img)
            self.label_notificacion.setGeometry(ancho_img + 15, (alto_ventana // 2) - 35, 390, 70)
        else:
            self.label_notificacion.setGeometry(10, 10, 390, 70)

    def mostrar_notificacion(self, texto: str):
        """Muestra una notificación flotante durante 4 segundos."""
        self.label_notificacion.setText(texto)
        self.label_notificacion.show()
        self.timer_notif.start(4000)