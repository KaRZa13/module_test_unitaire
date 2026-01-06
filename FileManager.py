from FileSelector import FileSelector

from dependencies import (
    ConsoleOutput,
    FileInspection,
    FileOperations,
    FileSelectorPort,
    OsFileInspection,
    Output,
    SystemFileOperations,
)

class FileManager:

    def __init__(
        self,
        file_selector: FileSelectorPort | None = None,
        inspector: FileInspection | None = None,
        ops: FileOperations | None = None,
        output: Output | None = None,
    ):
        self.file_selector = file_selector or FileSelector()
        self.inspector = inspector or OsFileInspection()
        self.ops = ops or SystemFileOperations()
        self.output = output or ConsoleOutput()

    def copy_files(self, destination):
        """Copy selected files"""
        try:
            selected_files = self.file_selector.get_selected_files()
            for file in selected_files:
                if self.inspector.exists(file):
                    self.ops.copy(file, destination)
            self.output.write(f"{len(selected_files)} file(s) copied")
            self.file_selector.clear_selection()
        except Exception as e:
            self.output.write(f"Copy error: {e}")

    def move_files(self, destination):
        """Move selected files"""
        try:
            selected_files = self.file_selector.get_selected_files()
            for file in selected_files:
                if self.inspector.exists(file):
                    self.ops.move(file, destination)
            self.output.write(f"{len(selected_files)} file(s) moved")
            self.file_selector.clear_selection()
        except Exception as e:
            self.output.write(f"Move error: {e}")

    def delete_files(self):
        """Delete selected files"""
        try:
            selected_files = self.file_selector.get_selected_files()
            for file in selected_files:
                if self.inspector.is_file(file):
                    self.ops.remove_file(file)
                elif self.inspector.is_dir(file):
                    self.ops.remove_dir(file)
            self.output.write(f"{len(selected_files)} file(s)/folder(s) deleted")
            self.file_selector.clear_selection()
        except Exception as e:
            self.output.write(f"Delete error: {e}")
