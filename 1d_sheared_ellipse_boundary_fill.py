import sys
import math
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# --- SCALING & GRID SETUP ---
UNIT = 8 
WINDOW_SIZE = 800
CENTER = WINDOW_SIZE // 2 # Pixel mapping for logical (0,0)

# Virtual Grid: 0 = Background, 1 = Boundary (White), 2 = Fill (Green)
grid = [[0 for _ in range(WINDOW_SIZE)] for _ in range(WINDOW_SIZE)]

# --- HELPER FUNCTIONS ---

# Safely sets a pixel in our virtual memory grid
def setPixel(x, y, value):
    x, y = int(x), int(y)
    if 0 <= x < WINDOW_SIZE and 0 <= y < WINDOW_SIZE:
        grid[x][y] = value

# Renders text for our axis labels
def drawText(x, y, text):
    glRasterPos2f(x, y)
    for c in str(text):
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(c))

# --- AXES DRAWING ---
def drawAxes():
    glColor3f(0.4, 0.4, 0.4) # Gray axes
    glBegin(GL_LINES)
    glVertex2f(0.0, CENTER); glVertex2f(WINDOW_SIZE, CENTER) # X-axis
    glVertex2f(CENTER, 0.0); glVertex2f(CENTER, WINDOW_SIZE) # Y-axis
    glEnd()

    glColor3f(0.8, 0.8, 0.8)
    for i in range(-40, 41, 5):
        if i == 0: continue 
        screen_coord = CENTER + (i * UNIT)
        
        # X-axis ticks & labels
        glBegin(GL_LINES); glVertex2f(screen_coord, CENTER - 5.0); glVertex2f(screen_coord, CENTER + 5.0); glEnd()
        drawText(screen_coord - 8.0, CENTER - 18.0, str(i))

        # Y-axis ticks & labels
        glBegin(GL_LINES); glVertex2f(CENTER - 5.0, screen_coord); glVertex2f(CENTER + 5.0, screen_coord); glEnd()
        drawText(CENTER - 25.0, screen_coord - 4.0, str(i))
        
    # Label ends of axes
    drawText(WINDOW_SIZE - 20.0, CENTER + 10.0, "X")
    drawText(CENTER + 10.0, WINDOW_SIZE - 20.0, "Y")
    
    # Explicitly label the origin with a yellow point
    glColor3f(1.0, 1.0, 0.0); glPointSize(5.0)
    glBegin(GL_POINTS); glVertex2i(CENTER, CENTER); glEnd()
    drawText(CENTER + 5.0, CENTER + 5.0, "Origin (0,0)")

# --- SHAPE GENERATION & FILLING ---

# Bresenham's Line Algorithm: Draws a solid straight line between two points.
# Used here because shearing a mathematical curve stretches the pixels apart;
# Drawing lines connects the sheared points tightly to prevent the fill algorithm leaking out of gaps.
def drawBoundaryLine(x0, y0, x1, y1):
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    dx = abs(x1 - x0)
    sx = 1 if x0 < x1 else -1
    dy = -abs(y1 - y0)
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        setPixel(x0, y0, 1) # Mark as Boundary (1)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy

