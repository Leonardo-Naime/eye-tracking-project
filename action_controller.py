import pyautogui
import time
from typing import Dict, Any
from config import EyeTrackingConfig


class ActionController:
    # Classe responsável por executar ações baseadas nos movimentos oculares
    
    def __init__(self, config: EyeTrackingConfig):
        self.config = config
        self.last_action_time = 0
        self.min_action_interval = 0.5  # Segundos entre ações para evitar spam
        
        # Configurações do pyautogui
        pyautogui.PAUSE = 0.1
        pyautogui.FAILSAFE = True  # Move mouse para canto superior esquerdo para parar
    
    def can_execute_action(self) -> bool:
        # Verifica se pode executar uma ação (evita spam)
        
        current_time = time.time()
        if current_time - self.last_action_time >= self.min_action_interval:
            self.last_action_time = current_time
            return True
        return False
    
    def execute_youtube_action(self, action_name: str) -> bool:
        # Executa uma ação específica do YouTube
        
        if not self.can_execute_action():
            return False
            
        if action_name not in self.config.YOUTUBE_ACTIONS:
            print(f"Ação '{action_name}' não encontrada!")
            return False
        
        try:
            key_combination = self.config.YOUTUBE_ACTIONS[action_name]
            
            # Suporte para combinações de teclas (ex: shift+n)
            if '+' in key_combination:
                keys = key_combination.split('+')
                pyautogui.hotkey(*keys)
            else:
                pyautogui.press(key_combination)
            
            return True
            
        except Exception as e:
            print(f"Erro ao executar ação {action_name}: {e}")
            return False
    
    def handle_blink_action(self, eye_name: str) -> None:
        # Ação executada quando uma piscada é detectada
        if(eye_name == 'left'):
            # Ação para piscada no olho esquerdo
            print("Retrocedeu 5 segundos")
            self.execute_youtube_action('backward_5s')
        elif(eye_name == 'right'):
            # Ação para piscada no olho direito
            print("Avançou 5 segundos")
            self.execute_youtube_action('forward_5s')
    
    def handle_blink_twice_action(self) -> None:
        # Ação executada quando uma piscada dupla é detectada
        self.execute_youtube_action('fullscreen')
        print("Abriu tela cheia")
    
    def handle_absence_action(self, action_name: str) -> None:
        # Ação executada quando há ausência prolongada de rosto
        
        self.execute_youtube_action('play_pause')
        if(action_name == 'play'):
            print("Rosto detectado - Retomando vídeo")
        else:
            print("Ausência detectada - Pausando vídeo")
    
    def handle_custom_gesture(self, gesture_type: str, **kwargs) -> None:
        # Manipula gestos customizados futuros
        # Args:
        #     gesture_type: Tipo do gesto
        #     **kwargs: Parâmetros adicionais do gesto
            
        # Placeholder para gestos futuros como:
        # - Piscar olho direito vs esquerdo
        # - Manter olhos fechados por tempo prolongado
        # - Movimentos de cabeça
        # - etc.
        
        gesture_actions = {
            'long_blink': lambda: self.execute_youtube_action('play_pause'),
            'double_blink': lambda: self.execute_youtube_action('fullscreen'),
            'wink_left': lambda: self.execute_youtube_action('backward_5s'),
            'wink_right': lambda: self.execute_youtube_action('forward_5s'),
        }
        
        if gesture_type in gesture_actions:
            gesture_actions[gesture_type]()
        else:
            print(f"Gesto '{gesture_type}' não implementado ainda")
    
    def get_available_actions(self) -> Dict[str, str]:
        # Retorna lista de ações disponíveis
        
        return self.config.YOUTUBE_ACTIONS.copy()
    
    def set_action_interval(self, interval: float) -> None:
        # Define o intervalo mínimo entre ações
        
        self.min_action_interval = max(0.1, interval)  # Mínimo de 0.1s