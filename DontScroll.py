import cv2
import mediapipe as mp
import pygame
import time
import os


SOUND_FILE = "sound.wav" 
THRESHOLD = 0.60         
COOLDOWN = 3             
SHAME_DIR = "shame_photos"

if not os.path.exists(SHAME_DIR):
    os.makedirs(SHAME_DIR)


pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init()

try:
    if os.path.exists(SOUND_FILE):
        joke_sound = pygame.mixer.Sound(SOUND_FILE)
        print(f"✅ Файл {SOUND_FILE} успешно загружен!")
    else:
        print(f"❌ Ошибка: Файл {SOUND_FILE} не найден в папке проекта!")
        joke_sound = None
except Exception as e:
    print(f"❌ Ошибка инициализации звука: {e}")
    joke_sound = None

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

cap = cv2.VideoCapture(0)
last_play_time = 0
shame_count = 0

print("🎥 Система запущена. Нажми ESC для выхода.")

while cap.isOpened():
    success, image = cap.read()
    if not success: break

    image = cv2.flip(image, 1)
    h, w, _ = image.shape
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_image)
    
    status_text = "Good"
    color = (0, 255, 0) 

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            nose = face_landmarks.landmark[1]
            nose_y = nose.y
            
            cx, cy = int(nose.x * w), int(nose.y * h)
            cv2.circle(image, (cx, cy), 5, (255, 0, 0), -1)

            if nose_y > THRESHOLD:
                status_text = "ALARM!"
                color = (0, 0, 255) 
                
                current_time = time.time()
                if current_time - last_play_time > COOLDOWN:
                    shame_count += 1
                    if joke_sound:
                        joke_sound.play()
                        print("🔊 Звуковой сигнал!")
                    
                    timestamp = time.strftime("%H-%M-%S")
                    cv2.imwrite(f"{SHAME_DIR}/shame_{timestamp}.jpg", image)
                    last_play_time = current_time
            
            cv2.putText(image, f"Level: {nose_y:.2f}", (10, 70), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            cv2.putText(image, f"Shame: {shame_count}", (10, 110), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    
    limit_y = int(THRESHOLD * h)
    cv2.line(image, (0, limit_y), (w, limit_y), (0, 255, 255), 2)
    
    cv2.putText(image, status_text, (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    cv2.imshow('Anti-Scroll', image)
    cv2.setWindowProperty('Anti-Scroll', cv2.WND_PROP_TOPMOST, 1)

    if cv2.waitKey(5) & 0xFF == 27: break

cap.release()
cv2.destroyAllWindows() 