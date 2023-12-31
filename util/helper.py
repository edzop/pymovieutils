
import datetime

def seconds_to_human_readable(seconds):
    seconds_int = int(seconds)
    m, s = divmod(seconds_int, 60)
    h, m = divmod(m, 60)

    #return ('{:d}:{:02d}:{:02d}'.format(h, m, s))

    return (f'{h:d}:{m:02d}:{s:02d}')

#def sizeof_fmt(num, suffix="B"):
#   return "%0.2f MB" % (size / (1024 * 1024) )

def getHumanReadableFileSize(num,suffix="B"):
    
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"