uniform float blend;
uniform sampler2D texture1;
uniform sampler2D texture2;
uniform float npw;
uniform float nph;

varying vec4 color1;
varying vec4 color2;

void main ()
{
    vec4 v = gl_Vertex;
    float lx, ly;
    vec2 lookup;

    lx = (v.x + (npw / 2.0)) / npw;
    ly = (v.y + (nph / 2.0)) / nph;
    lookup = vec2(lx, ly);

    color1 = texture2D(texture1, lookup);
    color2 = texture2D(texture2, lookup);

    float z1 = color1.x * 20.0;
    float z2 = color2.x * 20.0;

    v.z = z1 * blend + z2 * (1.0-blend);

    gl_Position = gl_ModelViewProjectionMatrix * v;
}
