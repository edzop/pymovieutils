# pymovieutils

Python tools for movie creation. 

## batch_transcode.py
A utility to batch transcode video files. 

| Option | Description |
| ----------- | ----------- |
| -i  --input | Search video files in the given path including sub-folders. |
| -o --output | Destination path of processed video files. |  
| -d --dryrun | Shows the list of videos that would be processed with ffmpeg and simulate the processing of videos |
| -v --verbose | Verbose output (more debugging info) |

## examples

Linux Example:

`python3 batch_transcode.py -i /home/user/videos -o /home/videos/encoded`

Windows Example:

`python batch_transcode.py -i D:/videos -o D:/videos/processed`

## Timecode

Not all cameras have the same metadata streams and we need to instruct ffmpeg which streams to copy. 

#### Gopro 
| Stream | Description | 
| ----------- | ----------- |
| 2      | GoPro TCD | 
| 3      | GoPro MET | 

#### Sony FX3 / Sony A7iv 
| Stream | Description | 
| ----------- | ----------- |
| 2      | Timed Metadata Media Handler | 

#### DJI drone
DJI drone didn't contain any data streams! 

batch_transcode will use `ffprobe -select_streams d` command to probe data streams from the source video file. This is passed to ffmpeg via the `-map_metadata` option to specify which streams to copy to ensure we maintain our timecode information. I could not find a blanket command to map all metadata streams so I thought using `ffprobe` first to query is the most portable way to ensure compatibility with the types of cameras we regularly use. 
