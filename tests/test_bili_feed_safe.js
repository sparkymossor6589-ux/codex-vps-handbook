// Project-held test code; MIT scope: ../LICENSE_SCOPE.md.
// Synthetic fixtures only. Run with: node tests/test_bili_feed_safe.js
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const code = fs.readFileSync(path.join(__dirname, '../src/bili_feed_safe.js'), 'utf8');
let networkCalls = 0;
function run(body, route = '/x/v2/feed/index', headers = {}) {
  const results = [];
  const blockedNetwork = () => { networkCalls++; throw new Error('Unexpected network call'); };
  vm.runInNewContext(code, {
    $request: { url: 'https://app.bilibili.com' + route },
    $response: { body, headers },
    $done: value => results.push(value),
    $httpClient: { get: blockedNetwork, post: blockedNetwork },
    $task: { fetch: blockedNetwork }, fetch: blockedNetwork
  }, { timeout: 1000 });
  assert.equal(results.length, 1, 'complete exactly once');
  return JSON.parse(JSON.stringify(results[0]));
}
const ordinary = [
  { goto: 'av', title: '普通视频🙂' }, { goto: 'vertical_av', id: 2 },
  { goto: 'live', id: 3 }, { card_type: 'unknown', is_ad: 0 }
];
const normal = JSON.stringify({ code: 0, data: { items: ordinary, cursor: { next: 17 } } }, null, 2);
assert.deepEqual(run(normal), {}, 'no ads: preserve original response bytes');

for (const route of ['/x/v2/feed/index', '/x/v2/feed/index/story', '/x/v2/feed/index/relate/story']) {
  const mixed = JSON.stringify({ code: 0, data: { items: ordinary.concat([
    { is_ad: 1 }, { is_ad: true }, { is_ad: '1' }, { goto: 'ad' },
    { card_type: 'cm_banner' }, { card_goto: 'ad_web' }
  ]), cursor: { next: 17 }, unknown: { keep: true } } });
  const out = run(mixed, route, { 'Content-Length': '99', 'content-encoding': 'gzip',
    'Transfer-Encoding': 'chunked', ETag: 'old', 'Content-MD5': 'old', 'Content-Type': 'application/json', 'X-Test': 'keep' });
  const result = JSON.parse(out.body);
  assert.deepEqual(result.data.items, ordinary);
  assert.deepEqual(result.data.cursor, { next: 17 });
  assert.deepEqual(result.data.unknown, { keep: true });
  assert.deepEqual(out.headers, { 'Content-Type': 'application/json', 'X-Test': 'keep' });
}
const splash = run(JSON.stringify({ code: 0, data: { show: [1], preload: [2], event_list: [3],
  account: { keep: true }, unknown: ['keep'] } }), '/x/v2/splash/list');
assert.deepEqual(JSON.parse(splash.body).data, { account: { keep: true }, unknown: ['keep'] });

for (const body of ['{broken', '', undefined, new Uint8Array([1, 2]), 'x'.repeat(2097153),
  JSON.stringify({ code: -1, data: { items: [{ is_ad: true }] } }), 'null']) {
  assert.deepEqual(run(body), {}, 'malformed, binary, oversize or error: pass through');
}
assert.deepEqual(run(JSON.stringify({ code: 0, data: { items: [{ is_ad: true }] } }),
  '/x/player/playurl'), {}, 'playback route untouched');
assert.equal(networkCalls, 0);
console.log('PASS: normal content, three feed routes, splash, headers, fail-open cases, playback, zero network');
