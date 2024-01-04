import os
import sys
import getopt
import subprocess

from util import ff_util
from util import helper


class Main:

    def __init__(self) -> None:

        self.printIntro()

        self.input_path = None
        self.output_path = None

        self.verbose=False

        self.dry_run = False

        self.video_extensions = (".mp4", ".MP4", ".mov", ".MOV")

        self.useprobe=True

        self.addbasepath=False

        self.videos = []

        self.total_input_video_size = 0
        self.total_output_video_size = 0

        self.failed_videos = []


    def commandLineHandler(self):

        argv = sys.argv[1:]

        try:
            opts, args = getopt.getopt(argv, "i:o:vbdh", ["input=", "output=", "verbose", "dryrun", "noprobe", "help"])

            if len(opts) == 0:
                self.help()

            for opt, arg in opts:
                if opt in ["-i", "--input"]:
                    # strip trailing slash if it exists
                    self.input_path = arg.rstrip(os.sep)

                elif opt in ["-v", "--verbose"]:
                    self.verbose=True
                    print("Verbose mode")

                elif opt in ["-b"]:
                    self.addbasepath=True

                elif opt in ["-o", "--output"]:
                    # strip trailing shash if it exists
                    self.output_path = arg.rstrip(os.sep)

                elif opt in ["-d", "--dryrun"]:
                    self.dry_run = True

                elif opt in ["--noprobe"]:
                    self.useprobe = False

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
        print("-b / --add base path")
        print("-h / --help")
        print("-v / --verbose")
        print("--noprobe\t\t Disable ffprobe metadata stream checking")

    # Return number of videos found
    def getVideos(self):

        if self.input_path == "":
            # use current directory if no input path specified
            self.input_path = os.getcwd().rstrip(os.sep)

        self.total_input_video_size = 0

        for root, dirs, files in os.walk(self.input_path):
            for file in files:
                if file.endswith(self.video_extensions):
                    video_directory = os.path.join(root, file)
                    self.videos.append(video_directory)
                    self.total_input_video_size += os.stat(video_directory).st_size

        print("Total videos to process: %s" % len(self.videos))
        print("Total video file size: %s" %helper.getHumanReadableFileSize(self.total_input_video_size))
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
    

    def processVideos(self):

        total_processed_video_size = 0

        input_base_path=os.path.basename(self.input_path)

        for index, video in enumerate(self.videos, start=1):

            video_input_path=os.path.dirname(video)

            subpath=str(video_input_path).replace(self.input_path,"")
            
            output_path=self.output_path + subpath

            if self.addbasepath:
                output_path=self.output_path + os.sep + input_base_path + subpath
            else:
                output_path=self.output_path + os.sep + subpath


            self.validate_output_path(output_path)

            output_file = output_path + os.sep + os.path.basename(video)

            if self.verbose:
                print()
                print("input_path: %s"%self.input_path)
                print("video_input_path: %s"%video_input_path)
                print("input_base_path: %s"%input_base_path)
                print("output_path: %s"%output_path)
                print("Output file: %s subpath: %s"%(output_file,subpath))
                print()

            input_streams=[]

            ffhelper = ff_util.ffprobe_helper(self.verbose)

            if self.useprobe:
                
                input_streams = ffhelper.get_timecodestream(video)

            output_video_size=0
            input_video_size = os.stat(video).st_size

            print()

            print("Processing %s of %s: %s (%s)" % 
                (index, 
                len(self.videos),
                video,
                helper.getHumanReadableFileSize(input_video_size)))
                

            if self.dry_run == False:
                if ffhelper.ffmpeg_encode(video, output_file, input_streams):
                    output_video_size = os.stat(output_file).st_size
                    self.total_output_video_size += output_video_size  
                else:
                    self.failed_videos.append(video)      

                
            total_processed_video_size += input_video_size

            percent_progress = total_processed_video_size / self.total_input_video_size * 100
            format_percent_progress = "{:.2f}%".format(percent_progress)

            compression_percent=0
            if output_video_size>0:
                compression_percent=output_video_size*100/input_video_size

            print("Output: %s"%output_file,end=' ')
            print("(%s - %0.2f%%) Progress: %s"%(
                   
                                                                        helper.getHumanReadableFileSize(output_video_size),
                                                                        compression_percent,
                                                                        format_percent_progress))
        print()

        total_compression_ratio=0

        if self.total_output_video_size>0:
            total_compression_ratio = self.total_output_video_size * 100 / self.total_input_video_size

        print("Total Input %s -> Total Output %s (%0.2f%%) failed: %d"%(
            helper.getHumanReadableFileSize(self.total_input_video_size),
            helper.getHumanReadableFileSize(self.total_output_video_size),
            total_compression_ratio,
            len(self.failed_videos)))

    def validate_output_path(self, video_dirname):
        # Replace input path with output path.
        new_output_path = str(video_dirname).replace(self.input_path, self.output_path)
        
        # Create output path if it doesn't exist
        if not os.path.exists(new_output_path):
            if self.verbose:
                print("Path: %s not found - creating"%new_output_path)
            os.makedirs(new_output_path)
        
        return new_output_path
    

main = Main()

main.commandLineHandler()

if main.input_path is None or main.output_path is None:
    exit()

if main.getVideos() > 0:
    main.processVideos()