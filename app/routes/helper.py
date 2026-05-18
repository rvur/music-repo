from flask import current_app
import yt_dlp
import os

def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )

def download_audio(youtube_url, output_dir="music"):
    ydl_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio",  # Prefer m4a, fallback to best audio
        "outtmpl": f"{output_dir}/%(title)s.%(ext)s",
        # Removed postprocessors to avoid ffmpeg requirement
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=True)
        
        # The file might be downloaded with extension like .m4a or .webm
        # Let's find the actual downloaded file
        thumbnail_url = info.get('thumbnail')
        base_name = f"{output_dir}/{info['title']}"
        for ext in ['.m4a', '.webm', '.mp4', '.opus']:
            potential_file = base_name + ext
            if os.path.exists(potential_file):
                return potential_file, info, thumbnail_url
        
        # Fallback: use the prepared filename
        filename = ydl.prepare_filename(info)
        return filename, info, thumbnail_url