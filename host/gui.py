#!/usr/bin/env python
import os, sys, math, cairo, tempfile, ghostscript, shutil, pyPdf
from gi.repository import Gtk, Gdk, GdkPixbuf
from pcbwriter import PCBWriter
from drawruler import draw_rulers

pcb = PCBWriter(called_from_gui=True)

# Signal handler class
class Handler:
    def __init__(self, *args):
        self.img = None
        self.scale = 5.0
        builder.get_object("adjustmentZoom").set_value(self.scale)
        self.devwidth = builder.get_object("adjustmentDeviceWidth").get_value()
        self.devheight = builder.get_object("adjustmentDeviceHeight").get_value()
        self.limits = 10

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

    def on_adjustmentDeviceWidth_value_changed(self, adj):
        self.devwidth = adj.get_value()
        Gtk.Widget.queue_draw(builder.get_object("drawingareaPreview"))

    def on_adjustmentDeviceHeight_value_changed(self, adj):
        self.devheight = adj.get_value()
        Gtk.Widget.queue_draw(builder.get_object("drawingareaPreview"))

    def on_drawingareaPreview_draw(self, da, cr):
        dawidth = da.get_allocation().width
        daheight = da.get_allocation().height

        # Set drawingarea size for proper scrolling
        da.set_size_request((self.devwidth + self.limits*2) * self.scale, (self.devheight + self.limits*2) * self.scale)

        # Fill background
        cr.set_source_rgb(0.8, 0.8, 0.8)
        cr.rectangle(0, 0, dawidth, daheight)
        cr.fill()

        # Draw rulers
        draw_rulers(cr, self.scale, (self.limits * self.scale, self.limits * self.scale), (dawidth, daheight), (self.devwidth, self.devheight))

        # Set origin
        cr.translate(self.limits * self.scale, self.limits * self.scale)

        # Draw device limits
        cr.set_source_rgb(0.6, 0.8, 0.8)
        cr.rectangle(0, 0, self.devwidth * self.scale, self.devheight * self.scale)
        cr.fill()

        # Draw image if an image is loaded
        if self.img is not None:
            self.img.draw(cr, dawidth)

    def on_buttonLoadimage_clicked(self, button):
        dialog = Gtk.FileChooserDialog("Please choose a file", builder.get_object("pcbwriter"),
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        filter_pdf = Gtk.FileFilter()
        filter_pdf.set_name("PDF Files")
        filter_pdf.add_mime_type("application/pdf")
        dialog.add_filter(filter_pdf)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.img = image()
            self.img.load(dialog.get_filename(), builder.get_object("drawingareaPreview"))
        elif response == Gtk.ResponseType.CANCEL:
            pass

        dialog.destroy()

    def on_buttonFitDevice_clicked(self, button):
        builder.get_object("adjustmentZoom").set_value(builder.get_object("scrolledwindowPreview").get_allocation().width / (self.devwidth + self.limits*2))
        Gtk.Widget.queue_draw(builder.get_object("drawingareaPreview"))

    def on_adjustmentZoom_value_changed(self, adj):
        self.scale = adj.get_value()
        Gtk.Widget.queue_draw(builder.get_object("drawingareaPreview"))

# Image loading and drawing
class image:
    def __init__(self):
        self.imgtmp = None
        self.pdftmp = None
        self.pixbuf = None
        self.quality = 2
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
            # Make working copy of PDF so it stays available
            h, self.pdftmp = tempfile.mkstemp()
            shutil.copy(filename, self.pdftmp)
            os.close(h)

            print_to_console("\nLoading image: \"%s\"" % filename)
            self.bbox = ghostscript.get_bbox(self.pdftmp)
            print self.bbox

            pdf = pyPdf.PdfFileReader(file(self.pdftmp))
            self.mbox = pdf.getPage(0).mediaBox
            print self.mbox

            pwidth = float(self.mbox[2] - self.mbox[0]) / 72.0 * 25.4
            pheight = float(self.mbox[3] - self.mbox[1]) / 72.0 * 25.4
            print_to_console("\nImage size: %.2f mm x %.2f mm" % (pwidth, pheight))

            Gtk.Widget.queue_draw(da)

    def render(self):
        # Using temporary png file because GdkPixbuf.Pixbuf.new_from_data() appears to be broken
        h, self.imgtmp = tempfile.mkstemp()
        print self.imgtmp
        imgtmp = open(self.imgtmp, "w")
        imgtmp.write(ghostscript.load_image(
            self.pdftmp,    # PDF Filename
            [0, 0, 0, 0],    # Don't supply a bounding box
            72 * self.quality,    # X Resolution * quality factor
            72 * self.quality,    # Y Resolution * quality factor
            0,    # 0 = Render entire page
            0,    # 0 = Render entire page
            "pngmono").tostring())
        imgtmp.close()
        os.close(h)
        return GdkPixbuf.Pixbuf.new_from_file(self.imgtmp)

    def draw(self, cr, width):
        if self.pixbuf is None:
            self.pixbuf = self.render()
        scale = builder.get_object("adjustmentZoom").get_value() / 72 * 25.4 / self.quality
        cr.save()
        cr.scale(scale, scale)
        Gdk.cairo_set_source_pixbuf(cr, self.pixbuf, 0, 0)
        cr.paint()
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
