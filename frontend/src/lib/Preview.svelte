<script>
  import { getConfig, previewSocket } from './api.js';

  let canvas = $state();
  let dims = $state({ width: 128, height: 64 });
  let connected = $state(false);

  $effect(() => {
    let ws;
    let closed = false;

    async function connect() {
      try {
        dims = await getConfig();
      } catch {
        // 기본값 사용
      }
      if (closed) return;
      const ctx = canvas.getContext('2d');
      const image = ctx.createImageData(dims.width, dims.height);

      ws = previewSocket();
      ws.binaryType = 'arraybuffer';
      ws.onopen = () => (connected = true);
      ws.onmessage = (ev) => {
        const rgb = new Uint8Array(ev.data);
        const px = image.data;
        for (let i = 0, j = 0; i < rgb.length; i += 3, j += 4) {
          px[j] = rgb[i];
          px[j + 1] = rgb[i + 1];
          px[j + 2] = rgb[i + 2];
          px[j + 3] = 255;
        }
        ctx.putImageData(image, 0, 0);
      };
      ws.onclose = () => {
        connected = false;
        if (!closed) setTimeout(connect, 2000);
      };
    }

    connect();
    return () => {
      closed = true;
      ws?.close();
    };
  });
</script>

<div class="preview">
  <canvas bind:this={canvas} width={dims.width} height={dims.height}></canvas>
  <span class="badge" class:on={connected}>
    {connected ? `LIVE ${dims.width}×${dims.height}` : '연결 중…'}
  </span>
</div>

<style>
  .preview {
    position: relative;
    background: #000;
    border: 1px solid #333846;
    border-radius: 10px;
    padding: 10px;
  }

  canvas {
    display: block;
    width: 100%;
    image-rendering: pixelated;
  }

  .badge {
    position: absolute;
    top: 0.6rem;
    right: 0.7rem;
    font-size: 0.7rem;
    color: #9aa1b2;
    background: rgba(0, 0, 0, 0.6);
    padding: 0.15rem 0.5rem;
    border-radius: 999px;
  }

  .badge.on {
    color: #5dd97c;
  }
</style>
