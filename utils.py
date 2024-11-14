import os
import secrets
from PIL import Image
from flask import current_app

def salvar_foto_perfil(foto_perfil):
    # Gera um nome único para a imagem usando um token aleatório
    nome_arquivo = secrets.token_hex(8)
    _, extensao_arquivo = os.path.splitext(foto_perfil.filename)
    nome_arquivo_final = nome_arquivo + extensao_arquivo

    # Define o caminho onde a imagem será salva
    caminho_imagem = os.path.join(current_app.root_path, 'static/fotos_perfil', nome_arquivo_final)

    # Redimensiona a imagem (opcional)
    tamanho_output = (200, 200)
    img = Image.open(foto_perfil)
    img.thumbnail(tamanho_output)

    # Salva a imagem no caminho definido
    img.save(caminho_imagem)

    return nome_arquivo_final
