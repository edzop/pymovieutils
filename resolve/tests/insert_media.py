# to launch:
# python3 tests/list_media.py

import sys, getopt

import resolve_helper

media_to_import=[]

exr_to_import=[]

clips_imported=[]

rh = resolve_helper.resolve_helper()


def main(argv):
	opts, args = getopt.getopt(argv,"i:e:")
	for opt, arg in opts:
		if opt==("-i"):
			media_to_import.append(arg)
		if opt==("-e"):
			exr_to_import.append(arg)

	for filename in media_to_import:
		clip=rh.importMedia(filename)
		clips_imported.append(clip)

	for filename in exr_to_import:
		clip=rh.importExrSequence(filename,0,10)
		clips_imported.append(clip)

	for clip in clips_imported:
		if clip is not None:
			rh.printClipProperties(clip)

	#rh.list_media_in_pool(rh.activeproject)


if __name__ == "__main__":
   main(sys.argv[1:])
