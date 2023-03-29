import os
import sys
import getopt
import subprocess
import platform
from better_ffmpeg_progress import FfmpegProcess

class Main:

    def __init__(self) -> None:
        self.input_path = ""
        self.output_path = ""
        self.dry_run = False
        self.os_environment = platform.system()
        self.video_extensions = (".mp4", ".MP4", ".mov", ".MOV")
        self.ffmpeg_binary = "/usr/bin/ffmpeg"
        self.ffmpeg_commands = []
        self.shell = False

        self.use_current_dir = False
        self.root_dir = "/home/user/Videos"
        self.current_basename = os.path.basename(self.root_dir)
        self.output_root = "/media/ek/2tb_m2/proxy_output"

        self.videos = []
        self.total_video_size = 0
        self.failed_videos = []

        if self.os_environment.lower() == "windows":
            self.ffmpeg_binary = "D:/ffmpeg/bin/ffmpeg.exe"
            self.shell = True
        
        elif self.os_environment.lower() == "linux":
            self.use_current_dir = True
            self.input_path = self.root_dir

    def commandLineHandler(self):
        # Parameters available: -i/--input <path>, -o/--output <path>, -v/--verbose, -d/--dryrun, -h/--help

        argv = sys.argv[1:]

        try:
            opts, args = getopt.getopt(argv, "i:o:vdh", ["input=", "output=", "verbose", "dryrun", "help"])

            if len(opts) == 0:
                self.help()

            for opt, arg in opts:
                if opt in ["-i", "--input"]:
                    self.input_path = arg
                
                elif opt in ["-o", "--output"]:
                    self.output_path = arg

                elif opt in ["-d", "--dryrun"]:
                    self.dry_run = True

                elif opt in ["-h", "--help"]:
                    self.help()

        except Exception as error:
            print("ERROR: Main - commandLineHandler - %s" % (error))
            print("Use -h or --help for available commands.")

    def help(self):

        print("========================================================")
        print("batch transcoder - https://github.com/edzop/pymovieutils")
        print("========================================================")

        print("Available commands:")
        print("-i / --input <path>")
        print("-o / --output <path>")
        print("-d / --dryrun")
        print("-h / --help")

    def getVideos(self):
        if self.input_path == "":
            print("No input path/directory found. Add input path/directory after -i/--input command. E.g. python app.py -i D:/videos -o D:/videos/processed")

        else:
            self.total_video_size = 0

            for root, dirs, files in os.walk(self.input_path):
                for file in files:
                    if file.endswith(self.video_extensions):
                        video_directory = os.path.join(root, file)
                        self.videos.append(video_directory)
                        self.total_video_size += os.stat(video_directory).st_size

            print()
            print("The following videos will be processed.")
            print(self.videos)
            print()
            print("Total videos to process: %s" % len(self.videos))
            print("Total video file size: %s MB" % "{:.2f}".format(self.total_video_size / (1024 * 1024)))
            print()

    def processVideos(self):

        if self.input_path == "":
            print("No output path/directory found. Add output path/directory after -o/--output command. E.g. python app.py -i D:/videos -o D:/videos/processed")

        else:
            process_video_size = 0

            for index, video in enumerate(self.videos, start=1):
                if self.os_environment.lower() == "windows":
                    self.make_ffmpeg_win_command(video)
                else:
                    output_directory = self.output_root + os.path.sep + self.current_basename + os.path.sep
                    self.validate_output_path(output_directory)
                    output_file = output_directory + os.path.basename(video)

                    print("video: %s"%video)

                    input_streams = self.get_timecodestream(video)

                    self.make_transcode_command(video, output_file, input_streams)

                if self.dry_run == False:
                    percent_progress = process_video_size / self.total_video_size * 100
                    format_percent_progress = "{:.2f}%".format(percent_progress)

                    print("Processing %s, (%s of %s) %s" % (video, index, len(self.videos), format_percent_progress))
                    print("with following commands: %s" % " ".join(self.ffmpeg_commands))

                    #process = FfmpegProcess(self.ffmpeg_commands)
                    #process.run()

                    if subprocess.run(self.ffmpeg_commands, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=self.shell).returncode == 0:
                        print("Successfully processed %s" % video)

                        process_video_size += os.stat(video).st_size
                    else:
                        self.failed_videos.append(video)
                        print("Failed to process %s" % video)

                else:
                    print("ffmpeg commands to execute for video %s" % video)
                    print(" ".join(self.ffmpeg_commands))
                    print()

            print("Processed videos can be found at %s" % self.output_path)
            print()

    def validate_output_path(self, video_dirname):
        # Replace input path with output path.
        new_output_path = str(video_dirname).replace(self.input_path, self.output_path)
        
        # Create output path if not existing.
        if not os.path.exists(new_output_path):
            os.makedirs(new_output_path)
        
        return new_output_path
    
    def make_ffmpeg_win_command(self, video):
        self.ffmpeg_commands = []
        self.ffmpeg_commands.append(self.ffmpeg_binary)
        self.ffmpeg_commands.append("-i")
        self.ffmpeg_commands.append("%s" % video)
        self.ffmpeg_commands.append("-c:v")
        self.ffmpeg_commands.append("libx264")
        self.ffmpeg_commands.append("-preset")
        self.ffmpeg_commands.append("fast")
        self.ffmpeg_commands.append("-crf")
        self.ffmpeg_commands.append("22")
        self.ffmpeg_commands.append("-s")
        self.ffmpeg_commands.append("1280x720")
        self.ffmpeg_commands.append("-c:a")
        self.ffmpeg_commands.append("aac")
        self.ffmpeg_commands.append("-b:a")
        self.ffmpeg_commands.append("196k")
        self.ffmpeg_commands.append("-ar")
        self.ffmpeg_commands.append("44100")
        self.ffmpeg_commands.append("-pix_fmt")
        self.ffmpeg_commands.append("yuv420p")
        self.ffmpeg_commands.append("%s/processed_%s" % (self.validate_output_path(os.path.dirname(video)), os.path.basename(video)))

    def get_timecodestream(self, input_file):
        ffprobe_binary = "/usr/bin/ffprobe"
        ffprobe_commands = []
        
        ffprobe_commands.append(ffprobe_binary)
        
        ffprobe_commands.append("-v")
        ffprobe_commands.append("error")
        
        ffprobe_commands.append("-select_streams")
        ffprobe_commands.append("d")
        
        ffprobe_commands.append("-show_entries")
        ffprobe_commands.append("stream=index")
        
        ffprobe_commands.append("-of")
        ffprobe_commands.append("csv=p=0")
        
        ffprobe_commands.append(input_file)

        print(ffprobe_commands)
        
        output = subprocess.check_output(ffprobe_commands).decode(sys.stdout.encoding).strip()
        
        result = []
        
        for line in output.splitlines():
            print(line)
            result.append(int(line))
            #result = int(output)
        
        print(result)
        
        return result

    def make_transcode_command(self, input_file, output_file, timecode_streams):
        self.ffmpeg_commands = []

        self.ffmpeg_commands.append(self.ffmpeg_binary)
        
        self.ffmpeg_commands.append("-y") # overwrite if exist
        
        self.ffmpeg_commands.append("-i")
        self.ffmpeg_commands.append(input_file)
        
        self.ffmpeg_commands.append("-pix_fmt")
        #self.ffmpeg_commands.append("yuv422p10le")
        self.ffmpeg_commands.append("yuv420p10le")

        #yuv420p10le
        
        self.ffmpeg_commands.append("-c:v")
        self.ffmpeg_commands.append("libx265")

        self.ffmpeg_commands.append("-x265-params")
        self.ffmpeg_commands.append("profile=main10")

        self.ffmpeg_commands.append("-vf")
        self.ffmpeg_commands.append("scale=960:-1")

        #ffmpeg_commands.append("-map_metadata")
        #ffmpeg_commands.append("0")
        
        for stream in timecode_streams:
            self.ffmpeg_commands.append("-map_metadata")
            self.ffmpeg_commands.append("0:s:%d"%stream)
        
        self.ffmpeg_commands.append("-crf")
        self.ffmpeg_commands.append("10")
        
        self.ffmpeg_commands.append(output_file)
        
main = Main()
main.commandLineHandler()
main.getVideos()
main.processVideos()