/* 서비스 워커: 브라우저 뒤에서 도는 작은 프로그램. 앱 파일을 폰에 저장해 두고(캐시) 인터넷이 없어도 열어 준다.
   방식: 캐시에 있으면 즉시 그걸 보여주고, 동시에 인터넷에서 새 버전을 받아 캐시를 갱신 → 다음에 열 때 반영. */
const CACHE = 'zh-typing-v1';
const FILES = ['./', './index.html', './manifest.json', './icons/icon-192.png', './icons/icon-512.png'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET' || url.origin !== location.origin) return;   // GitHub API, CDN 등 외부 요청은 건드리지 않음
  e.respondWith(caches.match(e.request, { ignoreSearch: true }).then(cached => {
    const fresh = fetch(e.request).then(res => { if (res && res.ok) caches.open(CACHE).then(c => c.put(e.request, res.clone())); return res; }).catch(() => cached);
    return cached || fresh;
  }));
});
