/* Service worker do Cortexplor: faz o site funcionar como app instalado.
   Gerado por scripts/engine/build.py a partir de templates/sw.js - edite o
   modelo, nao o /sw.js da raiz.

   Regras:
   - Paginas (capa, editorias, materias): rede primeiro, para o leitor ver
     sempre o que acabou de ser publicado. Sem internet, mostra a copia da
     ultima vez que a pagina foi aberta; se nunca foi, a pagina "sem conexao".
   - CSS, JS, fontes e imagens do proprio site: copia guardada primeiro (os
     enderecos mudam com ?v= quando o arquivo muda), atualizada em segundo
     plano.
   - Outros dominios (anuncios, estatisticas) e RSS: nunca passam por aqui. */
"use strict";

var VERSION = "__VERSION__";
var STATIC = "cx-static-" + VERSION;
var PAGES = "cx-pages";
var ASSETS = "cx-assets";
var PRECACHE = __PRECACHE__;
var LANGS = __LANGS__;
var DEFAULT_LANG = "__DEFAULT_LANG__";
var MAX_PAGES = 80;
var MAX_ASSETS = 150;

self.addEventListener("install", function (event) {
  event.waitUntil(
    caches.open(STATIC)
      .then(function (cache) { return cache.addAll(PRECACHE); })
      .then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener("activate", function (event) {
  event.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(keys.map(function (key) {
        if (key.indexOf("cx-static-") === 0 && key !== STATIC) return caches.delete(key);
      }));
    }).then(function () { return self.clients.claim(); })
  );
});

function trim(cacheName, max) {
  return caches.open(cacheName).then(function (cache) {
    return cache.keys().then(function (keys) {
      if (keys.length <= max) return;
      return Promise.all(keys.slice(0, keys.length - max).map(function (k) { return cache.delete(k); }));
    });
  });
}

function offlinePage(url) {
  var lang = url.pathname.split("/")[1];
  if (LANGS.indexOf(lang) === -1) lang = DEFAULT_LANG;
  return caches.match("/offline-" + lang + ".html");
}

function page(event) {
  var request = event.request;
  return fetch(request).then(function (response) {
    if (response.ok && response.type === "basic") {
      var copy = response.clone();
      event.waitUntil(caches.open(PAGES)
        .then(function (cache) { return cache.put(request, copy); })
        .then(function () { return trim(PAGES, MAX_PAGES); }));
    }
    return response;
  }).catch(function () {
    return caches.match(request, { ignoreSearch: true }).then(function (hit) {
      return hit || offlinePage(new URL(request.url));
    });
  });
}

function asset(event) {
  var request = event.request;
  return caches.match(request).then(function (hit) {
    var network = fetch(request).then(function (response) {
      if (response.ok && response.type === "basic") {
        var copy = response.clone();
        caches.open(ASSETS)
          .then(function (cache) { return cache.put(request, copy); })
          .then(function () { return trim(ASSETS, MAX_ASSETS); });
      }
      return response;
    });
    if (hit) {
      event.waitUntil(network.catch(function () {}));
      return hit;
    }
    // Sem copia exata (ex.: ?v= novo) e sem rede: qualquer versao guardada serve.
    return network.catch(function () {
      return caches.match(request, { ignoreSearch: true });
    });
  });
}

self.addEventListener("fetch", function (event) {
  var request = event.request;
  if (request.method !== "GET") return;
  var url = new URL(request.url);
  if (url.origin !== self.location.origin) return;
  if (/\.(xml|webmanifest)$/.test(url.pathname) || url.pathname === "/sw.js") return;

  if (request.mode === "navigate") {
    event.respondWith(page(event));
  } else if (url.pathname.indexOf("/assets/") === 0) {
    event.respondWith(asset(event));
  }
});
