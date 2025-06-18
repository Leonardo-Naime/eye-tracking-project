import cv2
import dlib
import numpy as np
from scipy.spatial import distance
from typing import List, Tuple, Optional
from config import EyeTrackingConfig


class EyeDetector:
    # Classe responsável pela detecção e análise dos olhos
    
    def __init__(self, config: EyeTrackingConfig):
        self.config = config
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(config.SHAPE_PREDICTOR_PATH)
        
        # Contadores de estado
        self.eye_closed_frames = 0
        self.eye_closed_frames2 = 0
        self.absence_frames = 0
        self.last_ear_values = []
        
    def calculate_ear(self, eye_points: List[Tuple[int, int]]) -> float:
        # Calcula o Eye Aspect Ratio (EAR) para determinar se o olho está fechado
        
        # Args:
        #     eye_points: Lista de coordenadas dos pontos do olho
            
        # Returns:
        #     float: Valor do EAR (menor = mais fechado)
        
        # Distâncias verticais      
        A = distance.euclidean(eye_points[1], eye_points[5])
        B = distance.euclidean(eye_points[2], eye_points[4])
        
        # Distância horizontal
        C = distance.euclidean(eye_points[0], eye_points[3])
        
        # Calcula EAR
        ear = (A + B) / (2.0 * C)
        return ear
    
    def extract_eye_points(self, landmarks, eye_indices: List[int]) -> List[Tuple[int, int]]:
        # Extrai as coordenadas dos pontos do olho
        
        # Args:
        #     landmarks: Pontos faciais detectados pelo dlib
        #     eye_indices: Índices dos pontos do olho
            
        # Returns:
        #     List[Tuple[int, int]]: Coordenadas dos pontos do olho
            
        return [(landmarks.part(i).x, landmarks.part(i).y) for i in eye_indices]
    
    def detect_faces_and_landmarks(self, frame: np.ndarray) -> Optional[dlib.shape_predictor]:
        # Detecta rostos e pontos faciais no frame
        
        # Args:
        #     frame: Frame da webcam
            
        # Returns:
        #     Pontos faciais detectados ou None se não encontrar rosto
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.detector(gray)
        
        if len(faces) == 0:
            self.absence_frames += 1
            return None
        
        self.absence_frames = 0
        face = faces[0]  # Usa o primeiro rosto detectado
        landmarks = self.predictor(gray, face)
        return landmarks
    
    def is_blink_detected(self, ear: float) -> bool:
        # Detecta se houve uma piscada baseada no EAR
        
        if ear < self.config.EAR_THRESHOLD:
            self.eye_closed_frames += 1
            
            if self.eye_closed_frames >= self.config.EAR_CONSECUTIVE_FRAMES:
                self.eye_closed_frames = 0  # Reset após detectar
                return True
        else:
            self.eye_closed_frames = 0  # Reset se olho abrir
            
        return False
    
    def is_blink_twice_detected(self, ear_left: float, ear_right: float) -> bool:
        # Detecta se houve uma piscada baseada no EAR
        
        # Ambos os olhos fechados
        if ear_left < self.config.EAR_THRESHOLD and ear_right < self.config.EAR_THRESHOLD:
            self.eye_closed_frames2 += 1
            
            if self.eye_closed_frames2 >= self.config.EAR_CONSECUTIVE_FRAMES:
                self.eye_closed_frames2 = 0  # Reset após detectar
                return True
        else:
            self.eye_closed_frames = 0  # Reset se olho abrir
            
        return False
    
    def is_absence_detected(self) -> bool:
        # Verifica se houve ausência prolongada de rosto
        
        if self.absence_frames > self.config.ABSENCE_THRESHOLD:
            self.absence_frames = 0  # Reset após detectar
            return True
        return False
    
    def draw_eye_points(self, frame: np.ndarray, eye_points: List[Tuple[int, int]], color: Tuple[int, int, int] = (0, 255, 0)) -> None:
        # Desenha os pontos do olho no frame
        
        # Args:
        #     frame: Frame onde desenhar
        #     eye_points: Pontos do olho
        #     color: Cor dos pontos (BGR)
        
        for (x, y) in eye_points:
            cv2.circle(frame, (x, y), 2, color, -1)
    
    def add_debug_info(self, frame: np.ndarray, ear_left: float, ear_right: float = None) -> None:
        # Adiciona informações de debug no frame
            
        y_offset = 30
        cv2.putText(frame, f"EAR Left: {ear_left:.3f}", (10, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        if ear_right is not None:
            y_offset += 30
            cv2.putText(frame, f"EAR Right: {ear_right:.3f}", (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Status
        y_offset += 30
        status = "OPEN"
        if ear_left <= self.config.EAR_THRESHOLD and ear_right <= self.config.EAR_THRESHOLD:
            status = "BOTH CLOSED"
        elif ear_left  <= self.config.EAR_THRESHOLD:
            status = "LEFT CLOSED"
        elif ear_right <= self.config.EAR_THRESHOLD:
            status = "RIGHT CLOSED"   
        
        color = (0, 255, 0) if status == "OPEN" else (0, 0, 255)
        cv2.putText(frame, f"Status: {status}", (10, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)