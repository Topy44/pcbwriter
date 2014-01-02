#!/usr/bin/env python
import os, sys, math, cairo, tempfile, ghostscript, shutil
from gi.repository import Gtk, Gdk, GdkPixbuf
from pcbwriter import PCBWriter
from drawruler import draw_ruler

pcb = PCBWriter(called_from_gui=True)

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
        dawidth = da.get_allocation().width
        daheight = da.get_allocation().height

        # Fill background
        cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.rectangle(0, 0, dawidth, daheight)
        cr.fill()

        cr.set_source_rgb(0.6, 0.8, 0.8)
        cr.rectangle(0, 0, 100, daheight)
        cr.rectangle(dawidth - 100, 0, 100, daheight)
        cr.fill()

        if self.img is not None:
            self.img.draw(cr, dawidth)

        # Apply scaling to fit surface
        scale = float(dawidth) / float(180)
        cr.scale(scale, scale)

        # Draw box in corner
        cr.set_source_rgba(1, 1, 1, 0.6)
        cr.rectangle(0, 0, 20/scale, 20/scale)
        cr.fill()

        # Draw rulers
        draw_ruler(da, cr, xpos=20/scale, ypos=0, len=dawidth  / scale, scale=scale, vertical=False, skipzero=True)
        draw_ruler(da, cr, xpos=0, ypos=20/scale, len=daheight / scale, scale=scale, vertical=True, skipzero=True)

    def on_buttonLoadimage_clicked(self, button):
        dialog = Gtk.FileChooserDialog("Please choose a file", builder.get_object("pcbwriter"),
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        filter_pdf = Gtk.FileFilter()
        filter_pdf.set_name("PDF Files")
        filter_pdf.add_mime_type("application/pdf")
        dialog.add_filter(filter_pdf)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.img = image()
            self.img.load(dialog.get_filename(), builder.get_object("drawingareaPreview"))
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

# Image loading and drawing
class image:
    def __init__(self):
        self.imgtmp = None
        self.pdftmp = None
        pass

    def __del__(self):
        print_to_console("\nRemoving temp files...")
        if self.imgtmp is not None: os.remove(self.imgtmp)
        if self.pdftmp is not None: os.remove(self.pdftmp)

    def load(self, filename, da):
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

            Gtk.Widget.queue_draw(da)

    def render(self, width):
        # Using temporary png file because GdkPixbuf.Pixbuf.new_from_data() appears to be broken
        h, self.imgtmp = tempfile.mkstemp()
        imgtmp = open(self.imgtmp, "w")
        imgtmp.write(ghostscript.load_image(self.pdftmp, self.bbox, 72, 72, self.bbox[2], self.bbox[3], "pnggray").tostring())
        imgtmp.close()
        os.close(h)
        self.img = GdkPixbuf.Pixbuf.new_from_file(self.imgtmp)
        print self.img.get_height()
        print self.img.get_width()

    def draw(self, cr, width):
        self.render(width)
        Gdk.cairo_set_source_pixbuf(cr, self.img, 20, 20)
        cr.paint()

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
