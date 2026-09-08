"use strict";

document.documentElement.classList.add("js-enabled");

// Six slides remain in the DOM; the viewport shows 3, 2 or 1 at a time.
const viewport = document.querySelector(".gallery-viewport");
const slides = Array.from(document.querySelectorAll(".gallery-slide"));
const controls = document.querySelector(".gallery-controls");
const status = document.querySelector("#gallery-status");

if (viewport && slides.length && controls) {
  let index = 0;
  const buttons = Array.from(controls.querySelectorAll("button"));

  function getVisibleCount() {
    if (window.matchMedia("(max-width: 767px)").matches) return 1;
    if (window.matchMedia("(max-width: 1100px)").matches) return 2;
    return 3;
  }

  function update({ announce = false } = {}) {
    const visibleCount = getVisibleCount();
    const lastIndex = Math.max(0, slides.length - visibleCount);
    index = Math.min(index, lastIndex);

    const step = slides.length > 1
      ? slides[1].offsetLeft - slides[0].offsetLeft
      : slides[0].getBoundingClientRect().width;

    viewport.scrollLeft = index * step;

    if (buttons[0]) buttons[0].disabled = index === 0;
    if (buttons[1]) buttons[1].disabled = index === lastIndex;

    slides.forEach((slide, i) => {
      slide.setAttribute("aria-hidden", String(i < index || i >= index + visibleCount));
    });

    if (status) {
      const end = Math.min(index + visibleCount, slides.length);
      status.textContent = announce
        ? `全${slides.length}枚中、${index + 1}〜${end}枚目を表示`
        : "";
    }
  }

  controls.hidden = false;
  viewport.style.overflowX = "hidden";

  buttons.forEach(button => {
    button.addEventListener("click", () => {
      const visibleCount = getVisibleCount();
      const lastIndex = Math.max(0, slides.length - visibleCount);
      index = Math.max(0, Math.min(lastIndex, index + Number(button.dataset.direction)));
      update({ announce:true });
    });
  });

  let resizeFrame = 0;
  const refresh = () => {
    cancelAnimationFrame(resizeFrame);
    resizeFrame = requestAnimationFrame(() => update());
  };

  if ("ResizeObserver" in window) {
    new ResizeObserver(refresh).observe(viewport);
  } else {
    window.addEventListener("resize", refresh);
  }

  update();
}

// Accessible mobile/tablet navigation.
const siteHeader = document.querySelector(".site-header");
const navToggle = document.querySelector(".nav-toggle");
const globalNav = document.querySelector("#global-nav");

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
      closeMenu({ returnFocus:true });
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

