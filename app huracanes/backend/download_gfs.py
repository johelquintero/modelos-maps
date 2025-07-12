import requests
from datetime import datetime, timedelta

# --- Configuración ---
# URL base del servidor NOMADS de NOAA
base_url = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod"
# Nombre del archivo a descargar. f000 es la hora de pronóstico 0 (el análisis).
# 0p25 es la resolución de 0.25 grados.
file_to_download = "gfs.t00z.pgrb2.0p25.f000" 
output_filename = file_to_download

def get_latest_gfs_rundate():
    """
    Determina la hora de la corrida más reciente del modelo GFS (00, 06, 12, 18 UTC).
    Los datos suelen tardar unas 3-4 horas en estar disponibles.
    """
    now_utc = datetime.utcnow()
    # Retrocedemos 5 horas para asegurar que la corrida esté disponible
    probable_time = now_utc - timedelta(hours=5)
    
    run_hour = (probable_time.hour // 6) * 6
    run_date = probable_time.strftime('%Y%m%d')
    
    return f"gfs.{run_date}/{run_hour:02d}/atmos"

def download_latest_gfs_file():
    """
    Descarga el archivo GRIB2 de la corrida más reciente del modelo GFS.
    """
    latest_run_path = get_latest_gfs_rundate()
    
    # Actualizamos el nombre del archivo para que coincida con la corrida
    # Ejemplo: gfs.20231027/12/atmos/gfs.t12z.pgrb2.0p25.f000
    run_hour_str = latest_run_path.split('/')[1]
    dynamic_filename = f"gfs.t{run_hour_str}z.pgrb2.0p25.f000"
    
    # La salida la renombramos al nombre genérico que espera process_gfs.py
    # para no tener que cambiar el nombre del archivo en el otro script.
    generic_output_filename = "gfs.t00z.pgrb2.0p25.f000" # Nombre esperado por process_gfs.py

    full_url = f"{base_url}/{latest_run_path}/{dynamic_filename}"
    
    print(f"Intentando descargar desde: {full_url}")

    try:
        # Realizar la petición de descarga
        response = requests.get(full_url, stream=True)
        response.raise_for_status()  # Lanza un error si la petición falla (ej. 404)

        # Descargar el archivo en trozos
        with open(generic_output_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"\n¡Éxito! Archivo descargado y guardado como: {generic_output_filename}")
        print("Ahora puedes ejecutar 'process_gfs.py' para procesar los datos.")

    except requests.exceptions.HTTPError as e:
        print(f"Error al descargar el archivo: {e}")
        print("Es posible que los datos de la corrida más reciente aún no estén disponibles.")
        print("Inténtalo de nuevo en unos minutos.")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    download_latest_gfs_file()