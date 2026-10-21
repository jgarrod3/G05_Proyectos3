import cv2
import numpy as np
import glob
import os

TABLERO = (9, 13)       # esquinas INTERNAS (columnas, filas)
TAM_CASILLA = 40        # mm

# NUEVO: modelo de distorsión simplificado.
# FIX_K3 evita el coeficiente que se "dispara" en los bordes de la imagen
# (es la causa típica de que la imagen rectificada salga deformada).
# ZERO_TANGENT_DIST asume que el sensor está bien alineado con la lente.
FLAGS_CALIBRACION = (
    cv2.CALIB_FIX_K3 +
    cv2.CALIB_ZERO_TANGENT_DIST +
    cv2.CALIB_FIX_PRINCIPAL_POINT +   # NUEVO: centro óptico = centro de la imagen
    cv2.CALIB_FIX_ASPECT_RATIO        # NUEVO: obliga a fx = fy (píxeles cuadrados)
)

# NUEVO: las fotos con más error que esto (en píxeles) se descartan
ERROR_MAX_FOTO = 1.0

puntos_3d = []
puntos_2d = []
nombres_validos = []   # NUEVO: para saber qué foto es cuál

puntos_tablero = np.zeros((TABLERO[0] * TABLERO[1], 3), np.float32)
puntos_tablero[:, :2] = np.mgrid[0:TABLERO[0], 0:TABLERO[1]].T.reshape(-1, 2)
puntos_tablero = puntos_tablero * TAM_CASILLA

imagenes = sorted(glob.glob("fotos/*.jpg"))

if len(imagenes) == 0:
    print("No hay imágenes en la carpeta fotos/")
    exit()

tam_imagen = None
fotos_validas = 0

criterio = (
    cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
    30,
    0.001
)

# NUEVO: flags de detección más robustos (los mismos que usa el PDF)
flags_deteccion = (
    cv2.CALIB_CB_ADAPTIVE_THRESH +
    cv2.CALIB_CB_NORMALIZE_IMAGE
)

for nombre in imagenes:
    imagen = cv2.imread(nombre)

    if imagen is None:
        print("No se ha podido abrir:", nombre)
        continue

    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

    # NUEVO: todas las fotos tienen que tener la misma resolución
    if tam_imagen is None:
        tam_imagen = gris.shape[::-1]
    elif gris.shape[::-1] != tam_imagen:
        print("Resolución distinta, se ignora:", nombre)
        continue

    encontrado, esquinas = cv2.findChessboardCorners(
        gris,
        TABLERO,
        flags_deteccion
    )

    if encontrado:
        esquinas = cv2.cornerSubPix(
            gris,
            esquinas,
            (11, 11),
            (-1, -1),
            criterio
        )

        puntos_3d.append(puntos_tablero)
        puntos_2d.append(esquinas)
        nombres_validos.append(nombre)
        fotos_validas += 1

        cv2.drawChessboardCorners(
            imagen,
            TABLERO,
            esquinas,
            encontrado
        )

        nombre_salida = "detectada_" + os.path.basename(nombre)
        cv2.imwrite(nombre_salida, imagen)

        print("OK:", nombre)
    else:
        print("No se ha encontrado el tablero:", nombre)

if fotos_validas < 10:
    print("\nERROR: Solo hay", fotos_validas, "fotos válidas.")
    print("Necesitas al menos 10 fotos donde se detecte el tablero completo.")
    exit()

ancho, alto = tam_imagen


# NUEVO: error de reproyección de cada foto (en píxeles)
def error_por_foto(matriz, dist, rots, trasl):
    errores = []
    for p3d, p2d, r, t in zip(puntos_3d, puntos_2d, rots, trasl):
        proyectados, _ = cv2.projectPoints(p3d, r, t, matriz, dist)
        diferencia = p2d.reshape(-1, 2) - proyectados.reshape(-1, 2)
        errores.append(np.sqrt(np.mean(np.sum(diferencia ** 2, axis=1))))
    return errores


# NUEVO: primera calibración, luego quitamos las fotos malas y repetimos
error, matriz_camara, distorsion, rotaciones, traslaciones = cv2.calibrateCamera(
    puntos_3d, puntos_2d, tam_imagen, None, None, flags=FLAGS_CALIBRACION
)

errores = error_por_foto(matriz_camara, distorsion, rotaciones, traslaciones)

