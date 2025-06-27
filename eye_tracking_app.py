import time
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
        self.cap: Optional[cv2.VideoCapture] = None # type: ignore
        
        self.isProgramRunning = False
        self.isVideoRunning = True
        self.wasPausedManually = False
        
        self.debug = False        
        
        self.ear_right_minimum = 100
        self.ear_left_minimum = 100

        self.volume_mode = False
        self.volume_mode_message_time = 0
        self.volume_mode_message = ""
        
        # Nova lógica para controle de tempo dos olhos fechados
        self.eyes_closed_start_time = 0
        self.eyes_were_closed = False
        self.fullscreen_threshold = 0.75  # 1.5 segundos para fullscreen
        self.volume_mode_threshold = 1.5  # 3 segundos para modo volume
    
    def initialize_camera(self) -> bool:
        # Inicializa a câmera
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
            # Reset do controle de olhos fechados se não há rosto
            self.eyes_were_closed = False
            return True

        if self.isVideoRunning == False and self.wasPausedManually == False:
            self.action_controller.handle_absence_action('play')
            self.isVideoRunning = True

        left_eye_points = self.eye_detector.extract_eye_points(landmarks, self.config.LEFT_EYE_POINTS)
        right_eye_points = self.eye_detector.extract_eye_points(landmarks, self.config.RIGHT_EYE_POINTS)
        ear_left = self.eye_detector.calculate_ear(left_eye_points)
        ear_right = self.eye_detector.calculate_ear(right_eye_points)

        # --- Nova lógica: mede tempo e executa ação apenas quando olhos abrem ---
        eyes_closed = ear_left < self.config.EAR_THRESHOLD_LEFT and ear_right < self.config.EAR_THRESHOLD_RIGHT
        current_time = time.time()
        
        if eyes_closed:
            if not self.eyes_were_closed:
                # Início do fechamento dos olhos
                self.eyes_closed_start_time = current_time
                self.eyes_were_closed = True
            else:
                # Olhos continuam fechados - apenas mostra feedback visual
                closed_duration = current_time - self.eyes_closed_start_time
                self.draw_eye_close_feedback(frame, closed_duration)
        else:
            # Olhos abertos - verifica se precisa executar ação baseada no tempo total
            if self.eyes_were_closed:
                total_closed_time = current_time - self.eyes_closed_start_time
                
                # Decide a ação baseada no tempo total usando if/elif para evitar conflitos
                if total_closed_time >= self.volume_mode_threshold:
                    # Tempo longo (≥3s): alterna modo volume
                    self.volume_mode = not self.volume_mode
                    self.volume_mode_message_time = current_time
                    if self.volume_mode:
                        self.volume_mode_message = "Modo Volume Ativado"
                    else:
                        self.volume_mode_message = "Modo Volume Desativado"
                        
                elif total_closed_time >= self.fullscreen_threshold:
                    # Tempo médio (≥1.5s e <3s): fullscreen
                      # Só executa fullscreen se não estiver no modo volume
                    self.action_controller.handle_blink_twice_action()
                
                # Reset do controle
                self.eyes_were_closed = False
            else:
                if self.volume_mode:
                    # Piscada olho direito: aumentar volume
                    if self.eye_detector.is_blink_detected(ear_right, 'right'):
                        self.action_controller.handle_volume_action('up')
                    # Piscada olho esquerdo: diminuir volume
                    elif self.eye_detector.is_blink_detected(ear_left, 'left'):
                        self.action_controller.handle_volume_action('down')
                else:
                    # Modo normal - piscadas individuais para navegação
                    # Piscada olho esquerdo: retroceder
                    if self.eye_detector.is_blink_detected(ear_left, 'left'):
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
    
    def draw_eye_close_feedback(self, frame, closed_duration):
        # Mostra barra de progresso com marcador visual para fullscreen no meio
        h, w = frame.shape[:2]
        
        # Calcula progresso total até o modo volume (3s)
        progress = min(closed_duration / self.volume_mode_threshold, 1.0)
        
        # Posição da barra
        bar_width = int(w * 0.6)
        bar_height = 30
        x = int((w - bar_width) / 2)
        y = int(h * 0.1)
        
        # Cores baseadas no estágio atual
        if closed_duration < self.fullscreen_threshold:
            color = (0, 255, 255)  # Amarelo - carregando para fullscreen
            text = f"Carregando Fullscreen: {closed_duration:.1f}s / {self.fullscreen_threshold}s"
        elif closed_duration < self.volume_mode_threshold:
            color = (0, 165, 255)  # Laranja - entre fullscreen e modo volume
            text = f"Carregando Modo Volume: {closed_duration:.1f}s / {self.volume_mode_threshold}s"
        else:
            color = (255, 0, 255)  # Magenta - modo volume pronto
            text = f"Modo Volume Pronto: {closed_duration:.1f}s"
        
        # Desenha fundo da barra (cinza)
        cv2.rectangle(frame, (x, y), (x + bar_width, y + bar_height), (100, 100, 100), -1)
        
        # Desenha progresso atual
        cv2.rectangle(frame, (x, y), (x + int(bar_width * progress), y + bar_height), color, -1)
        
        # Marca visual para fullscreen no meio da barra (linha branca vertical)
        fullscreen_pos = int(x + bar_width * (self.fullscreen_threshold / self.volume_mode_threshold))
        cv2.line(frame, (fullscreen_pos, y), (fullscreen_pos, y + bar_height), (255, 255, 255), 3)
        
        # Borda da barra
        cv2.rectangle(frame, (x, y), (x + bar_width, y + bar_height), (255, 255, 255), 2)
        
        # Texto de feedback
        cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        # Legendas das marcações
        cv2.putText(frame, f"FS: {self.fullscreen_threshold}s", (fullscreen_pos - 30, y + bar_height + 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        cv2.putText(frame, f"Vol: {self.volume_mode_threshold}s", (x + bar_width - 60, y + bar_height + 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    
    def draw_volume_mode_ui(self, frame):
        # Mostra mensagens do modo volume
        h, w = frame.shape[:2]
        
        # Mensagem de ativação/desativação do modo volume
        if self.volume_mode_message and (time.time() - self.volume_mode_message_time < 2):
            cv2.putText(frame, self.volume_mode_message, (int(w*0.25), int(h*0.15)), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 3)
        
        # Indicador permanente do modo volume
        if self.volume_mode:
            cv2.putText(frame, "MODO VOLUME ATIVO", (int(w*0.3), int(h*0.08)), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
    
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