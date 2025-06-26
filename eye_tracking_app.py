import time
import cv2 # type: ignore
from action_controller import ActionController
from config import EyeTrackingConfig
from eye_detector import EyeDetector


class EyeTrackingApp:
    # Classe da aplicação principal do sistema que integra todos os componentes
    
    def __init__(self):
        self.config = EyeTrackingConfig()
        self.eye_detector = EyeDetector(self.config)
        self.action_controller = ActionController(self.config)
        self.cap: Optional[cv2.VideoCapture] = None # type: ignore
        
        self.isProgramRunning = False
        self.isVideoRunning = True
        self.wasPausedManually = False
        
        self.debug = False        
        
        self.ear_right_minimum = 100
        self.ear_left_minimum = 100

        self.volume_mode = False
        self.volume_mode_loading = False
        self.volume_mode_loading_start = 0
        self.volume_mode_loading_duration = 3
        self.volume_mode_message_time = 0
        self.volume_mode_message = ""
          
        # Novas variáveis para controle de temporização
        self.last_action_time = 0
        self.action_delay = 0.5  # 500ms entre ações (ajuste conforme necessário)
        self.blink_count = 0
        self.last_blink_time = 0
        self.blink_window = 1.0  # Janela de tempo para contar piscadas múltiplas (1 segundo)

    
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
        landmarks = self.eye_detector.detect_faces_and_landmarks(frame)

        # --- Desenhar UI do modo volume sempre ---
        self.draw_volume_mode_ui(frame)

        if landmarks is None:
            if self.eye_detector.is_absence_detected() and self.isVideoRunning:
                self.action_controller.handle_absence_action('pause')
                self.isVideoRunning = False
                self.wasPausedManually = False
            cv2.putText(frame, "Nenhum rosto detectado", (50, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            return True

        if self.isVideoRunning == False and self.wasPausedManually == False:
            self.action_controller.handle_absence_action('play')
            self.isVideoRunning = True

        left_eye_points = self.eye_detector.extract_eye_points(landmarks, self.config.LEFT_EYE_POINTS)
        right_eye_points = self.eye_detector.extract_eye_points(landmarks, self.config.RIGHT_EYE_POINTS)
        ear_left = self.eye_detector.calculate_ear(left_eye_points)
        ear_right = self.eye_detector.calculate_ear(right_eye_points)

        # --- Lógica de ativação/desativação do modo volume ---
        eyes_closed = ear_left < self.config.EAR_THRESHOLD_LEFT and ear_right < self.config.EAR_THRESHOLD_RIGHT
        if eyes_closed:
            if not self.volume_mode_loading:
                self.volume_mode_loading = True
                self.volume_mode_loading_start = time.time()
            else:
                elapsed = time.time() - self.volume_mode_loading_start
                if elapsed >= self.volume_mode_loading_duration:
                    self.volume_mode = not self.volume_mode
                    self.volume_mode_loading = False
                    self.volume_mode_message_time = time.time()
                    if self.volume_mode:
                        self.volume_mode_message = "Modo Volume Ativado"
                    else:
                        self.volume_mode_message = "Modo Volume Desativado"
        else:
            self.volume_mode_loading = False

        # --- Gestos no modo volume ---
        if self.volume_mode:
            # Piscada olho direito: aumentar volume
            if self.eye_detector.is_blink_detected(ear_right, 'right'):
                self.action_controller.handle_volume_action('up')
            # Piscada olho esquerdo: diminuir volume
            elif self.eye_detector.is_blink_detected(ear_left, 'left'):
                self.action_controller.handle_volume_action('down')
            # Fullscreen continua funcionando normalmente
            elif self.eye_detector.is_blink_twice_detected(ear_left, ear_right):
                self.action_controller.handle_blink_twice_action()
        else:
            # Fullscreen (olhos fechados por tempo)
            if self.eye_detector.is_blink_twice_detected(ear_left, ear_right):
                self.action_controller.handle_blink_twice_action()
            # Piscada olho esquerdo: retroceder
            elif self.eye_detector.is_blink_detected(ear_left, 'left'):
                self.action_controller.handle_blink_action('left')
            # Piscada olho direito: avançar
            elif self.eye_detector.is_blink_detected(ear_right, 'right'):
                self.action_controller.handle_blink_action('right')

        # Desenhar pontos e debug
        if self.config.SHOW_EYE_POINTS:
            self.eye_detector.draw_eye_points(frame, left_eye_points)
            self.eye_detector.draw_eye_points(frame, right_eye_points)
        if self.config.SHOW_DEBUG_INFO:
            self.eye_detector.add_debug_info(frame, ear_left, ear_right)

        return True
    
    def draw_volume_mode_ui(self, frame):
        # Mostra barra de carregamento e mensagens do modo volume
        h, w = frame.shape[:2]
        if self.volume_mode_loading:
            elapsed = time.time() - self.volume_mode_loading_start
            progress = min(elapsed / self.volume_mode_loading_duration, 1.0)
            bar_width = int(w * 0.6)
            bar_height = 30
            x = int((w - bar_width) / 2)
            y = int(h * 0.1)
            cv2.rectangle(frame, (x, y), (x + bar_width, y + bar_height), (200, 200, 200), 2)
            cv2.rectangle(frame, (x, y), (x + int(bar_width * progress), y + bar_height), (0, 255, 0), -1)
            txt = "Ativando Modo Volume..." if not self.volume_mode else "Desativando Modo Volume..."
            cv2.putText(frame, txt, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        if self.volume_mode_message and (time.time() - self.volume_mode_message_time < 2):
            cv2.putText(frame, self.volume_mode_message, (int(w*0.35), int(h*0.15)), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 3)
        if self.volume_mode:
            cv2.putText(frame, "MODO VOLUME ATIVO", (int(w*0.35), int(h*0.08)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
    
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