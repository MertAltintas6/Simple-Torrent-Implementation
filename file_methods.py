import os, os.path
import hashlib
import datetime
from difflib import SequenceMatcher
import tempfile


#get md5sum of the requested file
def get_md5(path_file):
    path_file = "." + path_file.strip(".")
    with open(path_file, 'rb') as fh:
        m = hashlib.md5()
        while True:
            data = fh.read(8192)
            if not data:
                break
            m.update(data)
        return m.hexdigest()

#get file size of the requested file
def get_attiributes(filename):
    path_filename = "."+filename.strip(".")
    md5 = get_md5(path_filename)
    statinfo = os.stat(path_filename)
    size = statinfo.st_size

    ctime=statinfo.st_ctime
    c_readable = datetime.datetime.fromtimestamp(ctime).isoformat()
    #print("FileName:"+filename+" md5:"+md5+" FileSize:%d"%size+" ctime:"+c_readable+"\n")

    return md5,size

#similarity between files
def similar(a,b):
    a = a.lower()
    b = b.lower()
    str1 = str(a).split('.')
    str2 = str(b).split('.')
    sim1 = SequenceMatcher(None, str1[0], str2[0]).ratio()
    sim2 = SequenceMatcher(None, str1[1], str2[1]).ratio()
    sim3 = SequenceMatcher(None, a, b).ratio()
    return (sim1, sim2, sim3)

#get same and similar files by filename
def search_filename(filename, path_dir):
    if os.path.isdir(path_dir):
        dirs = os.listdir(path_dir)
        K=0
        T=0
        SimFiles = []
        SnameFiles = []
        SameFiles = []
        Same = []
        Sim = []
        Sname = []

        filename=filename.strip(" ")
        for file in dirs:
            #print("Filename: " + filename)
            if filename.count(".")==0:
                filename=filename+'.'
                #print("File: " + file)
            if file.count(".")==0:
                file=file+'.'
            path_filename = path_dir + filename
            #print("Path:" + path_filename)
            sim=similar(filename,file)
            path_file=path_dir+file
            #print("Path file: "+path_file)
            if os.path.exists(path_filename):
                if sim[2]==1 or (get_md5(path_filename)==get_md5(path_file)):
                    SameFiles.append(file)
                    K+=1

            if sim[0] >= 0.6:
                if os.path.exists(path_filename):
                    if get_md5(path_filename)!=get_md5(path_file):
                        SimFiles.append(file)
                        T+=1
                elif sim[0]==1:
                    SnameFiles.append(file)
                    T+=1
                else:
                    SimFiles.append(file)
                    T+=1

        if K>0:
            #print("\nThe most relevant results:")
            SameFiles_size=len(SameFiles)
            i=0
            while(i<SameFiles_size):
                if(SameFiles[i]==filename):
                    buf = path_dir + SameFiles[i]
                    get_attiributes(buf)
                    Same.append(buf)
                i+=1

            i=0
            while(i<SameFiles_size):
                if SameFiles[i]!=filename:
                    buf = path_dir + SameFiles[i]
                    get_attiributes(buf)
                    Same.append(buf)
                i+=1


        if T>0:
            #print("Similar results:")
            files_size=len(SimFiles)
            SnameFiles_size=len(SnameFiles)
            i=0
            while (i < SnameFiles_size):
                buf = path_dir + SnameFiles[i]
                get_attiributes(buf)
                Sname.append(buf)
                i+=1
            i=0
            while (i < files_size):
                buf = path_dir + SimFiles[i]
                get_attiributes(buf)
                Sim.append(buf)
                i+=1

        if K==0 and T==0:
            ##print("Error: file not found!")
            if filename.endswith('.'):
                print("Error: %s file not found!" %filename[:-1])
            else:
                print("Error: %s file not found!" %filename)



        return (Same, Sname, Sim)

    else:
        print("Error: %s path not found!" % path_dir)
        return False



#get same and similar files by md5
def search_md5(md5, path_dir):
    if os.path.isdir(path_dir):
        dirs = os.listdir(path_dir)
        L=0
        #SimFiles = []
        #SnameFiles = []
        SameFiles = []
        Same = []
        #Sim = []
        #Sname = []

        md5 = md5.strip(" ")
        for file in dirs:
            path_file = path_dir + file

            if get_md5(path_file)[:10] == md5[:10]:
                print(file)
                SameFiles.append(file)
                L += 1
        if L > 0:
            #print("\nThe most relevant results:")
            SameFiles_size = len(SameFiles)
            i = 0
            while (i < SameFiles_size):
                buf = path_dir + SameFiles[i]
                Same.append(buf)
                i += 1

        else:
            print("Error: %s md5 not found!" % md5)
            return False
        return Same

    else:
        print("Error: %s path not found!" % path_dir)
        return False



#creates meta and empty file of the requested file
def createMeta(Filename, checksum, File_size, chunkSize):
    # calculate the number of chunks to be created
    noOfChunks = File_size / chunkSize

    if (File_size % chunkSize):
        noOfChunks += 1

    # create a info.txt file for writing metadata
    line = []
    #line.append(Filename + ',' + 'chunk,' + str(int(noOfChunks)) + ',' + str(chunkSize) + '\n')

    for i in range(0, int(noOfChunks)):
        if i == (int(noOfChunks) - 1):
            buf = str(i) + " " + str(File_size - i * chunkSize) + "\n"
        else:
            buf = str(i) + " " + str(chunkSize) + "\n"
        line.append(buf)

    # open meta file
    meta_name = str(checksum[:10]).strip()+".txt"
    f = open(meta_name, 'w')
    for s in line:
        f.write(s)
    f.close()
    # open tmp file
    f = open(Filename, "wb")
    f.seek(File_size - 1)
    f.write(b'\0')
    f.close()

    return int(noOfChunks), meta_name

#get bytes of the requested chunk
def getChunkData(inputFile, chunkSize, requestedChunk):
    # read the contents of the file
    try:
        f = open(inputFile, 'rb')
        data = f.read()  # read the entire content of the file
        f.close()
        start_point = requestedChunk * chunkSize
        end_point = start_point + chunkSize
        requestedData = list(data[start_point:end_point])

        return requestedData
    except:
        return False
# define the function to join the chunks of files into a single file
def joinFiles(original_file, temporary_files, checksum):

    f = open(original_file, 'wb')

    for tmp in range(0, len(temporary_files)):
        tf = open(temporary_files[tmp], "rb")
        data = tf.read()
        f.write(data)
        tf.close()
        os.remove(temporary_files[tmp])
    f.close()
    meta_name = str(checksum[:10]).strip() + ".txt"
    os.remove(meta_name)