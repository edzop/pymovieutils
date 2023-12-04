# pymovieutils

Python tools for movie creation. 

## treesize.py
A python utility file to display a directory tree and combined file sizes for contents in a hierarchal fashion.

### example
`python3 treesize.py`

would yield:

`Test [312.9 MiB]`
`├── L1 [234.7 MiB`
`│   ├── L1_1 [182.6 MiB]`
│   │   ├── L1_1_1 [52.2 MiB]
│   │   └── L1_1_2 [104.3 MiB]
│   │       └── L1_1_2_1 [52.2 MiB]
│   ├── L1_2 [26.1 MiB]
│   └── L1_3 [0.0 B]
├── L2 [26.1 MiB]
├── L3 [26.1 MiB]
├── L4 [0.0 B]
└── L5 [0.0 B]


## batch_transcode.py
A utility to batch transcode video files. 

| Option | Description |
| ----------- | ----------- |
| -i  --input | Recursively Search video files in the given path. If input path is ommited - current path is used. |
| -o --output | Destination path of processed video files. |
| -b | add base path |
| -d --dryrun | Shows the list of videos that would be processed with ffmpeg and simulate the processing of videos |
| -v --verbose | Verbose output (more debugging info) |
| --noprobe | Disable ffprobe metadata stream checking |

### examples

Linux Example:

`python3 batch_transcode.py -i /home/user/videos -o /home/videos/encoded`

Windows Example:

`python batch_transcode.py -i D:/videos -o D:/videos/processed`


### base path option

Given parameters: `-b -i /input/test -o /output`

The result would be:

| input | output |
| ----------- | ----------- |
| `/input/test/1.mp4` | `/output/test/1.mp4` |
| `/input/test/sub1/2.mp4` | `/output/test/sub1/2.mp4` |
| `/input/test/sub2/3.mp4` | `/output/test/sub2/3.mp4` |

Note how `/test` is automatically added to the `/output` path because of the `-b` option. 

Without the `-b` option the parameters `-i /input/test -o /output` would yeild:

| input | output |
| ----------- | ----------- |
| `/input/test/1.mp4` | `/output/1.mp4` |
| `/input/test/sub1/2.mp4` | `/output/sub1/2.mp4` |
| `/input/test/sub2/3.mp4` | `/output/sub2/3.mp4` |


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
