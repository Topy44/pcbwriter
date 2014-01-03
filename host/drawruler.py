import cairo, math

def draw_rulers(cr, scale, zero, winsize, length):
    height = 20.0
    mark = 4.0
    ldist = 10.0 * scale
    sdist = 1.0 * scale

    # Draw background
    cr.set_source_rgba(1, 1, 1, 0.6)
    cr.rectangle(height, 0, winsize[0], height)
    cr.rectangle(0, height, height, winsize[1])
    cr.fill()

    # Draw edge
    cr.set_source_rgba(0, 0, 0, 0.7)
    cr.set_line_width(1.0)
    cr.move_to(0, height)
    cr.line_to(winsize[0], height)
    cr.move_to(height, 0)
    cr.line_to(height, winsize[1])
    cr.stroke()

    # Draw corner box
    cr.set_source_rgba(1, 1, 1, 0.6)
    cr.rectangle(0, 0, height, height)
    cr.fill()

    # Draw horizontal ruler
    cr.set_source_rgba(0, 0, 0, 0.7)
    cr.save()
    cr.translate(zero[0], 0)

    cr.select_font_face("Courier", cairo.FONT_SLANT_NORMAL)
    cr.set_font_size(15)
    if cr.text_extents("000")[4] > ldist:
        cr.set_font_size(15 / ((cr.text_extents("000")[4] * 0.9) / ldist))

    i = 0
    while (i-1) * ldist <= length[0] * scale - sdist:
        cr.move_to(i * ldist, 0)
        cr.line_to(i * ldist, height)
        if sdist >= 3.5 and i * ldist <= length[0] * scale - sdist:
            ii = 1
            while ii <= 9:
                cr.move_to(ii * sdist + i * ldist, height)
                cr.line_to(ii * sdist + i * ldist, height - mark)
                ii += 1
        cr.move_to(i * ldist + 0.5, height / 2 + cr.text_extents("000")[3] / 2)
        cr.show_text(str(int(i * (ldist / scale))))
        i += 1
    cr.restore()

    # Draw vertical ruler
    cr.save()
    cr.translate(height, zero[1])
    cr.rotate(math.radians(90))

    cr.select_font_face("Courier", cairo.FONT_SLANT_NORMAL)
    cr.set_font_size(15)
    if cr.text_extents("000")[4] > ldist:
        cr.set_font_size(15 / ((cr.text_extents("000")[4] * 0.9) / ldist))

    i = 0
    while (i-1) * ldist <= length[1] * scale - sdist:
        cr.move_to(i * ldist, 0)
        cr.line_to(i * ldist, height)
        if sdist >= 3.5 and i * ldist <= length[1] * scale - sdist:
            ii = 1
            while ii <= 9:
                cr.move_to(ii * sdist + i * ldist, 0)
                cr.line_to(ii * sdist + i * ldist, mark)
                ii += 1
        cr.move_to(i * ldist + 0.5, height / 2 + cr.text_extents("000")[3] / 2)
        cr.show_text(str(int(i * (ldist / scale))))
        i += 1
    cr.stroke()
    cr.restore()
