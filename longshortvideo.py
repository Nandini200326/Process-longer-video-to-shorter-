import os
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip, TextClip, vfx
from moviepy.audio.fx.all import audio_fadein

def create_short_video(input_video_path, output_video_path, clip_times, music_path, text_overlays):
    music = None  
    try:
        
        if not os.path.exists(input_video_path):
            print(f"Error: Video file '{input_video_path}' not found!")
            return
        
        if not os.path.exists(music_path):
            print(f"Error: Music file '{music_path}' not found!")
            return

        # Load the video
        video = VideoFileClip(input_video_path)
        print(f"Video duration: {video.duration} seconds")
        
        # Resize video to 9:16 aspect ratio (portrait mode), maintaining the original content center
        video_resized = video.resize(height=1920)  # Resize based on height for 9:16 aspect ratio
        video_resized = video_resized.crop(x1=0, y1=0, x2=1080, y2=1920)  # Crop to get the correct 9:16 frame

        # Extract clips based on provided time intervals
        clips = []
        for start, end in clip_times:
            if start < 0 or end > video_resized.duration or start >= end:
                print(f"Invalid clip times: start={start}, end={end}. Skipping...")
                continue
            try:
                clip = video_resized.subclip(start, end)
                if clip is not None:
                    clips.append(clip)
                else:
                    print(f"Subclip from {start} to {end} is None. Skipping...")
            except Exception as e:
                print(f"Error while creating subclip from {start} to {end}: {e}")
        
        # Check if we have valid clips
        if not clips:
            print("No valid clips to process. Exiting...")
            return

        # Apply zoom-in effect to focus on the robot and pan effect to focus on the target
        clips = [clip.fx(vfx.resize, 1.2).fx(vfx.crop, x_center=clip.w/2, y_center=clip.h/2, width=clip.w*0.8, height=clip.h*0.8) for clip in clips]

        # Apply crossfade transitions between clips
        clips_with_transitions = [clips[0]]
        for i in range(1, len(clips)):
            clips_with_transitions.append(clips[i].crossfadein(1))
        
        # Concatenate the clips to form the initial video
        final_video = concatenate_videoclips(clips_with_transitions, method="compose")

        # If the total duration is less than 30 seconds, loop the last clip to fill the remaining time
        while final_video.duration < 30:
            remaining_duration = 30 - final_video.duration
            last_clip = clips[-1].subclip(0, min(remaining_duration, clips[-1].duration))
            final_video = concatenate_videoclips([final_video, last_clip], method="compose")

        # Choose background music and ensure it fits the video duration
        music = AudioFileClip(music_path).subclip(0, final_video.duration)

        # Add fade-in to the music
        music = audio_fadein(music, 2)

        # Create timestamped text clips using MoviePy's TextClip
        text_clips = []
        for i, (start, end) in enumerate(clip_times):
            text = TextClip(f"{text_overlays[i]} - Timestamp: {start}", fontsize=50, color='white', bg_color='black').set_duration(end - start).set_position(('left', 'bottom')).set_start(start)
            text_clips.append(text)

        # Combine video with text overlays (timestamps)
        final_video = CompositeVideoClip([final_video] + text_clips)

        # Set audio
        final_video = final_video.set_audio(music)

        # Export the final video
        final_video.write_videofile(output_video_path, codec="libx264", audio_codec="aac", fps=24)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Explicitly close the video and audio clips to avoid resource leaks
        video.close()
        if music:
            music.close()
        for clip in clips:
            clip.close()


input_video_path = "C:/Users/HPlap/OneDrive/Desktop/fog/long.mp4"  
output_video_path = "C:/Users/HPlap/OneDrive/Desktop/fog/short_video.mp4" 
music_path = "C:/Users/HPlap/OneDrive/Desktop/fog/background.mp3"  
clip_times = [(5, 9), (9, 14), (14, 19), (19, 24), (24, 30)]  
text_overlays = ["Exciting Start", "Amazing Scene", "Thrilling Moment", "Dramatic Turn", "Epic Finale"]

create_short_video(input_video_path, output_video_path, clip_times, music_path, text_overlays)