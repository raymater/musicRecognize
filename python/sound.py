import http.client
import json
import subprocess
import os
import random
import string
import base64
import math


def randomString():
    characters = string.ascii_letters + string.digits
    random_string = ""
    for i in range(32):
        random_string += random.choice(characters)
    return random_string


def detectSong(encodeSong):
    conn = http.client.HTTPSConnection("shazam.p.rapidapi.com")
    apiKey = "... YOUR API KEY ..."
    headers = {
        'content-type': "text/plain",
        'X-RapidAPI-Key': apiKey,
        'X-RapidAPI-Host': "shazam.p.rapidapi.com"
    }
    conn.request("POST", "/songs/v2/detect?timezone=Europe%2FParis&locale=fr-FR", encodeSong, headers)
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))


def convertVideoToAudio(videoFile):
    filename = randomString()
    current_dir = os.getcwd()
    exe_path = os.path.join(current_dir, "bin", "ffmpeg", "ffmpeg.exe")
    video_path = os.path.join(current_dir, "upload", videoFile)
    extract_path = os.path.join(current_dir, "export", "extract", f"{filename}.mp3")
    subprocess.call([exe_path, "-y", "-i", video_path, extract_path], stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
    return (filename + ".mp3")


def encodeSong(soundFile, seconds):
    filename = randomString()
    current_dir = os.getcwd()
    sound_path = os.path.join(current_dir, "export", "extract", soundFile)
    extract_path = os.path.join(current_dir, "export", "raw", f"{filename}.wav")
    exe_path = os.path.join(current_dir, "bin", "ffmpeg", "ffmpeg.exe")
    outProcess = subprocess.check_output([exe_path, "-y", "-i", sound_path, "-b:a", "16", "-ac", "1", "-r", "44100", "-c:a", "pcm_s16le", "-ss", str(seconds), "-to", str(seconds+4), extract_path])
    with open(extract_path, "rb") as fileRead:
        binary_data = fileRead.read()
    byte_array = bytearray(binary_data)
    base64_encoded = base64.b64encode(byte_array)
    return base64_encoded


def getDurationVideo(videoFile):
    current_dir = os.getcwd()
    exe_path = os.path.join(current_dir, "bin", "ffmpeg", "ffprobe.exe")
    video_path = os.path.join(current_dir, "upload", videoFile)
    output = subprocess.check_output([exe_path, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", video_path])
    output_str = output.decode("utf-8")
    duration = output_str.strip()
    return int(math.trunc(float(duration)))


# Testing
duration = getDurationVideo("testvideofile.mp4")
audioVideo = convertVideoToAudio("testvideofile.mp4")
cursorSeconds = 0
detects = []
while(cursorSeconds < duration):
    soundToTest = encodeSong(audioVideo, cursorSeconds)
    cursorSeconds += 4
    result = detectSong(soundToTest)
    detects.append(result["matches"])
print("Results :")
print(json.dumps(detects))