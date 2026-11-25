"""LEWD Modded Exes updater for Mod Organizer 2.

Install: unpack so that <MO2>/plugins/lewd_updater/__init__.py exists, then restart MO2.
Works with plain Anomaly and with GAMMA. Never writes to the game's bin/ folder.
"""

import os
import threading

import mobase

try:
    from PyQt6.QtCore import QObject, pyqtSignal
    from PyQt6.QtWidgets import (QDialog, QLabel, QMessageBox, QPushButton,
                                 QVBoxLayout)
    _YES = QMessageBox.StandardButton.Yes
    _NO = QMessageBox.StandardButton.No
except ImportError:  # MO2 2.4 ships PyQt5
    from PyQt5.QtCore import QObject, pyqtSignal
    from PyQt5.QtWidgets import (QDialog, QLabel, QMessageBox, QPushButton,
                                 QVBoxLayout)
    _YES = QMessageBox.Yes
    _NO = QMessageBox.No

from . import core

PLUGIN_VERSION = "1.0.0"
PLUGIN_NAME = "LEWD Exes Updater"


class _Bridge(QObject):
    """Moves results from the worker thread back to MO2's UI thread."""
    checked = pyqtSignal(object, object, object, bool)   # manifest, assets, error, manual
    installed = pyqtSignal(object, object)                # version, error


