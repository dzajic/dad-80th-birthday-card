(function () {
  "use strict";

  var scenes = Array.prototype.slice.call(document.querySelectorAll(".scene"));
  var prev = document.getElementById("prev");
  var next = document.getElementById("next");
  var start = document.getElementById("start");
  var count = document.getElementById("count");
  var bar = document.getElementById("bar");
  var live = document.getElementById("live");
  var index = 0;

  function hashIndex() {
    var match = location.hash.match(/(\d+)/);
    var n = match ? Number(match[1]) : 1;
    if (n >= 1 && n <= scenes.length) return n - 1;
    return 0;
  }

  function render(push) {
    scenes.forEach(function (scene, i) {
      var on = i === index;
      scene.classList.toggle("active", on);
      scene.toggleAttribute("inert", !on);
      scene.setAttribute("aria-hidden", on ? "false" : "true");
    });
    var n = index + 1;
    count.textContent = n + " / " + scenes.length;
    prev.disabled = index === 0;
    start.disabled = index === 0;
    next.disabled = index === scenes.length - 1;
    bar.style.width = (n / scenes.length) * 100 + "%";
    var heading = scenes[index].querySelector("h1, h2");
    live.textContent = "Page " + n + " of " + scenes.length + (heading ? ". " + heading.textContent.replace(/\s+/g, " ").trim() : "");
    var url = "#" + n;
    if (push) history.pushState({ i: index }, "", url);
    else history.replaceState({ i: index }, "", url);
  }

  function go(n, push) {
    n = Math.max(0, Math.min(scenes.length - 1, n));
    if (n === index) return;
    index = n;
    render(push);
    window.scrollTo(0, 0);
  }

  prev.addEventListener("click", function () { go(index - 1, true); });
  next.addEventListener("click", function () { go(index + 1, true); });
  start.addEventListener("click", function () { go(0, true); });

  document.addEventListener("keydown", function (e) {
    if (e.altKey || e.metaKey || e.ctrlKey) return;
    if (e.key === "ArrowRight") { e.preventDefault(); go(index + 1, true); }
    else if (e.key === "ArrowLeft") { e.preventDefault(); go(index - 1, true); }
    else if (e.key === "Home") { e.preventDefault(); go(0, true); }
    else if (e.key === "End") { e.preventDefault(); go(scenes.length - 1, true); }
  });

  var touch = null;
  document.addEventListener("touchstart", function (e) {
    var t = e.changedTouches[0];
    touch = { x: t.clientX, y: t.clientY };
  }, { passive: true });
  document.addEventListener("touchend", function (e) {
    if (!touch) return;
    var t = e.changedTouches[0];
    var dx = t.clientX - touch.x;
    var dy = t.clientY - touch.y;
    touch = null;
    if (Math.abs(dx) < 64 || Math.abs(dx) < Math.abs(dy) * 1.6) return;
    go(index + (dx < 0 ? 1 : -1), true);
  }, { passive: true });

  window.addEventListener("popstate", function (e) {
    var i = e.state && Number.isInteger(e.state.i) ? e.state.i : hashIndex();
    if (i === index) return;
    index = i;
    render(false);
    window.scrollTo(0, 0);
  });

  index = hashIndex();
  render(false);
})();
