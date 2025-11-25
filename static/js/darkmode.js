document.addEventListener("DOMContentLoaded", () => {
  const themeToggle = document.getElementById("theme-toggle");
  const htmlElement = document.documentElement;

  if (localStorage.getItem("theme") === "dark") {
    htmlElement.classList.add("dark");
  }

  themeToggle.addEventListener("click", () => {
    htmlElement.classList.toggle("dark");
    localStorage.setItem(
      "theme",
      htmlElement.classList.contains("dark") ? "dark" : "light"
    );
  });
});
