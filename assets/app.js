/* Test 1 — G1097 · progress tracking, no account, localStorage only */
(function () {
  "use strict";

  var KEY = "g1097:test1:progress:v1";
  var THEME_KEY = "g1097:test1:theme";

  /* ---------------- storage ---------------- */
  function read() {
    try {
      var raw = localStorage.getItem(KEY);
      if (!raw) return {};
      var o = JSON.parse(raw);
      return (o && typeof o === "object") ? o : {};
    } catch (e) {
      return {};
    }
  }

  function write(state) {
    try {
      localStorage.setItem(KEY, JSON.stringify(state));
    } catch (e) {
      /* private mode / quota — page still works, just no persistence */
    }
  }

  var state = read();

  /* ---------------- theme ---------------- */
  function applyTheme(t) {
    if (t === "light" || t === "dark") {
      document.documentElement.setAttribute("data-theme", t);
    } else {
      document.documentElement.removeAttribute("data-theme");
    }
  }

  function currentTheme() {
    return document.documentElement.getAttribute("data-theme") || "auto";
  }

  try {
    var saved = localStorage.getItem(THEME_KEY);
    if (saved) applyTheme(saved);
  } catch (e) {}

  /* ---------------- checkboxes ---------------- */
  function toggle(el) {
    var key = el.getAttribute("data-key");
    if (!key) return;
    if (state[key]) {
      delete state[key];
      el.classList.remove("done");
      el.setAttribute("aria-checked", "false");
    } else {
      state[key] = 1;
      el.classList.add("done");
      el.setAttribute("aria-checked", "true");
    }
    write(state);
    refreshCounters();
  }

  function bindCheckboxes() {
    var nodes = document.querySelectorAll(".chk[data-key]");
    for (var i = 0; i < nodes.length; i++) {
      var el = nodes[i];
      var key = el.getAttribute("data-key");
      var done = !!state[key];
      el.classList.toggle("done", done);
      el.setAttribute("role", "checkbox");
      el.setAttribute("tabindex", "0");
      el.setAttribute("aria-checked", done ? "true" : "false");
      el.setAttribute("title", "Bifează când ai terminat");
      el.addEventListener("click", function (ev) {
        ev.preventDefault();
        toggle(this);
      });
      el.addEventListener("keydown", function (ev) {
        if (ev.key === " " || ev.key === "Enter") {
          ev.preventDefault();
          toggle(this);
        }
      });
    }
  }

  /* ---------------- counters ---------------- */
  function countDone(prefix) {
    var n = 0;
    for (var k in state) {
      if (!state.hasOwnProperty(k)) continue;
      if (!prefix || k.indexOf(prefix) === 0) n++;
    }
    return n;
  }

  function isEn() {
    return document.body && document.body.getAttribute("data-lang") === "en";
  }

  function refreshCounters() {
    var en = isEn();

    /* chapter page: progress for this chapter */
    var main = document.querySelector("main[data-chapter]");
    if (main) {
      var ch = main.getAttribute("data-chapter");
      var total = parseInt(main.getAttribute("data-total") || "0", 10);
      var done = countDone(ch + ".");
      var pct = total ? Math.round((done / total) * 100) : 0;
      var bar = document.getElementById("chBar");
      var txt = document.getElementById("chText");
      if (bar) bar.style.width = pct + "%";
      if (txt) txt.textContent = done + " / " + total + " (" + pct + "%)";
    }

    /* sidebar mini progress */
    var mini = document.getElementById("miniProgress");
    if (mini) {
      var all = 0, tot = parseInt(mini.getAttribute("data-total") || "0", 10);
      for (var k in state) if (state.hasOwnProperty(k)) all++;
      var p = tot ? Math.round((all / tot) * 100) : 0;
      mini.innerHTML = en
        ? "<b>" + p + "%</b> of " + tot + " checks (" + all + " done)"
        : "<b>" + p + "%</b> din " + tot + " bife (" + all + " făcute)";
    }

    /* index / section pages: per-chapter bars + totals */
    var grid = document.getElementById("chapterGrid") || document.getElementById("sectionGrid");
    if (grid) {
      var cards = grid.querySelectorAll("[data-chapter]");
      var gDone = 0, gTot = 0;
      for (var i = 0; i < cards.length; i++) {
        var c = cards[i];
        var cch = c.getAttribute("data-chapter");
        var ctot = parseInt(c.getAttribute("data-total") || "0", 10);
        var cdone = countDone(cch + ".");
        gDone += cdone;
        gTot += ctot;
        var cb = c.querySelector(".bar > i");
        var ct = c.querySelector(".cc-done");
        var cp = ctot ? Math.round((cdone / ctot) * 100) : 0;
        if (cb) cb.style.width = cp + "%";
        if (ct) ct.textContent = cdone + "/" + ctot;
      }
      var gp = gTot ? Math.round((gDone / gTot) * 100) : 0;
      /* root index */
      var gb = document.getElementById("globalBar");
      if (gb) gb.style.width = gp + "%";
      var g1 = document.getElementById("globalPct");
      var g2 = document.getElementById("globalDone");
      var g3 = document.getElementById("globalTotal");
      if (g1) g1.textContent = gp + "%";
      if (g2) g2.textContent = String(gDone);
      if (g3) g3.textContent = String(gTot);
      /* section landing */
      var sb = document.getElementById("sectionBar");
      if (sb) sb.style.width = gp + "%";
      var s1 = document.getElementById("sectionPct");
      var s2 = document.getElementById("sectionDone");
      if (s1) s1.textContent = gp + "%";
      if (s2) s2.textContent = String(gDone);
    }
  }

  /* ---------------- copy buttons ---------------- */
  function addCopyButtons() {
    var blocks = document.querySelectorAll(".codehilite, pre");
    for (var i = 0; i < blocks.length; i++) {
      (function (block) {
        if (block.querySelector(".copy-btn")) return;
        var btn = document.createElement("button");
        btn.className = "copy-btn";
        btn.type = "button";
        var en = document.body.getAttribute("data-lang") === "en";
        btn.textContent = en ? "Copy" : "Copiază";
        btn.addEventListener("click", function () {
          var code = block.querySelector("code");
          var text = code ? code.innerText : block.innerText;
          var done = function () {
            btn.textContent = en ? "✓ Copied" : "✓ Copiat";
            btn.classList.add("ok");
            setTimeout(function () {
              var en = document.body.getAttribute("data-lang") === "en";
        btn.textContent = en ? "Copy" : "Copiază";
              btn.classList.remove("ok");
            }, 1400);
          };
          if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text).then(done, function () {});
          } else {
            var ta = document.createElement("textarea");
            ta.value = text;
            document.body.appendChild(ta);
            ta.select();
            try { document.execCommand("copy"); done(); } catch (e) {}
            document.body.removeChild(ta);
          }
        });
        block.appendChild(btn);
      })(blocks[i]);
    }
  }

  /* ---------------- export / import / reset ---------------- */
  function exportProgress() {
    var blob = new Blob([JSON.stringify(state, null, 2)], { type: "application/json" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = (document.body.getAttribute("data-lang") === "en"
      ? "progress-test1-g1097.json" : "progres-test1-g1097.json");
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
  }

  function importProgress(file) {
    var fr = new FileReader();
    fr.onload = function () {
      try {
        var o = JSON.parse(fr.result);
        if (!o || typeof o !== "object") throw new Error("format");
        state = o;
        write(state);
        bindCheckboxes();
        refreshCounters();
        alert((document.body.getAttribute("data-lang") === "en"
          ? "Progress imported: " + Object.keys(state).length + " checks."
          : "Progres importat: " + Object.keys(state).length + " bife."));
      } catch (e) {
        alert((document.body.getAttribute("data-lang") === "en"
          ? "Invalid file. Expected JSON with keys like \"step:1.1\" or \"ex:2.3\"."
          : "Fișier invalid. Așteptat: JSON cu chei de forma \"step:1.1\" sau \"ex:2.3\"."));
      }
    };
    fr.readAsText(file);
  }

  function resetProgress() {
    var en = document.body.getAttribute("data-lang") === "en";
    if (!confirm(en ? "Delete all progress? This cannot be undone."
                    : "Ștergi tot progresul? Acțiunea nu poate fi anulată.")) return;
    state = {};
    write(state);
    bindCheckboxes();
    refreshCounters();
  }

  /* ---------------- sidebar / menu ---------------- */
  function initMenu() {
    var btn = document.getElementById("menuBtn");
    var side = document.getElementById("sidebar");
    if (!btn || !side) return;
    btn.addEventListener("click", function () {
      side.classList.toggle("open");
    });
    document.addEventListener("click", function (ev) {
      if (window.innerWidth > 980) return;
      if (side.contains(ev.target) || btn.contains(ev.target)) return;
      side.classList.remove("open");
    });
  }

  function initThemeToggle() {
    var btn = document.getElementById("themeBtn");
    if (!btn) return;
    btn.addEventListener("click", function () {
      var order = { auto: "light", light: "dark", dark: "auto" };
      var next = order[currentTheme()] || "light";
      applyTheme(next === "auto" ? null : next);
      try {
        if (next === "auto") localStorage.removeItem(THEME_KEY);
        else localStorage.setItem(THEME_KEY, next);
      } catch (e) {}
      var label = { auto: "🌗 Auto", light: "☀️ Light", dark: "🌙 Dark" }[next];
      btn.textContent = label;
    });
    var label = { auto: "🌗 Auto", light: "☀️ Light", dark: "🌙 Dark" }[currentTheme()];
    btn.textContent = label;
  }

  /* ---------------- expand / collapse all ---------------- */
  function initDetailsBtns() {
    var open = document.getElementById("openAll");
    var close = document.getElementById("closeAll");
    var nodes = document.querySelectorAll("main details");
    if (open) open.addEventListener("click", function () {
      for (var i = 0; i < nodes.length; i++) nodes[i].open = true;
    });
    if (close) close.addEventListener("click", function () {
      for (var i = 0; i < nodes.length; i++) nodes[i].open = false;
    });
  }

  /* ---------------- keyboard: j/k between steps ---------------- */
  function initKeys() {
    document.addEventListener("keydown", function (ev) {
      if (ev.target && /^(INPUT|TEXTAREA|SELECT)$/.test(ev.target.tagName)) return;
      if (ev.metaKey || ev.ctrlKey || ev.altKey) return;
      if (ev.key === "t") initThemeToggle && document.getElementById("themeBtn") &&
        document.getElementById("themeBtn").click();
    });
  }

  /* ---------------- boot ---------------- */
  function boot() {
    bindCheckboxes();
    refreshCounters();
    addCopyButtons();
    initMenu();
    initThemeToggle();
    initDetailsBtns();
    initKeys();

    var ex = document.getElementById("exportBtn");
    var im = document.getElementById("importBtn");
    var imf = document.getElementById("importFile");
    var rs = document.getElementById("resetBtn");
    if (ex) ex.addEventListener("click", exportProgress);
    if (im && imf) im.addEventListener("click", function () { imf.click(); });
    if (imf) imf.addEventListener("change", function () {
      if (this.files && this.files[0]) importProgress(this.files[0]);
      this.value = "";
    });
    if (rs) rs.addEventListener("click", resetProgress);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
