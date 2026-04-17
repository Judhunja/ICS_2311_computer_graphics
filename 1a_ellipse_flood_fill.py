import sys
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

UNIT = 15 
WINDOW_SIZE = 600
CENTER = WINDOW_SIZE // 2

# Virtual 2D grid acts as a canvas: 0 = Background, 1 = Boundary (Ellipse), 2 = Fill Color
grid = [[0 for _ in range(WINDOW_SIZE)] for _ in range(WINDOW_SIZE)]

# Safely sets a pixel value on the virtual grid if it's within window bounds
def setPixel(x, y, value):
    x, y = int(x), int(y)
    if 0 <= x < WINDOW_SIZE and 0 <= y < WINDOW_SIZE:
        grid[x][y] = value

def plotEllipsePoints(x, y):
    cx = CENTER + (-2 * UNIT)
    cy = CENTER + (2 * UNIT)
    
    setPixel(cx + x, cy + y, 1)
    setPixel(cx - x, cy + y, 1)
    setPixel(cx + x, cy - y, 1)
    setPixel(cx - x, cy - y, 1)

# Computes and plots the coordinates of the ellipse using the Midpoint Ellipse Algorithm.
# This algorithm traces the boundary of the shape without using any floating point multiplication in its core loop,
# making it highly efficient. We use this to draw a 'boundary' that our flood fill algorithm will later be trapped inside.
def computeMidpointEllipse():
    rx = 6 * UNIT
    ry = 5 * UNIT
    x = 0
    y = ry
    
    p1 = (ry * ry) - (rx * rx * ry) + (0.25 * rx * rx)
    dx = 2 * ry * ry * x
    dy = 2 * rx * rx * y
    
    while dx < dy:
        plotEllipsePoints(x, y)
        if p1 < 0:
            x += 1
            dx += (2 * ry * ry)
            p1 += dx + (ry * ry)
        else:
            x += 1
            y -= 1
            dx += (2 * ry * ry)
            dy -= (2 * rx * rx)
            p1 += dx - dy + (ry * ry)
            
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

# Flood Fill Algorithm implemented with an explicit Stack.
# Normally, Flood Fill uses recursion. However, Python has a strict limit on recursive depth (typically ~1000 calls).
# Since filling an ellipse will check thousands of pixels, recursion will crash python with a RecursionError.
# To solve this, we explicitly simulate a recursion stack using a standard python list `stk`.
# It starts at the seed coordinate (start_x, start_y) and replaces target_val with fill_val.
def floodFill(start_x, start_y, target_val, fill_val):
    start_x, start_y = int(start_x), int(start_y)
    
    # Initialize the stack with our starting seed pixel
    stk = [(start_x, start_y)]
    
    # Loop continuously while there are still pixels waiting to be evaluated
    while stk:
        # Pop the last added pixel from the list (LIFO behavior exactly replicates a recursion stack)
        px, py = stk.pop()
        
        # Guard against checking pixels completely off the screen
        if px < 0 or px >= WINDOW_SIZE or py < 0 or py >= WINDOW_SIZE:
            continue
        
        # If the pixel we pulled matches the blank background color we want to replace
        if grid[px][py] == target_val:
            # Color it with our fill color!
            grid[px][py] = fill_val
            
            # Queue up all 4 surrounding neighboring pixels to be checked on the next loop iterations
            # NOTE: this pushes duplicates to the stack which isn't efficient but guarantees coverage.
            stk.append((px + 1, py))
            stk.append((px - 1, py))
            stk.append((px, py + 1))
            stk.append((px, py - 1))

def drawText(x, y, text):
    glRasterPos2f(x, y)
    for c in str(text):
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(c))

def drawAxes():
    glColor3f(0.4, 0.4, 0.4)
    glBegin(GL_LINES)
    glVertex2f(0.0, CENTER); glVertex2f(WINDOW_SIZE, CENTER)
    glVertex2f(CENTER, 0.0); glVertex2f(CENTER, WINDOW_SIZE)
    glEnd()

    glColor3f(0.8, 0.8, 0.8)
    for i in range(-15, 16):
        if i == 0: continue 
        sc = CENTER + (i * UNIT)
        glBegin(GL_LINES); glVertex2f(sc, CENTER - 5.0); glVertex2f(sc, CENTER + 5.0); glEnd()
        drawText(sc - 5.0, CENTER - 18.0, str(i))
        glBegin(GL_LINES); glVertex2f(CENTER - 5.0, sc); glVertex2f(CENTER + 5.0, sc); glEnd()
        drawText(CENTER - 20.0, sc - 4.0, str(i))
        
    drawText(WINDOW_SIZE - 20.0, CENTER + 10.0, "X")
    drawText(CENTER + 10.0, WINDOW_SIZE - 20.0, "Y")
    
    glColor3f(1.0, 1.0, 0.0); glPointSize(4.0)
    glBegin(GL_POINTS); glVertex2i(CENTER, CENTER); glEnd()
    drawText(CENTER + 5.0, CENTER + 5.0, "(0,0)")

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    glBegin(GL_POINTS)
    for i in range(WINDOW_SIZE):
        for j in range(WINDOW_SIZE):
            if grid[i][j] == 1:
                glColor3f(1.0, 1.0, 1.0)
                glVertex2i(i, j)
            elif grid[i][j] == 2:
                glColor3f(0.0, 1.0, 1.0)
                glVertex2i(i, j)
    glEnd()
    
    drawAxes() # Draw axes on top of fill
    
    # Label Center
    glColor3f(1.0, 0.0, 0.0); glPointSize(4.0)
    glBegin(GL_POINTS); glVertex2i(CENTER + (-2 * UNIT), CENTER + (2 * UNIT)); glEnd()
    drawText(CENTER + (-2 * UNIT) + 5, CENTER + (2 * UNIT) + 5, "Center (-2,2)")
    
    glutSwapBuffers()

def init():
    glClearColor(0.1, 0.1, 0.1, 1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_SIZE, 0, WINDOW_SIZE)
    computeMidpointEllipse()
    floodFill(CENTER + (-2 * UNIT), CENTER + (2 * UNIT), 0, 2)

# Main entry point for the python PyOpenGL application
def main():
    glutInit(sys.argv)
    
    # GLUT_DOUBLE enables double buffering to eliminate screen tearing or flickering. it requires glutSwapBuffers()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WINDOW_SIZE, WINDOW_SIZE)
    # The 'b' prefix for byte-strings is often required by PyOpenGL to safely pass strings to underlying C-libraries.
    glutCreateWindow(b"Q1A: Flood Fill Cyan")
    
    init()
    glutDisplayFunc(display)
    
    # Begins the infinite rendering loop of GLUT
    glutMainLoop()

if __name__ == "__main__":
    main()
