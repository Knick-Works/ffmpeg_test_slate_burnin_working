
import subprocess
import os
import json
import datetime

# Define paths
input_path = 'C:/Code/FtrackStuff/zoo_slate_example.mp4'
output_path = 'C:/Code/FtrackStuff/zoo_slate_example_output.mp4'
intro_image_path = 'C:/Code/FtrackStuff/intro_frame.png'
intro_video_path = 'C:/Code/FtrackStuff/intro_frame.mp4'
temp_video_path = 'C:/Code/FtrackStuff/temp_video.mp4'
concat_list_path = 'C:/Code/FtrackStuff/concat_list.txt'

# Use ffprobe to get video metadata
ffprobe_command = [
    'ffprobe', '-v', 'error', '-select_streams', 'v:0',
    '-show_entries', 'stream=width,height,r_frame_rate,display_aspect_ratio,sample_aspect_ratio,nb_frames,duration,pix_fmt,codec_name,time_base',
    '-of', 'json', input_path
]

process = subprocess.Popen(ffprobe_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
output, error = process.communicate()

# Parse the metadata
metadata = json.loads(output.decode('utf-8'))
stream = metadata['streams'][0]
width = stream['width']
height = stream['height']
fps = eval(stream['r_frame_rate'])  # This evaluates the fraction correctly
single_frame_duration = 1 / fps  
total_frames = stream.get('nb_frames')
duration = stream.get('duration') 
total_duration = float(duration) + single_frame_duration
input_format = stream.get('pix_fmt', 'unknown')
input_codec = stream.get('codec_name', 'unknown')
input_time_base = stream.get('time_base', 'unknown')
input_timescale = input_time_base.split('/')[-1]
font_size = min(width, height) * 0.02

creation_date = datetime.datetime.fromtimestamp(os.path.getmtime(input_path)).strftime('%d %B %Y')
filename = os.path.basename(input_path)

# Step 1: Generate a black frame image
generate_image_command = [
    'ffmpeg', '-f', 'lavfi', '-i', f'color=c=black:s={width}x{height}', '-vf',
    f"drawtext=fontfile=Arial.ttf: text='{filename}': x=(w-tw)/2: y=(h-th)/2: fontcolor=white: fontsize={int(font_size)}",
    '-frames:v', '1', intro_image_path
]

subprocess.run(generate_image_command)

# Step 2: Create a video from this frame with a single frame duration

create_video_command = [
    'ffmpeg', '-loop', '1', '-i', intro_image_path, '-t', str(single_frame_duration), '-r', str(fps),
    '-vf', f"fps={fps},format={input_format}", '-video_track_timescale', input_timescale, intro_video_path
]
subprocess.run(create_video_command)



# Adjusted Step 3: Concatenate the frame with the original video without applying text overlays yet
with open(concat_list_path, 'w') as f:
    f.write(f"file '{intro_video_path}'\n")  # Add intro video
    f.write(f"file '{input_path}'\n")  # Add input video

concat_command = [
    'ffmpeg', '-f', 'concat', '-safe', '0', '-i', concat_list_path, '-c:v', 'copy', '-c:a', 'copy', temp_video_path  # Use temp_video_path for concatenated video
]
subprocess.run(concat_command)

# New Step 4: Apply text overlays to the concatenated video
apply_text_overlays_command = [
    'ffmpeg', '-i', temp_video_path, '-vf',
    f"drawtext=fontfile=Arial.ttf: text='{filename}_{width}x{height}_{fps}fps': x=(w-tw)/2: y=h-th-{int(font_size)}: fontcolor=white: fontsize={int(font_size)}: box=1: boxcolor=black@1: boxborderw=5,"
    f"drawtext=fontfile=Arial.ttf: text='%{{n}}': x=10: y=h-th-{int(font_size)}: fontcolor=white: fontsize={int(font_size)}: box=1: boxcolor=black@1: boxborderw=5,"
    f"drawtext=fontfile=Arial.ttf: text='{creation_date}': x=w-tw-10: y=h-th-{int(font_size)}: fontcolor=white: fontsize={int(font_size)}: box=1: boxcolor=black@1: boxborderw=5",
    '-c:v', input_codec, '-c:a', 'copy', output_path  # Output the final video with overlays
]

subprocess.run(apply_text_overlays_command)

# Clean up temporary files
os.remove(intro_image_path)
os.remove(intro_video_path)
os.remove(temp_video_path)  # Ensure this is the correct file to delete after confirming it's no longer needed
os.remove(concat_list_path)










