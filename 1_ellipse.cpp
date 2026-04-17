/*
 * FILE: q1_base_ellipse.cpp
 * DESCRIPTION: Draws the base ellipse using the Midpoint Algorithm.
 * Center explicitly set to (-2, 2), rx = 6, ry = 5.
 * Includes strictly scaled and labeled X and Y coordinate axes.
 */

#include <GL/glut.h>
#include <string>

const int UNIT = 15; // 1 logical unit = 15 pixels
const int WINDOW_SIZE = 600;
const int CENTER = WINDOW_SIZE / 2;

// Helper function to render text labels for coordinates
void drawText(float x, float y, std::string text) {
    glRasterPos2f(x, y);
    for (char c : text) {
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, c);
    }
}

// Function to draw and strictly label the X and Y axes with numerical scaling
void drawAxes() {
    glColor3f(0.4f, 0.4f, 0.4f); // Gray axes
    glBegin(GL_LINES);
    glVertex2f(0.0f, CENTER); glVertex2f(WINDOW_SIZE, CENTER); // X-axis
    glVertex2f(CENTER, 0.0f); glVertex2f(CENTER, WINDOW_SIZE); // Y-axis
    glEnd();

    glColor3f(0.8f, 0.8f, 0.8f);
    // Draw numerical ticks and coordinate labels based on our UNIT scale
    for (int i = -15; i <= 15; i++) {
        if (i == 0) continue; 
        float screen_coord = CENTER + (i * UNIT);
        
        // X-axis scaling
        glBegin(GL_LINES); glVertex2f(screen_coord, CENTER - 5.0f); glVertex2f(screen_coord, CENTER + 5.0f); glEnd();
        drawText(screen_coord - 5.0f, CENTER - 18.0f, std::to_string(i));

        // Y-axis scaling
        glBegin(GL_LINES); glVertex2f(CENTER - 5.0f, screen_coord); glVertex2f(CENTER + 5.0f, screen_coord); glEnd();
        drawText(CENTER - 20.0f, screen_coord - 4.0f, std::to_string(i));
    }
    
    // Explicitly label the axes and origin (x,y)
    drawText(WINDOW_SIZE - 20.0f, CENTER + 10.0f, "X");
    drawText(CENTER + 10.0f, WINDOW_SIZE - 20.0f, "Y");
    
    glColor3f(1.0f, 1.0f, 0.0f); // Yellow dot for origin
    glPointSize(4.0f);
    glBegin(GL_POINTS);
    glVertex2i(CENTER, CENTER);
    glEnd();
    drawText(CENTER + 5.0f, CENTER + 5.0f, "(0,0)");
}

// Plots 4 symmetric points around the specified center (-2, 2)
void plotEllipsePoints(int x, int y) {
    int cx = CENTER + (-2 * UNIT); // Center X = -2
    int cy = CENTER + (2 * UNIT);  // Center Y = 2
    
    glBegin(GL_POINTS);
    glVertex2i(cx + x, cy + y);
    glVertex2i(cx - x, cy + y);
    glVertex2i(cx + x, cy - y);
    glVertex2i(cx - x, cy - y);
    glEnd();
}

void display() {
    glClear(GL_COLOR_BUFFER_BIT);
    
    // Draw the explicitly labeled and scaled axes first
    drawAxes();
    
    // Draw the Ellipse
    glColor3f(1.0f, 1.0f, 1.0f); // White Ellipse
    
    float rx = 6 * UNIT, ry = 5 * UNIT;
    float x = 0, y = ry;
    
    // REGION 1: Top and bottom curves where the slope magnitude is less than 1 (dx < dy).
    // Initial decision parameter for region 1
    float p1 = (ry * ry) - (rx * rx * ry) + (0.25 * rx * rx);
    // Partial derivatives used to update the decision parameter efficiently
    float dx = 2 * ry * ry * x, dy = 2 * rx * rx * y;
    
    while (dx < dy) {
        plotEllipsePoints(x, y);
        if (p1 < 0) {
            x++; dx += (2 * ry * ry); p1 += dx + (ry * ry);
        } else {
            x++; y--; dx += (2 * ry * ry); dy -= (2 * rx * rx);
            p1 += dx - dy + (ry * ry);
        }
    }
            
    // REGION 2: Left and right curves where the slope magnitude is greater than 1 (dx >= dy).
    // Initial decision parameter for region 2 based on the last point of region 1
    float p2 = (ry * ry) * ((x + 0.5) * (x + 0.5)) + (rx * rx) * ((y - 1) * (y - 1)) - (rx * rx * ry * ry);
    while (y >= 0) {
        plotEllipsePoints(x, y);
        if (p2 > 0) {
            y--; dy -= (2 * rx * rx); p2 += (rx * rx) - dy;
        } else {
            y--; x++; dx += (2 * ry * ry); dy -= (2 * rx * rx);
            p2 += dx - dy + (rx * rx);
        }
    }
    
    // Explicitly label the center of the ellipse (-2, 2)
    glColor3f(1.0f, 0.0f, 0.0f); // Red dot for ellipse center
    glBegin(GL_POINTS);
    glVertex2i(CENTER + (-2 * UNIT), CENTER + (2 * UNIT));
    glEnd();
    drawText(CENTER + (-2 * UNIT) + 5.0f, CENTER + (2 * UNIT) + 5.0f, "Center (-2,2)");

    glutSwapBuffers();
}

void init() {
    glClearColor(0.1f, 0.1f, 0.1f, 1.0f);
    glMatrixMode(GL_PROJECTION); glLoadIdentity();
    gluOrtho2D(0, WINDOW_SIZE, 0, WINDOW_SIZE);
}

int main(int argc, char** argv) {
    glutInit(&argc, argv);
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB);
    glutInitWindowSize(WINDOW_SIZE, WINDOW_SIZE);
    glutCreateWindow("Question 1:Ellipse with center (-2, 2)");
    init();
    glutDisplayFunc(display);
    glutMainLoop();
    return 0;
}
