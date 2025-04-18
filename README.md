
# 🛡️ VisionGuard

**VisionGuard** é uma aplicação web para **monitoramento inteligente por vídeo**, com detecção em tempo real de **objetos cortantes** e identificação da presença de **pessoas na cena**, permitindo classificar contextualmente os alarmes como:

- 🔪 **Objeto cortante detectado**
- 🧍‍♂️🔪 **Pessoa com objeto cortante detectado**

A aplicação pode ser usada com a **webcam ao vivo** ou por **vídeos enviados** via upload. Alarmes são exibidos na interface e enviados por e-mail com imagem, além da geração de **relatórios automáticos em PDF**.

---

## 🔍 Funcionalidades

- 💬 Modal inicial para coleta do e-mail do usuário da sessão.
- 📷 Captura e monitoramento ao vivo via webcam.
- 🎞️ Upload de vídeos para análise assíncrona.
- 📍 Detecção automática de **objetos cortantes**.
- 🧠 Identificação de presença humana na cena para classificar alarmes.
- 📨 Envio de alarmes por e-mail com imagem em anexo.
- 📑 Geração automática de relatórios em PDF com as detecções do vídeo.
- 🧾 Modal com visualização ampliada de cada alarme.
- ⏱️ Barra de progresso no terminal para processamento de vídeos enviados.

---

## 🧠 Lógica Inteligente de Alarme

O VisionGuard não apenas detecta objetos cortantes, mas **analisa o contexto da cena** para determinar a gravidade da ameaça:

| Situação Detectada                  | Tipo de Alarme                         |
|------------------------------------|----------------------------------------|
| Faca isolada na cena               | 🔪 Objeto cortante detectado           |
| Faca + presença de uma pessoa      | 🧍‍♂️🔪 Pessoa com objeto cortante detectado |

Esse mecanismo reduz falsos positivos e aumenta a confiabilidade em situações críticas.

Além disso, o sistema garante que **um mesmo tipo de alarme não seja emitido repetidamente** enquanto a situação permanece inalterada.

---

## 🗂️ Estrutura do Projeto

```
visionguard/
├── server.py                 # Servidor Flask com WebSocket e processamento da aplicação
├── email_sender.py           # Envio de e-mails
├── report.py                 # Geração do relatório de alarmes
├── helpers.py                # Funções auxiliares
├── requirements.txt          # Dependências Python
├── static/
│   ├── style.css             # Estilos do frontend
│   ├── script.js             # Scripts da interface
├── templates/
│   └── index.html            # Página principal da aplicação
├── models/
│   └── knife/best.pt         # Modelo YOLOv8 treinado para detecção de objetos cortantes
├── uploads/
│   └── *.mp4                 # Arquivos de vídeo enviados
├── reports/
│   └── *.pdf                 # Relatórios gerados automaticamente
├── alarms/
│   └── *.jpg                 # Imagens salvas dos alarmes detectados
```

---

## ⚙️ Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/ccarvalhors/fiap_visionguard.git
cd visionguard
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

Certifique-se de que o arquivo do modelo YOLOv8 (`best.pt`) está salvo na pasta `models/knife/`.

---

## 🔐 Configuração do `.env`

Antes de executar a aplicação, crie um arquivo chamado `.env` na raiz do projeto e adicione as seguintes variáveis de ambiente:

```env
# Chave da API do Brevo (https://www.brevo.com/)
BREVO_API_KEY=sua_chave_api_aqui

# Endereço de e-mail do remetente (deve estar autorizado no Brevo)
EMAIL_FROM=seu_email@dominio.com
```

---

## ▶️ Executando

```bash
python server.py
```

Acesse no navegador:  
📍 [http://localhost:5000](http://localhost:5000)

---

## 🧪 Como usar

### 📸 Modo Webcam

1. Acesse a aplicação no navegador.
2. Insira seu e-mail no modal inicial.
3. Clique em "Ligar Câmera" e permita o acesso à webcam.
4. O sistema analisará os frames em tempo real:
   - Emitirá alarmes quando detectar objetos cortantes.
   - Identificará se há uma pessoa na cena para qualificar o alarme.
5. Você receberá o alarme por e-mail com uma imagem da detecção.

> Ao desligar a câmera, o sistema também enviará um sinal para desarmar qualquer alarme ativo.

---

### 📤 Upload de Vídeo

1. Selecione um vídeo `.mp4` e clique em "Enviar".
2. O vídeo será processado em segundo plano.
3. Um relatório em PDF com todas as detecções será enviado para seu e-mail.

---

## ✅ Requisitos

- Python 3.9+
- Flask
- Flask-SocketIO
- OpenCV
- ReportLab
- Ultralytics (YOLOv8)
- Brevo (para envio de e-mails)

---

## 📜 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

---

### 👥 Autores

- Cristiano Carvalho
- Fabiano Pimenta
- Gabriel Neves
- Gustavo Pinheiro
