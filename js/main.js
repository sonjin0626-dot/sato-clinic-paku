"use strict";

// Six slides remain in the DOM; three are visible and each action moves one.
const viewport = document.querySelector(".gallery-viewport");
const slides = Array.from(document.querySelectorAll(".gallery-slide"));
const controls = document.querySelector(".gallery-controls");
const status = document.querySelector("#gallery-status");
if (viewport && slides.length && controls) {
  const visibleCount = 3;
  const lastIndex = slides.length - visibleCount;
  let index = 0;
  const buttons = Array.from(controls.querySelectorAll("button"));
  function update() {
    const step = slides[1].offsetLeft - slides[0].offsetLeft;
    viewport.scrollLeft = index * step;
    buttons[0].disabled = index === 0;
    buttons[1].disabled = index === lastIndex;
    slides.forEach((slide, i) => {
      slide.setAttribute("aria-hidden", String(i < index || i >= index + visibleCount));
    });
    status.textContent = "全" + slides.length + "枚中、" + (index + 1) + "〜" + (index + visibleCount) + "枚目を表示";
  }
  controls.hidden = false;
  viewport.style.overflowX = "hidden";
  buttons.forEach(button => button.addEventListener("click", () => {
    index = Math.max(0, Math.min(lastIndex, index + Number(button.dataset.direction)));
    update();
  }));
  // Keep the same three images after a desktop window is resized.
  new ResizeObserver(update).observe(viewport);
  update();
}

const dialog = document.querySelector("#notice-dialog");
document.querySelectorAll("[data-notice]").forEach(link => {
  link.addEventListener("click", event => {
    if (!dialog || typeof dialog.showModal !== "function") return;
    event.preventDefault();
    document.querySelector("#dialog-title").textContent = link.dataset.notice;
    dialog.showModal();
  });
});
