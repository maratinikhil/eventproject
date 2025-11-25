// FAQ Accordion Functionality
document.addEventListener("DOMContentLoaded", function () {
  const faqQuestions = document.querySelectorAll(".faq-question");

  faqQuestions.forEach((question) => {
    question.addEventListener("click", function () {
      const answer = this.nextElementSibling;
      const icon = this.querySelector("i");

      // Toggle current answer
      answer.classList.toggle("hidden");
      icon.classList.toggle("rotate-180");

      // Close other answers
      faqQuestions.forEach((otherQuestion) => {
        if (otherQuestion !== question) {
          otherQuestion.nextElementSibling.classList.add("hidden");
          otherQuestion.querySelector("i").classList.remove("rotate-180");
        }
      });
    });
  });
});
