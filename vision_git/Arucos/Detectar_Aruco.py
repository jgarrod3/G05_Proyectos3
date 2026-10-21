import cv2
import numpy as np

# --- Configuración ---
DICT = cv2.aruco.DICT_4X4_50   # diccionario de los marcadores
MARKER_SIZE = 0.05             # lado del marcador en metros (mídelo al imprimir)
CAM_ID = 0                     # cámara del portátil

cap = cv2.VideoCapture(CAM_ID)
ok, frame = cap.read()
if not ok:
    raise SystemExit("No se pudo abrir la cámara")
h, w = frame.shape[:2]

# Matriz de cámara aproximada (sin calibración)
camera_matrix = np.array([[w, 0, w / 2],
                          [0, w, h / 2],
                          [0, 0, 1]], dtype=np.float64)
dist_coeffs = np.zeros(5)

# Esquinas del marcador en su propio sistema de referencia (orden de OpenCV)
s = MARKER_SIZE / 2
obj_points = np.array([[-s,  s, 0],
                       [ s,  s, 0],
                       [ s, -s, 0],
                       [-s, -s, 0]], dtype=np.float32)

aruco_dict = cv2.aruco.getPredefinedDictionary(DICT)
params = cv2.aruco.DetectorParameters()
# Compatibilidad con OpenCV >= 4.7 y versiones anteriores
if hasattr(cv2.aruco, "ArucoDetector"):
    detector = cv2.aruco.ArucoDetector(aruco_dict, params)
    detect = detector.detectMarkers
else:
    detect = lambda img: cv2.aruco.detectMarkers(img, aruco_dict, parameters=params)

while True:
    ok, frame = cap.read()
    if not ok:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = detect(gray)

    if ids is not None:
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)
        for c, marker_id in zip(corners, ids.flatten()):
            ok_pnp, rvec, tvec = cv2.solvePnP(obj_points, c[0], camera_matrix, dist_coeffs,
                                              flags=cv2.SOLVEPNP_IPPE_SQUARE)
            if ok_pnp:
                cv2.drawFrameAxes(frame, camera_matrix, dist_coeffs, rvec, tvec, MARKER_SIZE * 0.75)
                x, y = c[0][0].astype(int)
                cv2.putText(frame, f"ID {marker_id}  z={tvec[2][0]:.2f}m", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.imshow("ArUco", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()