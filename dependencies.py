from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from typing import Protocol


class Output(Protocol):
    def write(self, message: str) -> None:
        ...


class FileSelectorPort(Protocol):
    def get_selected_files(self) -> list[str]:
        ...

    def clear_selection(self) -> None:
        ...


class FileInspection(Protocol):
    def exists(self, path: str) -> bool:
        ...

    def is_file(self, path: str) -> bool:
        ...

    def is_dir(self, path: str) -> bool:
        ...


class FileOperations(Protocol):
    def copy(self, source: str, destination: str) -> None:
        ...

    def move(self, source: str, destination: str) -> None:
        ...

    def remove_file(self, path: str) -> None:
        ...

    def remove_dir(self, path: str) -> None:
        ...


@dataclass(frozen=True)
class ConsoleOutput:
    def write(self, message: str) -> None:
        print(message)


@dataclass(frozen=True)
class OsFileInspection:
    def exists(self, path: str) -> bool:
        return os.path.exists(path)

    def is_file(self, path: str) -> bool:
        return os.path.isfile(path)

    def is_dir(self, path: str) -> bool:
        return os.path.isdir(path)


@dataclass(frozen=True)
class SystemFileOperations:
    def copy(self, source: str, destination: str) -> None:
        shutil.copy2(source, destination)

    def move(self, source: str, destination: str) -> None:
        shutil.move(source, destination)

    def remove_file(self, path: str) -> None:
        os.remove(path)

    def remove_dir(self, path: str) -> None:
        shutil.rmtree(path)
