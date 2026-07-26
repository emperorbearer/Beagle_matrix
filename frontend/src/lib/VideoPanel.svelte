<script>
  import { listVideos, playVideo, uploadVideo } from './api.js';

  let { onchanged } = $props();

  let videos = $state([]);
  let loop = $state(true);
  let busy = $state(false);
  let error = $state('');

  async function refresh() {
    try {
      videos = (await listVideos()).videos;
    } catch (err) {
      error = String(err);
    }
  }

  async function onUpload(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    busy = true;
    error = '';
    try {
      const { name } = await uploadVideo(file);
      await refresh();
      await play(name);
    } catch (err) {
      error = String(err);
    } finally {
      busy = false;
      e.target.value = '';
    }
  }

  async function play(name) {
    error = '';
    try {
      await playVideo(name, loop);
      onchanged?.();
    } catch (err) {
      error = String(err);
    }
  }

  $effect(() => {
    refresh();
  });
</script>

<div class="panel">
  <label class="upload">
    영상 업로드 (mp4, webm, gif …) — 업로드하면 바로 재생됩니다
    <input type="file" accept="video/*,.gif" onchange={onUpload} disabled={busy} />
  </label>

  <label class="loop">
    <input type="checkbox" bind:checked={loop} style="width:auto" />
    반복 재생
  </label>

  {#if videos.length}
    <ul>
      {#each videos as name (name)}
        <li>
          <span>{name}</span>
          <button class="secondary" onclick={() => play(name)}>재생</button>
        </li>
      {/each}
    </ul>
  {:else}
    <p class="empty">업로드된 영상이 없습니다.</p>
  {/if}

  {#if error}<p class="error">{error}</p>{/if}
</div>

<style>
  .panel {
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
  }

  .loop {
    flex-direction: row;
    align-items: center;
    gap: 0.4rem;
  }

  ul {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
  }

  li {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #1b1e27;
    border-radius: 8px;
    padding: 0.4rem 0.7rem;
  }

  .empty {
    color: #9aa1b2;
    font-size: 0.9rem;
  }

  .error {
    color: #ff7b7b;
    font-size: 0.85rem;
  }
</style>
