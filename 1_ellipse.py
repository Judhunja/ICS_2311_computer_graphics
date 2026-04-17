import sys
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

UNIT = 15 # 1 logical unit = 15 pixels
WINDOW_SIZE = 600
CENTER = WINDOW_SIZE // 2

# Helper function to render text labels for coordinates
def drawText(x, y, text):
    glRasterPos2f(x, y)
    for c in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(c))

# Function to draw and strictly label the X and Y axes with numerical scaling
def drawAxes():
    glColor3f(0.4, 0.4, 0.4) # Gray axes
    glBegin(GL_LINES)
    glVertex2f(0.0, CENTER); glVertex2f(WINDOW_SIZE, CENTER) # X-axis
    glVertex2f(CENTER, 0.0); glVertex2f(CENTER, WINDOW_SIZE) # Y-axis
    glEnd()

    glColor3f(0.8, 0.8, 0.8)
    # Draw numerical ticks and coordinate labels based on our UNIT scale
    for i in range(-15, 16):
        if i == 0: continue 
        screen_coord = CENTER + (i * UNIT)
        
        # X-axis scaling
        glBegin(GL_LINES); glVertex2f(screen_coord, CENTER - 5.0); glVertex2f(screen_coord, CENTER + 5.0); glEnd()
        drawText(screen_coord - 5.0, CENTER - 18.0, str(i))

        # Y-axis scaling
        glBegin(GL_LINES); glVertex2f(CENTER - 5.0, screen_coord); glVertex2f(CENTER + 5.0, screen_coord); glEnd()
        drawText(CENTER - 20.0, screen_coord - 4.0, str(i))
    
    # Explicitly label the axes and origin (x,y)
    drawText(WINDOW_SIZE - 20.0, CENTER + 10.0, "X")
    drawText(CENTER + 10.0, WINDOW_SIZE - 20.0, "Y")
    
    glColor3f(1.0, 1.0, 0.0) # Yellow dot for origin
    glPointSize(4.0)
    glBegin(GL_POINTS)
    glVertex2i(CENTER, CENTER)
    glEnd()
    drawText(CENTER + 5.0, CENTER + 5.0, "(0,0)")

# Plots 4 symmetric points around the specified center (-2, 2)
def plotEllipsePoints(x, y):
    cx = CENTER + (-2 * UNIT) # Center X = -2
    cy = CENTER + (2 * UNIT)  # Center Y = 2
    
    glBegin(GL_POINTS)
    glVertex2i(int(cx + x), int(cy + y))
    glVertex2i(int(cx - x), int(cy + y))
    glVertex2i(int(cx + x), int(cy - y))
    glVertex2i(int(cx - x), int(cy - y))
    glEnd()

# The display function is called by the GLUT run loop every time the screen needs to be refreshed.
def display():
    # Clear the color frame buffer to give us a blank slate (using clear color set in init)
    glClear(GL_COLOR_BUFFER_BIT)
    
    # Draw the explicitly labeled and scaled axes first
    drawAxes()
    
    # Set current drawing color to White for the Ellipse boundary
    glColor3f(1.0, 1.0, 1.0)
    
    # Ellipse radii scaled by our display UNIT
    rx = 6 * UNIT
    ry = 5 * UNIT
    x = 0
    y = ry
    
    # REGION 1: Top and bottom curves where the slope magnitude is less than 1 (dx < dy).
    # Initial decision parameter for region 1
    p1 = (ry * ry) - (rx * rx * ry) + (0.25 * rx * rx)
    # Partial derivatives used to update the decision parameter efficiently
    dx = 2 * ry * ry * x
    dy = 2 * rx * rx * y
    
    while dx < dy:
        plotEllipsePoints(x, y)
        # If p1 < 0, the mapped midpoint is inside the ellipse. We only increment x.
        if p1 < 0:
            x += 1
            dx += (2 * ry * ry)
            p1 += dx + (ry * ry)
        # If the midpoint is outside or on the boundary, we step down in y as we step forward in x.
        else:
            x += 1
            y -= 1
            dx += (2 * ry * ry)
            dy -= (2 * rx * rx)
            p1 += dx - dy + (ry * ry)
            
    # REGION 2: Left and right curves where the slope magnitude is greater than 1 (dx >= dy).
    # Initial decision parameter for region 2 based on the last point of region 1
    p2 = (ry * ry) * ((x + 0.5) * (x + 0.5)) + (rx * rx) * ((y - 1) * (y - 1)) - (rx * rx * ry * ry)
    while y >= 0:
        plotEllipsePoints(x, y)
        if p2 > 0:
            y -= 1
            dy -= (2 * rx * rx)
            p2 += (rx * rx) - dy
        else:
            y -= 1
            x += 1
            dx += (2 * ry * ry)
            dy -= (2 * rx * rx)
            p2 += dx - dy + (rx * rx)
    
    # Explicitly label the center of the ellipse (-2, 2)
    glColor3f(1.0, 0.0, 0.0) # Red dot for ellipse center
    glBegin(GL_POINTS)
    glVertex2i(CENTER + (-2 * UNIT), CENTER + (2 * UNIT))
    glEnd()
    drawText(CENTER + (-2 * UNIT) + 5.0, CENTER + (2 * UNIT) + 5.0, "Center (-2,2)")

    # glutSwapBuffers swaps the hidden buffer where drawing occurs with the visible buffer on screen, 
    # ensuring smooth rendering without flickering.
    glutSwapBuffers()

# Initialize OpenGL context, viewing frustum, and application environment parameters
def init():
    # Set the background clear color to a dark gray (Red: 0.1, Green: 0.1, Blue: 0.1, Alpha: 1.0)
    glClearColor(0.1, 0.1, 0.1, 1.0)
    
    # We edit the Projection Matrix because we're setting up orthogonal 2D coordinates (not 3D perspective)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    
    # Defines a 2-D orthographic projection matrix. Bottom-Left is (0,0), Top-Right is (WINDOW, WINDOW)
    gluOrtho2D(0, WINDOW_SIZE, 0, WINDOW_SIZE)

# Main entry point for the python PyOpenGL application
def main():
    # Initialize the GLUT library
    glutInit(sys.argv)
    
    # Request a double buffered (GLUT_DOUBLE) window with an RGB color mode (GLUT_RGB)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WINDOW_SIZE, WINDOW_SIZE)
    # Bytes string 'b"..."' is often required in PyOpenGL C-bindings for Window Titles
    glutCreateWindow(b"Question 1:Ellipse with center (-2, 2)")
    
    init()
    
    # Register the display callback function that GLUT will run every render frame
    glutDisplayFunc(display)
    
    # Enters the GLUT event processing loop; it will continuously call display() rendering the graphic.
    glutMainLoop()

if __name__ == "__main__":
    main()
