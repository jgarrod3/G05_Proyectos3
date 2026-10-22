import cv2
 
# Genera un marcador ArUco para imprimir o mostrar en el móvil
DICT = cv2.aruco.DICT_4X4_50
MARKER_ID = 7
SIZE_PX = 400
 
aruco_dict = cv2.aruco.getPredefinedDictionary(DICT)
if hasattr(cv2.aruco, "generateImageMarker"):   # OpenCV >= 4.7
    img = cv2.aruco.generateImageMarker(aruco_dict, MARKER_ID, SIZE_PX)
else:
    img = cv2.aruco.drawMarker(aruco_dict, MARKER_ID, SIZE_PX)
 
img = cv2.copyMakeBorder(img, 50, 50, 50, 50, cv2.BORDER_CONSTANT, value=255)  # margen blanco
cv2.imwrite(f"aruco_{MARKER_ID}.png", img)
print(f"Guardado aruco_{MARKER_ID}.png")
 
