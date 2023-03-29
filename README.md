# pymovieutils

Python tools for movie creation. 

## batch_transcode.py
A utility to batch transcode video files. 

| Option | Description |
| ----------- | ----------- |
| -i  --input | Search video files in the given path including sub-folders. |
| -o / --output | Destination path of processed video files. |  
| -d / --dryrun | Shows the list of videos that would be processed with ffmpeg and simulate the processing of videos |

## examples

Linux Example:

`python3 batch_transcode.py -i /home/user/videos -o /home/videos/encoded`

Windows Example:

`python batch_transcode.py -i D:/videos -o D:/videos/processed`
