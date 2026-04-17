/*
 * FILE: q1d_sheared_boundary_fill.cpp
 * DESCRIPTION: Applies a 2x2 Shear to an ellipse centered at (-2,2).
 * Then uses a Boundary Fill algorithm to fill the shape with Green.
 * Includes strictly scaled and labeled coordinate axes.
 */

#include <GL/glut.h>
#include <vector>
#include <stack>
#include <cmath>
#include <string>

// --- SCALING & GRID SETUP ---
// We use a smaller unit scale because shearing stretches the shape dramatically.
const int UNIT = 8; 
const int WINDOW_SIZE = 800;
const int CENTER = WINDOW_SIZE / 2; // Pixel mapping for logical (0,0)

// Virtual Grid: 0 = Background, 1 = Boundary (White), 2 = Fill (Green)
std::vector<std::vector<int>> grid(WINDOW_SIZE, std::vector<int>(WINDOW_SIZE, 0));

// --- HELPER FUNCTIONS ---

// Safely sets a pixel in our virtual memory grid
void setPixel(int x, int y, int value) {
    if (x >= 0 && x < WINDOW_SIZE && y >= 0 && y < WINDOW_SIZE) {
        grid[x][y] = value;
    }
}

// Renders text for our axis labels
void drawText(float x, float y, std::string text) {
    glRasterPos2f(x, y);
    for (char c : text) glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, c);
}

// --- AXES DRAWING ---
// Draws the X and Y axes, ticks, and numerical scaling
void drawAxes() {
    glColor3f(0.4f, 0.4f, 0.4f); // Gray axes
    glBegin(GL_LINES);
    glVertex2f(0.0f, CENTER); glVertex2f(WINDOW_SIZE, CENTER); // X-axis
    glVertex2f(CENTER, 0.0f); glVertex2f(CENTER, WINDOW_SIZE); // Y-axis
    glEnd();

    glColor3f(0.8f, 0.8f, 0.8f);
    // Loop to draw scale ticks. We step by 5 to avoid text overlap.
    for (int i = -40; i <= 40; i += 5) {
        if (i == 0) continue; 
        float screen_coord = CENTER + (i * UNIT);
        
        // X-axis ticks & labels
        glBegin(GL_LINES); glVertex2f(screen_coord, CENTER - 5.0f); glVertex2f(screen_coord, CENTER + 5.0f); glEnd();
        drawText(screen_coord - 8.0f, CENTER - 18.0f, std::to_string(i));

        // Y-axis ticks & labels
        glBegin(GL_LINES); glVertex2f(CENTER - 5.0f, screen_coord); glVertex2f(CENTER + 5.0f, screen_coord); glEnd();
        drawText(CENTER - 25.0f, screen_coord - 4.0f, std::to_string(i));
    }
    
    // Label ends of axes
    drawText(WINDOW_SIZE - 20.0f, CENTER + 10.0f, "X");
    drawText(CENTER + 10.0f, WINDOW_SIZE - 20.0f, "Y");
    
    // Explicitly label origin
    glColor3f(1.0f, 1.0f, 0.0f); glPointSize(5.0f);
    glBegin(GL_POINTS); glVertex2i(CENTER, CENTER); glEnd();
    drawText(CENTER + 5.0f, CENTER + 5.0f, "Origin (0,0)");
}

// --- SHAPE GENERATION & FILLING ---

// Bresenham's Line Algorithm: We need this because shearing stretches pixels apart.
// This connects the sheared points with a solid line so the boundary fill doesn't leak.
void drawBoundaryLine(int x0, int y0, int x1, int y1) {
    int dx = std::abs(x1 - x0), sx = x0 < x1 ? 1 : -1;
    int dy = -std::abs(y1 - y0), sy = y0 < y1 ? 1 : -1;
    int err = dx + dy, e2;

    while (true) {
        setPixel(x0, y0, 1); // Mark as Boundary (1)
        if (x0 == x1 && y0 == y1) break;
        e2 = 2 * err;
        if (e2 >= dy) { err += dy; x0 += sx; }
        if (e2 <= dx) { err += dx; y0 += sy; }
    }
}

