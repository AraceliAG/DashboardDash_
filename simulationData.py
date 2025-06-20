import os
import pymodbus
import serial
import time
import numpy as np
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.transaction import ModbusRtuFramer
from datetime import datetime, timedelta
import struct
import random

# TIEMPO DE LECTURA DE CADA REGISTRO
tiempo_lectura = 5
conexion = True

def list_to_int(l):
    return np.dot(l, np.exp2(np.arange(len(l))))

def conversion(dato):  # FUNCION DE CONVERSION
    # Verifica que 'dato' sea una secuencia de bytes
    if not isinstance(dato, (bytes, bytearray)) or len(dato) != 4:
        raise ValueError("El dato debe ser una secuencia de 4 bytes.")
    
    # Usa struct para desempaquetar los bytes como un float IEEE 754 de 32 bits
    return struct.unpack('>f', dato)[0]

def stamp_time():  # FUNCION PARA TOMAR LA HORA Y FECHA ACTUAL ACTUAL
    now = datetime.now()
    seconds = now.second + now.microsecond / 1_000_000
    return now.strftime('%Y-%m-%d %H:%M:%S') 

def ensure_directory_exists(directory):  # FUNCION PARA LA CONDICION DE EXISTENCIA DE UNA CARPETA
    if not os.path.exists(directory):
        os.makedirs(directory)

def open_files(base_directory, timestamp):  # FUNCION PARA LA CREACION Y ESCRITURA DE LOS REGISTROS
    mes = datetime.now().strftime('%Y-%m-%d')  # FORMATO PARA EL NOMBRE DE CARPETA QUITE MINUTOS
    current_directory = os.path.join(base_directory, mes)

    ensure_directory_exists(current_directory)

    directories = {
        "Corriente_linea1": "Corriente_linea1",
        "Voltaje_fase_1": "Voltaje_fase_1",
        # "Potencia_activa_f1": "Potencia_activa_f1",
        # "Potencia_aparente_total": "Potencia_aparente_total",
        # "Factor_Potencia": "Factor_Potencia",
        # "frecuencia": "frecuencia",
        # "Energia_importada_activa_total": "Energia_importada_activa_total",
        # "Energia_importada_reactiva_total": "Energia_importada_reactiva_total"
    }

    files = {}
    for key, folder in directories.items():  # AQUI SE ESCRIBEN LOS REGISTROS EN SU RESPECTIVO ARCHIVO Y CARPETA
        folder_path = os.path.join(current_directory, folder)
        ensure_directory_exists(folder_path)
        
        fromartoN = datetime.now().strftime('%Y-%m-%d %H')  # LO ACABO DE AGREGAR XD
        
        files[key] = open(os.path.join(folder_path, f"{fromartoN}.csv"), "a+")
    
    return files  # RETORNA LA CARPETA JUNTO A SUS RESPECTIVOS ARCHIVOS

def close_files(files):  # FUNCION PARA EL CIERRE DE ARCHIVOS
    for file in files.values():
        file.close()


    


# Funciones para calcular el tiempo hasta la proxima medianoche y la proxima hora exacta
def time_until_next_midnight(): #PARA LA NOCHE 0:0:0
    now = datetime.now() #SE TOMA LA HORA ACTUAL
    next_midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return (next_midnight - now).total_seconds()

def time_until_next_hour(): #PARA CADA HORA
    now = datetime.now() #SE TOMA LA HORA ACTUAL
    next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0) 
    return (next_hour - now).total_seconds()
    
    # Main loop with file rotation
def bloque():
    
    base_directory = "DATA_BD" #cambiar por el nombre de la carpeta que se quiera
    ensure_directory_exists(base_directory)

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    files = open_files(base_directory, timestamp)
    directory_rotation_time = time.time() + time_until_next_midnight()
    file_rotation_time = time.time() + time_until_next_hour()

    while conexion == True:
        current_time = time.time()

        # CONDICION DONDE REALIZA LA ROTACION DE CARPETA A LAS 0:00 (MEDIANOCHE)
        if current_time >= directory_rotation_time:
            close_files(files)
            files = open_files(base_directory, timestamp)
            directory_rotation_time = time.time() + time_until_next_midnight()

        # CONDICION PARA LA CREACION DE ARCHIVOS CADA HORA
        if current_time >= file_rotation_time:
            close_files(files)
            files = open_files(base_directory, timestamp)
            file_rotation_time = time.time() + time_until_next_hour()

        # LECTURA DE REGISTROS DEL MEDIDOR Y ESCRITURA EN ARCHIVOS
        I1 = round(random.uniform(0.7816942930221558, 0.9347324324283234), 10)
        files["Corriente_linea1"].write(f"{stamp_time()}, {I1}\r\n")
        files["Corriente_linea1"].flush()  # Forzar escritura inmediata
        
        V1 = round(random.uniform(0.3816942930221558, 0.6347324324283234), 10)
        files["Voltaje_fase_1"].write(f"{stamp_time()}, {V1}\r\n")
        files["Voltaje_fase_1"].flush()
        
        # V1 = random.randint(123, 780)
        # files["Voltaje_fase_1"].write(f"{stamp_time()}, {V1}\r\n")
        
        # P1 = random.randint(123, 780)
        # files["Potencia_activa_f1"].write(f"{stamp_time()}, {P1}\r\n")
        
        # PA = random.randint(123, 780)
        # files["Potencia_aparente_total"].write(f"{stamp_time()}, {PA}\r\n")
        
        
        # FP = random.randint(123, 780)
        # files["Factor_Potencia"].write(f"{stamp_time()}, {FP}\r\n")
        
        # frec = random.randint(123, 780)
        # files["frecuencia"].write(f"{stamp_time()}, {frec}\r\n")
        
        # EIA = random.randint(123, 780)
        # files["Energia_importada_activa_total"].write(f"{stamp_time()}, {EIA}\r\n")          
            
        # EIR = random.randint(123, 780)
        # files["Energia_importada_reactiva_total"].write(f"{stamp_time()}, {EIR}\r\n")
        
        # Espera un corto periodo de tiempo antes de la siguiente lectura
        time.sleep(tiempo_lectura)


if __name__ == '__main__':  # METODO PRINCIPAL EN DONDE LE HABLAMOS A NUETRA FUNCION BLOQUE
    bloque()
