import resolve_helper
import add_text_helper

rh = resolve_helper.resolve_helper()

timeline = rh.getTimeline()

textObj=add_text_helper.textObj.new_timeline_text(timeline)
textObj.SetText("BottomLeft")
textObj.align_bottom_left()

textObj=textObj.appendText()
textObj.SetText("BottomRight")
textObj.align_bottom_right()

textObj=textObj.appendText()
textObj.SetText("TopLeft")
textObj.align_top_left()

textObj=textObj.appendText()
textObj.SetText("Center")
textObj.align_center()

textObj=textObj.appendText()
textObj.SetText("TopRight")
textObj.align_top_right()

#textObj2.setBorder()


