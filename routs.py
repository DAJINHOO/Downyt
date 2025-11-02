from app import app
from flask import render_template, request, url_for, redirect, send_file, after_this_request
from pytubefix import YouTube
from pytubefix.cli import on_progress
import tempfile

import os


def baixar_audio(video_link):
    yt = YouTube(video_link, on_progress_callback=on_progress)
    print(f"Título: {yt.title}")

    # cria arquivo temporário com extensão .m4a
    with tempfile.NamedTemporaryFile(delete=False, suffix=".m4a") as tmp:
        ys = yt.streams.get_audio_only()
        ys.download(filename=tmp.name)
        tmp.flush()

        # garante que o arquivo será removido depois do envio
        @after_this_request
        def remove_file(response):
            try:
                os.remove(tmp.name)
                print(f"🧹 Arquivo temporário removido: {tmp.name}")
            except Exception as e:
                print(f"Erro ao apagar arquivo temporário: {e}")
            return response

        print("✅ Áudio baixado com sucesso, enviando ao usuário...")
        return send_file(
            tmp.name,
            as_attachment=True,
            download_name=f"{yt.title}.m4a"
        )


def baixar_video(video_link):
    yt = YouTube(video_link, on_progress_callback=on_progress)
    print(f"Título: {yt.title}")

    # cria arquivo temporário com extensão .mp4
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        ys = yt.streams.get_highest_resolution()
        ys.download(filename=tmp.name)
        tmp.flush()

        # garante que o arquivo será removido depois do envio
        @after_this_request
        def remove_file(response):
            try:
                os.remove(tmp.name)
                print(f"🧹 Arquivo temporário removido: {tmp.name}")
            except Exception as e:
                print(f"Erro ao apagar arquivo temporário: {e}")
            return response

        print("✅ Vídeo baixado com sucesso, enviando ao usuário...")
        return send_file(
            tmp.name,
            as_attachment=True,
            download_name=f"{yt.title}.mp4"
        )




#rotas
@app.route("/",methods=['GET', 'POST'])
def homepage():
    
    return render_template ("index.html")


@app.route('/baixar', methods=['POST'])
def baixar():
    # Captura o link do YouTube
    video_link = request.form.get('youtubeLink')

    # Captura o formato escolhido (mp4 ou mp3)
    formato = request.form.get("formato")
    print(video_link)
    print(formato)
    # Validação simples
    if not video_link or not formato:
        return redirect(url_for('homepage'))
    if formato == "audio":
        baixar_audio(video_link)
    elif formato =="mp4":
        baixar_video(video_link)
        


   
    return redirect(url_for('homepage'))