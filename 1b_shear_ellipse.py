import sys
import math
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# --- SCALING & GRID SETUP ---
UNIT = 8 
WINDOW_SIZE = 800
CENTER = WINDOW_SIZE // 2 # Pixel mapping for logical (0,0)

# Virtual 2D grid acts as a canvas: 0 = Background, 1 = Boundary (Line), 2 = Fill Color
grid = [[0] * WINDOW_SIZE for _ in range(WINDOW_SIZE)]

# Safely sets a pixel value on the virtual grid if it's within window bounds
def setPixel(x, y, value):
    x, y = int(x), int(y)
    if 0 <= x < WINDOW_SIZE and 0 <= y < WINDOW_SIZE:
        grid[x][y] = value

# Bresenham's Line Algorithm: Draws a solid straight line between two points.
# Used to connect sheared curve points into a closed polygon to prevent gap leaks during filling.
def drawBoundaryLine(x0, y0, x1, y1):
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    dx = abs(x1 - x0)
    sx = 1 if x0 < x1 else -1
    dy = -abs(y1 - y0)
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        setPixel(x0, y0, 1)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy

# Stack-based Boundary Fill Algorithm (avoids recursive stack overflow limits of Python).
# It continually fills the area with 'fill_val' until it hits a pixel that is either already filled, or the 'boundary_val'.
def boundaryFill(start_x, start_y, fill_val, boundary_val):
    start_x, start_y = int(start_x), int(start_y)
    
    # Pre-flight boundary and exit check
    if not (0 <= start_x < WINDOW_SIZE and 0 <= start_y < WINDOW_SIZE): return
    if grid[start_x][start_y] == fill_val or grid[start_x][start_y] == boundary_val: return
    
    # Initialize the simulated recursion stack
    stk = [(start_x, start_y)]
    # Fast inner loop
    while stk:
        # Pop from the end of the python list strictly simulating LIFO stack behavior
        px, py = stk.pop()
        
        if grid[px][py] != fill_val and grid[px][py] != boundary_val:
            grid[px][py] = fill_val
            
            # Check neighbors before appending to significantly optimize stack size in python
            if px + 1 < WINDOW_SIZE and grid[px + 1][py] != fill_val and grid[px + 1][py] != boundary_val:
                stk.append((px + 1, py))
            if px - 1 >= 0 and grid[px - 1][py] != fill_val and grid[px - 1][py] != boundary_val:
                stk.append((px - 1, py))
            if py + 1 < WINDOW_SIZE and grid[px][py + 1] != fill_val and grid[px][py + 1] != boundary_val:
                stk.append((px, py + 1))
            if py - 1 >= 0 and grid[px][py - 1] != fill_val and grid[px][py - 1] != boundary_val:
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
    # Step by 5 units to prevent text overlap at this smaller UNIT scale
    for i in range(-40, 41, 5):
        if i == 0: continue 
        sc = CENTER + (i * UNIT)
        glBegin(GL_LINES); glVertex2f(sc, CENTER - 5.0); glVertex2f(sc, CENTER + 5.0); glEnd()
        drawText(sc - 8.0, CENTER - 18.0, str(i))
        glBegin(GL_LINES); glVertex2f(CENTER - 5.0, sc); glVertex2f(CENTER + 5.0, sc); glEnd()
        drawText(CENTER - 25.0, sc - 4.0, str(i))
        
    drawText(WINDOW_SIZE - 20.0, CENTER + 10.0, "X")
    drawText(CENTER + 10.0, WINDOW_SIZE - 20.0, "Y")
    
    glColor3f(1.0, 1.0, 0.0); glPointSize(4.0)
    glBegin(GL_POINTS); glVertex2i(CENTER, CENTER); glEnd()
    drawText(CENTER + 5.0, CENTER + 5.0, "(0,0)")

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    glBegin(GL_POINTS)
    # Using python builtins efficiently
    for i in range(WINDOW_SIZE):
        for j in range(WINDOW_SIZE):
            val = grid[i][j]
            if val == 1:
                glColor3f(1.0, 1.0, 1.0)
                glVertex2i(i, j)
            elif val == 2:
                glColor3f(0.0, 1.0, 1.0) # Cyan Fill
                glVertex2i(i, j)
    glEnd()
    
    drawAxes() # Draw axes over fill
    
    # Explicitly label new sheared center
    glColor3f(1.0, 0.0, 0.0); glPointSize(5.0)
    glBegin(GL_POINTS); glVertex2i(CENTER + (2 * UNIT), CENTER + (-2 * UNIT)); glEnd()
    drawText(CENTER + (2 * UNIT) + 5, CENTER + (-2 * UNIT) + 5, "New Center (2,-2)")

    glutSwapBuffers()

# Initializes the projection matrices, viewports, and handles all shape mathematics before rendering.
def init():
    # Set the background clear color to dark gray
    glClearColor(0.1, 0.1, 0.1, 1.0)
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_SIZE, 0, WINDOW_SIZE)
    
    # Pre-calculated mathematical parameters
    rx, ry = 6.0, 5.0
    sheared_points = []
    
    # Precompute trig values parametrically for a full 360 degrees
    for i in range(360):
        # Convert degree to Radian (required by math.cos and math.sin)
        theta = i * 3.14159 / 180.0
        
        # Original coordinates are translated to our specific center requirement (-2, 2)
        tx = (rx * math.cos(theta)) - 2.0
        ty = (ry * math.sin(theta)) - (-2.0)
        
        # Apply the Shear Transformation Matrix. 
        # Here we shear x by a factor of 2.0 against y, and y by a factor of 2.0 against x.
        sx = tx + (2.0 * ty)
        sy = (2.0 * tx) + ty
        
        # Convert Logical mathematical coordinates to physical Matrix/Pixel Coordinates (ints)
        sheared_points.append((CENTER + int(sx * UNIT), CENTER + int(sy * UNIT)))
        
    # We iterate over our calculated points and strictly connect them using Bresenham lines 
    # to guarantee there are zero gaps that the fill algorithm could leak out of.
    for i in range(len(sheared_points)):
        p1 = sheared_points[i]
        p2 = sheared_points[(i + 1) % len(sheared_points)]
        drawBoundaryLine(p1[0], p1[1], p2[0], p2[1])
        
    # The new center mathematically calculated after shearing the original (-2, 2). x' = 2, y' = -2
    boundaryFill(CENTER + (2 * UNIT), CENTER + (-2 * UNIT), 2, 1)

# Application Entry Point
def main():
    glutInit(sys.argv)
    # Enable double buffered window to eliminate flickering.
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WINDOW_SIZE, WINDOW_SIZE)
    # 'b' ensures it's interpreted as a strictly ASCII byte-string by PyOpenGL internals.
    glutCreateWindow(b"Q1BD: Sheared Boundary Fill")
    
    init()
    glutDisplayFunc(display)
    glutMainLoop()

if __name__ == "__main__":
    main()