# Stack-based Boundary Fill Algorithm (iterative instead of recursive to avoid Python's call-stack limits).
# Fills region with green until it hits pixels with boundary_val (white) or already filled.
def boundaryFill(start_x, start_y, fill_val, boundary_val):
    start_x, start_y = int(start_x), int(start_y)
    
    # Pre-flight boundary and exit checks
    if not (0 <= start_x < WINDOW_SIZE and 0 <= start_y < WINDOW_SIZE): return
    if grid[start_x][start_y] == fill_val or grid[start_x][start_y] == boundary_val: return
    
    # Initialize the explicit python list simulating our stack
    stk = [(start_x, start_y)]
    while stk:
        # Standard Python list memory pop handles LIFO stack behavior
        px, py = stk.pop()
        
        # If pixel is NOT the fill color AND NOT the boundary color
        if grid[px][py] != fill_val and grid[px][py] != boundary_val:
            grid[px][py] = fill_val # Color it Green (2)
            
            # Optimized push: Only append unvisited, non-boundary neighbors to prevent massive queue explosion
            if px + 1 < WINDOW_SIZE and grid[px + 1][py] != fill_val and grid[px + 1][py] != boundary_val:
                stk.append((px + 1, py))
            if px - 1 >= 0 and grid[px - 1][py] != fill_val and grid[px - 1][py] != boundary_val:
                stk.append((px - 1, py))
            if py + 1 < WINDOW_SIZE and grid[px][py + 1] != fill_val and grid[px][py + 1] != boundary_val:
                stk.append((px, py + 1))
            if py - 1 >= 0 and grid[px][py - 1] != fill_val and grid[px][py - 1] != boundary_val:
                stk.append((px, py - 1))

# --- OPENGL PIPELINE ---

def init():
    glClearColor(0.1, 0.1, 0.1, 1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_SIZE, 0, WINDOW_SIZE)
    
    # 1. Generate Mathematical Ellipse Points
    rx, ry = 6.0, 5.0
    sheared_points = []
    
    for i in range(360):
        # Parametric equation for base ellipse
        theta = i * 3.14159 / 180.0
        orig_x = rx * math.cos(theta)
        orig_y = ry * math.sin(theta)
        
        # Translate to required center (-2, 2)
        tx = orig_x - 2.0
        ty = orig_y + 2.0
        
        # Apply Shear Matrix (Shx = 2, Shy = 2)
        sheared_x = tx + (2.0 * ty)
        sheared_y = (2.0 * tx) + ty
        
        # Convert to pixel coordinates and store
        sheared_points.append((CENTER + int(sheared_x * UNIT), CENTER + int(sheared_y * UNIT)))
        
    # 2. Connect points to form a solid boundary in the grid
    for i in range(len(sheared_points)):
        p1 = sheared_points[i]
        p2 = sheared_points[(i + 1) % len(sheared_points)]
        drawBoundaryLine(p1[0], p1[1], p2[0], p2[1])
        
    # 3. Execute Boundary Fill
    # Mathematical sheared center is (2, -2). We start the fill exactly here.
    seed_x = CENTER + (2 * UNIT)
    seed_y = CENTER + (-2 * UNIT)
    boundaryFill(seed_x, seed_y, 2, 1) # Fill with 2 (Green), stop at 1 (Boundary)

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    
    # Render the calculated grid to the screen
    glBegin(GL_POINTS)
    for i in range(WINDOW_SIZE):
        for j in range(WINDOW_SIZE):
            if grid[i][j] == 1:
                glColor3f(1.0, 1.0, 1.0) # 1 = Boundary (White)
                glVertex2i(i, j)
            elif grid[i][j] == 2:
                glColor3f(0.0, 1.0, 0.0) # 2 = Filled Interior (Green)
                glVertex2i(i, j)
    glEnd()
    
    # Draw the axes on top of the shape
    drawAxes()
    
    # Explicitly mark and label the new sheared center
    glColor3f(1.0, 0.0, 0.0) # Red dot
    glPointSize(5.0)
    glBegin(GL_POINTS)
    glVertex2i(CENTER + (2 * UNIT), CENTER + (-2 * UNIT))
    glEnd()
    drawText(CENTER + (2 * UNIT) + 5.0, CENTER + (-2 * UNIT) + 5.0, "Sheared Center (2,-2)")

    glutSwapBuffers()

# Application Entry Run Function
def main():
    glutInit(sys.argv)
    # Using GLUT_DOUBLE buffer configuration alongside GLUT_RGB
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WINDOW_SIZE, WINDOW_SIZE)
    # Binary string window title format is natively supported by pyglut binaries
    glutCreateWindow(b"Q1(D): Boundary Fill of Sheared Ellipse")
    
    init()
    glutDisplayFunc(display)
    glutMainLoop()

if __name__ == "__main__":
    main()
