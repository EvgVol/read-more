// Select all module cards with the data-module-title attribute
const moduleCards = document.querySelectorAll("[data-module-title][data-id]");

// Click event handler for each module card
moduleCards.forEach((card) => {
  card.addEventListener("click", (event) => {
      // Get the module title and ID from the data attributes
      const moduleTitle = event.currentTarget.dataset.moduleTitle;
      const moduleId = event.currentTarget.dataset.id;

      // Find the first list group item in the Notifications panel and update its text content with the clicked module title
      const firstListGroupItem = document.querySelector(".sidebar-right .card-title");
      if (firstListGroupItem) {
          firstListGroupItem.textContent = moduleTitle;
      }

      // Hide all lessons in the Notifications panel
      const allLessons = document.querySelectorAll(".sidebar-right .list-group-item");
      allLessons.forEach(lesson => {
          lesson.style.display = "none";
      });

      // Show only the lessons belonging to the selected module
      const relatedLessons = document.querySelectorAll(`.sidebar-right .list-group-item[data-module-id="${moduleId}"]`);
      relatedLessons.forEach(lesson => {
          lesson.style.display = "list-item";
      });
  });
});