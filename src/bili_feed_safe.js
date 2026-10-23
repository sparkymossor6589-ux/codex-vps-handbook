// Local r25 synchronous filter core; private diagnostic wrappers omitted.
// Project-held rights: MIT; see ../CONTRIBUTIONS.md and ../LICENSE_SCOPE.md.
// Synchronous response-only filtering. No requests, cache, settings, URL rewriting
// or protobuf decoding; unrecognized/error responses retain the original bytes.
(function () {
  var done = {};
  try {
    var path = /^https?:\/\/(?:app\.bilibili\.com|app\.biliapi\.(?:net|com))(?::443)?([^?#]*)/.exec(String($request.url || ''));
    var raw = $response && $response.body;
    if (!path || typeof raw !== 'string' || !raw || raw.length > 2097152) { $done({}); return; }
    var obj = JSON.parse(raw), changed = false, route = path[1];
    if (!obj || obj.code !== 0 || !obj.data || typeof obj.data !== 'object') { $done({}); return; }
    function ad(item) {
      return item && typeof item === 'object' && (
        item.is_ad === true || item.is_ad === 1 || item.is_ad === '1' ||
        item.is_ad_loc === true || item.is_ad_loc === 1 ||
        item.ad_info && typeof item.ad_info === 'object' && Object.keys(item.ad_info).length > 0 ||
        item.ad_info_v2 && typeof item.ad_info_v2 === 'object' && Object.keys(item.ad_info_v2).length > 0 ||
        item.ad_card && typeof item.ad_card === 'object' && Object.keys(item.ad_card).length > 0 ||
        typeof item.goto === 'string' && /^ad(?:_|$)/.test(item.goto) ||
        typeof item.card_type === 'string' && /^cm_/.test(item.card_type) ||
        typeof item.card_goto === 'string' && /^ad_/.test(item.card_goto));
    }
    if (/^\/x\/v2\/feed\/index(?:\/(?:relate\/)?story)?\/?$/.test(route) && Array.isArray(obj.data.items)) {
      var keep = obj.data.items.filter(function (item) { return !ad(item); });
      if (keep.length !== obj.data.items.length) { obj.data.items = keep; changed = true; }
    } else if (/^\/x\/v2\/splash\/(?:list|show|brand\/list|event\/list2)\/?$/.test(route)) {
      // Only known array containers on dedicated splash APIs; retain timing and unknown fields.
      if (Array.isArray(obj.data.list) && obj.data.list.length) { obj.data.list = []; changed = true; }
      ['show','preload','event_list'].forEach(function (k) {
        if (Object.prototype.hasOwnProperty.call(obj.data,k)) { delete obj.data[k]; changed = true; }
      });
    }
    if (changed) {
      // The proxy has already decoded the text body; remove stale wire lengths.
      var headers = {}, old = $response.headers || {};
      Object.keys(old).forEach(function (k) {
        if (!/^(?:content-length|content-encoding|transfer-encoding|etag|content-md5)$/i.test(k)) headers[k] = old[k];
      });
      done = {body: JSON.stringify(obj), headers: headers};
    }
  } catch (_) { done = {}; }
  $done(done);
})();
