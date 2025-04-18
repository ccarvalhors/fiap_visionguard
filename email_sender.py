import requests
import base64
import os

def send_email_alarm_live(email_to, image_b64, timestamp, message):
    """
    Envia um e-mail de alarme ao vivo para o destinatário especificado com uma imagem em anexo.

    Parâmetros:
    email_to (str): O endereço de e-mail para o qual o alarme será enviado.
    image_b64 (str): A imagem em base64 que será anexada ao e-mail, representando a captura do alarme.
    timestamp (str): A data e hora em que o alarme foi gerado, para ser incluída no corpo do e-mail.
    message (str): A mensagem do alarme a ser destacada no e-mail (ex: "Objeto cortante detectado").

    Retorna:
    None: A função envia um e-mail e imprime um log com o código de status e resposta da API.
    """

    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": os.getenv("BREVO_API_KEY"),
        "content-type": "application/json"
    }

    html_content = f"""
    <h3>🚨 Alarme detectado</h3>
    <p><strong>{message}</strong> em {timestamp}</p>
    """

    data = {
        "sender": {"name": "Vision Guard", "email": os.getenv("EMAIL_FROM")},
        "to": [{"email": email_to}],
        "subject": "Alarme ao vivo - Vision Guard",
        "htmlContent": html_content,
        "attachment": [{
            "name": "alarme.jpg",
            "content": image_b64
        }]
    }

    response = requests.post(url, headers=headers, json=data)
    print("[INFO] Alarme ao vivo enviado por e-mail:", response.status_code, response.text)

def send_email_with_pdf(email_to, report_path, original_filename):
    """
    Envia um e-mail com um relatório em PDF anexado para o destinatário especificado.

    Parâmetros:
    email_to (str): O endereço de e-mail para o qual o relatório será enviado.
    report_path (str): O caminho do arquivo PDF a ser anexado no e-mail.
    original_filename (str): O nome original do arquivo PDF, usado no assunto do e-mail e no nome do arquivo anexado.

    Retorna:
    None: A função envia um e-mail com o relatório em PDF e imprime um log com o código de status e resposta da API.
    """

    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": os.getenv("BREVO_API_KEY"),
        "content-type": "application/json"
    }

    with open(report_path, "rb") as f:
        encoded_pdf = base64.b64encode(f.read()).decode()

    data = {
        "sender": {"name": "Vision Guard", "email": os.getenv("EMAIL_FROM")},
        "to": [{"email": email_to}],
        "subject": f"📄 Relatório Vision Guard - {original_filename}",
        "htmlContent": f"<p>Seu relatório chegou! Veja em anexo.</p>",
        "attachment": [{
            "name": f"relatorio_{original_filename}.pdf",
            "content": encoded_pdf
        }]
    }

    response = requests.post(url, headers=headers, json=data)
    print("[INFO] Relatório enviado por e-mail:", response.status_code, response.text)
    