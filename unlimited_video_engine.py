import os
import requests
import asyncio
import edge_tts
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from moviepy.editor import TextClip, AudioFileClip, VideoFileClip, CompositeVideoClip, ColorClip

app = FastAPI(title="Unlimited Script-to-Video Engine")

PEXELS_API_KEY = "m44mrxNCnMcHOnCiHVS96ptGORmnJHCZkaTOV96vEJRc0pc1elUlRJUb"

def download_broll_video(query: str, output_filename="broll.mp4"):
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=1&orientation=portrait"
    
    try:
        response = requests.get(url, headers=headers).json()
        if response.get("videos"):
            video_files = response["videos"][0]["video_files"]
            video_url = next(f["link"] for f in video_files if f["height"] >= 1080 or f["width"] >= 720)
            video_data = requests.get(video_url).content
            with open(output_filename, "wb") as f:
                f.write(video_data)
            return output_filename
    except Exception as e:
        print(f"B-roll error: {e}")
    return None

async def generate_voiceover(text: str, output_filename="voiceover.mp3"):
    communicate = edge_tts.Communicate(text, "en-US-ChristopherNeural")
    await communicate.save(output_filename)
    return output_filename

def render_final_video(script_text: str, audio_path: str, video_path: str, output_path="final_video.mp4"):
    audio = AudioFileClip(audio_path)
    audio_duration = audio.duration

    if video_path and os.path.exists(video_path):
        broll = VideoFileClip(video_path)
        if broll.duration < audio_duration:
            broll = broll.loop(duration=audio_duration)
        else:
            broll = broll.subclip(0, audio_duration)
        broll = broll.resize(newsize=(1080, 1920))
    else:
        broll = ColorClip(size=(1080, 1920), color=(15, 23, 42), duration=audio_duration)

    txt_clip = TextClip(
        script_text, fontsize=50, color='white', bg_color='black',
        size=(900, None), method='caption'
    ).set_position(('center', 1400)).set_duration(audio_duration)

    final_clip = CompositeVideoClip([broll, txt_clip]).set_audio(audio)
    final_clip.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac')
    return output_path

@app.post("/generate-video")
async def generate_video_endpoint(script: str, search_keyword: str = "nature"):
    try:
        audio_file = await generate_voiceover(script)
        video_file = download_broll_video(search_keyword)
        output_video = render_final_video(script, audio_file, video_file)
        return FileResponse(output_video, media_type="video/mp4", filename="generated_video.mp4")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
