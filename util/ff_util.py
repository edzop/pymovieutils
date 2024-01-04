import subprocess

import platform
import sys

class ffprobe_helper:

    verbose=False

    ffmpeg_binary = "/usr/bin/ffmpeg"
    ffprobe_binary = "/usr/bin/ffprobe"
    use_shell = False

    def __init__(self,verbose=False):
        self.verbose=verbose

        self.os_environment = platform.system()

        if self.os_environment.lower() == "windows":
            self.ffprobe_binary = "D:/ffmpeg/bin/ffprobe.exe"
            self.ffmpeg_binary = "D:/ffmpeg/bin/ffmpeg.exe"
            self.use_shell = True

    def get_video_duration(self,input_file):

        ffprobe_commands = []

        ffprobe_commands.append(self.ffprobe_binary)

        ffprobe_commands.append("-v")
        ffprobe_commands.append("error")

        ffprobe_commands.append("-show_entries")
        ffprobe_commands.append("format=duration")

        ffprobe_commands.append("-of")
        ffprobe_commands.append("default=noprint_wrappers=1:nokey=1")

        ffprobe_commands.append(input_file)

        if self.verbose:
            print(ffprobe_commands)
        
        output = subprocess.check_output(ffprobe_commands).decode(sys.stdout.encoding).strip()

        video_duration = 0

        for line in output.splitlines():

            video_duration+=float(line)
        
        return video_duration


    # Probe metadata streams from source video file using ffprobe
    def get_timecodestream(self, input_file):

        ffprobe_commands = []
        
        ffprobe_commands.append(self.ffprobe_binary)
        
        ffprobe_commands.append("-v")
        ffprobe_commands.append("error")
        
        ffprobe_commands.append("-select_streams")
        ffprobe_commands.append("d")
        
        ffprobe_commands.append("-show_entries")
        ffprobe_commands.append("stream=index")
        
        ffprobe_commands.append("-of")
        ffprobe_commands.append("csv=p=0")
        
        ffprobe_commands.append(input_file)

        if self.verbose:
            print(ffprobe_commands)
        
        output = subprocess.check_output(ffprobe_commands).decode(sys.stdout.encoding).strip()

        result = []
        
        for line in output.splitlines():

            result.append(int(line))

        if self.verbose:
            print("ffprobe data streams: %s"%result)

        return result
    
    def ffmpeg_encode(self, input_file, output_file, timecode_streams):
        ffmpeg_commands = []

        ffmpeg_commands.append(self.ffmpeg_binary)
        
        # overwrite if exist
        ffmpeg_commands.append("-y")
        
        ffmpeg_commands.append("-i")
        ffmpeg_commands.append(input_file)
        
        ffmpeg_commands.append("-pix_fmt")

        #ffmpeg_commands.append("yuv422p10le")
        ffmpeg_commands.append("yuv420p10le")
        
        ffmpeg_commands.append("-c:v")
        ffmpeg_commands.append("libx265")

        ffmpeg_commands.append("-x265-params")
        ffmpeg_commands.append("profile=main10")

        ffmpeg_commands.append("-vf")
        ffmpeg_commands.append("scale=960:-1")

        for stream in timecode_streams:
            ffmpeg_commands.append("-map_metadata")
            ffmpeg_commands.append("0:s:%d"%stream)
        
        ffmpeg_commands.append("-crf")
        ffmpeg_commands.append("10")
        
        ffmpeg_commands.append(output_file)
    
        if self.verbose:
            print("command: %s" % " ".join(ffmpeg_commands))

        output = subprocess.check_output(ffmpeg_commands)
        print(output)
        return_code = subprocess.run(ffmpeg_commands, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=self.use_shell).returncode

        if return_code == 0:
            return True
        else:
            print("error code: %d (Failed to process %s)" %(return_code,input_file))
            return False




