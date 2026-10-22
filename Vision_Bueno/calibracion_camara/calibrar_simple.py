import cv2
import numpy as np
import glob

TABLERO = (9, 13)    # esquinas internas (columnas, filas)
TAM_CASILLA = 40     # mm

# Modelo de distorsión simplificado: k3 = 0, sin distorsión tangencial,
# centro óptico en el centro de la imagen y fx = fy
FLAGS = (cv2.CALIB_FIX_K3 + cv2.CALIB_ZERO_TANGENT_DIST +
         cv2.CALIB_FIX_PRINCIPAL_POINT + cv2.CALIB_FIX_ASPECT_RATIO)

# Coordenadas 3D reales de las esquinas (Z = 0, tablero plano)
puntos_tablero = np.zeros((TABLERO[0] * TABLERO[1], 3), np.float32)
puntos_tablero[:, :2] = np.mgrid[0:TABLERO[0], 0:TABLERO[1]].T.reshape(-1, 2) * TAM_CASILLA

puntos_3d, puntos_2d = [], []
criterio = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
imagenes = sorted(glob.glob("fotos/*.jpg"))

# 1. Detectar las esquinas en cada foto
for nombre in imagenes:
    gris = cv2.cvtColor(cv2.imread(nombre), cv2.COLOR_BGR2GRAY)
    encontrado, esquinas = cv2.findChessboardCorners(gris, TABLERO)
    if encontrado:
        esquinas = cv2.cornerSubPix(gris, esquinas, (11, 11), (-1, -1), criterio)
        puntos_3d.append(puntos_tablero)
        puntos_2d.append(esquinas)
    print("OK:" if encontrado else "Sin tablero:", nombre)

# 2. Calibrar
tam = gris.shape[::-1]
error, K, dist, _, _ = cv2.calibrateCamera(puntos_3d, puntos_2d, tam, None, None, flags=FLAGS)
print(f"\nFotos válidas: {len(puntos_3d)} de {len(imagenes)}")
print("Error RMS (px):", error)
print("Matriz de cámara:\n", K)
print("Distorsión:", dist.ravel())

# 3. Guardar los parámetros
fs = cv2.FileStorage("camera_calibration.yml", cv2.FILE_STORAGE_WRITE)
fs.write("matriz_camara", K)
fs.write("distorsion", dist)
fs.write("error_calibracion", error)
fs.release()

# 4. Comparar original y rectificada (alpha = 1: se ve toda la imagen)
imagen = cv2.imread(imagenes[0])
nueva_K, _ = cv2.getOptimalNewCameraMatrix(K, dist, tam, 1, tam)
rectificada = cv2.undistort(imagen, K, dist, None, nueva_K)
comparacion = cv2.hconcat([imagen, rectificada])
cv2.putText(comparacion, "Original", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
cv2.putText(comparacion, "Rectificada", (tam[0] + 20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
cv2.imwrite("comparacion.jpg", comparacion)
print("Creado: camera_calibration.yml y comparacion.jpg")
