uniform float blend;
uniform sampler2D texture1;
uniform sampler2D texture2;
uniform int width;
uniform int height;

varying vec4 color1;
varying vec4 color2;

void main () {
    vec4 v = vec4(gl_Vertex);

    float lx = (v.x + (width/2.0)) / width;
    float ly = (v.y + (height/2.0)) / height;
    vec2 lookup = vec2(lx, ly);

    color1 = texture2D(texture1, lookup);
    color2 = texture2D(texture2, lookup);

    float h1 = color1.x * 20.0;
    float h2 = color2.x * 20.0;

    v.z = h1 * blend + h2 * (1-blend);

    gl_Position = gl_ModelViewProjectionMatrix * v;
}