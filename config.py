class EyeTrackingConfig:
    # Configurações principais do sistema
    
    # Dados dos pontos dos olhos
    SHAPE_PREDICTOR_PATH = "eye_points.dat"
    
    # Configurações da webcam
    CAMERA_INDEX = 0
    
    # Parâmetros de detecção ocular
    EAR_THRESHOLD = 0.15  # Limiar para detecção de olho fechado (0.15-0.25)
    EAR_CONSECUTIVE_FRAMES = 3  # Frames consecutivos para confirmar piscada
    
    # Parâmetros de ausência de rosto
    ABSENCE_THRESHOLD = 30  # Frames sem rosto para pausar
    
    # Índices dos pontos faciais (dlib 68-point model)
    LEFT_EYE_POINTS = list(range(36, 42))
    RIGHT_EYE_POINTS = list(range(42, 48))
    
    # Configurações de display
    WINDOW_NAME = "Eye Tracking Control"
    SHOW_EYE_POINTS = True
    SHOW_DEBUG_INFO = True
    
    # Teclas de controle
    QUIT_KEY = ord('q')
    
    # Ações do YouTube
    YOUTUBE_ACTIONS = {
        'play_pause': 'space',
        # 'next_video': 'shift+n',
        # 'previous_video': 'shift+p',
        'forward_5s': 'right',
        'backward_5s': 'left',
        # 'volume_up': 'up',
        # 'volume_down': 'down',
        # 'mute': 'm',
        'fullscreen': 'f'
    }