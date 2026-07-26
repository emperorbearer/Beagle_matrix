<script>
  import Preview from './lib/Preview.svelte';
  import TextPanel from './lib/TextPanel.svelte';
  import VideoPanel from './lib/VideoPanel.svelte';
  import { getStatus, stopDisplay } from './lib/api.js';

  let tab = $state('text');
  let status = $state({ mode: 'off', detail: {} });

  async function refreshStatus() {
    try {
      status = await getStatus();
    } catch {
      // 백엔드가 아직 안 떠 있으면 무시
    }
  }

  async function stop() {
    await stopDisplay();
    await refreshStatus();
  }

  $effect(() => {
    refreshStatus();
    const t = setInterval(refreshStatus, 3000);
    return () => clearInterval(t);
  });
</script>

<main>
  <header>
    <h1>🐶 Beagle Matrix</h1>
    <div class="status">
      상태: <strong>{status.mode}</strong>
      {#if status.mode !== 'off'}
        <button class="secondary" onclick={stop}>끄기</button>
      {/if}
    </div>
  </header>

  <Preview />

  <nav>
    <button class:active={tab === 'text'} class="secondary" onclick={() => (tab = 'text')}>
      문자
    </button>
    <button class:active={tab === 'video'} class="secondary" onclick={() => (tab = 'video')}>
      영상
    </button>
  </nav>

  {#if tab === 'text'}
    <TextPanel onchanged={refreshStatus} />
  {:else}
    <VideoPanel onchanged={refreshStatus} />
  {/if}
</main>

<style>
  main {
    max-width: 720px;
    margin: 0 auto;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  h1 {
    font-size: 1.3rem;
    margin: 0;
  }

  .status {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    color: #9aa1b2;
    font-size: 0.9rem;
  }

  nav {
    display: flex;
    gap: 0.5rem;
  }

  nav button.active {
    background: #2f6fed;
  }
</style>
