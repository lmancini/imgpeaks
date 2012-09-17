uniform float blend;
uniform sampler2D texture1;
uniform sampler2D texture2;
varying vec4 color1;
varying vec4 color2;
void main(void)
{
    vec4 color = color1 * blend + color2 * (1.0-blend);
    gl_FragColor = color;
}
