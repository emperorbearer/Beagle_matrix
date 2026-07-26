<script>
  import { showText } from './api.js';

  let { onchanged } = $props();

  let text = $state('안녕하세요!');
  let color = $state('#ffcc00');
  let bg = $state('#000000');
  let speed = $state(40);
  let fontSize = $state(0);
  let busy = $state(false);
  let error = $state('');

  async function submit(e) {
    e.preventDefault();
    busy = true;
    error = '';
    try {
      await showText({ text, color, bg, speed: Number(speed), font_size: Number(fontSize) });
      onchanged?.();
    } catch (err) {
      error = String(err);
    } finally {
      busy = false;
    }
  }
</script>

<form onsubmit={submit}>
  <label>
    내용
    <input bind:value={text} maxlength="500" required placeholder="출력할 문자를 입력하세요" />
  </label>

  <div class="row">
    <label>
      글자색
      <input type="color" bind:value={color} />
    </label>
    <label>
      배경색
      <input type="color" bind:value={bg} />
    </label>
    <label>
      스크롤 속도 (px/s, 0 = 정지)
      <input type="number" bind:value={speed} min="0" max="500" />
    </label>
    <label>
      글자 크기 (0 = 자동)
      <input type="number" bind:value={fontSize} min="0" max="256" />
    </label>
  </div>

  <button disabled={busy}>매트릭스에 출력</button>
  {#if error}<p class="error">{error}</p>{/if}
</form>

<style>
  form {
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
  }

  .row {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
  }

  .error {
    color: #ff7b7b;
    font-size: 0.85rem;
  }
</style>
