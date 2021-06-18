# Muntherr anati 
import glob
import os
import os.path
import shutil  # module to support file moving and deletion


class Command:
    def __init__(self, file_name, Path):
        self.filename = file_name
        self.path = Path

    def grep(self):
        try:
            Found_path = glob.glob(self.path + "/*/" + self.filename,
                                   recursive=True)  # To search for specific files in subdirectories
            return True
        except FileNotFoundError as not_found:
            return False

    def mv_last(self):
        flag = True
        if os.path.exists(self.path) or os.path.isdir(self.path):
            files_path = os.path.join(self.filename, '*')
            files = sorted(glob.iglob(files_path), key=os.path.getctime, reverse=True)
            Last_recent_dir = files[0]  # last recent file in index 0
            shutil.move(Last_recent_dir,
                        self.path)  # Move the last recent folder from source directory to specific dir.
            print("The last recent file is moved from [" + self.path + "] to[" + Last_recent_dir + "]")
            flag = True
        else:
            flag = False

        return flag

    def Categorize(self, threshold_size):
        if len(os.listdir(self.path)) == 0:
            return False
        else:
            Files = list(os.listdir(self.path))  # Save all directories files in Files
            File = dict()  # Function to create the Dictionary
            for i in Files:  # Calculate size for all files here.
                file_stat = os.stat(self.path + '/' + str(i))  # get status of the specified path.
                File[i] = file_stat  # save all status of file to dictionary
                if os.path.exists(self.path + "\\more") == False:
                    os.mkdir(self.path + '\more')
                if os.path.exists(self.path + "\\less") == False:
                    os.mkdir(self.path + '\less')
            for j in File:  # Split files to two types
                if j == "more" or j == "less":
                    continue
                if File[j].st_size > threshold_size:
                    shutil.move(self.path + '\\' + j, self.path + '\more\\' + j)

                elif File[j].st_size < threshold_size:
                    shutil.move(self.path + '\\' + j, self.path + '\less\\' + j)
            return True
