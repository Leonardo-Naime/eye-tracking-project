# Eye Tracking YouTube Controller

Sistema avançado de controle do YouTube através de movimentos oculares usando OpenCV, dlib e eye tracking com múltiplas funcionalidades baseadas em gestos.

## 🎯 Funcionalidades

### Controles por Gestos Oculares
- **Piscada Olho Esquerdo**: Retrocede 5 segundos no vídeo
- **Piscada Olho Direito**: Avança 5 segundos no vídeo
- **Olhos Fechados (1.5s)**: Alterna tela cheia
- **Olhos Fechados (3s)**: Ativa/desativa modo volume
- **Detecção de Ausência**: Pausa automaticamente quando não detecta rosto

### Modo Volume
- **Piscada Olho Esquerdo** (no modo volume): Diminui volume
- **Piscada Olho Direito** (no modo volume): Aumenta volume
- Interface visual para indicar quando o modo está ativo

### Interface Visual
- Mostra pontos dos olhos em tempo real
- Barra de progresso para gestos de tempo prolongado
- Indicadores visuais para diferentes modos
- Informações de debug com valores EAR
- Feedback visual para todas as ações

## 📁 Estrutura do Projeto

```
eye-tracking-project/
├── main.py                 # Ponto de entrada da aplicação
├── eye_tracking_app.py     # Aplicação principal e lógica de integração
├── config.py              # Configurações do sistema
├── eye_detector.py        # Detecção e análise ocular
├── action_controller.py   # Controle de ações e integração com YouTube
├── requirements.txt       # Dependências Python
├── README.md             # Documentação do projeto
└── eye_points.dat        # Modelo de pontos faciais (dlib)
```

## 🚀 Como Usar

### 1. Instalação das Dependências

```bash
pip install -r requirements.txt
```

### 2. Executar a Aplicação

```bash
python3 main.py
```

## 🎮 Controles e Gestos

### Gestos Automáticos

| Gesto | Ação | Descrição |
|-------|------|-----------|
| Piscada olho esquerdo | ⏪ Retroceder 5s | No modo normal |
| Piscada olho direito | ⏩ Avançar 5s | No modo normal |
| Olhos fechados 1.5s | 🔳 Fullscreen | Alterna tela cheia |
| Olhos fechados 3s | 🔊 Modo Volume | Ativa/desativa controle de volume |
| Ausência de rosto | ⏸️ Pause/Play | Pausa quando sai, retoma quando volta |

### Modo Volume (após ativar)

| Gesto | Ação | Descrição |
|-------|------|-----------|
| Piscada olho esquerdo | 🔉 Volume - | Diminui volume (10 unidades) |
| Piscada olho direito | 🔊 Volume + | Aumenta volume (10 unidades) |
| Olhos fechados 3s | ❌ Desativar | Sai do modo volume |

### Controles Manuais (para teste)

| Tecla | Ação |
|-------|------|
| `q` | Sair da aplicação |
| `p` | Play/Pause manual |
| `m` | Mudo manual |

## ⚙️ Configurações Personalizáveis

Edite `config.py` para ajustar:

### Sensibilidade de Detecção
```python
EAR_THRESHOLD_RIGHT = 0.131  # Limiar olho direito
EAR_THRESHOLD_LEFT = 0.138   # Limiar olho esquerdo
EAR_CONSECUTIVE_FRAMES = 5   # Frames para confirmar piscada
```

### Detecção de Ausência
```python
ABSENCE_THRESHOLD = 30  # Frames sem rosto para pausar
```

### Câmera
```python
CAMERA_INDEX = 0  # Índice da webcam (0 = padrão)
```

### Ações do YouTube
```python
YOUTUBE_ACTIONS = {
    'play_pause': 'space',
    'forward_5s': 'right',
    'backward_5s': 'left',
    'volume_up': 'up',
    'volume_down': 'down',
    'fullscreen': 'f'
}
```

## 🎨 Interface Visual

### Feedback em Tempo Real
- **Pontos dos olhos**: Círculos verdes nos pontos detectados
- **Valores EAR**: Mostrados no canto superior esquerdo
- **Status dos olhos**: OPEN/LEFT CLOSED/RIGHT CLOSED/BOTH CLOSED

### Barra de Progresso
- **Amarelo**: Carregando para fullscreen (0-1.5s)
- **Laranja**: Carregando para modo volume (1.5-3s)
- **Magenta**: Modo volume pronto (3s+)
- **Linha branca**: Marca do fullscreen (1.5s)

### Indicadores de Modo
- **"MODO VOLUME ATIVO"**: Mostrado quando o modo volume está ligado
- **Mensagens temporárias**: Confirmação de ações executadas

### Ajustar Cooldowns

```python
# Em action_controller.py
self.min_action_interval = 0.5      # Intervalo geral entre ações
self.fullscreen_cooldown = 1.0      # Cooldown específico para fullscreen
```

### Personalizar Tempos de Gesto

```python
# Em eye_tracking_app.py
self.fullscreen_threshold = 1.5     # Tempo para fullscreen
self.volume_mode_threshold = 3.0    # Tempo para modo volume
```

## 🐛 Resolução de Problemas

### Câmera não detectada
```bash
# Teste diferentes índices de câmera
# Edite CAMERA_INDEX em config.py: 0, 1, 2...
```

### Detecção muito sensível/pouco sensível
```python
# Ajuste os limiares EAR em config.py
EAR_THRESHOLD_RIGHT = 0.131  # Diminua para menos sensível
EAR_THRESHOLD_LEFT = 0.138   # Aumente para mais sensível
```

### Ações executando muito rápido
```python
# Aumente os cooldowns em action_controller.py
self.min_action_interval = 1.0  # Era 0.5
```

### Fullscreen não funciona
- Certifique-se de que o YouTube está na aba ativa
- Alguns navegadores podem bloquear automação
- Teste a tecla 'f' manualmente no YouTube

## 📊 Valores de Referência

### EAR (Eye Aspect Ratio)
- **Olho aberto**: ~0.25-0.35
- **Olho fechado**: ~0.10-0.15
- **Limiar recomendado**: 0.13-0.14

### Timing dos Gestos
- **Piscada normal**: ~0.1-0.3s
- **Fullscreen**: 1.5s de olhos fechados
- **Modo volume**: 3.0s de olhos fechados

**Nota**: Certifique-se de que o YouTube está na aba ativa do navegador para que os controles funcionem corretamente.