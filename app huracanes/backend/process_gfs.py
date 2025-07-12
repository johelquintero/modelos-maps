import pygrib
import json
import numpy as np
import os

# --- Configuración ---
# Nombre del archivo GRIB2 de entrada. Asumimos que está en el mismo directorio que el script.
grib_filename = 'gfs.t00z.pgrb2.0p25.f000' 
# Ruta de salida para el archivo JSON.
output_json_path = os.path.join('..', 'frontend', 'data', 'wind.json')

def process_gfs_to_json():
    """
    Lee un archivo GRIB2, extrae los datos de viento (componentes U y V)
    y los convierte a un formato JSON compatible con leaflet-velocity.
    """
    print(f"Iniciando el procesamiento del archivo: {grib_filename}")

    try:
        # Abrir el archivo GRIB2
        grib_file = pygrib.open(grib_filename)
        print("Archivo GRIB2 abierto exitosamente.")

        # Seleccionar las componentes del viento a 10 metros sobre el suelo
        # Estas son descripciones estándar en los archivos GFS.
        u_wind = grib_file.select(name='10 metre U wind component')[0]
        v_wind = grib_file.select(name='10 metre V wind component')[0]
        
        print("Capas de viento U y V extraídas.")

        # Obtener los datos como arrays de numpy
        u_data = u_wind.values
        v_data = v_wind.values

        # Obtener metadatos geoespaciales de una de las capas (son iguales)
        lats, lons = u_wind.latlons()
        ny, nx = lats.shape
        
        # La librería leaflet-velocity necesita la esquina de inicio y el espaciado
        la1 = lats[0, 0]
        lo1 = lons[0, 0]
        la2 = lats[-1, -1]
        lo2 = lons[-1, -1]
        dx = (lons[0, 1] - lons[0, 0])
        dy = (lats[0, 0] - lats[1, 0])

        print(f"Dimensiones de la grilla: {nx}x{ny}")
        print(f"Esquina Suroeste (lat/lon): {la2}/{lo1}")
        print(f"Esquina Noreste (lat/lon): {la1}/{lo2}")

        # Construir la estructura de datos para el JSON
        # leaflet-velocity espera dos objetos separados, uno para cada componente.
        wind_data = [
            {
                "header": {
                    "parameterUnit": "m.s-1",
                    "parameterNumberName": "U-component_of_wind",
                    "parameterNumber": 2,
                    "refTime": u_wind.analDate.strftime('%Y-%m-%d %H:%M:%S'),
                    "nx": nx,
                    "ny": ny,
                    "lo1": lo1,
                    "la1": la1,
                    "dx": dx,
                    "dy": dy
                },
                "data": u_data.flatten().tolist() # Aplanar el array y convertir a lista
            },
            {
                "header": {
                    "parameterUnit": "m.s-1",
                    "parameterNumberName": "V-component_of_wind",
                    "parameterNumber": 3,
                    "refTime": v_wind.analDate.strftime('%Y-%m-%d %H:%M:%S'),
                    "nx": nx,
                    "ny": ny,
                    "lo1": lo1,
                    "la1": la1,
                    "dx": dx,
                    "dy": dy
                },
                "data": v_data.flatten().tolist() # Aplanar el array y convertir a lista
            }
        ]
        
        print("Estructura de datos JSON creada.")

        # Asegurarse de que el directorio de salida exista
        os.makedirs(os.path.dirname(output_json_path), exist_ok=True)

        # Guardar los datos en el archivo JSON
        with open(output_json_path, 'w') as f:
            json.dump(wind_data, f)
            
        print(f"¡Éxito! Datos de viento guardados en: {output_json_path}")

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{grib_filename}'.")
        print("Asegúrate de descargarlo primero, por ejemplo, usando el script 'download_gfs.py'.")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
    finally:
        if 'grib_file' in locals() and grib_file:
            grib_file.close()

if __name__ == "__main__":
    process_gfs_to_json()