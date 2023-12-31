# pymovieutils

Python tools for movie creation. 

## treesize.py
A python utility file to display a directory tree and combined file sizes for contents in a hierarchal fashion.

I tried really hard to find a way to determine the total file size recursively using the `tree` command and limit directory depth but if you limit the directory depth with the `tree` command it does not include the undisplayed directories in the total file sizes. 

~~I would like to add additional metrics to include length (in minutes) of video files included to determine and summarize how complex a video project is.~~

Metrics have been added to recursively display video length and video file count.

### example
`python3 treesize.py`

would yield:
```bash
 video_cloned_tree_test [Size: 143.7 MiB Length: 0:02:53 Count: 12]
├── A1 [Size: 23.0 MiB Length: 0:00:27 Count: 2]
│   └── A2 [Size: 11.5 MiB Length: 0:00:13 Count: 1]
├── A2 [Size: 46.0 MiB Length: 0:00:55 Count: 4]
│   └── A2 [Size: 23.0 MiB Length: 0:00:27 Count: 2]
└── B [Size: 38.2 MiB Length: 0:00:44 Count: 3]
    └── Br [Size: 11.5 MiB Length: 0:00:13 Count: 1]
```

The `depth=` command line parameter can be added to command line to determine depth of tree displayed. Note this is only for display output - maximum directory depth is evaluated for calculating total file sizes.

`python3 treesize.py --depth=1`
```bash
 Test [312.9 MiB]
├── L1 [234.7 MiB]
├── L2 [26.1 MiB]
├── L3 [26.1 MiB]
├── L4 [0.0 B]
└── L5 [0.0 B]
```

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


### Timecode

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
