import json
import os

class StorageManager:
    """Gestiona la carga y guardado de las listas de logros, notas y opciones en un archivo JSON local."""
    def __init__(self, filename="data.json"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.filepath = os.path.join(base_dir, "..", filename)

    def cargar_datos(self) -> dict:
        """Carga los datos desde el archivo JSON. Si no existe, devuelve una estructura por defecto."""
        default_data = {
            "opciones": {
                "margen_izquierdo": 20,
                "margen_inferior": -10,
                "mostrar_imagen": True,
                "escala_menu": 1.0,       # 1.0 = Tamaño normal (340x420)
                "opacidad_overlay": 1.0   # 1.0 = Opaco, valores menores lo hacen translúcido
            },
            "listas": {
                "General": [
                    {"nombre": "Terminar el tutorial", "completado": False},
                    {"nombre": "Derrotar al primer jefe", "completado": False}
                ],
                "Coleccionables": [
                    {"nombre": "Encontrar la llave dorada", "completado": False},
                    {"nombre": "Recoger 100 monedas", "completado": False}
                ]
            },
            "notas": {}  # <-- Añadido para almacenar el bloc de notas
        }
        
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "listas" not in data and "opciones" not in data:
                        return {
                            "opciones": default_data["opciones"],
                            "listas": data,
                            "notas": {}
                        }
                    
                    # Asegurar que existan todas las claves principales si el JSON es antiguo
                    if "notas" not in data:
                        data["notas"] = {}
                    
                    # Asegurar que las nuevas opciones existan si el JSON es antiguo
                    if "opciones" in data:
                        for k, v in default_data["opciones"].items():
                            if k not in data["opciones"]:
                                data["opciones"][k] = v
                    else:
                        data["opciones"] = default_data["opciones"]

                    return data
            except Exception as e:
                print(f"Error al leer el archivo de datos: {e}")
        
        return default_data

    def guardar_datos(self, datos: dict):
        """Guarda el diccionario actual en el archivo JSON."""
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(datos, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error al guardar los datos: {e}")