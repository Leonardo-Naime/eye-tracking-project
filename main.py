# main

import sys
from eye_tracking_app import EyeTrackingApp


def main():
    # Função para iniciar a aplicação de eye tracking
    try:
        app = EyeTrackingApp()
        app.run()
    except Exception as e:
        print(f"Erro na aplicação: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()