class LewdUpdater(mobase.IPluginTool):

    def __init__(self):
        super().__init__()
        self._org = None
        self._window = None
        self._busy = False
        self._bridge = None

    # ---- IPlugin ----
    def init(self, organizer):
        self._org = organizer
        self._bridge = _Bridge()
        self._bridge.checked.connect(self._on_checked)
        self._bridge.installed.connect(self._on_installed)
        organizer.onUserInterfaceInitialized(self._on_ui_ready)
        organizer.onAboutToRun(self._on_about_to_run)
        return True

    def name(self):
        return PLUGIN_NAME

    def author(self):
        return "LEWD"

    def description(self):
        return ("Installs and updates the LEWD Modded Exes into the game's bin_lewd folder, "
                "and starts them in place of the stock exes.")

    def version(self):
        major, minor, patch = (int(x) for x in PLUGIN_VERSION.split("."))
        return mobase.VersionInfo(major, minor, patch, mobase.ReleaseType.FINAL)

    def settings(self):
        return [
            mobase.PluginSetting("check_on_start", "Check for new LEWD exes when MO2 starts", True),
            mobase.PluginSetting("use_lewd_exes", "Start the LEWD exes in place of the stock ones from bin", True),
            mobase.PluginSetting("repo", "GitHub repository the releases come from", core.DEFAULT_REPO),
            mobase.PluginSetting("skipped_version", "A version the player chose to skip", ""),
        ]

    # ---- IPluginTool ----
    def displayName(self):
        return "LEWD Modded Exes"

    def tooltip(self):
        return "Check for updates, roll back, or switch the LEWD exes on or off"

    def icon(self):
        try:
            from PyQt6.QtGui import QIcon
        except ImportError:
            from PyQt5.QtGui import QIcon
        return QIcon()

    def display(self):
        self._show_panel()

    # ---- helpers ----
    def _setting(self, key):
        return self._org.pluginSetting(self.name(), key)

    def _set(self, key, value):
        self._org.setPluginSetting(self.name(), key, value)

    def _game_dir(self):
        return self._org.managedGame().gameDirectory().absolutePath()

    def _parent(self):
        return self._window

    def _ask(self, title, text):
        return QMessageBox.question(self._parent(), title, text, _YES | _NO) == _YES

    def _info(self, title, text):
        QMessageBox.information(self._parent(), title, text)

    def _warn(self, title, text):
        QMessageBox.warning(self._parent(), title, text)

    # ---- startup check ----
    def _on_ui_ready(self, window):
        self._window = window
        if self._setting("check_on_start"):
            self._check(manual=False)

    def _check(self, manual):
        if self._busy:
            return
        self._busy = True
        repo = self._setting("repo") or core.DEFAULT_REPO

        def work():
            try:
                manifest, assets = core.latest_release(repo)
                self._bridge.checked.emit(manifest, assets, None, manual)
            except Exception as e:  # offline, rate limit, no release yet
                self._bridge.checked.emit(None, None, e, manual)

        threading.Thread(target=work, daemon=True).start()

    def _on_checked(self, manifest, assets, error, manual):
        self._busy = False
        if error is not None:
            if manual:
                self._warn("LEWD Modded Exes", f"Could not check for updates:\n{error}")
            return

        # Updater first: a newer updater may be needed to install the newer exes.
        plugin = manifest.get("plugin") or {}
        if core.is_newer(plugin.get("version", ""), PLUGIN_VERSION):
            if self._ask("LEWD Modded Exes",
                         f"A new version of the LEWD updater is out ({plugin['version']}).\n"
                         "Update it now? MO2 needs a restart afterwards."):
                try:
                    v = core.self_update(os.path.dirname(os.path.abspath(__file__)), plugin, assets)
                    self._info("LEWD Modded Exes", f"Updater {v} installed. Please restart MO2.")
                except Exception as e:
                    self._warn("LEWD Modded Exes", f"Updater update failed:\n{e}")
                return

        remote = manifest.get("version", "")
        local = core.installed_version(self._game_dir())
        if not core.is_newer(remote, local):
            if manual:
                self._info("LEWD Modded Exes", f"You have the newest LEWD exes ({local}).")
            return
        if not manual and remote == self._setting("skipped_version"):
            return

        if local:
            text = f"LEWD Modded Exes {remote} is out (you have {local}). Update now?"
        else:
            text = (f"Install the LEWD Modded Exes {remote}?\n\n"
                    "They go into a separate bin_lewd folder; your normal bin folder is not touched. "
                    "MO2 will start them in place of the stock exes.")
        box = QMessageBox(self._parent())
        box.setWindowTitle("LEWD Modded Exes")
        box.setText(text)
        update_btn = box.addButton("Update" if local else "Install", QMessageBox.ButtonRole.AcceptRole
                                   if hasattr(QMessageBox, "ButtonRole") else QMessageBox.AcceptRole)
        box.addButton("Later", QMessageBox.ButtonRole.RejectRole
                      if hasattr(QMessageBox, "ButtonRole") else QMessageBox.RejectRole)
        skip_btn = box.addButton("Skip this version", QMessageBox.ButtonRole.DestructiveRole
                                 if hasattr(QMessageBox, "ButtonRole") else QMessageBox.DestructiveRole)
        box.exec() if hasattr(box, "exec") else box.exec_()
        clicked = box.clickedButton()
        if clicked == skip_btn:
            self._set("skipped_version", remote)
        elif clicked == update_btn:
            self._install(manifest, assets)

    # ---- install ----
    def _mod_dir(self):
        mod = self._org.modList().getMod(core.MOD_NAME)
        if mod is None:
            mod = self._org.createMod(mobase.GuessedString(core.MOD_NAME))
        if mod is None:
            raise core.UpdateError(f"Could not create the MO2 mod '{core.MOD_NAME}'")
        return mod.absolutePath()

    def _install(self, manifest, assets):
        if self._busy:
            return
        try:
            mod_dir = self._mod_dir()
        except Exception as e:
            self._warn("LEWD Modded Exes", str(e))
            return
        self._busy = True
        game_dir = self._game_dir()

        def work():
            try:
                v = core.install_release(game_dir, mod_dir, manifest, assets)
                self._bridge.installed.emit(v, None)
            except Exception as e:
                self._bridge.installed.emit(None, e)

        threading.Thread(target=work, daemon=True).start()

    def _on_installed(self, version, error):
        self._busy = False
        if error is not None:
            self._warn("LEWD Modded Exes", f"Install failed, nothing was changed in your game:\n{error}")
            return
        ml = self._org.modList()
        try:
            ml.setActive(core.MOD_NAME, True)
            ml.setPriority(core.MOD_NAME, 0)   # lowest priority: every other mod wins
        except Exception:
            pass
        self._org.refresh()
        self._info("LEWD Modded Exes",
                   f"LEWD Modded Exes {version} installed.\n\n"
                   "Start the game from MO2 as usual. If this is your first install, "
                   "clear the shader cache once in the Anomaly launcher.")

    # ---- launch redirect ----
    def _on_about_to_run(self, path, *rest):
        """Starts bin_lewd\\X.exe when MO2 is about to start bin\\X.exe."""
        if not self._setting("use_lewd_exes"):
            return True
        try:
            target = core.lewd_exe_for(self._game_dir(), path)
            if not target:
                return True
            args = rest[1] if len(rest) >= 2 and isinstance(rest[1], str) else ""
            self._org.startApplication(target, [args] if args else [], os.path.dirname(target))
            return False   # we started the LEWD exe instead
        except Exception:
            return True    # on any problem, let the stock exe run

    # ---- tool panel ----
    def _show_panel(self):
        game_dir = self._game_dir()
        dlg = QDialog(self._parent())
        dlg.setWindowTitle("LEWD Modded Exes")
        lay = QVBoxLayout(dlg)
        ver = core.installed_version(game_dir) or "not installed"
        on = bool(self._setting("use_lewd_exes"))
        lay.addWidget(QLabel(f"Installed: {ver}\nUpdater: {PLUGIN_VERSION}\n"
                             f"Start LEWD exes: {'on' if on else 'off'}"))

        b_check = QPushButton("Check for updates now")
        b_check.clicked.connect(lambda: (dlg.accept(), self._check(manual=True)))
        lay.addWidget(b_check)

        b_toggle = QPushButton("Use stock exes" if on else "Use LEWD exes")
        b_toggle.clicked.connect(lambda: (self._set("use_lewd_exes", not on), dlg.accept()))
        lay.addWidget(b_toggle)

        b_back = QPushButton("Roll back to the previous build")
        b_back.setEnabled(os.path.isdir(os.path.join(game_dir, core.BIN_DIR + ".prev")))

        def do_rollback():
            dlg.accept()
            try:
                v = core.rollback(game_dir)
                self._info("LEWD Modded Exes", f"Rolled back to {v or 'the previous build'}.")
            except Exception as e:
                self._warn("LEWD Modded Exes", str(e))

        b_back.clicked.connect(do_rollback)
        lay.addWidget(b_back)
        dlg.exec() if hasattr(dlg, "exec") else dlg.exec_()


def createPlugin():
    return LewdUpdater()
