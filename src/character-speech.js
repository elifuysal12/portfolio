/* A small textured lip mesh. The open-mouth render supplies the lip/teeth
   texture; the mesh compresses the mouth cavity and shapes vowels continuously.
   Outside this patch the original portrait is never redrawn or replaced. */
function createPortraitSpeechRig(canvas, source) {
  const size = [244, 172];
  let gl, program, openingUniform, widthUniform;
  let ready = false, failed = false, visible = 0;
  let opening = 0, width = 1, targetOpening = 0, targetWidth = 1;

  function shader(type, text) {
    const result = gl.createShader(type);
    gl.shaderSource(result, text);
    gl.compileShader(result);
    if (!gl.getShaderParameter(result, gl.COMPILE_STATUS)) throw new Error('Lip shader failed');
    return result;
  }

  function initialize() {
    if (ready) return;
    try {
      gl = canvas.getContext('webgl', {alpha:true, antialias:false, premultipliedAlpha:false, depth:false});
      if (!gl) { failed = true; canvas.dataset.rig='fallback'; return; }
      program = gl.createProgram();
      gl.attachShader(program, shader(gl.VERTEX_SHADER, `
        attribute vec2 point;
        varying vec2 sourcePoint;
        uniform float opening;
        uniform float mouthWidth;
        void main() {
          vec2 p = vec2(510.0, 450.0) + point * vec2(244.0, 172.0);
          sourcePoint = p;
          float across = 1.0 - smoothstep(58.0, 112.0, abs(p.x - 632.0));
          // Inner mouth collapses into a line; the lower lip keeps its volume.
          float jaw = p.y < 507.0 ? 0.0 : p.y < 528.0 ? p.y - 507.0
                    : 21.0 * (1.0 - smoothstep(528.0, 600.0, p.y));
          p.y -= (1.0 - opening) * jaw * across;
          float aroundLips = exp(-pow((sourcePoint.y - 515.0) / 40.0, 2.0));
          p.x += (p.x - 632.0) * (mouthWidth - 1.0) * aroundLips * across;
          vec2 position = (p - vec2(510.0, 450.0)) / vec2(244.0, 172.0);
          gl_Position = vec4(position.x * 2.0 - 1.0, 1.0 - position.y * 2.0, 0.0, 1.0);
        }
      `));
      gl.attachShader(program, shader(gl.FRAGMENT_SHADER, `
        precision mediump float;
        varying vec2 sourcePoint;
        uniform sampler2D portrait;
        void main() {
          vec4 color = texture2D(portrait, sourcePoint / 1254.0);
          float edge = length((sourcePoint - vec2(632.0, 533.0)) / vec2(117.0, 78.0));
          float feather = 1.0 - smoothstep(0.65, 1.0, edge);
          gl_FragColor = vec4(color.rgb, color.a * feather);
        }
      `));
      gl.linkProgram(program);
      if (!gl.getProgramParameter(program, gl.LINK_STATUS)) throw new Error('Lip program failed');
      gl.useProgram(program);
      const vertices = [], rows = 48, columns = 48;
      for (let y = 0; y < rows; y++) for (let x = 0; x < columns; x++) {
        const x0=x/columns, x1=(x+1)/columns, y0=y/rows, y1=(y+1)/rows;
        vertices.push(x0,y0, x0,y1, x1,y0, x1,y0, x0,y1, x1,y1);
      }
      gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
      gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertices), gl.STATIC_DRAW);
      const point = gl.getAttribLocation(program, 'point');
      gl.enableVertexAttribArray(point);
      gl.vertexAttribPointer(point, 2, gl.FLOAT, false, 0, 0);
      gl.bindTexture(gl.TEXTURE_2D, gl.createTexture());
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, source);
      openingUniform = gl.getUniformLocation(program, 'opening');
      widthUniform = gl.getUniformLocation(program, 'mouthWidth');
      gl.viewport(0, 0, size[0], size[1]);
      ready = true;
      canvas.dataset.rig = 'ready';
    } catch (_) {
      failed = true;
      canvas.style.opacity = '0';
      canvas.dataset.rig = 'fallback';
    }
  }

  source.addEventListener('load', initialize, {once:true});
  if (source.complete && source.naturalWidth) initialize();
  canvas.addEventListener('webglcontextlost', event => {
    event.preventDefault(); ready=false; canvas.style.opacity='0';
  });
  canvas.addEventListener('webglcontextrestored', () => { failed=false; initialize(); });

  return {
    cue(glyph) {
      const c = glyph.toLocaleLowerCase('tr');
      if (/[.!?…,;:—\s]/.test(c)) { targetOpening=0; targetWidth=1; }
      else if (/[mbp]/.test(c)) { targetOpening=0; targetWidth=.97; }
      else if (/[aâ]/.test(c)) { targetOpening=1.08; targetWidth=1.02; }
      else if (/[eê]/.test(c)) { targetOpening=.66; targetWidth=1.08; }
      else if (/[iıîy]/.test(c)) { targetOpening=.36; targetWidth=1.06; }
      else if (/[oö]/.test(c)) { targetOpening=.88; targetWidth=.80; }
      else if (/[uüûw]/.test(c)) { targetOpening=.56; targetWidth=.78; }
      else if (/[fv]/.test(c)) { targetOpening=.14; targetWidth=1; }
      else { targetOpening=Math.max(.18, targetOpening*.78); targetWidth+=(1-targetWidth)*.35; }
    },
    update(dt, speaking, reducedMotion) {
      if (!ready || failed) return;
      if (reducedMotion) {
        visible=opening=targetOpening=0; width=targetWidth=1;
        canvas.style.opacity='0'; return;
      }
      if (!speaking) { targetOpening=0; targetWidth=1; }
      // Lips close faster than they open; vowel widths blend more slowly.
      const close = targetOpening < opening;
      opening += (targetOpening-opening) * -Math.expm1(-dt/(close?38:65));
      width += (targetWidth-width) * -Math.expm1(-dt/85);
      visible += ((speaking?1:0)-visible) * -Math.expm1(-dt/(speaking?65:100));
      if (!speaking && visible < .01) {
        visible=0; canvas.style.opacity='0'; return;
      }
      gl.clear(gl.COLOR_BUFFER_BIT);
      gl.uniform1f(openingUniform, Math.max(.015, opening));
      gl.uniform1f(widthUniform, width);
      gl.drawArrays(gl.TRIANGLES, 0, 48*48*6);
      canvas.style.opacity=visible>.995?'1':visible.toFixed(3);
    }
  };
}
