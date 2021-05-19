#!/usr/bin/python3
"""
Quickly convert a LaTeX formula to a gif image,
preview it, copy it to the clipboard, or save it.
"""
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository.GLib import Error as GLibError

import os
import subprocess
from multiprocessing import Process

CWD = os.getcwd()
PATH = os.path.dirname(os.path.realpath(__file__))
os.chdir('/tmp/')

TEX_FOOT = r"""
\end{displaymath}
\end{document}
"""

XCLIP_STRING = b"""x-special/nautilus-clipboard
copy
file:///tmp/latexpreview.gif
"""


def tex_head(packages):
    """
    Compute the appropriate header given a list of packages
    """
    r = r"""\documentclass[12pt]{article}
"""

    for p in packages:
        r += r"\usepackage{" + p + "}\n"

    r += r"""\pagestyle{empty}
\begin{document}
\begin{displaymath}
"""
    return r


def call(command: list, stdin = ""):
    """Call an external program"""
    try:
        subprocess.check_output(
            command, stderr=subprocess.STDOUT, input=stdin
        )
    except OSError as e:
        error_dialog("Failed to run {}:\n{}".format(command[0], e))
    except subprocess.CalledProcessError as e:
        return e
    return None


def error_dialog(e):
    dialog = Gtk.MessageDialog(
        parent                 = None,
        message_type           = Gtk.MessageType.ERROR,
        buttons                = Gtk.ButtonsType.OK,
        text                   = e)
    dialog.set_title('Error!')
    dialog.show()
    dialog.run()
    dialog.destroy()


class LogWindow(Gtk.Window):
    def __init__(self) -> None:
        super().__init__()
        self.set_title("/tmp/latexpreview.log")
        self.sw = Gtk.ScrolledWindow()
        self.log = Gtk.TextView()
        self.log.set_editable(False)
        self.sw.set_size_request(750,400)
        buff = Gtk.TextBuffer()
        try:
            with open('latexpreview.log', 'r') as file:
                buff.set_text(file.read())
            self.log.set_buffer(buff)
        except FileNotFoundError:
            pass

        self.sw.add(self.log)
        self.add(self.sw)


class MainWindow:
    def __init__(self):
        # load up builder
        self.builder = Gtk.Builder()
        try: self.builder.add_from_file(
                os.path.join(PATH, "latexpreview.ui"))
        except GLibError as e:
            error_dialog(e)
            self.good = False
            return
        self.good = True

        handlers = {
            "on_save": self.on_save,
            "on_copy": self.on_copy,
            "on_resolution_changed": self.on_resolution_changed,
            "on_preview": self.on_preview,
            "on_log": self.on_log,
            "on_packages": self.on_packages,
            "on_quit": self.on_quit
        }

        self.builder.connect_signals(handlers)
        self.resolution_spin = self.builder.get_object("resolution_spin")
        self.editor = self.builder.get_object("editor")
        self.preview = self.builder.get_object("preview")
        self.packages_pop = self.builder.get_object("packages_pop")

        # check if xclip is installed
        r = subprocess.call("command -v xclip >> /dev/null", shell=True)
        if r:
            self.builder.get_object("cpy_btn").set_sensitive(False)

        # initialize the packages pop-over
        renderer = Gtk.CellRendererText()
        renderer.set_property("editable", True)
        column = Gtk.TreeViewColumn("packages", renderer, text=0)
        self.packages = Gtk.ListStore(str)
        packages_tree = Gtk.TreeView(model=self.packages)
        packages_tree.append_column(column)
        self.packages_pop.add(packages_tree)

        # load up packages
        try:
            with open(os.path.join(PATH, ".packages")) as f:
                for line in f: self.packages.append([line[:-1]])
        except FileNotFoundError:
            pass
        self.packages.append(["<add a LaTeX package>"])

        self.clipboard = []
        self.builder.get_object('window').show_all()

    def generate(self):
        """
        Generate the preview
        Return True if the compilation was successful,
        False otherwise
        """
        latex = [
            "latex",
            "-interaction=nonstopmode",
            "latexpreview.tex"
        ]
        dvigif = [
            "dvigif",
            "latexpreview.dvi",
            '-D',
            str(self.resolution_spin.get_value()),
            '-T', 'tight', '-bg', 'Transparent', '-o', 'latexpreview.gif'
        ]
        # generate the latex
        with open('latexpreview.tex', 'w') as tex:
            buff = self.editor.get_buffer()
            tex.write(tex_head([row[0] for row in self.packages]) + buff.get_text(
                buff.get_start_iter(), buff.get_end_iter(), True
            ) + TEX_FOOT)
        # build the latex
        e = call(latex)
        if e is not None:
            self.preview.set_from_icon_name("emblem-unreadable", 6)
            return False
        # convert to image
        e = call(dvigif)
        if e is not None:
            error_dialog("{} terminated with exit status {}:\n{}".format(
                e.cmd[0], e.returncode, e.output.decode("ascii")))
        # update preview
        self.preview.set_from_file('latexpreview.gif')
        return True

    def on_save(self, widget):
        if not self.generate(): return

        os.chdir(CWD) # so we don't pop up in the /tmp folder

        dialog = Gtk.FileChooserDialog(title="Please choose a file",
            action=Gtk.FileChooserAction.SAVE)

        dialog.add_filter(self.builder.get_object('GIF'))
        dialog.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        dialog.add_button(Gtk.STOCK_SAVE, Gtk.ResponseType.OK)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            file_path = dialog.get_filename()
            os.rename('/tmp/latexpreview.gif', file_path)

        dialog.destroy()

        os.chdir('/tmp/')

    def on_copy(self, widget):
        # xclip needs to run for as long as the selection exists
        # hence we need to use threading
        def copy():
            e = call(
                ["xclip", "-selection", "clipboard"],
                XCLIP_STRING
            )
            if e is not None:
                error_dialog("{} terminated with exit status {}:\n{}".format(
                    e.cmd[0], e.returncode, e.output.decode("ascii")))

        if not self.generate(): return

        selection = Process(target=copy)
        selection.start()
        self.clipboard.append(selection)

    def on_quit(self, widget):
        # kill the running xclips and quit Gtk
        for t in self.clipboard: t.terminate()
        Gtk.main_quit()

    def on_resolution_changed(self, widget):
        self.generate()

    def on_preview(self, widget):
        self.generate()

    def on_log(self, widget):
        w = LogWindow()
        w.show_all()

    def on_packages(self, widget):
        self.packages_pop.show_all()


if __name__ == '__main__':
    w = MainWindow()
    if w.good: Gtk.main()
