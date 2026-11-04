"""Tests de los respaldos: crear, listar, restaurar y limpiar."""

import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from src.core.config_service import FileCopyService
from src.models.domain_models import BackupInfo


def make_config(path: Path, keys: str, remotecache: str = None) -> None:
    """Crea una carpeta 570 mínima con un archivo de teclas."""
    path.joinpath("local", "cfg").mkdir(parents=True, exist_ok=True)
    path.joinpath("local", "cfg", "user_keys_0_slot0.vcfg").write_text(keys)
    if remotecache is not None:
        path.joinpath("remotecache.vdf").write_text(remotecache)


def keys_of(path: Path) -> str:
    return path.joinpath("local", "cfg", "user_keys_0_slot0.vcfg").read_text()


class TestBackups(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.service = FileCopyService(backup_dir=self.root / "backups")

    def tearDown(self):
        self._tmp.cleanup()

    def _backup(self, steamid: str, stamp: str, keys: str) -> Path:
        path = self.root / "backups" / f"backup_{steamid}_{stamp}"
        make_config(path, keys)
        return path

    def test_create_backup_skips_empty_account(self):
        empty = self.root / "userdata" / "1" / "570"
        self.assertIsNone(self.service.create_backup("1", empty))
        self.assertEqual(self.service.list_backups(), [])

    def test_list_backups_newest_first_and_ignores_other_folders(self):
        self._backup("111", "20261101_100000", "a")
        self._backup("111", "20261103_100000", "b")
        self._backup("222", "20261102_100000", "c")
        (self.root / "backups" / "carpeta_cualquiera").mkdir()

        backups = self.service.list_backups()
        self.assertEqual([b.path.name for b in backups], [
            "backup_111_20261103_100000",
            "backup_222_20261102_100000",
            "backup_111_20261101_100000",
        ])
        self.assertEqual(len(self.service.list_backups("222")), 1)

    def test_restore_backs_up_current_and_keeps_remotecache(self):
        account = self.root / "userdata" / "111" / "570"
        make_config(account, "actual", remotecache="nube actual")
        old = self._backup("111", "20261101_100000", "antigua")
        old.joinpath("remotecache.vdf").write_text("nube vieja")

        backup = self.service.list_backups("111")[0]
        ok, _ = self.service.restore_backup(backup, account)

        self.assertTrue(ok)
        self.assertEqual(keys_of(account), "antigua")
        self.assertEqual(account.joinpath("remotecache.vdf").read_text(), "nube actual")
        # Se guardó la configuración que había, para poder deshacer
        newest = self.service.list_backups("111")[0]
        self.assertNotEqual(newest.path, old)
        self.assertEqual(keys_of(newest.path), "actual")

    def test_cleanup_keeps_newest_per_account(self):
        for day in range(1, 8):
            self._backup("111", f"202611{day:02d}_100000", str(day))
        self._backup("222", "20261001_100000", "única")

        self.service.cleanup_old_backups(max_per_account=5)

        remaining = self.service.list_backups("111")
        self.assertEqual(len(remaining), 5)
        self.assertEqual(remaining[-1].path.name, "backup_111_20261103_100000")
        # La cuenta con un solo respaldo no pierde el suyo
        self.assertEqual(len(self.service.list_backups("222")), 1)

    def test_created_text_is_readable(self):
        info = BackupInfo("1", datetime(2026, 11, 4, 3, 44, 56), Path("x"))
        self.assertEqual(info.created_text, "4 nov 2026, 03:44")


if __name__ == "__main__":
    unittest.main()
