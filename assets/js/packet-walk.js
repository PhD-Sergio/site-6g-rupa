// Packet walkthrough: steps one packet through a layered path, box by box.
// Each .pw element carries its config as JSON (see the packet-walk shortcode).
(function () {
  "use strict";

  var STATE = { wrap: "wraps", up: "hands up", relay: "relays" };

  function el(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html !== undefined) e.innerHTML = html;
    return e;
  }

  function envelopes(cfg, keys, read, mode) {
    var inner = '<div class="pw-env pw-env--data pw-k-app">' + cfg.data + "</div>";
    for (var j = keys.length - 1; j >= 0; j--) {
      var e = cfg.env[keys[j]], cls = "", st = "";
      if (mode === "in") {
        if (read.indexOf(keys[j]) >= 0) { cls = " pw-env--read"; st = "opened here"; }
        else { cls = " pw-env--sealed"; st = "not opened here"; }
      } else if (j === 0) { st = "new outer envelope"; }
      inner = '<div class="pw-env pw-k-' + e.k + cls + '"><div class="pw-env__lbl"><span>' + e.name +
        (e.dst ? " → " + e.dst : "") + '</span><span class="pw-env__st">' + st + "</span></div>" + inner + "</div>";
    }
    return inner;
  }

  function init(root) {
    var cfg = JSON.parse(root.querySelector('script[type="application/json"]').textContent);
    var i = 0;

    var table = el("div", "pw-addr");
    var t = '<table><thead><tr><th>Layer</th>';
    cfg.cols.forEach(function (c) { t += "<th>" + c + "</th>"; });
    t += "</tr></thead><tbody>";
    cfg.addr.forEach(function (row) {
      t += '<tr><td class="pw-addr__layer pw-c-' + row[1] + '">' + row[0] + "</td>";
      row[2].forEach(function (a) { t += "<td>" + a + "</td>"; });
      t += "</tr>";
    });
    table.innerHTML = t + "</tbody></table>";

    var fig = el("div", "pw-figwrap", cfg.svg);
    var hint = el("p", "pw-hint", "Click a box to jump to it. The line is the packet so far: in each box it climbs to the layer that relays it.");
    var work = el("div", "pw-work");
    var left = el("div", "pw-box"), right = el("div", "pw-packet");
    work.appendChild(left); work.appendChild(right);
    var words = el("div", "pw-words");
    words.setAttribute("aria-live", "polite");
    var nav = el("div", "pw-nav");
    var prev = el("button", "pw-btn pw-btn--ghost", "← Back"); prev.type = "button";
    var next = el("button", "pw-btn", "Next box →"); next.type = "button";
    var count = el("span", "pw-count");
    nav.appendChild(prev); nav.appendChild(next); nav.appendChild(count);

    var mount = root.querySelector(".pw-mount");
    [table, fig, hint, work, words, nav].forEach(function (n) { mount.appendChild(n); });

    var svg = fig.querySelector("svg");
    var cells = svg.querySelectorAll("[data-cell]");
    var segs = svg.querySelectorAll("[data-seg]");
    var dot = svg.querySelector(".pw-dot");
    var colsEls = svg.querySelectorAll(".pw-col");
    svg.classList.add("pw-walking");

    function render() {
      var s = cfg.steps[i];
      cells.forEach(function (c) { c.classList.toggle("pw-lit", s.lit.indexOf(c.getAttribute("data-cell")) >= 0); });
      segs.forEach(function (g) {
        var k = +g.getAttribute("data-seg");
        g.classList.toggle("pw-done", k < i); g.classList.toggle("pw-now", k === i);
      });
      dot.setAttribute("cx", cfg.ends[i][0]); dot.setAttribute("cy", cfg.ends[i][1]);
      colsEls.forEach(function (g) { g.classList.toggle("pw-on", +g.getAttribute("data-stop") === i); });

      var h = '<h3 class="pw-h">Inside ' + s.name + '</h3><p class="pw-sub">' + s.role + '</p><div class="pw-stack">';
      s.stack.forEach(function (c) {
        h += '<div class="pw-cell pw-k-' + c[0] + (c[2] === "relay" ? " pw-cell--relay" : "") + '"><span class="pw-tag">' +
          STATE[c[2]] + '</span><span><span class="pw-cell__name">' + c[1] + "</span><br>" + c[3] + "</span></div>";
      });
      left.innerHTML = h + "</div>";

      var p = '<h3 class="pw-h">The packet</h3><p class="pw-sub">' +
        (s.hop ? "Thick: envelopes this box opens. Dashed: envelopes it never opens." : "Built from the inside out, then sent.") + "</p>";
      if (s.hop) p += '<p class="pw-sub pw-sub--gap">Arrives on ' + cfg.hops[s.hop] + "</p>" + envelopes(cfg, cfg.wires[s.hop], s.read, "in");
      if (s.out) p += '<p class="pw-sub pw-sub--gap">' + (s.hop ? "Leaves" : "Sent") + " on " + cfg.hops[s.out] + "</p>" + envelopes(cfg, cfg.wires[s.out], [], "out");
      right.innerHTML = p;
      words.innerHTML = s.words;
      count.textContent = "box " + (i + 1) + " of " + cfg.steps.length;
      prev.disabled = i === 0;
      next.disabled = i === cfg.steps.length - 1;
    }

    function go(k) { if (k >= 0 && k < cfg.steps.length) { i = k; render(); } }
    prev.addEventListener("click", function () { go(i - 1); });
    next.addEventListener("click", function () { go(i + 1); });
    root.addEventListener("keydown", function (e) {
      if (e.target.tagName === "BUTTON" || e.target.classList.contains("pw-col") || e.target === root) {
        if (e.key === "ArrowRight") { e.preventDefault(); go(i + 1); }
        if (e.key === "ArrowLeft") { e.preventDefault(); go(i - 1); }
      }
    });
    colsEls.forEach(function (g) {
      var k = +g.getAttribute("data-stop");
      g.addEventListener("click", function () { go(k); });
      g.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); go(k); } });
    });
    render();
  }

  function start() { document.querySelectorAll(".pw").forEach(init); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start); else start();
})();
