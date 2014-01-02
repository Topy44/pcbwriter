import cairo, math

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