$(document).ready(function() {
  window.setTimeout(function() {
    $(".alert:not(.alert-dismissible)").fadeTo(500, 0).slideUp(500, function() {
      $(this).remove();
    });
  }, 5000);
});
