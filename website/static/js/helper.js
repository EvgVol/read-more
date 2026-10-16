// Активируем всплывающие подсказки
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  var tooltip = new bootstrap.Tooltip(tooltipTriggerEl);
  
  // Добавляем обработчик события показа подсказки
  tooltipTriggerEl.addEventListener('shown.bs.tooltip', function () {
    // Запускаем таймер для скрытия подсказки через 3 секунды
    setTimeout(function () {
      tooltip.hide();
    }, 3000);
  });
  
  return tooltip;
});