from FileSelector import FileSelector
import os
import shutil

class FileManager:
    def __init__(self, file_selector=None):
        self.file_selector = file_selector or FileSelector()

    def copy_files(self, destination):
        """Copy selected files"""
        try:
            selected_files = self.file_selector.get_selected_files()
            for file in selected_files:
                if os.path.exists(file):
                    shutil.copy2(file, destination)
            print(f"{len(selected_files)} file(s) copied")
            self.file_selector.clear_selection()
        except Exception as e:
            print(f"Copy error: {e}")

    def move_files(self, destination):
        """Move selected files"""
        try:
            selected_files = self.file_selector.get_selected_files()
            for file in selected_files:
                if os.path.exists(file):
                    shutil.move(file, destination)
            print(f"{len(selected_files)} file(s) moved")
            self.file_selector.clear_selection()
        except Exception as e:
            print(f"Move error: {e}")

    def delete_files(self):
        """Delete selected files"""
        try:
            selected_files = self.file_selector.get_selected_files()
            for file in selected_files:
                if os.path.isfile(file):
                    os.remove(file)
                elif os.path.isdir(file):
                    shutil.rmtree(file)
            print(f"{len(selected_files)} file(s)/folder(s) deleted")
            self.file_selector.clear_selection()
        except Exception as e:
            print(f"Delete error: {e}")
