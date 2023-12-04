from pathlib import Path
import os
import sys

def sizeof_fmt(num, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

class MyPath:

    tree_filename_prefix_middle = '├──'
    tree_filename_prefix_last = '└──'
    tree_parent_prefix_middle = '    '
    tree_parent_prefix_last = '│   '

    def __init__(self,path,parent=None,depth=0):
        self.path=Path(str(path))
        self.depth=depth
        self.parent=parent
        self.children_files=[]
        self.children_directories=[]
        self.children_filesize=0
        self.children_directorycount=0
        self.is_last=False

    def __lt__(self, other):
        return self.path < other.path
    
    def make_tree(self,idx):

        
        
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
            self.children_filesize+=filesize

        for directory in self.children_directories:
            self.children_filesize+=directory.process_children()

        #print(self.children_filesize)

        self.children_directories.sort()

        for idx,directory in enumerate(self.children_directories):
            if idx==self.children_directorycount-1:
                directory.is_last=True

        return self.children_filesize


    def display(self,parent,max_depth,depth=0):

        #print("%d %s"%(depth,self.path))

        if depth>max_depth:
            return

        siblingcount=0

        if parent is not None:
            siblingcount=parent.children_directorycount
    
        printname = self.make_tree(0)
        basename = os.path.basename(self.path)

        print("%s %s [%s]"% (
            printname,
            basename,
            sizeof_fmt(self.children_filesize),
            ))
        
     
        #print("[%s] %s (%d) %s (%d/%d) "%(  
        #            ,
        #           sizeof_fmt(self.children_filesize).ljust(10),
        #            printname,                     
                    
       #             self.depth,
       #             str(isLast),
       #             child_index,siblingcount
                    
       #             ))


        for child in self.children_directories:
            child.display(self,max_depth,depth+1)

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

current_directory = os.getcwd()

p = MyPath(current_directory)

p.crawl()

p.process_children()

max_depth=999
if len(sys.argv)>1:
    max_depth=int(sys.argv[1])

p.display(parent=None,max_depth=max_depth)