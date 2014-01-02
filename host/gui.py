#!/usr/bin/env python
import os, sys, math, cairo, tempfile, ghostscript, shutil
from gi.repository import Gtk, Gdk, GdkPixbuf
from pcbwriter import PCBWriter

pcb = PCBWriter(called_from_gui=True)

#print dir(GdkPixbuf.Pixbuf)

# Signal handler class
class Handler:
    img = None

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

        if self.img is not None:
            self.img.draw(cr)

        # Apply scaling to fit surface
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
        self.img = image()
        self.img.load("helloworld.pdf")

class image:
    def __init__(self):
        self.imgtmp = None
        self.pdftmp = None
        pass

    def __del__(self):
        print_to_console("\nRemoving temp files...")
        if self.imgtmp is not None: os.remove(self.imgtmp)
        if self.pdftmp is not None: os.remove(self.pdftmp)

    def load(self, filename):
        # Check if file exists
        if not os.path.isfile(filename):
            print_to_console("\nFile \"%s\" not found." % filename )
        else:
            print_to_console("\nLoading image: \"%s\"" % filename)
            self.bbox = ghostscript.get_bbox(filename)
            print_to_console("\nImage size: %d mm x %d mm" % (self.bbox[2], self.bbox[3]))

            # Make working copy of PDF so it stays available
            h, self.pdftmp = tempfile.mkstemp()
            shutil.copy(filename, self.pdftmp)
            os.close(h)

            # Using temporary png file because GdkPixbuf.Pixbuf.new_from_data() appears to be broken
            h, self.imgtmp = tempfile.mkstemp()
            imgtmp = open(self.imgtmp, "w")
            imgtmp.write(ghostscript.load_image(self.pdftmp, self.bbox, 144, 144, self.bbox[2]*2, self.bbox[3]*2, "pnggray").tostring())
            imgtmp.close()
            os.close(h)

            self.img = GdkPixbuf.Pixbuf.new_from_file(self.imgtmp)
            print self.img.get_height()
            print self.img.get_width()
            Gtk.Widget.queue_draw(builder.get_object("drawingareaPreview"))

    def draw(self, cr):
        Gdk.cairo_set_source_pixbuf(cr, self.img, 20, 20)
        cr.paint()

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
    print message

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
