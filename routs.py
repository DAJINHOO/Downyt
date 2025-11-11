import os
from app import app
from flask import render_template, request, url_for, redirect, send_file, after_this_request
from pytubefix import YouTube
from pytubefix.cli import on_progress
import tempfile


def baixar_audio(video_link):
    try:
        yt = YouTube(video_link)
        print(f"🎵 Baixando áudio: {yt.title}")

        # Cria arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix=".m4a") as tmp:
            tmp_path = tmp.name
        
        # FAZ O DOWNLOAD FORA do bloco with
        ys = yt.streams.get_audio_only()
        if not ys:
            return "Nenhum stream de áudio encontrado", 400
            
        print("⬇️ Iniciando download...")
        ys.download(output_path=os.path.dirname(tmp_path), filename=os.path.basename(tmp_path))
        print("✅ Download completo!")
        
        # Verifica se o arquivo tem conteúdo
        file_size = os.path.getsize(tmp_path)
        print(f"📁 Tamanho do arquivo: {file_size} bytes")
        
        if file_size == 0:
            return "Arquivo baixado está vazio", 500

        @after_this_request
        def remove_file(response):
            try:
                os.remove(tmp_path)
                print(f"🧹 Arquivo removido: {tmp_path}")
            except Exception as e:
                print(f"Erro ao remover arquivo: {e}")
            return response

        return send_file(
            tmp_path,
            as_attachment=True,
            download_name=f"{yt.title}.m4a"
        )
        
    except Exception as e:
        print(f"❌ Erro no áudio: {e}")
        return f"Erro no download do áudio: {str(e)}", 500

def baixar_video(video_link):
    try:
        yt = YouTube(video_link, on_progress_callback=on_progress)
        print(f"Título: {yt.title}")

        # cria arquivo temporário com extensão .mp4
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp_path = tmp.name
        
        ys = yt.streams.get_highest_resolution()
        if not ys:
            return "Nenhum stream de video encontrado", 400
        
        ys.download(output_path=os.path.dirname(tmp_path), filename=os.path.basename(tmp_path))
        print("✅ Download completo!")
        
        @after_this_request
        def remove_file(response):
            try:
                os.remove(tmp_path)
                print(f"🧹 Arquivo removido: {tmp_path}")
            except Exception as e:
                print(f"Erro ao remover arquivo: {e}")
            return response

        return send_file(
            tmp_path,
            as_attachment=True,
            download_name=f"{yt.title}.mp4")
    except:
        print("erro no processo de download")



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
        return baixar_audio(video_link)
    elif formato =="mp4":
        return baixar_video(video_link)
        


   
    return redirect(url_for('homepage'))