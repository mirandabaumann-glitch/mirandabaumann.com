/*
  Light/dark theme toggle for mirandabaumann.com.
  Runs in <head> so a saved choice applies before the page paints (no flash).
  Without JavaScript, the page simply follows the device setting via CSS.
*/
(function () {
  var KEY = "theme";
  var root = document.documentElement;

  function getSaved() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }
  function save(value) {
    try { localStorage.setItem(KEY, value); } catch (e) { /* storage unavailable: choice lasts for this page view only */ }
  }
  function deviceIsDark() {
    return !!(window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches);
  }
  function current() {
    var t = root.getAttribute("data-theme");
    if (t === "light" || t === "dark") return t;
    return deviceIsDark() ? "dark" : "light";
  }

  var saved = getSaved();
  if (saved === "light" || saved === "dark") root.setAttribute("data-theme", saved);

  document.addEventListener("DOMContentLoaded", function () {
    var button = document.getElementById("theme-toggle");
    if (!button) return;
    function sync() { button.setAttribute("aria-pressed", current() === "dark" ? "true" : "false"); }
    button.addEventListener("click", function () {
      var next = current() === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      save(next);
      sync();
    });
    if (window.matchMedia) {
      var mq = window.matchMedia("(prefers-color-scheme: dark)");
      if (mq.addEventListener) mq.addEventListener("change", sync);
    }
    sync();
    button.hidden = false;
  });
})();
