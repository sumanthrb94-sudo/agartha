/* Agartha — privacy-first, cookieless visitor analytics.
   Logs anonymous pageview + engagement events to the same Supabase backend the
   lead forms use (insert-only publishable key; only allowlisted admins can read
   the data back, in the Analytics Console at /analytics).

   Principles:
     • No cookies, no cross-site tracking, no PII. A random first-party id is
       kept in localStorage purely to tell new vs returning visitors apart.
     • Honors Do-Not-Track and Global Privacy Control — opts out entirely.
     • Skips obvious bots and the admin/console pages themselves.
     • Fully non-blocking and failure-silent: it can never break the site.  */

(function () {
  "use strict";

  var backend = window.AGARTHA_BACKEND || null;
  if (!backend || !backend.url || !backend.key) return;

  // ----- Opt-out & bot guards -----
  try {
    var dnt = navigator.doNotTrack || window.doNotTrack || navigator.msDoNotTrack;
    if (dnt === "1" || dnt === "yes" || navigator.globalPrivacyControl === true) return;
  } catch (e) {}

  var ua = "";
  try { ua = navigator.userAgent || ""; } catch (e) {}
  if (navigator.webdriver) return;
  if (/bot|crawl|spider|slurp|bing|headless|lighthouse|pingdom|monitor|preview/i.test(ua)) return;

  // Never track the admin surfaces (they are noindex tools, not visitors).
  var path = location.pathname || "/";
  if (/\/admin|\/analytics/i.test(path)) return;

  // ----- Identity: cookieless first-party ids -----
  var SESSION_MS = 30 * 60 * 1000; // a "session" ends after 30 min idle

  function rid() {
    return Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 12);
  }
  function ls(get, k, v) {
    try { return get ? localStorage.getItem(k) : localStorage.setItem(k, v); }
    catch (e) { return null; }
  }

  var vid = ls(true, "ag_vid");
  var isNew = !vid;
  if (!vid) { vid = rid(); ls(false, "ag_vid", vid); }

  var sid = ls(true, "ag_sid");
  var sidTs = parseInt(ls(true, "ag_sid_ts") || "0", 10);
  var now = Date.now();
  if (!sid || !sidTs || now - sidTs > SESSION_MS) sid = rid();
  ls(false, "ag_sid", sid);
  ls(false, "ag_sid_ts", String(now));

  // ----- Context: device, browser, referrer, campaign -----
  function detectDevice() {
    var w = window.innerWidth || screen.width || 0;
    if (/Mobi|iPhone|iPod|Android.*Mobile/i.test(ua)) return "mobile";
    if (/iPad|Tablet|PlayBook|Silk|Android(?!.*Mobile)/i.test(ua)) return "tablet";
    if (w && w < 768) return "mobile";
    if (w && w < 1024) return "tablet";
    if (!w) return "unknown";
    return "desktop";
  }
  function detectBrowser() {
    if (/Edg\//.test(ua)) return "Edge";
    if (/OPR\/|Opera/.test(ua)) return "Opera";
    if (/SamsungBrowser/.test(ua)) return "Samsung";
    if (/Firefox\/|FxiOS/.test(ua)) return "Firefox";
    if (/CriOS|Chrome\//.test(ua)) return "Chrome";
    if (/Safari\//.test(ua)) return "Safari";
    return "Other";
  }

  var ref = "";
  try { ref = document.referrer || ""; } catch (e) {}
  var refHost = "direct";
  if (ref) {
    try {
      var h = new URL(ref).hostname.replace(/^www\./, "");
      refHost = h === location.hostname.replace(/^www\./, "") ? "internal" : h;
    } catch (e) { refHost = "other"; }
  }

  var utm = { source: null, medium: null, campaign: null };
  try {
    var q = new URLSearchParams(location.search);
    utm.source = q.get("utm_source");
    utm.medium = q.get("utm_medium");
    utm.campaign = q.get("utm_campaign");
    // Infer organic search when a known engine referred with no UTM tag.
    if (!utm.source && /google\.|bing\.|yahoo\.|duckduckgo\.|ecosia\./i.test(refHost)) {
      utm.source = refHost; utm.medium = "organic";
    }
  } catch (e) {}

  var device = detectDevice();
  var browser = detectBrowser();
  var lang = "";
  try { lang = (navigator.language || "").slice(0, 20); } catch (e) {}

  function clip(s, n) { return s == null ? null : String(s).slice(0, n); }

  function post(type, extra) {
    var body = {
      event_type: type,
      path: clip(path, 512),
      referrer: ref ? clip(ref, 1024) : null,
      referrer_host: clip(refHost, 255),
      session_id: sid,
      visitor_id: vid,
      is_new_visitor: isNew,
      device: device,
      browser: browser,
      screen_w: window.innerWidth || screen.width || null,
      lang: lang || null,
      utm_source: clip(utm.source, 200),
      utm_medium: clip(utm.medium, 200),
      utm_campaign: clip(utm.campaign, 200),
      meta: {}
    };
    if (extra) for (var k in extra) body[k] = extra[k];
    try {
      fetch(backend.url + "/rest/v1/agartha_events", {
        method: "POST",
        keepalive: true, // survives page unload without the sendBeacon header limits
        headers: {
          "Content-Type": "application/json",
          apikey: backend.key,
          Authorization: "Bearer " + backend.key,
          Prefer: "return=minimal"
        },
        body: JSON.stringify(body)
      }).catch(function () {});
    } catch (e) {}
  }

  // ----- Pageview (fires once, now) -----
  post("pageview");

  // ----- Engagement: max scroll depth + dwell time, sent once on leave -----
  var start = now;
  var maxScroll = 0;
  function onScroll() {
    try {
      var doc = document.documentElement;
      var seen = (window.scrollY || doc.scrollTop || 0) + window.innerHeight;
      var pct = Math.max(0, Math.min(100, Math.round((seen / (doc.scrollHeight || 1)) * 100)));
      if (pct > maxScroll) maxScroll = pct;
    } catch (e) {}
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  var engagementSent = false;
  function sendEngagement() {
    if (engagementSent) return;
    engagementSent = true;
    post("engagement", {
      dwell_ms: Math.max(0, Math.min(86400000, Date.now() - start)),
      scroll_pct: maxScroll
    });
  }
  document.addEventListener("visibilitychange", function () {
    if (document.visibilityState === "hidden") sendEngagement();
  });
  window.addEventListener("pagehide", sendEngagement);

  // ----- Conversion intent: lead form submissions -----
  document.addEventListener("submit", function (e) {
    var form = e.target;
    if (form && form.matches && form.matches("form[data-lead]")) {
      post("form_submit", { meta: { form_type: form.getAttribute("data-lead") || "contact" } });
    }
  }, true);

  // Small public hook for manual events (e.g. a tracked CTA click).
  window.AgarthaAnalytics = {
    track: function (type, meta) {
      post(/^(cta_click|outbound_click|form_submit)$/.test(type) ? type : "cta_click",
           { meta: meta || {} });
    }
  };
})();
