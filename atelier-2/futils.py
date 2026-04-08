import os
from typing import Callable, Protocol
from ui import UserInterface

class FileListProvider(Protocol):
    def subset(self, indices: list[int]) -> list[str]:
        pass


class FileSelection(Protocol):
    def get_and_reset(self) -> list[str]:
        pass


class FileSystem(Protocol):
    def copy(self, src: str, dest: str) -> None:
        pass

    def move(self, src: str, dest: str) -> None:
        pass

    def delete(self, path: str) -> None:
        pass


class FileSelector(FileSelection):
    def __init__(self):
        self.selected_files = []
    
    def select_files_by_indices(self, indices: list[int], file_explorer: FileListProvider) -> list[str]:
        """Select files based on indices"""
        try:
            selected_indices = [int(i.strip()) for i in indices.split(',')]
            
            self.selected_files = file_explorer.subset(selected_indices)
            
            print("Selected files:")
            for file in self.selected_files:
                print(f" - {os.path.basename(file)}")
            
            return self.selected_files
        except ValueError:
            print("Invalid input. Please enter valid indices.")
            return []
        except Exception as e:
            print(f"Error selecting files: {e}")
            return []
 
    def get_and_reset(self) -> list[str]:
        """Return the list of currently selected files"""
        res = self.selected_files.copy()
        self.selected_files.clear()
        return res


class FileExplorer(FileListProvider):
    def __init__(self):
        self._set_current_path(os.path.expanduser('~'))

    def _set_current_path(self, path: str) -> None:
        """Set current path and update the contents of the current directory"""
        self.current_path = path
        self.current_directory_contents = os.listdir(self.current_path)

    def display_directory_contents(self) -> None:
        """Display contents of the current directory"""
        try:
            print(f"\nCurrent Directory: {self.current_path}")
            print("-" * 50)
            for index, element in enumerate(self.current_directory_contents):
                full_path = os.path.join(self.current_path, element)
                element_type = "📁 Folder" if os.path.isdir(full_path) else "📄 File"
                print(f"{index}. {element_type}: {element}")
        except PermissionError:
            print("Access denied to this directory.")
        except Exception as e:
            print(f"Error: {e}")

    def navigate(self, index: int) -> None:
        """Navigate to a subdirectory"""
        try:
            selected_element = self.current_directory_contents[index]
            full_path = os.path.join(self.current_path, selected_element)
            
            if os.path.isdir(full_path):
                self._set_current_path(full_path)
                self.display_directory_contents()
            else:
                print(f"Cannot open file {selected_element}")
        except Exception as e:
            print(f"Navigation error: {e}")

    def go_to_parent_directory(self) -> None:
        """Move to the parent directory"""
        self._set_current_path(os.path.dirname(self.current_path))
        self.display_directory_contents()

    def subset(self, indices: list[int]) -> list[str]:
        """Return a subset of the current directory contents"""
        selected_files = []
        for index in indices:
            if 0 <= index < len(self.current_directory_contents):
                full_path = os.path.join(self.current_path, self.current_directory_contents[index])
                selected_files.append(full_path)
        return selected_files


class FileManager:
    def __init__(self, sel: FileSelection, fs: FileSystem, ui: UserInterface):
        self.sel = sel
        self.fs = fs
        self.ui = ui
        
    def _process_files(self, title: str, action: Callable[[str, str], None], destination: str=None) -> int:
        """Process files based on the action"""
        try:
            selected_files = self.sel.get_and_reset()
            for file in selected_files:
                action(file, destination)
            return len(selected_files)
        except Exception as e:
            self.ui.error(f"{title}: {e}")
            return 0
        
    def copy_files(self, destination) -> int:
        """Copy selected files"""
        return self._process_files("Copy", self.fs.copy, destination)

    def move_files(self, destination) -> int:
        """Move selected files"""
        return self._process_files("Move", self.fs.move, destination)

    def delete_files(self) -> int:
        """Delete selected files"""
        return self._process_files("Delete", action=lambda path, _ : self.fs.delete(path))
