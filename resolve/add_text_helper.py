import resolve_helper
import time

def add_basic_text(timeline,text):

    title=timeline.InsertTitleIntoTimeline("Text")

    #title=timeline.InsertTitleIntoTimeline("Scroll")

    # How to change position / attributes of title?

class textObj:
    Red1=255
    Green1=255
    Blue1=255
    VerticalTopCenterBottom=0
    HorizontalLeftCenterRight=0
    Size=0.09
    #Enabled=1
    Center=[0.5,0.5]

    Text="Test" # StyledText

    def __init__(self):
        Text="test"
 
#    def __init__(self):
#        Text="Test2"

    tool=None
    composition=None
    media_out=None
    merge=None

    # line.StyledText = textwrap.fill(sub.content, width = LINE_WRAP_CHARS)

    def setBorder(thickness=0.05,red=1,green=1,blue=1):
        self.tool.Enabled2=1
        self.tool.Thickness2=thickness
        self.tool.Red2=red
        self.tool.Green2=green
        self.tool.Blue2=blue

    def align_top_left(self):
        self.tool.HorizontalLeftCenterRight=-1
        self.tool.Center=[0,1]
        self.tool.VerticalTopCenterBottom=-1

    def align_top_right(self):
        time.sleep(0.1)
        self.tool.Center=[1,1]
        self.tool.HorizontalLeftCenterRight=1
        self.tool.VerticalTopCenterBottom=-1
        time.sleep(0.1)

    def align_bottom_right(self):
        self.tool.VerticalTopCenterBottom=1 
        self.tool.Center=[1,0]
        self.tool.HorizontalLeftCenterRight=1

    def align_bottom_left(self):
        self.tool.Center=[0,0]
        self.tool.HorizontalLeftCenterRight=-1
        self.tool.VerticalTopCenterBottom=1

    def align_center(self):
        self.tool.HorizontalLeftCenterRight=0
        self.tool.VerticalTopCenterBottom=0
        self.tool.Center=[0.5,0.5]

    def assign_attributes(self):
        self.tool.Red1=self.Red1
        self.tool.Green1=self.Green1
        self.tool.Blue1=self.Blue1

        self.tool.Size=self.Size

        self.tool.Center=self.Center

    def SetText(self,text):
        self.tool.StyledText=text


    def appendText(self):
        newTextObject = textObj()

        newTextObject.composition=self.composition
        newTextObject.media_out=self.media_out

        newTextObject.tool=self.composition.AddTool("TextPlus")

        time.sleep(0.01)
        #newTextObject.tool=self.composition.AddTool("TextPlus",1,1)
        
        time.sleep(0.01)
        if self.merge is not None:
            newTextObject.merge = self.composition.Merge({"Background": self.merge, "Foreground": newTextObject.tool})
        else:
            newTextObject.merge = self.composition.Merge({"Background": self.tool, "Foreground": newTextObject.tool})
        
        newTextObject.media_out.ConnectInput("Input",newTextObject.merge)

        #newTextObject.media_out=merge

        #merge = self.composition.Merge({"Foreground": self.media_out, "Background": newTextObject.tool})


        return newTextObject

    @classmethod
    def new_timeline_text(cls,timeline):

        newObj=cls()

        newtext = timeline.InsertFusionTitleIntoTimeline("Text+")

        newObj.composition=newtext.GetFusionCompByIndex(1)
        
        toolList = newObj.composition.GetToolList()

        newObj.tool = toolList[1]
        newObj.media_out=toolList[2]
        

        #return tool

        # Enabled 2 = Border

        # Enabled 3 = Shadow

        # Enabled 4 = Background

        # Enabled 5 = Border2
        #tool.Thickness5=0.1

        #toolList.Enabled=textObj.Enabled

        return newObj

