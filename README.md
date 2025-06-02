# Eye Tracking YouTube Controller

Sistema de controle do YouTube através de movimentos oculares usando OpenCV, dlib e eye tracking.

## 🎯 Funcionalidades

- **Detecção de Piscadas**: Avança o vídeo em 5 segundos
- **Detecção de Ausência**: Pausa automaticamente quando não detecta rosto
- **Interface Visual**: Mostra pontos dos olhos e informações de debug
- **Controles Manuais**: Teclas de teste para ações do YouTube

## 📁 Estrutura do Projeto

```
eye_control/
├── main.py              # Aplicação principal
├── config.py            # Configurações do sistema
├── eye_detector.py      # Detecção e análise ocular
├── action_controller.py # Controle de ações
├── requirements.txt     # Dependências
├── README.md           # Documentação
└── eye_points.dat      # Modelo de pontos faciais (dlib)
```

## 🚀 Como Usar

### 1. Instalação

```bash
pip install -r requirements.txt
```

### 2. Baixar Modelo do dlib

Baixe o arquivo `shape_predictor_68_face_landmarks.dat` e renomeie para `eye_points.dat`:

```bash
wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
bunzip2 shape_predictor_68_face_landmarks.dat.bz2
mv shape_predictor_68_face_landmarks.dat eye_points.dat
```

### 3. Executar

```bash
python main.py
```

## ⌨️ Controles

### Automáticos
- **Piscada**: Avança 5 segundos no vídeo
- **Ausência de rosto**: Pausa o vídeo

### Manuais (para teste)
- `q`: Sair da aplicação
- `p`: Play/Pause
- `f`: Tela cheia
- `m`: Mudo

## ⚙️ Configurações

Edite `config.py` para ajustar:

- `EAR_THRESHOLD`: Sensibilidade de detecção (0.15-0.25)
- `EAR_CONSECUTIVE_FRAMES`: Frames necessários para confirmar piscada
- `ABSENCE_THRESHOLD`: Frames sem rosto para pausar
- Ações do YouTube e teclas correspondentes

## 🎮 Ações Disponíveis

| Ação | Tecla | Descrição |
|------|-------|-----------|
| play_pause | space | Play/Pause |
| forward_5s | right | Avançar 5s |
| backward_5s | left | Retroceder 5s |
| forward_10s | l | Avançar 10s |
| backward_10s | j | Retroceder 10s |
| volume_up | up | Volume + |
| volume_down | down | Volume - |
| mute | m | Mudo |
| fullscreen | f | Tela cheia |
| next_video | shift+n | Próximo vídeo |
| previous_video | shift+p | Vídeo anterior |

## 🔧 Personalização

### Adicionar Nova Ação

1. Edite `YOUTUBE_ACTIONS` em `config.py`
2. Implemente a lógica em `action_controller.py`
3. Associe ao gesto desejado em `main.py`

### Adicionar Novo Gesto

1. Implemente detecção em `eye_detector.py`
2. Adicione ação correspondente em `action_controller.py`
3. Integre no loop principal em `main.py`

## 🐛 Resolução de Problemas

### Câmera não funciona
- Verifique se outra aplicação está usando a câmera
- Tente alterar `CAMERA_INDEX` em `config.py`

### Detecção imprecisa
- Ajuste `EAR_THRESHOLD` em `config.py`
- Melhore a iluminação do ambiente
- Posicione-se a uma distância adequada da câmera

### Ações muito frequentes
- Aumente `min_action_interval` em `ActionController`
- Ajuste `EAR_CONSECUTIVE_FRAMES` para mais frames

## 🚀 Próximas Funcionalidades

- [ ] Detecção de piscada de olho específico (esquerdo/direito)
- [ ] Gestos com movimentos de cabeça
- [ ] Interface gráfica para configurações
- [ ] Calibração automática de sensibilidade
- [ ] Suporte a outras plataformas (Netflix, etc.)
- [ ] Gravação e replay de gestos
- [ ] Controle de volume por duração da piscada

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob licença MIT. Veja LICENSE para detalhes.