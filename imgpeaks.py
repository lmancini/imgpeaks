#!/usr/bin/env python

import math
import ctypes
from contextlib import contextmanager

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo
from PIL import Image

import pygame

class ImageTexture(object):
    def __init__(self, image):
        self.width = image.size[0]
        self.height = image.size[1]
        self.buffer = image.convert("RGBA").tobytes("raw", "RGBA", 0, -1)

        self._tex_id = glGenTextures(1)

        self.bind()
        glTexImage2D(GL_TEXTURE_2D, 0, 4, self.width, self.height,
                     0, GL_RGBA, GL_UNSIGNED_BYTE, self.buffer);
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR);

    def bind(self):
        glBindTexture(GL_TEXTURE_2D, self._tex_id)

class Shader(object):
    type = None

    def __init__(self, source):
        self._shader = glCreateShader(self.type)
        # glShaderSource actually expects a list of strings...
        if isinstance(source, basestring):
            source = [source]
        glShaderSource(self._shader, source)
        glCompileShader(self._shader)

        result = glGetShaderiv(self._shader, GL_COMPILE_STATUS)

        if result != 1:
            log = glGetShaderInfoLog(self._shader)
            print "Shader compile failed\nShader compilation Log:\n"+log
            raise Exception()

class VertexShader(Shader):
    type = GL_VERTEX_SHADER

class FragmentShader(Shader):
    type = GL_FRAGMENT_SHADER

class Program(object):
    def __init__(self, vs, fs):
        self._program = glCreateProgram()
        glAttachShader(self._program, vs._shader)
        glAttachShader(self._program, fs._shader)
        glLinkProgram(self._program)

    @contextmanager
    def in_use(self):
        try:
            try:
                glUseProgram(self._program)
            except OpenGL.error.GLError:
                print glGetProgramInfoLog(self._program)
                raise
            yield
        finally:
            glUseProgram(0)

    def setUniform1i(self, name, value):
        u = glGetUniformLocation(self._program, name)
        glUniform1i(u, value)

    def setUniform1f(self, name, value):
        u = glGetUniformLocation(self._program, name)
        glUniform1f(u, value)

it1 = it2 = None
program = None
point_lattice = None
points = None

def initGL():
    im = Image.open(sys.argv[1])
    im = im.convert('L')
    global it1
    it1 = ImageTexture(im)

    im = Image.open(sys.argv[2])
    im = im.convert('L')
    global it2
    it2 = ImageTexture(im)

    vs = VertexShader(open("peaks.vs").read())
    fs = FragmentShader(open("peaks.fs").read())

    global program
    program = Program(vs, fs)

    # Create array of points
    global point_lattice, points
    points = (ctypes.c_float * 2 * 100 * 100)()
    for x in xrange(100):
        for y in xrange(100):
            points[x][y][0] = (x - 50)
            points[x][y][1] = (y - 50)
    point_lattice = vbo.VBO(points)

    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(90,1,0.01,1000)
    gluLookAt(0,0,100,0,0,0,0,1,0)

    glClearColor(0.3, 0.3, 0.3, 1.0)

    glEnableClientState(GL_VERTEX_ARRAY)

angle = 0.0
anglex = 0.0
angley = 0.0

def paintGL(elapsed):

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    global point_lattice, points, program, it1, it2
    global angle, anglex, angley

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glRotated(anglex, 1, 0, 0)
    glRotated(angley, 0, 1, 0)

    # 90 deg/s
    angle += (elapsed * 360.0) / 4000.0
    blend = (math.sin(math.radians(angle)) + 1.0) / 2.0

    with program.in_use():
        program.setUniform1f("blend", blend)
        program.setUniform1f("npw", float(len(points)))
        program.setUniform1f("nph", float(len(points[0])))

        glActiveTexture(GL_TEXTURE0 + 0)
        it1.bind()
        program.setUniform1i("texture1", 0)

        glActiveTexture(GL_TEXTURE0 + 1)
        it2.bind()
        program.setUniform1i("texture2", 1)

        with point_lattice:
            glVertexPointerf(point_lattice)
            glDrawArrays(GL_POINTS, 0, 100*100)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print "Usage: imgpeaks.py <image1> <image2>"
        sys.exit(1)

    pygame.init()
    pygame.display.set_mode((800, 600), pygame.OPENGL|pygame.DOUBLEBUF)

    initGL()

    then = pygame.time.get_ticks()

    running = True
    mdown = False
    mpos = (0, 0)
    while running:
        now = pygame.time.get_ticks()
        elapsed = now - then
        then = now

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
                mdown = True
                mpos = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                mdown = False
            elif mdown and event.type == pygame.MOUSEMOTION:
                dx = event.pos[0] - mpos[0]
                dy = event.pos[1] - mpos[1]
                anglex += dy
                angley -= dx
                mpos = event.pos

        paintGL(elapsed)

        pygame.display.flip()
        pygame.time.wait(0)
