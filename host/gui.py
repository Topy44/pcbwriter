#!/usr/bin/env python
from gi.repository import Gtk
from pcbwriter import PCBWriter

pcb = PCBWriter()

class Handler:
    def onDeleteWindow(self, *args):
        Gtk.main_quit(*args)

    def onHomePressed(self, button):
        pcb.home_stepper(wait=True);

builder = Gtk.Builder()
builder.add_from_file("example.glade")
builder.connect_signals(Handler())

window = builder.get_object("window1")
window.show_all()

Gtk.main()

print("yay!")