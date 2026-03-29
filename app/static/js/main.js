/**
 * SeminarHub – Client-side validation & UX enhancements
 */

document.addEventListener('DOMContentLoaded', function () {

  /* ------------------------------------------------------------------ */
  /* Bootstrap 5 client-side form validation                             */
  /* ------------------------------------------------------------------ */
  const form = document.getElementById('registrationForm');
  if (form) {
    form.addEventListener('submit', function (event) {
      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      } else {
        // Show loading state on submit button
        const btn = document.getElementById('submitBtn');
        if (btn) {
          btn.classList.add('loading');
          btn.disabled = true;
          btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Submitting…';
        }
      }
      form.classList.add('was-validated');
    }, false);
  }

  /* ------------------------------------------------------------------ */
  /* Auto-dismiss flash alerts after 5 seconds                           */
  /* ------------------------------------------------------------------ */
  document.querySelectorAll('.alert.alert-dismissible').forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 5000);
  });

  /* ------------------------------------------------------------------ */
  /* Pre-select seminar from URL query param ?seminar=...                */
  /* ------------------------------------------------------------------ */
  const seminarSelect = document.getElementById('seminar');
  if (seminarSelect) {
    const params = new URLSearchParams(window.location.search);
    const preselect = params.get('seminar');
    if (preselect) {
      Array.from(seminarSelect.options).forEach(function (opt) {
        if (opt.value === preselect) opt.selected = true;
      });
    }
  }

});
