from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QCheckBox, QPushButton, QFrame, QScrollArea, 
    QTabWidget, QLineEdit, QStackedWidget, QMessageBox, QApplication
)
from core.storage import StorageManager

class MenuWindow(QWidget):
    """Menú desplegable con pestañas, gestión de listas, opciones de diseño y persistencia."""
    def __init__(self, overlay_window):
        super().__init__()
        self.overlay = overlay_window
        self.storage = StorageManager()
        
        self.datos_completos = self.storage.cargar_datos()
        self.datos_checklists = self.datos_completos.get("listas", {})
        self.opciones = self.datos_completos.get("opciones", {})
        
        self.lista_actual = None

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        # Calcular tamaño del menú aplicando la escala guardada
        escala = self.opciones.get("escala_menu", 1.0)
        self.ancho_base = int(340 * escala)
        self.alto_base = int(420 * escala)

        self.setGeometry(self.overlay.x_ventana, self.overlay.y_ventana - self.alto_base - 20, self.ancho_base, self.alto_base)

        self.init_ui()

    def init_ui(self):
        layout_externo = QVBoxLayout(self)
        layout_externo.setContentsMargins(0, 0, 0, 0)
        
        container = QFrame(self)
        container.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 2px solid #ffb6c1;
                border-radius: 12px;
            }
            QLabel {
                color: #000000;
                font-family: 'Segoe UI';
                font-size: 12px;
                border: none;
                background: transparent;
            }
            QPushButton {
                background-color: #ffb6c1;
                color: #000000;
                border: none;
                border-radius: 6px;
                padding: 6px 10px;
                font-family: 'Segoe UI';
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff9eaa;
            }
            QLineEdit {
                border: 1px solid #ffb6c1;
                border-radius: 5px;
                padding: 4px;
                background: #fff0f3;
                color: #000000;
                font-family: 'Segoe UI';
            }
            QCheckBox {
                color: #000000;
                font-family: 'Segoe UI';
                font-size: 12px;
                spacing: 8px;
                border: none;
                background: transparent;
            }
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                background: #fce4ec;
                color: #000000;
                padding: 6px 8px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
                font-family: 'Segoe UI';
                font-size: 11px;
            }
            QTabBar::tab:selected {
                background: #ffb6c1;
                font-weight: bold;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #ffb6c1;
                border-radius: 3px;
            }
        """)

        layout_interno = QVBoxLayout(container)
        layout_interno.setContentsMargins(12, 12, 12, 12)
        layout_interno.setSpacing(10)

        # Sistema de pestañas
        self.tabs = QTabWidget()
        
        # Pestaña 1: Listas personalizadas
        self.tab_checklist = QWidget()
        self.setup_tab_checklist()
        self.tabs.addTab(self.tab_checklist, "Listas")

        # Pestaña 2: Steam (Reservada)
        self.tab_steam = QWidget()
        layout_steam = QVBoxLayout(self.tab_steam)
        lbl_proximamente = QLabel("<b>Logros de Steam</b><br><br>Próximamente conexión con API oficial.")
        lbl_proximamente.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_steam.addWidget(lbl_proximamente)
        self.tabs.addTab(self.tab_steam, "Steam")

        # Pestaña 3: Opciones avanzadas
        self.tab_opciones = QWidget()
        self.setup_tab_opciones()
        self.tabs.addTab(self.tab_opciones, "Opciones")

        layout_interno.addWidget(self.tabs)

        # Botón de cierre general
        btn_cerrar = QPushButton("Cerrar programa")
        btn_cerrar.clicked.connect(QApplication.quit)
        layout_interno.addWidget(btn_cerrar)

        # Texto informativo del atajo
        lbl_atajo = QLabel("Ctrl+Shift+A para ocultar el menú")
        lbl_atajo.setStyleSheet("color: #888888; font-size: 10px;")
        lbl_atajo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_interno.addWidget(lbl_atajo)

        layout_externo.addWidget(container)
        self.hide()

    def setup_tab_checklist(self):
        layout_principal = QVBoxLayout(self.tab_checklist)
        layout_principal.setContentsMargins(0, 0, 0, 0)

        self.stack_vistas = QStackedWidget()
        
        # Página 0: Vista General de Listas
        self.pagina_listas = QWidget()
        layout_p0 = QVBoxLayout(self.pagina_listas)
        layout_p0.setContentsMargins(0, 0, 0, 0)
        layout_p0.setSpacing(6)

        layout_crear_lista = QHBoxLayout()
        self.input_nueva_lista = QLineEdit()
        self.input_nueva_lista.setPlaceholderText("Nombre nueva lista...")
        btn_crear_lista = QPushButton("+ Crear")
        btn_crear_lista.clicked.connect(self.crear_nueva_lista)
        layout_crear_lista.addWidget(self.input_nueva_lista)
        layout_crear_lista.addWidget(btn_crear_lista)
        layout_p0.addLayout(layout_crear_lista)

        self.scroll_lista_categorias = QScrollArea()
        self.scroll_lista_categorias.setWidgetResizable(True)
        self.scroll_lista_categorias.setStyleSheet("background: transparent;")
        
        self.actualizar_vista_categorias()
        layout_p0.addWidget(self.scroll_lista_categorias)
        self.stack_vistas.addWidget(self.pagina_listas)

        # Página 1: Vista Detalle de Logros
        self.pagina_detalle = QWidget()
        layout_p1 = QVBoxLayout(self.pagina_detalle)
        layout_p1.setContentsMargins(0, 0, 0, 0)
        layout_p1.setSpacing(6)

        layout_cabecera = QHBoxLayout()
        btn_volver = QPushButton("← Volver")
        btn_volver.clicked.connect(lambda: self.stack_vistas.setCurrentIndex(0))
        self.lbl_titulo_detalle = QLabel("<b>Lista</b>")
        self.lbl_titulo_detalle.setStyleSheet("color: #d87093; font-size: 13px;")
        layout_cabecera.addWidget(btn_volver)
        layout_cabecera.addWidget(self.lbl_titulo_detalle)
        layout_cabecera.addStretch()
        layout_p1.addLayout(layout_cabecera)

        layout_crear_logro = QHBoxLayout()
        self.input_nuevo_logro = QLineEdit()
        self.input_nuevo_logro.setPlaceholderText("Nuevo logro a completar...")
        btn_crear_logro = QPushButton("+ Añadir")
        btn_crear_logro.clicked.connect(self.crear_nuevo_logro)
        layout_crear_logro.addWidget(self.input_nuevo_logro)
        layout_crear_logro.addWidget(btn_crear_logro)
        layout_p1.addLayout(layout_crear_logro)

        self.scroll_logros_detalle = QScrollArea()
        self.scroll_logros_detalle.setWidgetResizable(True)
        self.scroll_logros_detalle.setStyleSheet("background: transparent;")
        
        layout_p1.addWidget(self.scroll_logros_detalle)
        self.stack_vistas.addWidget(self.pagina_detalle)

        layout_principal.addWidget(self.stack_vistas)

    def setup_tab_opciones(self):
        """Configura la pestaña de opciones con márgenes, visibilidad, escala y opacidad."""
        layout = QVBoxLayout(self.tab_opciones)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)

        lbl_titulo = QLabel("<b>Configuración Avanzada</b>")
        lbl_titulo.setStyleSheet("color: #d87093; font-size: 12px;")
        layout.addWidget(lbl_titulo)

        # Margen Izquierdo
        layout_izq = QHBoxLayout()
        layout_izq.addWidget(QLabel("Margen Izquierdo (px):"))
        self.input_margen_izq = QLineEdit(str(self.opciones.get("margen_izquierdo", 20)))
        layout_izq.addWidget(self.input_margen_izq)
        layout.addLayout(layout_izq)

        # Margen Inferior
        layout_inf = QHBoxLayout()
        layout_inf.addWidget(QLabel("Margen Inferior (px):"))
        self.input_margen_inf = QLineEdit(str(self.opciones.get("margen_inferior", -10)))
        layout_inf.addWidget(self.input_margen_inf)
        layout.addLayout(layout_inf)

        # Escala del Menú
        layout_esc = QHBoxLayout()
        layout_esc.addWidget(QLabel("Tamaño del menú (ej. 1.0):"))
        self.input_escala_menu = QLineEdit(str(self.opciones.get("escala_menu", 1.0)))
        layout_esc.addWidget(self.input_escala_menu)
        layout.addLayout(layout_esc)

        # Opacidad del Overlay
        layout_opc = QHBoxLayout()
        layout_opc.addWidget(QLabel("Opacidad overlay (0.1 - 1.0):"))
        self.input_opacidad = QLineEdit(str(self.opciones.get("opacidad_overlay", 1.0)))
        layout_opc.addWidget(self.input_opacidad)
        layout.addLayout(layout_opc)

        # Checkbox Mostrar Imagen
        self.chk_mostrar_imagen = QCheckBox("Mostrar imagen del personaje")
        self.chk_mostrar_imagen.setChecked(self.opciones.get("mostrar_imagen", True))
        layout.addWidget(self.chk_mostrar_imagen)

        layout.addStretch()

        # Botón guardar opciones
        btn_guardar_opciones = QPushButton("Guardar opciones")
        btn_guardar_opciones.clicked.connect(self.guardar_opciones)
        layout.addWidget(btn_guardar_opciones)

    def guardar_opciones(self):
        """Valida y guarda los nuevos ajustes de diseño y opacidad."""
        try:
            nuevo_izq = int(self.input_margen_izq.text().strip())
            nuevo_inf = int(self.input_margen_inf.text().strip())
            nueva_escala = float(self.input_escala_menu.text().strip())
            nueva_opacidad = float(self.input_opacidad.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Error", "Introduce valores numéricos válidos (usa punto para decimales).")
            return

        # Actualizar opciones en memoria
        self.opciones["margen_izquierdo"] = nuevo_izq
        self.opciones["margen_inferior"] = nuevo_inf
        self.opciones["escala_menu"] = max(0.6, min(2.0, nueva_escala))
        self.opciones["opacidad_overlay"] = max(0.1, min(1.0, nueva_opacidad))
        self.opciones["mostrar_imagen"] = self.chk_mostrar_imagen.isChecked()

        # Guardar en JSON
        self.datos_completos["opciones"] = self.opciones
        self.datos_completos["listas"] = self.datos_checklists
        self.storage.guardar_datos(self.datos_completos)

        # Aplicar tamaño de menú actualizado
        self.ancho_base = int(340 * self.opciones["escala_menu"])
        self.alto_base = int(420 * self.opciones["escala_menu"])
        self.resize(self.ancho_base, self.alto_base)

        # Actualizar overlay al instante
        self.overlay.actualizar_configuracion()
        self.overlay.mostrar_notificacion("¡Ajustes y opacidad guardados!")

    def actualizar_vista_categorias(self):
        widget_contenido = QWidget()
        widget_contenido.setStyleSheet("background: transparent;")
        layout_scroll = QVBoxLayout(widget_contenido)
        layout_scroll.setContentsMargins(0, 0, 0, 0)
        layout_scroll.setSpacing(6)

        if not self.datos_checklists:
            lbl_vacio = QLabel("No hay listas creadas.")
            lbl_vacio.setStyleSheet("color: #888888; font-size: 11px;")
            layout_scroll.addWidget(lbl_vacio)

        for nombre_lista in list(self.datos_checklists.keys()):
            fila_lista = QHBoxLayout()
            fila_lista.setContentsMargins(0, 0, 0, 0)

            btn_lista = QPushButton(nombre_lista)
            btn_lista.setStyleSheet("""
                QPushButton {
                    background-color: #fce4ec;
                    color: #000000;
                    text-align: left;
                    padding: 10px 14px;
                    border-radius: 6px;
                    font-weight: bold;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #ffb6c1;
                }
            """)
            btn_lista.clicked.connect(lambda checked, l=nombre_lista: self.abrir_lista(l))

            btn_borrar = QPushButton("✕")
            btn_borrar.setFixedWidth(35)
            btn_borrar.setStyleSheet("""
                QPushButton {
                    background-color: #ffebee;
                    color: #d32f2f;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #ffcdd2;
                }
            """)
            btn_borrar.clicked.connect(lambda checked, l=nombre_lista: self.borrar_lista(l))

            fila_lista.addWidget(btn_lista)
            fila_lista.addWidget(btn_borrar)

            contenedor_fila = QWidget()
            contenedor_fila.setLayout(fila_lista)
            layout_scroll.addWidget(contenedor_fila)

        widget_contenido.setLayout(layout_scroll)
        self.scroll_lista_categorias.setWidget(widget_contenido)

    def borrar_lista(self, nombre_lista):
        """Muestra un panel de confirmación integrado para evitar cierres inesperados."""
        dialogo = QWidget(self)
        dialogo.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint)
        dialogo.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        dialogo.setGeometry(self.x() + 20, self.y() + 100, 300, 130)

        layout_ext = QVBoxLayout(dialogo)
        layout_ext.setContentsMargins(0, 0, 0, 0)

        marco = QFrame(dialogo)
        marco.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 2px solid #ffb6c1;
                border-radius: 10px;
            }
            QLabel {
                color: #000000;
                font-family: 'Segoe UI';
                font-size: 12px;
                border: none;
                background: transparent;
            }
            QPushButton {
                background-color: #ffb6c1;
                color: #000000;
                border: none;
                border-radius: 5px;
                padding: 6px;
                font-family: 'Segoe UI';
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff9eaa;
            }
        """)

        layout_int = QVBoxLayout(marco)
        layout_int.setContentsMargins(15, 15, 15, 15)
        layout_int.setSpacing(10)

        lbl_texto = QLabel(f"¿Borrar la lista <b>'{nombre_lista}'</b>?")
        lbl_texto.setWordWrap(True)
        layout_int.addWidget(lbl_texto)

        layout_botones = QHBoxLayout()
        btn_si = QPushButton("Sí, borrar")
        btn_no = QPushButton("Cancelar")

        btn_si.clicked.connect(lambda: [
            self.datos_checklists.pop(nombre_lista, None),
            self.datos_completos.update({"listas": self.datos_checklists}),
            self.storage.guardar_datos(self.datos_completos),
            self.actualizar_vista_categorias(),
            dialogo.close()
        ])
        
        btn_no.clicked.connect(dialogo.close)

        layout_botones.addWidget(btn_si)
        layout_botones.addWidget(btn_no)
        layout_int.addLayout(layout_botones)

        layout_ext.addWidget(marco)
        dialogo.show()

    def abrir_lista(self, nombre_lista):
        self.lista_actual = nombre_lista
        self.lbl_titulo_detalle.setText(f"<b>{nombre_lista}</b>")
        self.actualizar_vista_detalle_logros()
        self.stack_vistas.setCurrentIndex(1)

    def actualizar_vista_detalle_logros(self):
        widget_contenido = QWidget()
        widget_contenido.setStyleSheet("background: transparent;")
        layout_scroll = QVBoxLayout(widget_contenido)
        layout_scroll.setContentsMargins(0, 0, 0, 0)
        layout_scroll.setSpacing(6)

        logros = self.datos_checklists.get(self.lista_actual, [])

        if not logros:
            lbl_vacio = QLabel("Esta lista está vacía.")
            lbl_vacio.setStyleSheet("color: #888888; font-size: 11px;")
            layout_scroll.addWidget(lbl_vacio)

        for item in logros:
            cb = QCheckBox(item["nombre"])
            cb.setChecked(item["completado"])
            self.actualizar_estilo_checkbox(cb, item["completado"])
            cb.stateChanged.connect(lambda state, item_ref=item, checkbox=cb: self.al_marcar_item(item_ref, state, checkbox))
            layout_scroll.addWidget(cb)

        widget_contenido.setLayout(layout_scroll)
        self.scroll_logros_detalle.setWidget(widget_contenido)

    def actualizar_estilo_checkbox(self, cb: QCheckBox, completado: bool):
        if completado:
            cb.setStyleSheet("color: #a0a0a0; text-decoration: line-through; border: none; background: transparent;")
        else:
            cb.setStyleSheet("color: #000000; text-decoration: none; border: none; background: transparent;")

    def crear_nueva_lista(self):
        nombre = self.input_nueva_lista.text().strip()
        if not nombre:
            return
        
        if nombre not in self.datos_checklists:
            self.datos_checklists[nombre] = []
            self.datos_completos["listas"] = self.datos_checklists
            self.storage.guardar_datos(self.datos_completos)
            self.input_nueva_lista.clear()
            self.actualizar_vista_categorias()
        else:
            QMessageBox.warning(self, "Aviso", "Esa lista ya existe.")

    def crear_nuevo_logro(self):
        nombre_logro = self.input_nuevo_logro.text().strip()
        if not nombre_logro or not self.lista_actual:
            return

        self.datos_checklists[self.lista_actual].append({
            "nombre": nombre_logro,
            "completado": False
        })
        self.datos_completos["listas"] = self.datos_checklists
        self.storage.guardar_datos(self.datos_completos)
        self.input_nuevo_logro.clear()
        self.actualizar_vista_detalle_logros()

    def al_marcar_item(self, item_ref, estado, checkbox):
        marcado = (estado == 2)
        item_ref["completado"] = marcado
        self.datos_completos["listas"] = self.datos_checklists
        self.storage.guardar_datos(self.datos_completos)
        self.actualizar_estilo_checkbox(checkbox, marcado)
        
        if marcado:
            self.overlay.mostrar_notificacion(f"¡Completado: {item_ref['nombre']}!")

    def alternar(self):
        """Muestra u oculta el menú flotante."""
        if self.isVisible():
            self.hide()
        else:
            self.setGeometry(self.overlay.x_ventana, self.overlay.y_ventana - self.height() - 15, self.width(), self.height())
            self.show()