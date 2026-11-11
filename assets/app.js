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
  function initSubnav() {
    var btn = document.getElementById("snMore");
    var panel = document.getElementById("snPanel");
    if (!btn || !panel) return;
    function close() {
      panel.hidden = true;
      btn.setAttribute("aria-expanded", "false");
    }
    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      panel.hidden = !panel.hidden;
      btn.setAttribute("aria-expanded", panel.hidden ? "false" : "true");
    });
    panel.addEventListener("click", function (e) {
      if (e.target.tagName === "A") close();
    });
    document.addEventListener("click", function (e) {
      if (!panel.hidden && !panel.contains(e.target) && e.target !== btn) close();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") close();
    });
  }

  function boot() {
    bindCheckboxes();
    refreshCounters();
    addCopyButtons();
    initMenu();
    initThemeToggle();
    initDetailsBtns();
    initKeys();
    initSubnav();

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


  /* ---------------- code browser panel ---------------- */
  var cpState = { files: null, loaded: false, current: null, dirs: {} };

  function cpPanel() { return document.getElementById("codePanel"); }

  function loadTree(cb) {
    if (cpState.loaded) { cb(); return; }
    var panel = cpPanel();
    var base = panel ? (panel.getAttribute("data-base") || "") : "";
    fetch(base + "assets/tree.json")
      .then(function (r) { return r.json(); })
      .then(function (data) {
        cpState.files = data.files || [];
        cpState.loaded = true;
        cb();
      })
      .catch(function () {
        var tree = document.getElementById("cpTree");
        if (tree) tree.innerHTML = '<p class="cp-hint">tree.json missing</p>';
      });
  }

  function buildTree() {
    var tree = document.getElementById("cpTree");
    if (!tree) return;
    tree.innerHTML = "";
    var folders = {};   // path -> element
    var frag = document.createDocumentFragment();

    function ensureFolder(parts) {
      var key = "";
      var parentEl = frag;
      for (var i = 0; i < parts.length; i++) {
        key = key ? key + "/" + parts[i] : parts[i];
        if (!folders[key]) {
          var wrap = document.createElement("div");
          var head = document.createElement("div");
          head.className = "cp-dir";
          head.textContent = "▾ " + parts[i];
          var kids = document.createElement("div");
          kids.className = "cp-children";
          wrap.appendChild(head);
          wrap.appendChild(kids);
          parentEl.appendChild(wrap);
          var depth = key.split("/").length;
          var startOpen = depth <= 2;   // deep project trees start collapsed
          if (!startOpen) {
            kids.classList.add("cp-hidden");
            head.textContent = "▸ " + parts[i];
          }
          folders[key] = { head: head, kids: kids, open: startOpen };
          head.addEventListener("click", function (el) {
            return function () {
              var st = folders[el];
              st.open = !st.open;
              st.kids.classList.toggle("cp-hidden", !st.open);
              st.head.textContent = (st.open ? "▾ " : "▸ ") + st.head.textContent.slice(2);
            };
          }(key));
        }
        parentEl = folders[key].kids;
      }
      return parentEl;
    }

    cpState.files.forEach(function (f) {
      var parts = f.p.split("/");
      var name = parts.pop();
      var parent = parts.length ? ensureFolder(parts) : frag;
      var a = document.createElement("a");
      a.className = "cp-file";
      a.href = "#";
      a.textContent = name;
      a.setAttribute("data-i", f.i);
      a.setAttribute("data-p", f.p);
      a.addEventListener("click", function (ev) {
        ev.preventDefault();
        openCode(this.getAttribute("data-i"), this.getAttribute("data-p"), this);
      });
      parent.appendChild(a);
    });

    tree.appendChild(frag);
  }

  function openCode(i, path, el) {
    var panel = cpPanel();
    if (!panel) return;
    var base = panel.getAttribute("data-base") || "";
    var box = document.getElementById("cpCode");
    var prev = document.querySelector(".cp-file.active");
    if (prev) prev.classList.remove("active");
    if (el) el.classList.add("active");
    cpState.current = path;
    try { localStorage.setItem("g1097:test1:codeFile", path); } catch (e) {}
    box.innerHTML = '<p class="cp-hint">…</p>';
    fetch(base + "code/" + i + ".html")
      .then(function (r) { return r.text(); })
      .then(function (html) {
        box.innerHTML = '<p class="cp-path">' + path.replace(/&/g, "&amp;").replace(/</g, "&lt;") +
                        '</p><pre class="hl">' + html + "</pre>";
      })
      .catch(function () { box.innerHTML = '<p class="cp-hint">Could not load the file.</p>'; });
  }

  function cpOpen() {
    var panel = cpPanel();
    if (!panel) return;
    panel.classList.add("open");
    panel.setAttribute("aria-hidden", "false");
    loadTree(function () {
      if (!document.querySelector(".cp-file")) buildTree();
      if (!cpState.restored && cpState.current === null) {
        cpState.restored = true;
        var saved = null;
        try { saved = localStorage.getItem("g1097:test1:codeFile"); } catch (e) {}
        if (saved) {
          var f = cpState.files.filter(function (x) { return x.p === saved; })[0];
          if (f) openCode(f.i, f.p, document.querySelector('.cp-file[data-p="' + saved + '"]'));
        }
      }
    });
  }

  function cpClose() {
    var panel = cpPanel();
    if (!panel) return;
    panel.classList.remove("open");
    panel.setAttribute("aria-hidden", "true");
  }

  function initCodePanel() {
    var btn = document.getElementById("codeBtn");
    var panel = cpPanel();
    if (!btn || !panel) return;

    btn.addEventListener("click", function () {
      if (panel.classList.contains("open")) cpClose(); else cpOpen();
    });

    var close = document.getElementById("cpClose");
    if (close) close.addEventListener("click", cpClose);

    document.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape" && panel.classList.contains("open")) cpClose();
    });

    /* resizable */
    var grip = document.getElementById("cpResize");
    if (grip) {
      var dragging = false;
      grip.addEventListener("mousedown", function (ev) {
        dragging = true; ev.preventDefault();
        document.body.style.userSelect = "none";
      });
      document.addEventListener("mousemove", function (ev) {
        if (!dragging) return;
        var w = window.innerWidth - ev.clientX;
        w = Math.max(340, Math.min(w, window.innerWidth * 0.96));
        panel.style.setProperty("--cp-w", w + "px");
      });
      document.addEventListener("mouseup", function () {
        if (!dragging) return;
        dragging = false;
        document.body.style.userSelect = "";
        try {
          localStorage.setItem("g1097:test1:codeW",
            panel.style.getPropertyValue("--cp-w") || "");
        } catch (e) {}
      });
      try {
        var savedW = localStorage.getItem("g1097:test1:codeW");
        if (savedW) panel.style.setProperty("--cp-w", savedW);
      } catch (e) {}
    }

    /* search */
    var search = document.getElementById("cpSearch");
    if (search) {
      search.addEventListener("input", function () {
        var q = this.value.toLowerCase().trim();
        var nodes = document.querySelectorAll(".cp-tree .cp-file");
        for (var i = 0; i < nodes.length; i++) {
          var p = (nodes[i].getAttribute("data-p") || "").toLowerCase();
          nodes[i].style.display = (!q || p.indexOf(q) !== -1) ? "" : "none";
        }
        var dirs = document.querySelectorAll(".cp-tree .cp-children");
        for (var j = 0; j < dirs.length; j++) dirs[j].classList.remove("cp-hidden");
      });
    }
  }

  initCodePanel();

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
