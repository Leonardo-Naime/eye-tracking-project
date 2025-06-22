import cv2
from action_controller import ActionController
from config import EyeTrackingConfig
from eye_detector import EyeDetector


class EyeTrackingApp:
    # Classe da aplicação principal do sistema que integra todos os componentes
    
    def __init__(self):
        self.config = EyeTrackingConfig()
        self.eye_detector = EyeDetector(self.config)
        self.action_controller = ActionController(self.config)
        self.cap: Optional[cv2.VideoCapture] = None
        
        self.isProgramRunning = False
        self.isVideoRunning = True
        self.wasPausedManually = False
    
    def initialize_camera(self) -> bool:
        # Inicializa a câmera
        
        # Returns:
        #     bool: True se câmera foi inicializada com sucesso
        try:
            self.cap = cv2.VideoCapture(self.config.CAMERA_INDEX)
            if not self.cap.isOpened():
                print("Erro: Não foi possível abrir a câmera")
                return False
            
            # Configurações opcionais da câmera
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            print("Câmera inicializada com sucesso")
            return True
            
        except Exception as e:
            print(f"Erro ao inicializar câmera: {e}")
            return False
    
    def process_frame(self, frame) -> bool:
        # Processa um frame da câmera
        
        # Detecta pontos faciais
        landmarks = self.eye_detector.detect_faces_and_landmarks(frame)
        
        
        if landmarks is None:
            # Verifica ausência prolongada
            if self.eye_detector.is_absence_detected() and self.isVideoRunning:
                self.action_controller.handle_absence_action('pause')
                self.isVideoRunning = False
                self.wasPausedManually = False
            
            # Mostra mensagem na tela
            cv2.putText(frame, "Nenhum rosto detectado", (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        else:
            # Despausa vídeo se foi pausado por ausência
            if self.isVideoRunning == False and self.wasPausedManually == False:
                self.action_controller.handle_absence_action('play')
                self.isVideoRunning = True
            
            # Extrai pontos do olho esquerdo
            left_eye_points = self.eye_detector.extract_eye_points(
                landmarks, self.config.LEFT_EYE_POINTS
            )
            
            # Extrai pontos do olho direito
            right_eye_points = self.eye_detector.extract_eye_points(
                landmarks, self.config.RIGHT_EYE_POINTS
            ) 
            
            # Calcula EAR
            ear_left = self.eye_detector.calculate_ear(left_eye_points)
            ear_right = self.eye_detector.calculate_ear(right_eye_points)

            
            # Detecta piscada dupla
            if self.eye_detector.is_blink_twice_detected(ear_left, ear_right):
                self.action_controller.handle_blink_twice_action()
            # Detecta piscada no olho esquerdo
            elif self.eye_detector.is_blink_detected(ear_left):
                self.action_controller.handle_blink_action('left')
            # Detecta piscada no olho direito
            elif self.eye_detector.is_blink_detected(ear_right):
                self.action_controller.handle_blink_action('right')
            
            # Desenha pontos do olho se habilitado
            if self.config.SHOW_EYE_POINTS:
                self.eye_detector.draw_eye_points(frame, left_eye_points)
                self.eye_detector.draw_eye_points(frame, right_eye_points)
            # Mostra informações de debug se habilitado
            if self.config.SHOW_DEBUG_INFO:
                self.eye_detector.add_debug_info(frame, ear_left, ear_right)
        
        return True
    
    def run(self) -> None:
        # Loop que acontece enquanto o programa está rodando
        
        if not self.initialize_camera():
            return
        
        print("Sistema iniciado! Pressione 'q' para sair")
        print("Ações disponíveis:")
        for action, key in self.action_controller.get_available_actions().items():
            print(f"  {action}: {key}")
        print("\nControles atuais:")
        print("  - Piscada: Avançar 5 segundos")
        print("  - Ausência: Pausar vídeo")
        
        self.isProgramRunning = True
        
        try:
            while self.isProgramRunning:
                ret, frame = self.cap.read()
                if not ret:
                    print("Erro: Não foi possível capturar frame")
                    break
                
                # Processa o frame
                self.process_frame(frame)
                
                # Mostra o frame
                cv2.imshow(self.config.WINDOW_NAME, frame)
                
                # Verifica tecla de saída
                key = cv2.waitKey(1) & 0xFF
                if key == self.config.QUIT_KEY:
                    break
                
                # Teclas adicionais para teste manual
                elif key == ord('p'):  # Play/Pause
                    self.action_controller.execute_youtube_action('play_pause')
                elif key == ord('m'):  # Mute
                    self.action_controller.execute_youtube_action('mute')
        
        except KeyboardInterrupt:
            print("\nInterrompido pelo usuário")
        
        finally:
            self.cleanup()
    
    def cleanup(self) -> None:
        # Limpa recursos utilizados
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("Recursos liberados. Aplicação encerrada.")