// Boundary Fill Algorithm (Iterative, Stack-Based to prevent crashes)
// It stops when it encounters the boundary_val (1).
void boundaryFill(int start_x, int start_y, int fill_val, int boundary_val) {
    std::stack<std::pair<int, int>> stk;
    stk.push({start_x, start_y});
    
    while (!stk.empty()) {
        auto current = stk.top(); stk.pop();
        int px = current.first, py = current.second;
        
        // Bounds checking
        if (px < 0 || px >= WINDOW_SIZE || py < 0 || py >= WINDOW_SIZE) continue;
        
        // If pixel is NOT the fill color AND NOT the boundary color
        if (grid[px][py] != fill_val && grid[px][py] != boundary_val) {
            grid[px][py] = fill_val; // Color it Green (2)
            
            // Push 4-way neighbors to the stack
            stk.push({px + 1, py}); stk.push({px - 1, py});
            stk.push({px, py + 1}); stk.push({px, py - 1});
        }
    }
}

// --- OPENGL PIPELINE ---

void init() {
    glClearColor(0.1f, 0.1f, 0.1f, 1.0f);
    glMatrixMode(GL_PROJECTION); glLoadIdentity();
    gluOrtho2D(0, WINDOW_SIZE, 0, WINDOW_SIZE);
    
    // 1. Generate Mathematical Ellipse Points
    float rx = 6.0f, ry = 5.0f;
    std::vector<std::pair<int, int>> sheared_points;
    
    for (int i = 0; i < 360; i++) {
        // Parametric equation for base ellipse
        float theta = i * 3.14159f / 180.0f;
        float orig_x = rx * cos(theta);
        float orig_y = ry * sin(theta);
        
        // Translate to required center (-2, 2)
        float tx = orig_x - 2.0f;
        float ty = orig_y + 2.0f;
        
        // Apply Shear Matrix (Shx = 2, Shy = 2)
        float sheared_x = tx + (2.0f * ty);
        float sheared_y = (2.0f * tx) + ty;
        
        // Convert to pixel coordinates and store
        sheared_points.push_back({CENTER + (int)(sheared_x * UNIT), CENTER + (int)(sheared_y * UNIT)});
    }
    
    // 2. Connect points to form a solid boundary in the grid
    for (size_t i = 0; i < sheared_points.size(); i++) {
        auto p1 = sheared_points[i];
        auto p2 = sheared_points[(i + 1) % sheared_points.size()]; // Wrap around to close shape
        drawBoundaryLine(p1.first, p1.second, p2.first, p2.second);
    }
    
    // 3. Execute Boundary Fill
    // Mathematical sheared center is (2, -2). We start the fill exactly here.
    int seed_x = CENTER + (2 * UNIT);
    int seed_y = CENTER + (-2 * UNIT);
    boundaryFill(seed_x, seed_y, 2, 1); // Fill with 2 (Green), stop at 1 (Boundary)
}

void display() {
    glClear(GL_COLOR_BUFFER_BIT);
    
    // Render the calculated grid to the screen
    glBegin(GL_POINTS);
    for (int i = 0; i < WINDOW_SIZE; i++) {
        for (int j = 0; j < WINDOW_SIZE; j++) {
            if (grid[i][j] == 1) {
                glColor3f(1.0f, 1.0f, 1.0f); // 1 = Boundary (White)
                glVertex2i(i, j);
            } else if (grid[i][j] == 2) {
                glColor3f(0.0f, 1.0f, 0.0f); // 2 = Filled Interior (Green)
                glVertex2i(i, j);
            }
        }
    }
    glEnd();
    
    // Draw the axes on top of the shape
    drawAxes();
    
    // Explicitly mark and label the new sheared center
    glColor3f(1.0f, 0.0f, 0.0f); // Red dot
    glPointSize(5.0f);
    glBegin(GL_POINTS);
    glVertex2i(CENTER + (2 * UNIT), CENTER + (-2 * UNIT));
    glEnd();
    drawText(CENTER + (2 * UNIT) + 5.0f, CENTER + (-2 * UNIT) + 5.0f, "Sheared Center (2,-2)");

    glutSwapBuffers();
}

int main(int argc, char** argv) {
    glutInit(&argc, argv);
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB);
    glutInitWindowSize(WINDOW_SIZE, WINDOW_SIZE);
    glutCreateWindow("Q1(D): Boundary Fill of Sheared Ellipse");
    init();
    glutDisplayFunc(display);
    glutMainLoop();
    return 0;
}
