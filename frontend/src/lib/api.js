async function json(res) {
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`${res.status}: ${body}`);
  }
  return res.json();
}

export const getConfig = () => fetch('/api/config').then(json);
export const getStatus = () => fetch('/api/status').then(json);
export const listVideos = () => fetch('/api/videos').then(json);

export const showText = (payload) =>
  fetch('/api/display/text', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }).then(json);

export const playVideo = (name, loop) =>
  fetch('/api/display/video', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, loop }),
  }).then(json);

export const stopDisplay = () => fetch('/api/display/stop', { method: 'POST' }).then(json);

export const uploadVideo = (file) => {
  const form = new FormData();
  form.append('file', file);
  return fetch('/api/videos', { method: 'POST', body: form }).then(json);
};

export function previewSocket() {
  const proto = location.protocol === 'https:' ? 'wss' : 'ws';
  return new WebSocket(`${proto}://${location.host}/api/ws/preview`);
}
