import os

from FileSelector import FileSelector


class FileExplorer:
	def __init__(self, start_path=None, file_selector=None):
		self.current_path = start_path or os.path.expanduser('~')
		self.file_selector = file_selector or FileSelector()

	def display_directory_contents(self):
		"""Display contents of the current directory"""
		try:
			contents = self.file_selector.load_directory_contents(self.current_path)
			print(f"\nCurrent Directory: {self.current_path}")
			print("-" * 50)
			for index, element in enumerate(contents):
				full_path = os.path.join(self.current_path, element)
				element_type = "📁 Folder" if os.path.isdir(full_path) else "📄 File"
				print(f"{index}. {element_type}: {element}")
		except PermissionError:
			print("Access denied to this directory.")
		except Exception as e:
			print(f"Error: {e}")

	def navigate(self, index):
		"""Navigate to a subdirectory"""
		try:
			contents = self.file_selector.load_directory_contents(self.current_path)
			selected_element = contents[index]
			full_path = os.path.join(self.current_path, selected_element)

			if os.path.isdir(full_path):
				self.current_path = full_path
				self.display_directory_contents()
			else:
				print(f"Cannot open file {selected_element}")
		except Exception as e:
			print(f"Navigation error: {e}")

	def go_to_parent_directory(self):
		"""Move to the parent directory"""
		self.current_path = os.path.dirname(self.current_path)
		self.display_directory_contents()

