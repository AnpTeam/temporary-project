import logging
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips

# Configure logging for easier debugging in a server environment
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_video_compilation(video_paths, audio_path, output_path):
    """
    Concatenates videos and applies a background audio track.
    
    :param video_paths: List of strings (paths to video files)
    :param audio_path: String (path to audio file)
    :param output_path: String (where to save the final file)
    """
    video_clips = []
    final_clip = None
    audio_clip = None
    
    try:
        # 1. Load video clips
        logger.info(f"Loading {len(video_paths)} video clips...")
        video_clips = [VideoFileClip(p) for p in video_paths]
        
        # 2. Concatenate
        logger.info("Concatenating clips...")
        combined = concatenate_videoclips(video_clips, method="compose")
        
        # 3. Load and attach audio
        logger.info("Loading and attaching audio...")
        audio_clip = AudioFileClip(audio_path)
        
        # Ensure the audio matches the video duration
        # (Optional: loop the audio if it's shorter than the video)
        final_clip = combined.with_audio(audio_clip)
        
        # 4. Export
        logger.info(f"Writing output to {output_path}...")
        final_clip.write_videofile(
            output_path, 
            codec="libx264", 
            audio_codec="aac",
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )
        return True

    except Exception as e:
        logger.error(f"Error processing video: {e}")
        return False

    finally:
        # 5. Resource cleanup (Critical for API stability)
        if final_clip: final_clip.close()
        if audio_clip: audio_clip.close()
        for clip in video_clips:
            clip.close()
        logger.info("Resources cleaned up.")