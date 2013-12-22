#!/usr/bin/env python
import sys, StringIO
from gi.repository import Gtk
from pcbwriter import PCBWriter

pcb = PCBWriter(called_from_gui=True)

class Handler:
    def onDeleteEvent(self, *args):
        Gtk.main_quit(*args)

    def onImagemenuitemFileQuitActivate(self, *args):
        Gtk.main_quit(*args)

    def onButtonHomeClicked(self, button):
        pcb.home_stepper(wait=True)

    def onButtonFindDeviceClicked(self, button):
        pcb.find_device()
        if pcb.dev:
            builder.get_object("buttonHome").set_sensitive(True)
            console.insert(console.get_end_iter(), "\nDevice found!")
        else:
            builder.get_object("buttonHome").set_sensitive(False)
            console.insert(console.get_end_iter(), "\nDevice not found...")

    def onButtonStepperOffClicked(self, button):
        pcb.stepper_off()

# Load GUI layout
builder = Gtk.Builder()
builder.add_from_file("pcbwriter.glade")
builder.connect_signals(Handler())

console = builder.get_object("textviewConsole").get_buffer()
console.set_text("PCBWriter GUI")

window = builder.get_object("pcbwriter")
window.show_all()

Gtk.main()

print("Successfully terminated")