print("\n--- ERROR POR FOTO (píxeles) ---")
for nombre, e in zip(nombres_validos, errores):
    marca = "  <-- MALA" if e > ERROR_MAX_FOTO else ""
    print(f"{e:6.3f}  {nombre}{marca}")

buenas = [i for i, e in enumerate(errores) if e <= ERROR_MAX_FOTO]

if len(buenas) < len(errores) and len(buenas) >= 10:
    print("\nDescartando", len(errores) - len(buenas), "fotos malas y recalibrando...")
    puntos_3d = [puntos_3d[i] for i in buenas]
    puntos_2d = [puntos_2d[i] for i in buenas]
    nombres_validos = [nombres_validos[i] for i in buenas]
    fotos_validas = len(buenas)

    error, matriz_camara, distorsion, rotaciones, traslaciones = cv2.calibrateCamera(
        puntos_3d, puntos_2d, tam_imagen, None, None, flags=FLAGS_CALIBRACION
    )
elif len(buenas) < len(errores):
    print("\nHay fotos malas pero quedarían menos de 10: no se descartan.")
    print("Haz más fotos (ver cobertura.jpg).")

# alpha=0 -> recorta lo negro (como antes)
nueva_matriz, roi = cv2.getOptimalNewCameraMatrix(
    matriz_camara,
    distorsion,
    (ancho, alto),
    0,
    (ancho, alto)
)

print("\n--- RESULTADOS ---")
print("Fotos válidas:", fotos_validas)
print("Error de calibración (RMS):", error)
print("\nMatriz de cámara:")
print(matriz_camara)
print("\nCoeficientes de distorsión:")
print(distorsion)

# NUEVO: dibujamos dónde han estado las esquinas en TODAS las fotos.
# Si hay zonas vacías (sobre todo los bordes), la calibración es mala ahí.
cobertura = np.zeros((alto, ancho, 3), np.uint8)
celdas = set()
for esquinas in puntos_2d:
    for x, y in esquinas.reshape(-1, 2):
        cv2.circle(cobertura, (int(x), int(y)), 3, (0, 255, 0), -1)
        celdas.add((min(int(x * 4 / ancho), 3), min(int(y * 4 / alto), 3)))

cv2.imwrite("cobertura.jpg", cobertura)
print(f"\nZonas de la imagen cubiertas (cuadrícula 4x4): {len(celdas)}/16")
if len(celdas) < 12:
    print("AVISO: faltan fotos con el tablero en los bordes y esquinas de la imagen.")
    print("Mira cobertura.jpg: las zonas negras son las que NO has calibrado.")

archivo = cv2.FileStorage(
    "camera_calibration.yml",
    cv2.FILE_STORAGE_WRITE
)

archivo.write("matriz_camara", matriz_camara)
archivo.write("distorsion", distorsion)
archivo.write("nueva_matriz_camara", nueva_matriz)
archivo.write("roi", np.array(roi))
archivo.write("tam_casilla_mm", TAM_CASILLA)
archivo.write("esquinas_internas", np.array(TABLERO))
archivo.write("error_calibracion", error)

archivo.release()

print("\nArchivo creado: camera_calibration.yml")

# NUEVO: comparación de las 3 primeras fotos, y con dos versiones:
#  - "completa": alpha=1, se ve TODO (con negro). Es la prueba honesta.
#  - "sin_negro": alpha=0 + recorte, como antes.
matriz_completa, _ = cv2.getOptimalNewCameraMatrix(
    matriz_camara, distorsion, (ancho, alto), 1, (ancho, alto)
)

for k, nombre in enumerate(nombres_validos[:3]):
    imagen = cv2.imread(nombre)

    completa = cv2.undistort(
        imagen, matriz_camara, distorsion, None, matriz_completa
    )

    rectificada = cv2.undistort(
        imagen, matriz_camara, distorsion, None, nueva_matriz
    )
    x, y, w, h = roi
    rectificada = rectificada[y:y + h, x:x + w]
    rectificada = cv2.resize(rectificada, (ancho, alto))

    for etiqueta, resultado in (("completa", completa), ("sin_negro", rectificada)):
        comparacion = cv2.hconcat([imagen, resultado])

        cv2.putText(comparacion, "Original", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.putText(comparacion, "Rectificada", (ancho + 20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        salida = f"comparacion_{etiqueta}_{k + 1}.jpg"
        cv2.imwrite(salida, comparacion)
        print("Imagen creada:", salida)