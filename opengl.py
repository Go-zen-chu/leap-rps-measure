#!/usr/bin/env python
# -*- coding: utf-8 -*-

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys

class OpenGLWindow(object):
    """
    Window that animates hand position
    """
    stack = None
    view_degree = 80
    view_pos = (0,300,300)

    def __init__(self, title=b"opengl", width=800, height=600):
        if type(title) != bytes:
            return Exception("title has to be bytes of char")
        self.title = title
        self.width = width
        self.height = height
        glutInit()
        glutInitDisplayMode(GLUT_RGB | GLUT_SINGLE | GLUT_DEPTH)
        glutInitWindowSize(self.width, self.height)
        glutInitWindowPosition(100, 100)
        glutCreateWindow(title)      # show window
        glutDisplayFunc(self.display)         # draw callback function
        glutReshapeFunc(self.reshape)         # resize callback function
        self.init_window(width, height)

    def set_data_stack(self, stack):
        self.stack = stack

    def init_window(self, width, height):
        """ initialize """
        glClearColor(0.0, 0.0, 0.0, 1.0) # black
        glEnable(GL_DEPTH_TEST) # enable shading

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        # set perspective
        gluPerspective(self.view_degree, float(width)/float(height), 0.1, 100.0)
        # set camera
        gluLookAt(self.view_pos[0], self.view_pos[1], self.view_pos[2], 0, 0, 0, 0, 1, 0)

    def start_window(self):
        # run window loop
        glutMainLoop()

    def draw_axis(self):
        axis_len = 200
        glLineWidth(5)
        # 一旦 off にしないと色がなくなる
        glDisable(GL_LIGHTING)
        glBegin(GL_LINES)
        glColor3f(1.0, 0.0, 0.0) # x, red
        glVertex3f(-axis_len, 0.0, 0.0)
        glVertex3f(axis_len, 0.0, 0.0)
        glColor3f(0.0, 1.0, 0.0) # y, green
        glVertex3f(0.0, axis_len, 0.0)
        glVertex3f(0.0, -axis_len, 0.0)
        glColor3f(0.0, 0.0, 1.0) # z, blue
        glVertex3f(0.0, 0.0 , -axis_len)
        glVertex3f(0.0, 0.0, axis_len)
        glEnd()
        glEnable(GL_LIGHTING);

    def draw_sphere(self, center_vec=(10,0,10)):
        rad = 5
        glPushMatrix()
        glTranslated(center_vec[0],center_vec[1],center_vec[2])
        glutWireSphere(rad, 30, 30) # rad, resolution
        glPopMatrix()

    def display(self):
        """ display """
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        # enable lighting to show object
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        ##set camera
        gluLookAt(self.view_pos[0], self.view_pos[1], self.view_pos[2], 0, 0, 0, 0, 1, 0)
        self.draw_axis()
        if self.stack != None:
            if self.stack.empty() == False:
                try:
                    center_vec = self.stack.get()
                    self.draw_sphere(center_vec)
                except:
                    print("stack is empty")
        glFlush()  # enforce OpenGL command
        glutPostRedisplay() # for animation, call display again

    def reshape(self, width, height):
        """callback function resize window"""
        print("reshape called")
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.view_degree, float(width)/float(height), 0.1, 500.0)
