
import DaVinciResolveScript  as dvr


class resolve_helper:

    resolve=None
    fusion=None
    activeproject=None

    mediaPool=None

    def timecode_to_frames(self,timecode,framerate=24):
        return sum(f * int(t) for f,t in zip((3600*framerate, 60*framerate, framerate, 1), timecode.split(':')))


    def __init__(self):

        self.resolve = dvr.scriptapp("Resolve")

        if not self.resolve:
            print("Please launch DaVinci Resolve first.")
            sys.exit()

        
        self.fusion = dvr.scriptapp('Fusion')

        self.projectmanager = self.resolve.GetProjectManager()

        if self.projectmanager is None:
            print("Project Manager not found...")
            sys.exit()

        self.activeproject = self.projectmanager.GetCurrentProject()

        if self.activeproject is None:
            print("No Current project")
        else:
            print("Using Project: %s"%self.activeproject.GetName())

            self.mediaPool = self.activeproject.GetMediaPool()

        #self.timeline = self.projectmanager.GetCurrentTimeline()


    def getTimeline(self):
        timeline=self.activeproject.GetCurrentTimeline()

        if not timeline:
	        self.mediaPool.CreateEmptyTimeline("Timeline1")        
        return timeline

    def print_folder_media(self,folder):

        print("Folder: %s"%folder.GetName())

        clips = folder.GetClipList()

        for clip in clips:
            file_name=clip.GetClipProperty('File Name')
            clip_type=clip.GetClipProperty('Type')
            resolution=clip.GetClipProperty('Resolution')
            print("%10s:\t%10s\t%s"%(clip_type,resolution,file_name))

        for subfolder in folder.GetSubFolderList():

            self.print_folder_media(subfolder)

    def list_media_in_pool(self,project):

        #self.mediaPool = self.activeproject.GetMediaPool()
        rootFolder = self.mediaPool.GetRootFolder()
        
        self.print_folder_media(rootFolder)

    def printClipProperties(self,clip):

        file_path = clip.GetClipProperty('File Path')
        print("File Path: %s"%file_path)

        duration=clip.GetClipProperty('Duration')  # Full Path
        print("Frames: %d"%self.timecode_to_frames(duration))

        color_space = clip.GetClipProperty("Input Color Space")
        print("Color space: %s"%color_space)

    def setClipProperties(self,clip):
        clip.SetClipProperty("Input Color Space","ACES")


    def importExrSequence(self,filepath,startFrame,endFrame):
        
        # example file path: "path/bpy_beats_1.[0000-1334].cycles.exr"

        #firstDot = filepath.find(".")

        #if firstDot!=-1:
        #    secondDot = filepath.find(".",firstDot+1)

        #print("First: %d Second: %d"%(firstDot,secondDot))    

        # TODO work in progress
        #mediaPath="path/bpy_beats_1.[0000-1334].cycles.exr"

        qualified_path = filepath + "%04d.cycles.exr"

        print("Qualified path: %s"%qualified_path)

        #clips=[]
        clips = self.mediaPool.ImportMedia([{"FilePath": qualified_path, "StartIndex":startFrame, "EndIndex":endFrame}])

        if len(clips)==0:
            return None

        return clips[0]


    def importMedia(self,filename):

        clips = self.mediaPool.ImportMedia([ filename ])

        # Alternate ways to add media:

        #clip = mediaPool.ImportMedia([{"FilePath": filename }])
        #clips = resolve.GetMediaStorage().AddItemListToMediaPool( [ filename ])
        
        return clips[0]




