(function () {
  function initBestOneHomepage() {
    const track = document.getElementById('bo-gallery-track');
    const windowEl = document.getElementById('bo-gallery-window');

    if (!track || !windowEl) return;

    const slides = Array.from(track.querySelectorAll('.bo-gallery-slide'));
    const dots = Array.from(document.querySelectorAll('.bo-gallery-dot'));
    const prev = document.getElementById('bo-slider-prev');
    const next = document.getElementById('bo-slider-next');
    const counter = document.getElementById('bo-gallery-counter');

    if (!slides.length) return;

    let current = 0;
    let startX = 0;
    let endX = 0;
    let autoplay = null;
    let paused = false;

    const reducedMotion = window.matchMedia(
      '(prefers-reduced-motion: reduce)'
    ).matches;

    function showSlide(index) {
      current = (index + slides.length) % slides.length;

      track.style.transform = 'translateX(-' + (current * 100) + '%)';

      dots.forEach(function (dot, i) {
        const active = i === current;
        dot.classList.toggle('is-active', active);
        dot.setAttribute('aria-current', active ? 'true' : 'false');
      });

      if (counter) {
        counter.textContent =
          String(current + 1).padStart(2, '0') +
          ' / ' +
          String(slides.length).padStart(2, '0');
      }
    }

    function stopAutoplay() {
      if (autoplay) {
        window.clearInterval(autoplay);
        autoplay = null;
      }
    }

    function startAutoplay() {
      stopAutoplay();

      if (reducedMotion || paused || slides.length < 2) return;

      autoplay = window.setInterval(function () {
        showSlide(current + 1);
      }, 6000);
    }

    if (prev) {
      prev.addEventListener('click', function () {
        showSlide(current - 1);
        startAutoplay();
      });
    }

    if (next) {
      next.addEventListener('click', function () {
        showSlide(current + 1);
        startAutoplay();
      });
    }

    dots.forEach(function (dot) {
      dot.addEventListener('click', function () {
        showSlide(Number(dot.dataset.slide) || 0);
        startAutoplay();
      });
    });

    windowEl.addEventListener('mouseenter', function () {
      paused = true;
      stopAutoplay();
    });

    windowEl.addEventListener('mouseleave', function () {
      paused = false;
      startAutoplay();
    });

    windowEl.addEventListener('focusin', function () {
      paused = true;
      stopAutoplay();
    });

    windowEl.addEventListener('focusout', function (event) {
      if (!windowEl.contains(event.relatedTarget)) {
        paused = false;
        startAutoplay();
      }
    });

    windowEl.addEventListener('touchstart', function (event) {
      startX = event.changedTouches[0].clientX;
      endX = startX;
      paused = true;
      stopAutoplay();
    }, { passive: true });

    windowEl.addEventListener('touchend', function (event) {
      endX = event.changedTouches[0].clientX;
      const difference = endX - startX;

      if (Math.abs(difference) > 45) {
        showSlide(difference < 0 ? current + 1 : current - 1);
      }

      paused = false;
      startAutoplay();
    }, { passive: true });

    document.addEventListener('visibilitychange', function () {
      if (document.hidden) {
        stopAutoplay();
      } else {
        startAutoplay();
      }
    });

    showSlide(0);
    startAutoplay();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initBestOneHomepage);
  } else {
    initBestOneHomepage();
  }
})();