// Instant step switching for the course trainer.
//
// The page renders one step at a time (only the active step's content is in
// the DOM). Clicking a step in the stepper or the "back / next" links swaps
// the region in place with the fragment from /step/ (no full page reload),
// keeps ?step=N in the URL, and supports the browser back/forward buttons.
// Without JavaScript everything keeps working: every step link is a plain
// <a href="?step=N"> and the server renders each step on a full reload.

(function () {
  'use strict';

  var root = document.getElementById('course-trainer');
  if (!root) {
    return;
  }
  var fragmentUrl = root.getAttribute('data-lesson-fragment-url');
  if (!fragmentUrl) {
    return;
  }

  var region = root.querySelector('.course-learning__stage-region');
  if (!region) {
    return;
  }

  var MIN_STEP = 1;
  var MAX_STEP = 5;
  var inFlight = false;

  function clampStep(step) {
    if (!Number.isFinite(step)) {
      return MIN_STEP;
    }
    return Math.min(MAX_STEP, Math.max(MIN_STEP, step));
  }

  function currentStep() {
    return clampStep(parseInt(region.getAttribute('data-step') || '1', 10));
  }

  function pageUrlWithStep(step) {
    var url = new URL(window.location.href);
    url.searchParams.set('step', String(step));
    url.searchParams.delete('quiz_attempt');
    return url.toString();
  }

  function fragmentUrlWithStep(step) {
    var url = new URL(fragmentUrl, window.location.href);
    url.searchParams.set('step', String(step));
    return url.toString();
  }

  function swapRegion(html, step, pushState, focusActive) {
    var holder = document.createElement('div');
    holder.innerHTML = html;
    var nextRegion = holder.querySelector('.course-learning__stage-region');
    if (!nextRegion) {
      return;
    }
    region.replaceWith(nextRegion);
    region = nextRegion;

    if (pushState) {
      window.history.pushState({ lessonStep: step }, '', pageUrlWithStep(step));
    }
    if (focusActive) {
      var activeLink = region.querySelector('.course-learning__stepper-link[aria-current="step"]');
      if (activeLink) {
        activeLink.focus();
      }
    }
    // Read each step from the top: if the reader has scrolled past the top of
    // the region, snap back to it; otherwise (already at the top) leave them.
    var newTop = region.getBoundingClientRect().top + window.scrollY;
    if (newTop < window.scrollY - 120) {
      window.scrollTo({ top: Math.max(0, newTop - 12), behavior: 'smooth' });
    }
  }

  function fetchFragment(step) {
    return window
      .fetch(fragmentUrlWithStep(step), { headers: { Accept: 'text/html' } })
      .then(function (response) {
        if (!response.ok) {
          throw new Error('fragment http ' + response.status);
        }
        return response.text();
      });
  }

  function goToStep(step, push, focus) {
    step = clampStep(step);
    if (step === currentStep() || inFlight) {
      return;
    }
    inFlight = true;
    fetchFragment(step)
      .then(function (html) {
        swapRegion(html, step, push, focus);
      })
      .catch(function () {
        // Network/fragment problem: fall back to a normal full-page load.
        window.location.href = pageUrlWithStep(step);
      })
      .finally(function () {
        inFlight = false;
      });
  }

  // Seed history so browser back/forward works even on a direct ?step=N load.
  if (!window.history.state || !Number.isFinite(window.history.state.lessonStep)) {
    window.history.replaceState(
      { lessonStep: currentStep() },
      '',
      window.location.href,
    );
  }

  // Step links (stepper pills, arrows, "назад/следующий" buttons) delegate
  // through the stable root, because the region itself gets replaced.
  root.addEventListener('click', function (event) {
    var link = event.target.closest('a[data-step]');
    if (!link || !region.contains(link)) {
      return;
    }
    event.preventDefault();
    goToStep(parseInt(link.getAttribute('data-step') || '1', 10), true, true);
  });

  window.addEventListener('popstate', function (event) {
    if (!event.state || !Number.isFinite(event.state.lessonStep)) {
      return;
    }
    goToStep(event.state.lessonStep, false, false);
  });
})();