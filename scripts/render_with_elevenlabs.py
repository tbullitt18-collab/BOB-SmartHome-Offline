import os
import subprocess
import time
from pathlib import Path
import requests
import dotenv

ROOT_DIR = Path(r"C:\Users\tbull\.gemini\antigravity\scratch\BOB-SmartHome-Offline")
MEDIA_DIR = ROOT_DIR / "docs" / "media"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

# Load ElevenLabs credentials from the existing config
env_path = r"C:\Users\tbull\.gemini\antigravity\scratch\19pine-replica\.env"
env = dotenv.dotenv_values(env_path)
API_KEY = env.get("ELEVENLABS_API_KEY")
VOICE_ID = env.get("ELEVENLABS_VOICE_ID", "EkR0b2fNU4kBZ6syl9Vn")
MODEL_ID = env.get("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")

SCENES = [
    {
        "id": "scene1_intro",
        "text": "Welcome to BOB, the edge-native, offline-first smart home survival system built for the IBM TechXchange 2026 Hackathon. When severe storms knock out municipal power and internet connections, modern cloud-dependent smart homes become completely unresponsive. Homeowners are locked out, life-safety sensors fail, and backup battery reserves are rapidly depleted.",
    },
    {
        "id": "scene2_dashboard",
        "text": "BOB completely eliminates cloud vulnerability. Our command center operates entirely on local edge hardware with zero external dependencies. Running on pure vanilla JavaScript and a lightweight local API bridge, it provides real-time telemetry on circuit power consumption, local network health, UPS battery reserves, climate zones, and security locks.",
    },
    {
        "id": "scene3_watson_ai",
        "text": "BOB embeds Watson-class machine learning models directly on the edge hardware. Using local barometric pressure telemetry, our Random Forest storm predictor calculates outage probabilities offline. Simultaneously, an Isolation Forest anomaly detector monitors circuit currents, detecting power spikes to prevent electrical fires during severe weather.",
    },
    {
        "id": "scene4_occupancy_closed_loop",
        "text": "Unlike standard timers, BOB uses time-series occupancy modeling validated against millions of rows from the CASAS smart home dataset. During a disaster, BOB automatically sheds electrical load in unoccupied rooms while keeping life-safety zones powered, extending UPS battery survival from 4 hours to over 36 hours.",
    },
    {
        "id": "scene5_enterprise_scale",
        "text": "For enterprise multi-family communities and critical microgrids, BOB scales with K3s Kubernetes high-availability clustering, EMQX MQTT message brokers handling over one hundred thousand sensor messages per second, and Nginx edge load balancing with offline Graphite and Grafana metrics.",
    },
    {
        "id": "scene6_ibm_bob_usage",
        "text": "IBM Bob 2.0 served as our autonomous multi-agent engineering swarm, coordinating specialized subagents to generate edge machine learning, construct enterprise architecture, and execute rigorous chaos stress testing. BOB transforms fragile smart homes into resilient off-grid lifeboats.",
    }
]

def generate_elevenlabs_audio():
    print(f"Generating ElevenLabs Audio using Cloned Voice ID: {VOICE_ID}...")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    }

    for scene in SCENES:
        out_mp3 = MEDIA_DIR / f"{scene['id']}.mp3"
        print(f"   -> Synthesizing narration for {scene['id']} with cloned voice...")
        
        payload = {
            "text": scene['text'],
            "model_id": MODEL_ID,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.85,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }
        
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            with open(out_mp3, "wb") as f:
                f.write(response.content)
            print(f"      [OK] Saved {out_mp3.name} ({len(response.content)} bytes)")
        else:
            print(f"      [ERROR] ElevenLabs failed: {response.status_code} - {response.text}")
            raise RuntimeError(f"ElevenLabs TTS failed for {scene['id']}")

def reencode_video():
    print("Re-rendering HD Video Segments with Cloned Voice...")
    ffmpeg_exe = r"C:\ffmpeg\bin\ffmpeg.exe"
    video_segments = []

    for scene in SCENES:
        slide_img = MEDIA_DIR / f"{scene['id']}_slide.png"
        audio_mp3 = MEDIA_DIR / f"{scene['id']}.mp3"
        out_segment = MEDIA_DIR / f"{scene['id']}_segment.mp4"

        cmd = [
            ffmpeg_exe, "-y",
            "-loop", "1", "-i", str(slide_img),
            "-i", str(audio_mp3),
            "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            str(out_segment)
        ]
        print(f"   -> Rendering: {out_segment.name}...")
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        video_segments.append(out_segment)

    concat_list_file = MEDIA_DIR / "concat_list.txt"
    with open(concat_list_file, "w", encoding="utf-8") as f:
        for seg in video_segments:
            seg_escaped = str(seg).replace("\\", "/")
            f.write(f"file '{seg_escaped}'\n")

    final_video = ROOT_DIR / "docs" / "BOB_Hackathon_Demo_Video.mp4"
    print(f"   -> Assembling Final MP4: {final_video.name}...")
    concat_cmd = [
        ffmpeg_exe, "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list_file),
        "-c", "copy",
        str(final_video)
    ]
    subprocess.run(concat_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"🎉 FINAL VIDEO READY WITH CLONED VOICE: {final_video} ({final_video.stat().st_size / 1024 / 1024:.2f} MB)")

if __name__ == "__main__":
    generate_elevenlabs_audio()
    reencode_video()
