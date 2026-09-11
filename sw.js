/* 서비스 워커: 브라우저 뒤에서 도는 작은 프로그램. 앱 파일을 폰에 저장해 두고(캐시) 인터넷이 없어도 열어 준다.
   방식(네트워크 우선): 인터넷이 되면 항상 최신 파일을 받아 보여주고 캐시를 갱신, 안 되면 저장본을 보여줌.
   → 새 버전을 올리면 다음 열 때 바로 반영되고, 오프라인에서도 열린다. */
const CACHE = 'zh-typing-v2';
const FILES = ['./', './index.html', './manifest.json', './icons/icon-192.png', './icons/icon-512.png'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET' || url.origin !== location.origin) return;   // GitHub API, CDN 등 외부 요청은 건드리지 않음
  e.respondWith(
    fetch(e.request, { cache: 'no-cache' })
      .then(res => { if (res && res.ok) caches.open(CACHE).then(c => c.put(e.request, res.clone())); return res; })
      .catch(() => caches.match(e.request, { ignoreSearch: true }))
  );
});
