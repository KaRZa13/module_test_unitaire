import unittest

from FileManager import FileManager


class FakeSelector:
    def __init__(self, selected_files):
        self._selected_files = list(selected_files)
        self.cleared = False

    def get_selected_files(self):
        return list(self._selected_files)

    def clear_selection(self):
        self.cleared = True


class FakeInspector:
    def __init__(self, *, exists=None, files=None, dirs=None):
        self._exists = set(exists or [])
        self._files = set(files or [])
        self._dirs = set(dirs or [])

    def exists(self, path: str) -> bool:
        return path in self._exists

    def is_file(self, path: str) -> bool:
        return path in self._files

    def is_dir(self, path: str) -> bool:
        return path in self._dirs


class FakeOps:
    def __init__(self, *, raise_on=None):
        self.calls = []
        self._raise_on = raise_on

    def copy(self, source: str, destination: str) -> None:
        if self._raise_on == ("copy", source):
            raise RuntimeError("boom")
        self.calls.append(("copy", source, destination))

    def move(self, source: str, destination: str) -> None:
        self.calls.append(("move", source, destination))

    def remove_file(self, path: str) -> None:
        self.calls.append(("remove_file", path))

    def remove_dir(self, path: str) -> None:
        self.calls.append(("remove_dir", path))


class FakeOutput:
    def __init__(self):
        self.messages = []

    def write(self, message: str) -> None:
        self.messages.append(message)


class FileManagerTests(unittest.TestCase):
    def test_copy_files_uses_ops_and_clears_selection(self):
        selector = FakeSelector(["/a", "/b", "/missing"])
        inspector = FakeInspector(exists={"/a", "/b"})
        ops = FakeOps()
        out = FakeOutput()

        manager = FileManager(file_selector=selector, inspector=inspector, ops=ops, output=out)
        manager.copy_files("/dest")

        self.assertEqual(ops.calls, [("copy", "/a", "/dest"), ("copy", "/b", "/dest")])
        self.assertTrue(selector.cleared)
        self.assertIn("3 file(s) copied", out.messages[-1])

    def test_move_files_uses_ops_and_clears_selection(self):
        selector = FakeSelector(["/a"])
        inspector = FakeInspector(exists={"/a"})
        ops = FakeOps()
        out = FakeOutput()

        manager = FileManager(file_selector=selector, inspector=inspector, ops=ops, output=out)
        manager.move_files("/dest")

        self.assertEqual(ops.calls, [("move", "/a", "/dest")])
        self.assertTrue(selector.cleared)
        self.assertIn("1 file(s) moved", out.messages[-1])

    def test_delete_files_calls_remove_file_or_remove_dir(self):
        selector = FakeSelector(["/f", "/d", "/unknown"])
        inspector = FakeInspector(files={"/f"}, dirs={"/d"})
        ops = FakeOps()
        out = FakeOutput()

        manager = FileManager(file_selector=selector, inspector=inspector, ops=ops, output=out)
        manager.delete_files()

        self.assertEqual(ops.calls, [("remove_file", "/f"), ("remove_dir", "/d")])
        self.assertTrue(selector.cleared)
        self.assertIn("3 file(s)/folder(s) deleted", out.messages[-1])

    def test_copy_files_on_exception_writes_error_and_does_not_clear(self):
        selector = FakeSelector(["/a"])
        inspector = FakeInspector(exists={"/a"})
        ops = FakeOps(raise_on=("copy", "/a"))
        out = FakeOutput()

        manager = FileManager(file_selector=selector, inspector=inspector, ops=ops, output=out)
        manager.copy_files("/dest")

        self.assertFalse(selector.cleared)
        self.assertTrue(any(msg.startswith("Copy error:") for msg in out.messages))


if __name__ == "__main__":
    unittest.main()
