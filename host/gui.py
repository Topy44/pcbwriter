#!/usr/bin/env python
import sys, StringIO
from gi.repository import Gtk
from pcbwriter import PCBWriter

pcb = PCBWriter()

class Handler:
    def onDeleteWindow(self, *args):
        Gtk.main_quit(*args)

    def onImagemenuitemQuitActivate(self, *args):
        Gtk.main_quit(*args)

builder = Gtk.Builder()
builder.add_from_file("pcbwriter.glade")
builder.connect_signals(Handler())

window = builder.get_object("pcbwriter")
window.show_all()

Gtk.main()
