// glsl_master.frag
uniform float idx;
uniform float hue_idx;
uniform vec2 res;

out vec4 fragColor;

// HSV to RGB conversion
vec3 hsv2rgb(vec3 c) {
    vec4 K = vec4(1.0, 2.0/3.0, 1.0/3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

void main() {
    vec2 uv = vUV.st;
    float ramp = 0.0;
    int shape_idx = int(idx);
    if (shape_idx == 0) ramp = uv.x;
    else if (shape_idx == 1) ramp = uv.y;
    else if (shape_idx == 2) ramp = length(uv - 0.5) * 2.0;
    else if (shape_idx == 3) ramp = fract(length(uv - 0.5) * 10.0);
    else if (shape_idx == 4) ramp = (uv.x + uv.y) * 0.5;
    else if (shape_idx == 5) ramp = abs(fract(uv.x * 2.0) * 2.0 - 1.0);
    else if (shape_idx == 6) ramp = abs(fract(uv.y * 2.0) * 2.0 - 1.0);
    else if (shape_idx == 7) ramp = abs(sin(uv.x * 20.0));
    else if (shape_idx == 8) ramp = fract(uv.x * 5.0);
    else if (shape_idx == 9) ramp = fract(uv.y * 5.0);
    else if (shape_idx == 10) ramp = mod(floor(uv.x * 8.0) + floor(uv.y * 8.0), 2.0);
    else if (shape_idx == 11) ramp = 0.5 + 0.5 * sin(uv.x * 10.0);
    else if (shape_idx == 12) ramp = 0.5 + 0.5 * cos(uv.y * 10.0);
    else if (shape_idx == 13) {
        float a = atan(uv.y - 0.5, uv.x - 0.5);
        float r = length(uv-0.5);
        ramp = fract((a + r * 10.0) / 6.2831);
    }
    else if (shape_idx == 14) ramp = step(0.5, fract(atan(uv.y - 0.5, uv.x - 0.5) * 8.0 / 6.2831));
    else if (shape_idx == 15) ramp = fract(length(uv - 0.5) * 20.0);
    else if (shape_idx == 16) ramp = smoothstep(0.2, 0.8, uv.x * uv.y);
    else if (shape_idx == 17) ramp = mod(floor(uv.x * 10.0), 2.0);
    else if (shape_idx == 18) ramp = mod(floor(uv.y * 10.0), 2.0);
    else if (shape_idx == 19) ramp = fract((uv.x * uv.y) * 5.0);
    else if (shape_idx == 20) ramp = pow(uv.x, 2.0);
    else if (shape_idx == 21) ramp = pow(uv.y, 2.0);
    else if (shape_idx == 22) ramp = abs(uv.x - 0.5) + abs(uv.y - 0.4);
    else if (shape_idx == 23) ramp = fract((uv.x + uv.y) * 5.0);
    else if (shape_idx == 24) ramp = fract((uv.x - uv.y) * 5.0);
    else if (shape_idx == 25) ramp = step(0.5, fract(uv.x * uv.y * 10.0));
    else if (shape_idx == 26) ramp = fract(sin(uv.x * 10.0 + uv.y * 10.0));
    else if (shape_idx == 27) ramp = length(uv - 0.5);
    else if (shape_idx == 28) ramp = atan(uv.y - 0.5, uv.x - 0.5)/3.14159;
    else if (shape_idx == 29) ramp = fract(sin((uv.x + uv.y) * 20.0));
    else if (shape_idx == 30) ramp = step(0.5, fract(uv.x * uv.y * 30.0));
    else if (shape_idx == 31) ramp = fract(fract(uv.x * 10.0) * fract(uv.y * 10.0));
    else if (shape_idx == 33) { // white
        fragColor = vec4(1.0, 1.0, 1.0, 1.0);
        return;
      }
    else if (shape_idx == 33) { // white
        fragColor = vec4(1.0, 1.0, 1.0, 1.0);
        return;
    }
    else if (shape_idx == 34) { // black
        fragColor = vec4(0.0, 0.0, 0.0, 1.0);
        return;
    }
    else if (shape_idx == 35) { // uv
        fragColor = vec4(0.5, 0.0, 1.0, 1.0);
        return;
    }

    // Hue remap
    // vec3 hsv = vec3(fract(hue_idx + ramp), 1.0, 1.0);
    // vec3 rgb = hsv2rgb(hsv);
    vec3 hsv = vec3(fract(ramp), 1.0, 1.0);

    // fragColor = vec4(rgb, 1.0);
    fragColor = vec4(vec3(ramp), 1.0);
}
