/*
Group 15
Joshua Muimi - SCT211-0244/2023
Jude Hunja - SCT211-0309/2023
*/

#include <GL/glut.h>
#include <vector>
#include <stack>
#include <cmath>
#include <string>

const int UNIT = 8; 
const int WINDOW_SIZE = 800;
const int CENTER = WINDOW_SIZE / 2;

// Virtual 2D grid acts as a canvas: 0 = Background, 1 = Boundary (Line), 2 = Fill Color
std::vector<std::vector<int>> grid(WINDOW_SIZE, std::vector<int>(WINDOW_SIZE, 0));

// Safely sets a pixel value on the virtual grid if it's within window bounds
void setPixel(int x, int y, int value) {
    if (x >= 0 && x < WINDOW_SIZE && y >= 0 && y < WINDOW_SIZE) grid[x][y] = value;
}

// Bresenham's Line Algorithm: Draws a solid straight line between two points.
// Used to connect sheared curve points into a closed polygon to prevent gap leaks during filling.
void drawBoundaryLine(int x0, int y0, int x1, int y1) {
    int dx = std::abs(x1 - x0), sx = x0 < x1 ? 1 : -1;
    int dy = -std::abs(y1 - y0), sy = y0 < y1 ? 1 : -1;
    int err = dx + dy, e2;
    while (true) {
        setPixel(x0, y0, 1);
        if (x0 == x1 && y0 == y1) break;
        e2 = 2 * err;
        if (e2 >= dy) { err += dy; x0 += sx; }
        if (e2 <= dx) { err += dx; y0 += sy; }
    }
}

// Stack-based Boundary Fill Algorithm (avoids recursive stack overflow)
// Fills region with fill_val until it encounters pixels with boundary_val or already filled ones.
void boundaryFill(int start_x, int start_y, int fill_val, int boundary_val) {
    std::stack<std::pair<int, int>> stk;
    stk.push({start_x, start_y});
    while (!stk.empty()) {
        auto current = stk.top(); stk.pop();
        int px = current.first, py = current.second;
        if (px < 0 || px >= WINDOW_SIZE || py < 0 || py >= WINDOW_SIZE) continue;
        if (grid[px][py] != fill_val && grid[px][py] != boundary_val) {
            grid[px][py] = fill_val;
            stk.push({px + 1, py}); stk.push({px - 1, py});
            stk.push({px, py + 1}); stk.push({px, py - 1});
        }
    }
}

void drawText(float x, float y, std::string text) {
    glRasterPos2f(x, y);
    for (char c : text) glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, c);
}

void drawAxes() {
    glColor3f(0.4f, 0.4f, 0.4f);
    glBegin(GL_LINES);
    glVertex2f(0.0f, CENTER); glVertex2f(WINDOW_SIZE, CENTER);
    glVertex2f(CENTER, 0.0f); glVertex2f(CENTER, WINDOW_SIZE);
    glEnd();

    glColor3f(0.8f, 0.8f, 0.8f);
    // Step by 5 units to prevent text overlap at this smaller UNIT scale
    for (int i = -40; i <= 40; i += 5) {
        if (i == 0) continue; 
        float sc = CENTER + (i * UNIT);
        glBegin(GL_LINES); glVertex2f(sc, CENTER - 5.0f); glVertex2f(sc, CENTER + 5.0f); glEnd();
        drawText(sc - 8.0f, CENTER - 18.0f, std::to_string(i));
        glBegin(GL_LINES); glVertex2f(CENTER - 5.0f, sc); glVertex2f(CENTER + 5.0f, sc); glEnd();
        drawText(CENTER - 25.0f, sc - 4.0f, std::to_string(i));
    }
    drawText(WINDOW_SIZE - 20.0f, CENTER + 10.0f, "X");
    drawText(CENTER + 10.0f, WINDOW_SIZE - 20.0f, "Y");
    
    glColor3f(1.0f, 1.0f, 0.0f); glPointSize(4.0f);
    glBegin(GL_POINTS); glVertex2i(CENTER, CENTER); glEnd();
    drawText(CENTER + 5.0f, CENTER + 5.0f, "(0,0)");
}

void display() {
    glClear(GL_COLOR_BUFFER_BIT);
    glBegin(GL_POINTS);
    for (int i = 0; i < WINDOW_SIZE; i++) {
        for (int j = 0; j < WINDOW_SIZE; j++) {
            if (grid[i][j] == 1) { glColor3f(1.0f, 1.0f, 1.0f); glVertex2i(i, j); } 
            else if (grid[i][j] == 2) { glColor3f(0.0f, 1.0f, 1.0f); glVertex2i(i, j); } // Green Fill
        }
    }
    glEnd();
    
    drawAxes(); // Draw axes over fill
    
    // Explicitly label new sheared center
    glColor3f(1.0f, 0.0f, 0.0f); glPointSize(5.0f);
    glBegin(GL_POINTS); glVertex2i(CENTER + (2 * UNIT), CENTER + (-2 * UNIT)); glEnd();
    drawText(CENTER + (2 * UNIT) + 5, CENTER + (-2 * UNIT) + 5, "New Center (2,-2)");

    glutSwapBuffers();
}

void init() {
    glClearColor(0.1f, 0.1f, 0.1f, 1.0f);
    glMatrixMode(GL_PROJECTION); glLoadIdentity();
    gluOrtho2D(0, WINDOW_SIZE, 0, WINDOW_SIZE);
    
    float rx = 6.0f, ry = 5.0f;
    std::vector<std::pair<int, int>> sheared_points;
    for (int i = 0; i < 360; i++) {
        float theta = i * 3.14159f / 180.0f;
        float tx = (rx * cos(theta)) - 2.0f;
        float ty = (ry * sin(theta)) + 2.0f;
        // Apply Shear Transformation Matrix (Shx = 2.0, Shy = 2.0)
        float sx = tx + (2.0f * ty);
        float sy = (2.0f * tx) + ty;
        sheared_points.push_back({CENTER + (int)(sx * UNIT), CENTER + (int)(sy * UNIT)});
    }
    
    for (size_t i = 0; i < sheared_points.size(); i++) {
        auto p1 = sheared_points[i];
        auto p2 = sheared_points[(i + 1) % sheared_points.size()];
        drawBoundaryLine(p1.first, p1.second, p2.first, p2.second);
    }
    // New center calculated mathematically: x' = 2, y' = -2
    boundaryFill(CENTER + (2 * UNIT), CENTER + (-2 * UNIT), 2, 1);
}

int main(int argc, char** argv) {
    glutInit(&argc, argv);
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB);
    glutInitWindowSize(WINDOW_SIZE, WINDOW_SIZE);
    glutCreateWindow("Q1BD: Sheared Boundary Fill");
    init();
    glutDisplayFunc(display);
    glutMainLoop();
    return 0;
}
