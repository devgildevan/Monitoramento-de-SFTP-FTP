import os
import time
import asyncio
import paramiko
from telegram import Bot
from datetime import datetime

# Função para se conectar ao servidor SFTP (agora com a configuração de porta)
def conectar_sftp(host, username, password, port=22):  # Porta padrão 22
    try:
        # Estabelece a conexão SSH com a porta especificada
        transport = paramiko.Transport((host, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        return sftp
    except Exception as e:
        print(f"Erro ao conectar ao servidor SFTP: {e}")
        return None

# Função para listar arquivos do diretório SFTP
def listar_arquivos_sftp(sftp, caminho_pasta):
    try:
        arquivos = sftp.listdir_attr(caminho_pasta)
        return {arquivo.filename: arquivo.st_mtime for arquivo in arquivos}
    except Exception as e:
        print(f"Erro ao listar arquivos no SFTP: {e}")
        return {}

# Função para monitorar a pasta SFTP
async def monitorar_sftp(caminho_pasta, bot_token, chat_id, host, username, password, port=22):
    print(f"Iniciando monitoramento do SFTP: {caminho_pasta}")

    # Conecta ao servidor SFTP usando a porta fornecida
    sftp = conectar_sftp(host, username, password, port)
    if sftp is None:
        print("Falha na conexão SFTP.")
        return

    # Armazena os timestamps dos arquivos inicialmente
    arquivos_anteriores = listar_arquivos_sftp(sftp, caminho_pasta)

    try:
        while True:
            # Verifica o diretório a cada 10 segundos
            time.sleep(10)
            arquivos_atuais = listar_arquivos_sftp(sftp, caminho_pasta)

            # Compara os arquivos atuais com os anteriores
            for arquivo, mtime in arquivos_atuais.items():
                if arquivo not in arquivos_anteriores or arquivos_anteriores[arquivo] != mtime:
                    tipo_evento = "modificado" if arquivo in arquivos_anteriores else "criado"
                    mensagem = (
                        f"📂 Movimento detectado no SFTP!\n"
                        f"🔹 Tipo de evento: {tipo_evento}\n"
                        f"🔹 Arquivo: {arquivo}\n"
                        f"🔹 Caminho: {caminho_pasta}/{arquivo}\n"
                        f"🔹 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
                    )
                    await enviar_mensagem_telegram(bot_token, chat_id, mensagem)

            # Atualiza os arquivos anteriores
            arquivos_anteriores = arquivos_atuais

    except KeyboardInterrupt:
        print("Monitoramento encerrado.")

# Função para enviar a mensagem via Telegram
async def enviar_mensagem_telegram(bot_token, chat_id, mensagem):
    bot = Bot(token=bot_token)
    await bot.send_message(chat_id=chat_id, text=mensagem)

# Configurações do Telegram
BOT_TOKEN = "Aqui vai o token do bot"
CHAT_ID = "Aqui vai o ID do chat do telegram."  # Substitua pelo ID do grupo ou chat do Telegram

# Configurações do SFTP
SFTP_HOST = "SEU HOST"  # Substitua pelo seu host SFTP
SFTP_USERNAME = "USER"  # Substitua pelo seu nome de usuário
SFTP_PASSWORD = 'PASSWOD'  # Substitua pela sua senha
SFTP_PORT = 22  # Substitua pela porta correta, se diferente de 22

# Caminho da pasta a ser monitorada no SFTP
CAMINHO_PASTA = "cAMINHO DO SFTP"  # Substitua pelo caminho desejado no SFTP

# Inicia o monitoramento
asyncio.run(monitorar_sftp(CAMINHO_PASTA, BOT_TOKEN, CHAT_ID, SFTP_HOST, SFTP_USERNAME, SFTP_PASSWORD, SFTP_PORT))
