from pathlib import Path
import os
import sys
import subprocess
import getopt


from util import helper
from util import ff_util




class MyPath:

    video_extensions = [ ".mov", ".avi", ".mp4", ".wav" ]

    verbose=False

    tree_filename_prefix_middle = '├──'
    tree_filename_prefix_last = '└──'
    tree_parent_prefix_middle = '    '
    tree_parent_prefix_last = '│   '

    max_display_depth=99


    def __init__(self,path=None,parent=None,depth=0):

        if path is None:
            current_directory = os.getcwd()
            self.path=Path(current_directory)
        else:
            self.path=Path(str(path))

        self.depth=depth
        self.parent=parent
        self.children_files=[]
        self.children_directories=[]

        self.children_total_filesize=0
        self.children_total_video_duration=0
        self.children_total_filecount=0

        self.children_directorycount=0
        self.is_last=False

    def __lt__(self, other):
        return self.path < other.path
    
    # creates a printable string to represent this part of the tree
    # takes depth of parent hierarchy into consideration
    def make_display_tree(self,idx):

        if self.parent is None:
            return ""
        
        if self.is_last:
            filename_prefix=self.tree_filename_prefix_last
        else:
            filename_prefix=self.tree_filename_prefix_middle

        parts = [ filename_prefix]

        parent = self.parent
        while parent and parent.parent is not None:
            if not parent.is_last:
                parts.append(self.tree_parent_prefix_last)
            else:
                parts.append(self.tree_parent_prefix_middle)

            parent = parent.parent
    
        return ''.join(reversed(parts))

    def process_children(self):

        #print("process: %s"%self.path)

        for file in self.children_files:
            filesize=os.path.getsize(file)
            #print("- %s %d"%(self.path,filesize))

            video_duration = 0

            if file.suffix.lower() in self.video_extensions:
                ffprobe = ff_util.ffprobe_helper(self.verbose)
                video_duration = ffprobe.get_video_duration(file)
                self.children_total_filesize+=filesize
                self.children_total_filecount+=1

            if self.verbose:
                print("file: %s %s"%(file,helper.seconds_to_human_readable(video_duration)))
            
            self.children_total_video_duration+=video_duration

        for directory in self.children_directories:
            children_data=directory.process_children()
            self.children_total_filesize+=children_data[0]
            self.children_total_filecount+=children_data[1]
            self.children_total_video_duration+=children_data[2]

        #print(self.children_total_filesize)

        self.children_directories.sort()

        for idx,directory in enumerate(self.children_directories):
            if idx==self.children_directorycount-1:
                directory.is_last=True

        return self.children_total_filesize, self.children_total_filecount, self.children_total_video_duration


    def display(self,parent,max_display_depth=99,depth=0):

        #print(max_display_depth)
        # print("%d %s"%(depth,self.path))

        if depth>max_display_depth:
            return

        siblingcount=0

        if parent is not None:
            siblingcount=parent.children_directorycount
    
        printname = self.make_display_tree(0)
        basename = os.path.basename(self.path)

        

        if self.children_total_filecount>0:
            summary_text="[Size: %s Length: %s Count: %d]"% (
                helper.getHumanReadableFileSize(self.children_total_filesize),
                helper.seconds_to_human_readable(self.children_total_video_duration),
                self.children_total_filecount
            )
        else: 
            summary_text=""


        print("%s %s %s"% (
            printname,
            basename,
            summary_text,
            
            ))



        for child in self.children_directories:
            child.display(self,max_display_depth,depth+1)

    def crawl(self):

        #print("%s / (%d)"%(self.path,self.depth))

        for path in self.path.iterdir():

            if path.is_dir():
            
                subpath = MyPath(path,parent=self,
                                 depth=self.depth+1)

                self.children_directories.append(subpath)
                self.children_directorycount+=1

                subpath.crawl()

            else:
                #print("crawl: %s (%d) "%(path,self.depth))
                #print()
                self.children_files.append(path)

    def help(self):

        print("Available commands:")
        print("-i / --input <path>")
        print("-o / --output <path>")
        print("-v / --verbose")


    def printIntro(self):
        print("========================================================")
        print("treesize - https://github.com/edzop/pymovieutils")
        print("========================================================")



    def commandLineHandler(self):


        self.printIntro()

        argv = sys.argv[1:]

        try:
            opts, args = getopt.getopt(argv, "i:o:vbdh", ["input=", "depth=", "verbose", "dryrun", "noprobe", "help"])

            for opt, arg in opts:
                if opt in ["-i", "--input"]:
                    # strip trailing slash if it exists
                    self.input_path = arg.rstrip(os.sep)

                if opt in ["--depth"]:
                    self.max_display_depth=int(arg)

                elif opt in ["-v", "--verbose"]:
                    self.verbose=True

                elif opt in ["-h", "--help"]:
                    self.help()

                elif opt in ["--noprobe"]:
                    self.useprobe = False

        except Exception as error:
            print("ERROR: Main - commandLineHandler - %s" % (error))
            print("Use -h or --help for available commands.")
            return False
        
        return True



p = MyPath()

if p.commandLineHandler():

    p.crawl()

    p.process_children()

    p.display(parent=None,max_display_depth=p.max_display_depth)
