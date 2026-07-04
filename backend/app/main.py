from backend.app.schemas import VideoRequest
from backend.worker.processors.editor import process_video_compilation
from fastapi import FastAPI
from fastapi.responses import FileResponse
from backend.app.schemas import TTSRequest
from backend.worker.processors import get_irodori_speech

# Initialize the FastAPI application instance
app = FastAPI()

@app.get("/")
def read_root():
    """
    Root endpoint to verify that the backend API is up and running.
    """
    return {"message": "Hello World from Backend!"}


@app.post("/synthesize")
async def synthesize(request: TTSRequest):
    """
    Endpoint to handle text-to-speech synthesis requests.
    Takes a validated TTSRequest, generates the speech audio, and 
    returns the resulting WAV file directly to the client.
    """
    # Get the generated audio file path from the TTS service
    file_path = await get_irodori_speech(request.text)
    
    # Return the audio file directly as a FileResponse
    return FileResponse(
        path=file_path, 
        media_type="audio/wav", 
        filename="speech.wav"
    )


@app.post("/compile-video")
async def compile_video(request: VideoRequest):
    """
    Endpoint to trigger background video compilation.
    """
    # Add the task to FastAPI's background runner
    vdo_file = process_video_compilation(request.video_paths, request.audio_path, request.output_path)
    return FileResponse(
        path=vdo_file,
        media_type="video/mp4",
        filename="output.mp4"
    )