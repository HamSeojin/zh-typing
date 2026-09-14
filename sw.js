/* 서비스 워커: 브라우저 뒤에서 도는 작은 프로그램. 앱 파일을 폰에 저장해 두고(캐시) 인터넷이 없어도 열어 준다.
   방식(네트워크 우선): 인터넷이 되면 항상 최신 파일을 받아 보여주고 캐시를 갱신, 안 되면 저장본을 보여줌.
   → 새 버전을 올리면 다음 열 때 바로 반영되고, 오프라인에서도 열린다. */
const CACHE = 'zh-typing-v4';
const FILES = ['./', './index.html', './manifest.json', './icons/icon-192.png', './icons/icon-512.png'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET' || url.origin !== location.origin) return;   // GitHub API, CDN 등 외부 요청은 건드리지 않음
  // 소리·영상처럼 조각(Range)으로 나눠 받는 요청은 손대지 않는다 — 서비스 워커가 통째로 된 응답을 주면 재생기가 멈춘다
  if (e.request.headers.has('range') || e.request.destination === 'audio' || e.request.destination === 'video') return;
  // data/ 아래 파일은 이름에 내용 해시가 붙어 있어 내용이 바뀌면 이름도 바뀜 → 한 번 받으면 캐시에서 바로 꺼내 씀(캐시 우선)
  if (/\/data\//.test(url.pathname) && !url.pathname.endsWith('index.json')){
    e.respondWith(caches.match(e.request).then(hit => hit || fetch(e.request).then(res => { if (res && res.ok) caches.open(CACHE).then(c => c.put(e.request, res.clone())); return res; })));
    return;
  }
  e.respondWith(
    fetch(e.request, { cache: 'no-cache' })
      .then(res => { if (res && res.ok) caches.open(CACHE).then(c => c.put(e.request, res.clone())); return res; })
      .catch(() => caches.match(e.request, { ignoreSearch: true }))
  );
});
// 앱이 현재 쓰는 data/ 파일 목록을 보내 주면, 캐시에 남은 옛 버전 data/ 파일을 지운다 (해시가 바뀔 때마다 쌓이지 않게)
self.addEventListener('message', e => {
  if (!e.data || e.data.type !== 'keep-data') return;
  const keep = new Set(e.data.urls.map(u => new URL(u, location.href).href));
  caches.open(CACHE).then(c => c.keys().then(reqs => reqs.forEach(r => { if (/\/data\//.test(new URL(r.url).pathname) && !keep.has(r.url)) c.delete(r); })));
});
