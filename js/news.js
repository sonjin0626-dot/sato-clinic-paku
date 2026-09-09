"use strict";

// 下層ページ用の最小限のprogressive enhancement。
// 記事本文はHTMLに保持し、JavaScriptで生成しない。
document.documentElement.classList.add("js-enabled");

const siteHeader = document.querySelector(".subpage-header");
const navToggle = document.querySelector(".nav-toggle");
const globalNav = document.querySelector("#global-nav");

function revealHashFaq() {
  if (!window.location.hash) return;

  const target = document.getElementById(window.location.hash.slice(1));
  if (!(target instanceof HTMLDetailsElement) || !target.closest(".faq-page .faq-list")) return;

  target.open = true;
  target.scrollIntoView({ block: "start", behavior: "auto" });
}

revealHashFaq();
window.addEventListener("hashchange", revealHashFaq);

if (siteHeader && navToggle && globalNav) {
  function closeMenu({ returnFocus = false } = {}) {
    siteHeader.classList.remove("is-menu-open");
    navToggle.setAttribute("aria-expanded", "false");
    navToggle.setAttribute("aria-label", "メニューを開く");
    if (returnFocus) navToggle.focus();
  }

  navToggle.addEventListener("click", () => {
    const willOpen = navToggle.getAttribute("aria-expanded") !== "true";
    siteHeader.classList.toggle("is-menu-open", willOpen);
    navToggle.setAttribute("aria-expanded", String(willOpen));
    navToggle.setAttribute("aria-label", willOpen ? "メニューを閉じる" : "メニューを開く");
  });

  globalNav.addEventListener("click", event => {
    if (event.target.closest("a")) closeMenu();
  });

  document.addEventListener("keydown", event => {
    if (event.key === "Escape" && siteHeader.classList.contains("is-menu-open")) {
      closeMenu({ returnFocus: true });
    }
  });

  const desktopQuery = window.matchMedia("(min-width: 1101px)");
  const handleDesktopChange = event => {
    if (event.matches) closeMenu();
  };

  if (typeof desktopQuery.addEventListener === "function") {
    desktopQuery.addEventListener("change", handleDesktopChange);
  } else if (typeof desktopQuery.addListener === "function") {
    desktopQuery.addListener(handleDesktopChange);
  }
}
