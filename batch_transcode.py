import os
import sys
import getopt
import subprocess
import platform
from better_ffmpeg_progress import FfmpegProcess

class Main:

    def __init__(self) -> None:

        self.printIntro()

        self.input_path = ""
        self.verbose=False

        self.dry_run = False
        self.os_environment = platform.system()
        self.video_extensions = (".mp4", ".MP4", ".mov", ".MOV")
        self.ffmpeg_binary = "/usr/bin/ffmpeg"
        self.ffprobe_binary = "/usr/bin/ffprobe"
        self.ffmpeg_commands = []
        self.use_shell = False

        self.videos = []

        self.total_input_video_size = 0
        self.total_output_video_size = 0

        self.failed_videos = []

        if self.os_environment.lower() == "windows":
            self.ffmpeg_binary = "D:/ffmpeg/bin/ffmpeg.exe"
            self.ffprobe_binary = "D:/ffmpeg/bin/ffprobe.exe"
            self.use_shell = True
        

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

                elif opt in ["-v", "--verbose"]:
                    self.verbose=True

                elif opt in ["-o", "--output"]:
                    self.output_path = arg

                elif opt in ["-d", "--dryrun"]:
                    self.dry_run = True

                elif opt in ["-h", "--help"]:
                    self.help()

        except Exception as error:
            print("ERROR: Main - commandLineHandler - %s" % (error))
            print("Use -h or --help for available commands.")

    def printIntro(self):
        print("========================================================")
        print("batch transcoder - https://github.com/edzop/pymovieutils")
        print("========================================================")


    def help(self):

        print("Available commands:")
        print("-i / --input <path>")
        print("-o / --output <path>")
        print("-d / --dryrun")
        print("-h / --help")

    # Return number of videos found
    def getVideos(self):

        if self.input_path == "":
            print("No input path found.")
            return 0

        self.total_input_video_size = 0

        for root, dirs, files in os.walk(self.input_path):
            for file in files:
                if file.endswith(self.video_extensions):
                    video_directory = os.path.join(root, file)
                    self.videos.append(video_directory)
                    self.total_input_video_size += os.stat(video_directory).st_size

        print("Total videos to process: %s" % len(self.videos))
        print("Total video file size: %s" %self.getHumanReadableFileSize(self.total_input_video_size))
        print()

        print("Input path: %s"%self.input_path)
        print("Output path: %s"%self.output_path)
        print()

        if self.verbose:
            print()
            print("The following videos will be processed.")
            print(self.videos)
            print()

        return len(self.videos)
    
    def getHumanReadableFileSize(self,size):
        return "%0.2f MB" % (size / (1024 * 1024) )

    def processVideos(self):

        total_processed_video_size = 0

        for index, video in enumerate(self.videos, start=1):

            output_directory = self.output_path + os.path.sep
            self.validate_output_path(output_directory)

            output_file = output_directory + os.path.basename(video)

            input_streams = self.get_timecodestream(video)

            self.make_transcode_command(video, output_file, input_streams)


            print("(%s of %s): %s" % (index, len(self.videos),video))
                
            if self.verbose:
                print("command: %s" % " ".join(self.ffmpeg_commands))

                #process = FfmpegProcess(self.ffmpeg_commands)
                #process.run()

            output_video_size=0
            input_video_size = os.stat(video).st_size

            if self.dry_run == False:
                if subprocess.run(self.ffmpeg_commands, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=self.use_shell).returncode == 0:
                    output_video_size = os.stat(output_file).st_size
                    self.total_output_video_size += output_video_size        
                else:
                    self.failed_videos.append(video)
                    print("Failed to process %s" % video)

            total_processed_video_size += input_video_size

            percent_progress = total_processed_video_size / self.total_input_video_size * 100
            format_percent_progress = "{:.2f}%".format(percent_progress)

            compression_percent=0
            if output_video_size>0:
                compression_percent=output_video_size*100/input_video_size

            print("Input: %s Output: %s (%0.2f%%) Progress: %s"%(self.getHumanReadableFileSize(input_video_size),
                                                                       self.getHumanReadableFileSize(output_video_size),
                                                                       compression_percent,
                                                                       format_percent_progress))

        print()
        print("Processed videos can be found at %s" % self.output_path)
        print()

    def validate_output_path(self, video_dirname):
        # Replace input path with output path.
        new_output_path = str(video_dirname).replace(self.input_path, self.output_path)
        
        # Create output path if it doesn't exist
        if not os.path.exists(new_output_path):
            if self.verbose:
                print("Path: %s not found - creating"%new_output_path)
            os.makedirs(new_output_path)
        
        return new_output_path
    
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

    def make_transcode_command(self, input_file, output_file, timecode_streams):
        self.ffmpeg_commands = []

        self.ffmpeg_commands.append(self.ffmpeg_binary)
        
        # overwrite if exist
        self.ffmpeg_commands.append("-y")
        
        self.ffmpeg_commands.append("-i")
        self.ffmpeg_commands.append(input_file)
        
        self.ffmpeg_commands.append("-pix_fmt")

        #self.ffmpeg_commands.append("yuv422p10le")
        self.ffmpeg_commands.append("yuv420p10le")
        
        self.ffmpeg_commands.append("-c:v")
        self.ffmpeg_commands.append("libx265")

        self.ffmpeg_commands.append("-x265-params")
        self.ffmpeg_commands.append("profile=main10")

        self.ffmpeg_commands.append("-vf")
        self.ffmpeg_commands.append("scale=960:-1")

        for stream in timecode_streams:
            self.ffmpeg_commands.append("-map_metadata")
            self.ffmpeg_commands.append("0:s:%d"%stream)
        
        self.ffmpeg_commands.append("-crf")
        self.ffmpeg_commands.append("10")
        
        self.ffmpeg_commands.append(output_file)
        
main = Main()

main.commandLineHandler()

if main.getVideos() > 0:
    main.processVideos()