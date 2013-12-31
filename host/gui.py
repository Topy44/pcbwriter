#!/usr/bin/env python
import sys, math, cairo
from gi.repository import Gtk
from pcbwriter import PCBWriter

pcb = PCBWriter(called_from_gui=True)

# Signal handler class
class Handler:
    def onDeleteEvent(self, *args):
        Gtk.main_quit(*args)

    def onImagemenuitemFileQuitActivate(self, *args):
        Gtk.main_quit(*args)

    def on_buttonHome_clicked(self, button):
        pcb.home_stepper(wait=True)

    def on_buttonFindDevice_clicked(self, button):
        pcb.find_device()
        if pcb.dev:
            builder.get_object("buttonHome").set_sensitive(True)
            print_to_console("\nDevice found!")
        else:
            builder.get_object("buttonHome").set_sensitive(False)
            print_to_console("\nDevice not found...")

    def on_buttonStepperOff_clicked(self, button):
        pcb.stepper_off()

    def on_drawingareaPreview_draw(self, da, cr):
        # Fill background
        cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.rectangle(0, 0, da.get_allocation().width, da.get_allocation().height)
        cr.fill()

        cr.set_source_rgb(0.6, 0.8, 0.8)
        cr.rectangle(0, 0, 100, da.get_allocation().height)
        cr.rectangle(da.get_allocation().width - 100, 0, 100, da.get_allocation().height)
        cr.fill()

        scale = float(da.get_allocation().width) / float(180)
        cr.scale(scale, scale)

        # Draw box in corner
        cr.set_source_rgba(1, 1, 1, 0.6)
        cr.rectangle(0, 0, 20/scale, 20/scale)
        cr.fill()

        # Draw rulers
        draw_ruler(da, cr, xpos=20/scale, ypos=0, len=da.get_allocation().width  / scale, scale=scale, vertical=False, skipzero=True)
        draw_ruler(da, cr, xpos=0, ypos=20/scale, len=da.get_allocation().height / scale, scale=scale, vertical=True, skipzero=True)

    def on_buttonLoadimage_clicked(self, button):
        pass

def draw_ruler(da, cr, xpos, ypos, len, scale, offset=0, vertical=False, skipzero=False):
    # Parameters
    height = 20.0/scale    # Height of ruler
    sheight = 4.0/scale    # Length of short marks
    ldist = 10.0    # Distance between long marks (and between measure numbers)
    sdist = 1.0    # Distance between short marks

    if vertical:
        xpos -= height
        xpos, ypos = ypos, xpos
        cr.save()
        cr.rotate(math.radians(90))

    # Draw background
    cr.set_source_rgba(1, 1, 1, 0.6)
    cr.rectangle(xpos, ypos, len, height)
    cr.fill()

    # Draw edge
    cr.set_source_rgba(0, 0, 0, 0.7)
    cr.set_line_width(1.0/scale)
    if vertical:
        cr.move_to(xpos, ypos)
        cr.line_to(len, ypos)
    else:
        cr.move_to(xpos, ypos + height)
        cr.line_to(len, ypos + height)
    cr.stroke()

    # Draw long marks
    i = 0.0
    while i * ldist <= len:
        cr.move_to(i * ldist + xpos, ypos)
        cr.line_to(i * ldist + xpos, ypos + height)
        i += 1
    cr.stroke()

    # Draw short marks
    i = 0.0
    while i * sdist <= len:
        if vertical:
            cr.move_to(i * sdist + xpos, ypos + sheight)
            cr.line_to(i * sdist + xpos, ypos )
        else:
            cr.move_to(i * sdist + xpos, ypos + height - sheight)
            cr.line_to(i * sdist + xpos, ypos + height)
        i += 1
    cr.stroke()

    # Draw measures
    cr.select_font_face("Courier", cairo.FONT_SLANT_NORMAL)
    cr.set_font_size(15/scale)
    if cr.text_extents("000")[4] > ldist:
        cr.set_font_size(15/scale / (cr.text_extents("000")[4] / ldist))

    i = 0.0
    while i * ldist <= len:
        cr.move_to(i * ldist + xpos + 0.5, ypos + height / 2 + cr.text_extents(str(i * ldist - offset))[3] / 2)
        cr.show_text(str(int(i * ldist + offset)))
        i += 1

    if vertical:
        cr.restore()

def print_to_console(message):
    console.get_buffer().insert(console.get_buffer().get_end_iter(), message)
    console.scroll_mark_onscreen(console.get_buffer().get_insert())

# Load GUI layout
builder = Gtk.Builder()
builder.add_from_file("pcbwriter.glade")
builder.connect_signals(Handler())

# Prepare the main window
window = builder.get_object("pcbwriter")

# Prepare the console
console = builder.get_object("textviewConsole")
print_to_console("PCBWriter GUI")

# Prepare the image preview
preview = builder.get_object("drawingareaPreview")

# Show the main window
window.show_all()

Gtk.main()

# Cleanup
print("Successfully terminated")
