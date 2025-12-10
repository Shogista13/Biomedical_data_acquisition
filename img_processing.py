import cv2 as cv
import numpy as np

img = cv.imread("Resprite_exports/Bullet1.png")
out = np.where(img>0)
columns = list(out[0])
rows = list(out[1])
img_cut = img[min(columns):max(columns),min(rows):max(rows)]
img_resized = cv.resize(img_cut, None, fx=1.5, fy=1.5, interpolation=cv.INTER_CUBIC)
b,g,r = cv.split(img_resized)
alfa = np.array([[255 if j > 0 else 0 for j in i] for i in b],dtype=np.uint8)
new_img = cv.merge([g,b,r,alfa])
old_img = cv.merge([b,g,r,alfa])
cv.imshow("nowa",new_img)
cv.imshow('stara',old_img)
print(alfa)
#cv.imwrite("Resprite_exports/EnemyBullet1.png",old_img)
#cv.imwrite("Resprite_exports/PlayerBullet1.png",new_img)
cv.waitKey(0)