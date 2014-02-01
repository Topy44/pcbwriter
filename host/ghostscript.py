from __future__ import division
import array
import subprocess
import platform

def get_bbox(fname):
    if platform.system() == "Windows":
        args = ["C:/Program Files (x86)/gs/gs9.10/bin/gswin32c.exe"]
    else:
        args = ["gs"]
    args += ["-o", "%stdout%"]
    args += ["-dQUIET"]
    args += ["-dLastPage=1"]
    args += ["-sDEVICE=bbox"]
    args += ["-f", fname]

    print " ".join(args)

    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout_data, stderr_data) = p.communicate(None)

    bbox = None
    for line in stderr_data.splitlines():
        data = line.split()
        if data[0] == "%%HiResBoundingBox:":
            bbox = [ float(s) for s in data[1:5] ]

    return bbox

def load_image(fname, bbox, xres, yres, width_px, height_px, device="bit"):
    if platform.system() == "Windows":
        args = ["C:/Program Files (x86)/gs/gs9.10/bin/gswin32c.exe"]
    else:
        args = ["gs"]

    args += ["-o", "%stdout%"]
    args += ["-dQUIET"]
    args += ["-dBATCH"]
    args += ["-dNOPAUSE"]
    args += ["-dLastPage=1"]
    args += ["-sDEVICE=" + device]
    args += ["-r%dx%d" % (xres, yres)]
    args += ["-f", fname]
    args += ["-g%dx%d" % (width_px, height_px)]
    args += ["-c", "<</Install {%f %f translate}>> setpagedevice" % (-bbox[0], -bbox[1])]

    print " ".join(args)

    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout_data, stderr_data) = p.communicate(None)

    if stderr_data != "":
        print "Ghostscript subprocess encountered an error:"
        print stderr_data
        raise RuntimeError

    img_inv = array.array("B", stdout_data)
    img = array.array("B", [v ^ 0xFF for v in img_inv])

    return img_inv


