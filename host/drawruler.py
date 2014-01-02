import cairo, math

def draw_ruler(da, cr, xpos, ypos, length, scale, offset=0, limit=None, vertical=False, skipzero=False):
    # Parameters
    height = 20.0    # Height of ruler (pixels)
    sheight = 4.0    # Length of short marks (pixels)
    ldist = 10.0*scale    # Distance between long marks (and between measure numbers) (points)
    sdist = 1.0*scale    # Distance between short marks (points)

    if limit is None: limit = length

    if vertical:
        xpos -= height
        xpos, ypos = ypos, xpos
        cr.save()
        cr.rotate(math.radians(90))

    # Draw background
    cr.set_source_rgba(1, 1, 1, 0.6)
    cr.rectangle(xpos, ypos, length, height)
    cr.fill()

    # Draw edge
    cr.set_source_rgba(0, 0, 0, 0.7)
    cr.set_line_width(1.0)
    if vertical:
        cr.move_to(xpos, ypos)
        cr.line_to(length, ypos)
    else:
        cr.move_to(xpos, ypos + height)
        cr.line_to(length, ypos + height)
    cr.stroke()

    # Draw long marks
    i = 0.0
    while i * ldist <= length:
        cr.move_to(i * ldist + offset, ypos)
        cr.line_to(i * ldist + offset, ypos + height)
        i += 1
    cr.stroke()

    # Draw short marks
    i = 0.0
    while i * sdist <= limit:
        if vertical:
            cr.move_to(i * sdist + offset, ypos + sheight)
            cr.line_to(i * sdist + offset, ypos )
        else:
            cr.move_to(i * sdist + offset, ypos + height - sheight)
            cr.line_to(i * sdist + offset, ypos + height)
        i += 1
    #i = 0.0
    #while i * sdist <= offset - xpos:
        #cr.move_to(xpos + offset - i * sdist, ypos + height - sheight)
        #cr.line_to(xpos + offset - i * sdist, ypos + height)
        #i += 1
    cr.stroke()

    # Draw measures
    cr.select_font_face("Courier", cairo.FONT_SLANT_NORMAL)
    cr.set_font_size(15)
    if cr.text_extents("000")[4] > ldist:
        cr.set_font_size(15 / (cr.text_extents("000")[4] / ldist))

    i = 0.0
    while i * ldist <= length:
        cr.move_to(i * ldist + offset + 0.5, ypos + height / 2 + cr.text_extents(str(i * ldist))[3] / 2)
        cr.show_text(str(int(i * (ldist / scale))))
        i += 1

    if vertical:
        cr.restore()