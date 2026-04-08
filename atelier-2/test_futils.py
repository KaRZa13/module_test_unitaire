import unittest
from unittest.mock import MagicMock, create_autospec, call

from futils import FileSelection, FileSystem, FileManager
from ui import UserInterface


class TestFManager(unittest.TestCase):
    """Tests unitaires de FileManager avec simulation des trois dépendances."""

    # ─── Fabrique ─────────────────────────────────────────────────────────────

    def new_file_manager(self,
                         selected_files=None,
                         fs_delete_side_effect=None,
                         fs_copy_side_effect=None,
                         fs_move_side_effect=None) -> FileManager:
        """Construit un FileManager dont les trois dépendances sont des mocks."""
        sel = create_autospec(FileSelection, spec_set=True)
        fs  = create_autospec(FileSystem,   spec_set=True)
        ui  = create_autospec(UserInterface, spec_set=True)

        fs.delete.side_effect = fs_delete_side_effect
        fs.copy.side_effect   = fs_copy_side_effect
        fs.move.side_effect   = fs_move_side_effect

        sel.get_and_reset.return_value = selected_files if selected_files is not None else []
        return FileManager(sel, fs, ui)

    # ─── delete_files ─────────────────────────────────────────────────────────

    def test_delete_empty_list(self):
        """Aucun fichier sélectionné → aucune suppression, retourne 0."""
        fm = self.new_file_manager(selected_files=[])

        self.assertEqual(0, fm.delete_files())
        fm.fs.delete.assert_not_called()

    def test_delete_single_file(self):
        """Un fichier sélectionné → supprimé, retourne 1."""
        fm = self.new_file_manager(selected_files=["file1"])

        self.assertEqual(1, fm.delete_files())
        fm.fs.delete.assert_called_once_with("file1")

    def test_delete_multiple_files(self):
        """Plusieurs fichiers → tous supprimés dans l'ordre, retourne le count."""
        fm = self.new_file_manager(selected_files=["file1", "file2", "file3"])

        self.assertEqual(3, fm.delete_files())
        fm.fs.delete.assert_has_calls([
            call("file1"), call("file2"), call("file3")
        ])
        self.assertEqual(3, fm.fs.delete.call_count)

    def test_delete_with_io_error(self):
        """Erreur I/O sur le seul fichier → ui.error appelé, retourne 0."""
        fm = self.new_file_manager(
            selected_files=["file1"],
            fs_delete_side_effect=OSError("Permission denied"),
        )

        self.assertEqual(0, fm.delete_files())
        fm.ui.error.assert_called_once()
        fm.fs.delete.assert_called_once_with("file1")

    def test_delete_partial_error(self):
        """Erreur sur le 2e fichier parmi 3 → les autres sont traités, retourne 2."""
        fm = self.new_file_manager(
            selected_files=["file1", "file2", "file3"],
            fs_delete_side_effect=[None, OSError("Locked"), None],
        )

        self.assertEqual(2, fm.delete_files())
        fm.ui.error.assert_called_once()
        self.assertEqual(3, fm.fs.delete.call_count)

    def test_delete_all_errors(self):
        """Erreur sur chaque fichier → ui.error appelé à chaque fois, retourne 0."""
        fm = self.new_file_manager(
            selected_files=["file1", "file2"],
            fs_delete_side_effect=OSError("Disk error"),
        )

        self.assertEqual(0, fm.delete_files())
        self.assertEqual(2, fm.ui.error.call_count)

    def test_delete_get_and_reset_is_called(self):
        """get_and_reset doit être appelé une seule fois par opération."""
        fm = self.new_file_manager(selected_files=["file1", "file2"])

        fm.delete_files()
        fm.sel.get_and_reset.assert_called_once()

    def test_copy_empty_list(self):
        """Aucun fichier sélectionné → aucune copie, retourne 0."""
        fm = self.new_file_manager(selected_files=[])

        self.assertEqual(0, fm.copy_files("/dest"))
        fm.fs.copy.assert_not_called()

    def test_copy_single_file(self):
        """Un fichier → copié vers la destination, retourne 1."""
        fm = self.new_file_manager(selected_files=["file1"])

        self.assertEqual(1, fm.copy_files("/dest"))
        fm.fs.copy.assert_called_once_with("file1", "/dest")

    def test_copy_multiple_files(self):
        """Plusieurs fichiers → tous copiés vers la même destination, retourne le count."""
        fm = self.new_file_manager(selected_files=["file1", "file2", "file3"])

        self.assertEqual(3, fm.copy_files("/dest"))
        fm.fs.copy.assert_has_calls([
            call("file1", "/dest"),
            call("file2", "/dest"),
            call("file3", "/dest"),
        ])
        self.assertEqual(3, fm.fs.copy.call_count)

    def test_copy_with_io_error(self):
        """Erreur I/O sur le seul fichier → ui.error appelé, retourne 0."""
        fm = self.new_file_manager(
            selected_files=["file1"],
            fs_copy_side_effect=OSError("Disk full"),
        )

        self.assertEqual(0, fm.copy_files("/dest"))
        fm.ui.error.assert_called_once()
        fm.fs.copy.assert_called_once_with("file1", "/dest")

    def test_copy_partial_error(self):
        """Erreur sur le 2e fichier parmi 3 → les autres sont traités, retourne 2."""
        fm = self.new_file_manager(
            selected_files=["file1", "file2", "file3"],
            fs_copy_side_effect=[None, OSError("Disk full"), None],
        )

        self.assertEqual(2, fm.copy_files("/dest"))
        fm.ui.error.assert_called_once()
        self.assertEqual(3, fm.fs.copy.call_count)

    def test_copy_all_errors(self):
        """Erreur sur chaque fichier → ui.error appelé à chaque fois, retourne 0."""
        fm = self.new_file_manager(
            selected_files=["file1", "file2"],
            fs_copy_side_effect=OSError("Disk full"),
        )

        self.assertEqual(0, fm.copy_files("/dest"))
        self.assertEqual(2, fm.ui.error.call_count)

    def test_copy_destination_is_forwarded(self):
        """La destination passée à copy_files est bien transmise à fs.copy."""
        fm = self.new_file_manager(selected_files=["file1"])

        fm.copy_files("/my/special/path")
        fm.fs.copy.assert_called_once_with("file1", "/my/special/path")

    def test_copy_get_and_reset_is_called(self):
        """get_and_reset doit être appelé une seule fois par opération."""
        fm = self.new_file_manager(selected_files=["file1"])

        fm.copy_files("/dest")
        fm.sel.get_and_reset.assert_called_once()

    # ─── move_files ───────────────────────────────────────────────────────────

    def test_move_empty_list(self):
        """Aucun fichier sélectionné → aucun déplacement, retourne 0."""
        fm = self.new_file_manager(selected_files=[])

        self.assertEqual(0, fm.move_files("/dest"))
        fm.fs.move.assert_not_called()

    def test_move_single_file(self):
        """Un fichier → déplacé vers la destination, retourne 1."""
        fm = self.new_file_manager(selected_files=["file1"])

        self.assertEqual(1, fm.move_files("/dest"))
        fm.fs.move.assert_called_once_with("file1", "/dest")

    def test_move_multiple_files(self):
        """Plusieurs fichiers → tous déplacés vers la même destination, retourne le count."""
        fm = self.new_file_manager(selected_files=["file1", "file2", "file3"])

        self.assertEqual(3, fm.move_files("/dest"))
        fm.fs.move.assert_has_calls([
            call("file1", "/dest"),
            call("file2", "/dest"),
            call("file3", "/dest"),
        ])
        self.assertEqual(3, fm.fs.move.call_count)

    def test_move_with_io_error(self):
        """Erreur I/O sur le seul fichier → ui.error appelé, retourne 0."""
        fm = self.new_file_manager(
            selected_files=["file1"],
            fs_move_side_effect=OSError("File locked"),
        )

        self.assertEqual(0, fm.move_files("/dest"))
        fm.ui.error.assert_called_once()
        fm.fs.move.assert_called_once_with("file1", "/dest")

    def test_move_partial_error(self):
        """Erreur sur le 2e fichier parmi 3 → les autres sont traités, retourne 2."""
        fm = self.new_file_manager(
            selected_files=["file1", "file2", "file3"],
            fs_move_side_effect=[None, OSError("File locked"), None],
        )

        self.assertEqual(2, fm.move_files("/dest"))
        fm.ui.error.assert_called_once()
        self.assertEqual(3, fm.fs.move.call_count)

    def test_move_all_errors(self):
        """Erreur sur chaque fichier → ui.error appelé à chaque fois, retourne 0."""
        fm = self.new_file_manager(
            selected_files=["file1", "file2"],
            fs_move_side_effect=OSError("File locked"),
        )

        self.assertEqual(0, fm.move_files("/dest"))
        self.assertEqual(2, fm.ui.error.call_count)

    def test_move_destination_is_forwarded(self):
        """La destination passée à move_files est bien transmise à fs.move."""
        fm = self.new_file_manager(selected_files=["file1"])

        fm.move_files("/my/special/path")
        fm.fs.move.assert_called_once_with("file1", "/my/special/path")

    def test_move_get_and_reset_is_called(self):
        """get_and_reset doit être appelé une seule fois par opération."""
        fm = self.new_file_manager(selected_files=["file1"])

        fm.move_files("/dest")
        fm.sel.get_and_reset.assert_called_once()
