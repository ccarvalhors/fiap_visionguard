
# 🛡️ VisionGuard

**VisionGuard** é uma aplicação web para detecção de objetos em tempo real via câmera ou a partir de vídeos enviados por upload. A aplicação permite visualizar alarmes no navegador, receber alertas por e-mail e gerar relatórios em PDF com as detecções realizadas.

---

## 🔍 Funcionalidades

- 💬 Modal inicial para coleta do e-mail do usuário da sessão.
- 📷 Captura e monitoramento ao vivo via webcam.
- 🎞️ Upload de vídeos para análise assíncrona.
- 📍 Detecção de objetos em imagens e vídeos.
- 📨 Envio de alarmes por e-mail com imagem em anexo.
- 📑 Geração automática de relatórios em PDF com as detecções do vídeo.
- 🧾 Modal com visualização ampliada de cada alarme.
- ⏱️ Barra de progresso no terminal para processamento de vídeos enviados.

---

## 🗂️ Estrutura do Projeto

```
visionguard/
├── server.py                 # Servidor Flask com WebSocket
├── requirements.txt          # Dependências Python
├── static/
│   ├── style.css             # Estilos do frontend
│   ├── script.js             # Scripts da interface
├── templates/
│   └── index.html            # Página principal da aplicação
├── reports/
│   └── *.pdf                 # Relatórios gerados
├── uploads/
│   └── *.mp4                 # Arquivos de vídeo enviados
```

---

## ⚙️ Instalação

### Instale as dependências

```bash
pip install -r requirements.txt
```

## ▶️ Executando

```bash
python server.py
```

Acesse no navegador:  
📍 `http://localhost:5000`

---

## 🧪 Como usar

### 📸 Modo Webcam

- Acesse a aplicação.
- Permita o uso da câmera.
- O sistema emitirá alarmes sempre que detectar novos objetos conforme configurado.
- Você receberá o alarme por e-mail com uma imagem.

### 📤 Upload de Vídeo

- Faça upload de um arquivo `.mp4`.
- Um alerta será exibido indicando que o relatório será enviado por e-mail.
- O servidor processa o vídeo em segundo plano e envia um relatório em PDF quando pronto.

---

## ✅ Requisitos

- Python 3.9+
- Flask + Flask-SocketIO
- OpenCV
- ReportLab
- Brevo (para envio de e-mails)

---

## 📜 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).
