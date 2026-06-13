const menuToggle = document.querySelector(".menu-toggle");
const siteNav = document.querySelector(".site-nav");
const filterButtons = [...document.querySelectorAll("[data-filter]")];
const publicationRows = [...document.querySelectorAll(".publication-row")];
const railButtons = [...document.querySelectorAll("[data-rail-target]")];
const autoplayRails = [...document.querySelectorAll("[data-rail-autoplay='true']")];
const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

function getRailStep(viewport) {
  return Math.max(280, Math.round(viewport.clientWidth * 0.82));
}

function getRailLoopWidth(viewport) {
  return Number(viewport.dataset.railLoopWidth || "0");
}

function normalizeRailPosition(viewport) {
  const loopWidth = getRailLoopWidth(viewport);

  if (!loopWidth) {
    return;
  }

  while (viewport.scrollLeft >= loopWidth) {
    viewport.scrollLeft -= loopWidth;
  }

  while (viewport.scrollLeft < 0) {
    viewport.scrollLeft += loopWidth;
  }
}

function prepareLoopingRail(viewport) {
  if (viewport.dataset.railPrepared === "true") {
    const originalCount = Number(viewport.dataset.railOriginalCount || "0");
    const originalFirst = viewport.children[0];
    const firstClone = originalCount ? viewport.children[originalCount] : null;

    if (originalFirst && firstClone) {
      viewport.dataset.railLoopWidth = String(firstClone.offsetLeft - originalFirst.offsetLeft);
    }

    normalizeRailPosition(viewport);
    return;
  }

  const originalCards = [...viewport.children];

  if (!originalCards.length) {
    return;
  }

  viewport.dataset.railOriginalCount = String(originalCards.length);

  originalCards.forEach((card) => {
    const clone = card.cloneNode(true);
    clone.setAttribute("aria-hidden", "true");
    clone.querySelectorAll("a, button, input, select, textarea").forEach((node) => {
      node.setAttribute("tabindex", "-1");
      node.setAttribute("aria-hidden", "true");
    });
    viewport.append(clone);
  });

  viewport.dataset.railPrepared = "true";
  prepareLoopingRail(viewport);
}

function moveRail(viewport, direction) {
  const loopWidth = getRailLoopWidth(viewport);
  const maxScroll = Math.max(0, viewport.scrollWidth - viewport.clientWidth);

  if (!maxScroll) {
    return;
  }

  normalizeRailPosition(viewport);

  if (loopWidth && direction < 0 && viewport.scrollLeft <= getRailStep(viewport) + 12) {
    viewport.scrollLeft += loopWidth;
  }

  if (!loopWidth) {
    if (direction > 0 && viewport.scrollLeft >= maxScroll - 12) {
      viewport.scrollTo({
        left: 0,
        behavior: "smooth",
      });
      return;
    }

    if (direction < 0 && viewport.scrollLeft <= 12) {
      viewport.scrollTo({
        left: maxScroll,
        behavior: "smooth",
      });
      return;
    }
  }

  viewport.scrollBy({
    left: getRailStep(viewport) * direction,
    behavior: "smooth",
  });

  window.setTimeout(() => {
    normalizeRailPosition(viewport);
  }, 460);
}

if (menuToggle && siteNav) {
  menuToggle.addEventListener("click", () => {
    const isExpanded = menuToggle.getAttribute("aria-expanded") === "true";
    menuToggle.setAttribute("aria-expanded", String(!isExpanded));
    siteNav.classList.toggle("is-open", !isExpanded);
  });

  siteNav.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      menuToggle.setAttribute("aria-expanded", "false");
      siteNav.classList.remove("is-open");
    });
  });
}

if (filterButtons.length && publicationRows.length) {
  filterButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const filter = button.dataset.filter || "all";

      filterButtons.forEach((item) => {
        item.classList.toggle("is-active", item === button);
      });

      publicationRows.forEach((row) => {
        const topics = row.dataset.topics || "";
        row.hidden = filter !== "all" && !topics.includes(filter);
      });
    });
  });
}

if (railButtons.length) {
  railButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const targetId = button.dataset.railTarget;
      const direction = Number(button.dataset.railDirection || "1");
      const viewport = targetId ? document.getElementById(targetId) : null;

      if (!viewport) {
        return;
      }

      viewport.__railStop?.();
      moveRail(viewport, direction);
      viewport.__railScheduleResume?.();
    });
  });
}

if (autoplayRails.length) {
  autoplayRails.forEach((viewport) => {
    prepareLoopingRail(viewport);

    const speedPxPerSecond = Number(viewport.dataset.railSpeed || "26");
    const resumeDelayMs = Number(viewport.dataset.railResumeDelay || "1400");
    let frameId = 0;
    let resumeId = 0;
    let lastTimestamp = 0;
    let driftPosition = viewport.scrollLeft;

    const stop = () => {
      window.cancelAnimationFrame(frameId);
      frameId = 0;
      lastTimestamp = 0;
    };

    const tick = (timestamp) => {
      if (!frameId) {
        return;
      }

      if (!lastTimestamp) {
        lastTimestamp = timestamp;
      }

      const deltaSeconds = (timestamp - lastTimestamp) / 1000;
      lastTimestamp = timestamp;

      if (!document.hidden) {
        driftPosition += speedPxPerSecond * deltaSeconds;

        const loopWidth = getRailLoopWidth(viewport);

        if (loopWidth) {
          while (driftPosition >= loopWidth) {
            driftPosition -= loopWidth;
          }

          while (driftPosition < 0) {
            driftPosition += loopWidth;
          }
        }

        viewport.scrollLeft = driftPosition;
      }

      frameId = window.requestAnimationFrame(tick);
    };

    const start = () => {
      if (prefersReducedMotion.matches) {
        return;
      }

      prepareLoopingRail(viewport);

      if (frameId || viewport.scrollWidth <= viewport.clientWidth + 8) {
        return;
      }

      driftPosition = viewport.scrollLeft;
      lastTimestamp = 0;
      frameId = window.requestAnimationFrame(tick);
    };

    const scheduleResume = () => {
      window.clearTimeout(resumeId);
      resumeId = window.setTimeout(start, resumeDelayMs);
    };

    viewport.__railStop = stop;
    viewport.__railScheduleResume = scheduleResume;
    viewport.__railSyncPosition = () => {
      driftPosition = viewport.scrollLeft;
    };

    viewport.addEventListener("pointerenter", stop);
    viewport.addEventListener("pointerleave", scheduleResume);
    viewport.addEventListener("focusin", stop);
    viewport.addEventListener("focusout", scheduleResume);
    viewport.addEventListener("touchstart", () => {
      stop();
      scheduleResume();
    }, { passive: true });
    viewport.addEventListener("wheel", () => {
      stop();
      scheduleResume();
    }, { passive: true });

    start();

    window.addEventListener("resize", () => {
      stop();
      prepareLoopingRail(viewport);
      scheduleResume();
    });
  });
}
