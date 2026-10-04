/* Comportamento do site. Sem dependencias, e tudo opcional: sem JavaScript o
   site continua completo, so sem o botao de tema e com datas absolutas. */
(function () {
  "use strict";
  var root = document.documentElement;
  var lang = root.getAttribute("lang") || "en";

  // Tema claro/escuro. O <head> ja aplicou a escolha salva antes de pintar;
  // aqui so liga o botao e grava a troca.
  var toggle = document.querySelector("[data-theme-toggle]");
  function isDark() { return root.getAttribute("data-theme") === "dark"; }
  function syncToggle() {
    if (toggle) toggle.setAttribute("aria-pressed", isDark() ? "true" : "false");
  }
  if (toggle) {
    toggle.hidden = false;
    syncToggle();
    toggle.addEventListener("click", function () {
      var next = isDark() ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("theme", next); } catch (e) { /* navegacao privada */ }
      syncToggle();
    });
  }

  // "ha 2 h", "ontem". O HTML e gerado uma vez e servido por dias; um horario
  // relativo escrito no build ficaria errado. Acima de uma semana, mantem a
  // data absoluta que ja veio no HTML.
  var rtf = null, short = null;
  try { rtf = new Intl.RelativeTimeFormat(lang, { numeric: "auto", style: "short" }); } catch (e) {}
  try { short = new Intl.DateTimeFormat(lang, { day: "numeric", month: "short" }); } catch (e) {}
  if (rtf) {
    var now = Date.now();
    var times = document.querySelectorAll("time[data-relative]");
    for (var i = 0; i < times.length; i++) {
      var el = times[i];
      var at = Date.parse(el.getAttribute("datetime"));
      if (isNaN(at)) continue;
      var seconds = Math.min((at - now) / 1000, -60);
      var abs = Math.abs(seconds);
      var text = null;
      if (abs < 3600) text = rtf.format(Math.round(seconds / 60), "minute");
      else if (abs < 86400) text = rtf.format(Math.round(seconds / 3600), "hour");
      else if (abs < 7 * 86400) text = rtf.format(Math.round(seconds / 86400), "day");
      // Mais velho que uma semana: data curta ("25 de set."). Ano so quando
      // nao e o atual - numa coluna estreita a data longa quebra em duas linhas.
      else if (short && new Date(at).getFullYear() === new Date(now).getFullYear()) text = short.format(at);
      if (text) {
        if (!el.title) el.title = el.textContent.trim();
        el.textContent = text;
      }
    }
  }

  // Data de hoje no topo, pelo relogio de quem le.
  var today = document.querySelectorAll("[data-today]");
  if (today.length) {
    var d = new Date();
    var weekday = "", date = "";
    try {
      weekday = new Intl.DateTimeFormat(lang, { weekday: "long" }).format(d);
      date = new Intl.DateTimeFormat(lang, { day: "numeric", month: "long", year: "numeric" }).format(d);
    } catch (e) {}
    if (date) {
      var iso = d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" +
        String(d.getDate()).padStart(2, "0");
      for (var j = 0; j < today.length; j++) {
        var node = today[j];
        node.setAttribute("datetime", iso);
        node.textContent = "";
        if (weekday) {
          var wd = document.createElement("span");
          wd.className = "weekday";
          wd.textContent = weekday + ", ";
          node.appendChild(wd);
        }
        node.appendChild(document.createTextNode(date));
        node.hidden = false;
      }
    }
  }
})();
