#!/usr/bin/env python

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo
from PIL import Image
from numpy import array

import pygame
from pygame.locals import *

class ImageTexture(object):
    def __init__(self, image):
        self.width = image.size[0]
        self.height = image.size[1]
        self.buffer = image.convert("RGBA").tostring("raw", "RGBA", 0, -1)

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

vs_src = """
uniform sampler2D texture;

void main () {
    vec4 v = vec4(gl_Vertex);
    v.z = texture2D(texture, vec2((v.x + 50) / 100, (v.y + 50) / 100)) * 20;
    gl_Position = gl_ModelViewProjectionMatrix * v;
}
"""

fs_src = """
void main(void)
{
    gl_FragColor = vec4(0.5, 0.5, 0.5, 0);
}
"""

class Program(object):
    def __init__(self, vs, fs):
        self._program = glCreateProgram()
        glAttachShader(self._program, vs._shader)
        glAttachShader(self._program, fs._shader)
        glLinkProgram(self._program)

    def use(self):
        try:
            glUseProgram(self._program)
        except OpenGL.error.GLError:
            print glGetProgramInfoLog(self._program)
            raise

    def done(self):
        glUseProgram(0)

    def getUniform(self, name):
        return glGetUniformLocation(self._program, name)

it = None
program = None
height_texture = None
point_lattice = None

def initGL():
    im = Image.open(sys.argv[1])
    im = im.convert('L')

    global it
    it = ImageTexture(im)

    vs = VertexShader(vs_src)
    fs = FragmentShader(fs_src)

    global program
    program = Program(vs, fs)
    global height_texture
    height_texture = program.getUniform("texture")

    # Create array of points
    global point_lattice
    point_lattice = vbo.VBO(
        array([(x-50, y-50, 0) for x in xrange(100) for y in xrange(100)], 'f')
    )

    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(90,1,0.01,1000)
    gluLookAt(0,0,-100,0,0,0,0,1,0)

    glClearColor(0.3, 0.3, 0.3, 1.0)

angle = 0

def paintGL():
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    global point_lattice, program, height_texture, it, angle

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glRotated(angle, 0, 1, 0)
    angle += 0.01

    program.use()
    try:
        glUniform1i(height_texture, 0)        
        glActiveTexture(GL_TEXTURE0 + 0);
        glBindTexture(GL_TEXTURE_2D, it._tex_id);
        point_lattice.bind()
        try:
            glEnableClientState(GL_VERTEX_ARRAY)
            glVertexPointerf(point_lattice)
            glDrawArrays(GL_POINTS, 0, 100*100)
        finally:
            glDisableClientState(GL_VERTEX_ARRAY)
            point_lattice.unbind()
    finally:
        program.done()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print "Usage: imgpeaks.py <image>"
        sys.exit(1)

    pygame.init() 
    pygame.display.set_mode((800, 600), pygame.OPENGL|pygame.DOUBLEBUF)

    initGL()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        paintGL()

        pygame.display.flip()
