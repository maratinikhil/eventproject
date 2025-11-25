// static/js/base.js

// Theme Toggle
function initializeTheme() {
  const themeToggle = document.getElementById("theme-toggle");
  const htmlElement = document.documentElement;

  // Initialize theme
  if (
    localStorage.getItem("theme") === "dark" ||
    (!localStorage.getItem("theme") &&
      window.matchMedia("(prefers-color-scheme: dark)").matches)
  ) {
    htmlElement.classList.add("dark");
  }

  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      htmlElement.classList.toggle("dark");
      localStorage.setItem(
        "theme",
        htmlElement.classList.contains("dark") ? "dark" : "light"
      );
    });
  }
}

// Mobile Menu Toggle
function initializeMobileMenu() {
  const mobileMenuButton = document.getElementById("mobile-menu-button");
  const mobileMenu = document.getElementById("mobile-menu");

  if (mobileMenuButton && mobileMenu) {
    mobileMenuButton.addEventListener("click", () => {
      mobileMenu.classList.toggle("hidden");
      mobileMenu.classList.toggle("animate-slide-down");
    });

    // Close mobile menu when clicking outside
    document.addEventListener("click", (event) => {
      if (
        !mobileMenuButton.contains(event.target) &&
        !mobileMenu.contains(event.target)
      ) {
        mobileMenu.classList.add("hidden");
      }
    });
  }
}

// Smooth scroll for anchor links
function initializeSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute("href"));
      if (target) {
        target.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    });
  });
}

// Check if current page is public
function isPublicPage() {
  const currentPath = window.location.pathname;
  const publicPaths = [
    "/",
    "/login/",
    "/signup/",
    "/contactus/",
    "/aboutus/",
    "/help-center/",
    "/terms-conditions/",
    "/privacy-policy/",
    "/refund-policy/",
    "/login/otp/",
    "/login/password/",
  ];

  return publicPaths.some((path) => currentPath === path);
}

// Authentication and session management
function initializeAuth() {
  // Only run authentication check if we have the necessary variables
  if (typeof window.isAuthenticated === "undefined") {
    console.log("Authentication variables not defined");
    return;
  }

  const isAuthenticated = window.isAuthenticated;
  const currentPath = window.location.pathname;

  console.log("Auth check:", { isAuthenticated, currentPath });

  // If not authenticated and on protected page, redirect to login
  if (!isAuthenticated && !isPublicPage()) {
    console.log("Redirecting to login - not authenticated on protected page");
    // Use setTimeout to avoid redirect loops
    setTimeout(() => {
      window.location.href = window.loginUrl || "/";
    }, 100);
    return;
  }

  // If authenticated and on login page, redirect to home
  if (
    isAuthenticated &&
    (currentPath === "/" ||
      currentPath === "/login/" ||
      currentPath === "/signup/")
  ) {
    console.log("Redirecting to home - authenticated on login page");
    setTimeout(() => {
      window.location.href = window.homeUrl || "/home/";
    }, 100);
    return;
  }

  // Session timeout handling (only for authenticated users)
  if (isAuthenticated) {
    initializeSessionTimeout();
  }
}

// Session timeout handling
function initializeSessionTimeout() {
  let inactivityTimer;

  function resetTimer() {
    clearTimeout(inactivityTimer);
    // Set timeout for 1 hour (3600000 ms)
    inactivityTimer = setTimeout(logoutDueToInactivity, 60 * 60 * 1000);
  }

  function logoutDueToInactivity() {
    // Show session expired message
    if (window.isAuthenticated) {
      if (confirm("Your session has expired. Would you like to login again?")) {
        window.location.href = window.logoutUrl || "/logout/";
      }
    }
  }

  // Reset timer on user activity
  window.addEventListener("load", resetTimer);
  document.addEventListener("mousemove", resetTimer);
  document.addEventListener("keypress", resetTimer);
  document.addEventListener("click", resetTimer);
  document.addEventListener("scroll", resetTimer);

  // Also reset timer when page becomes visible again
  document.addEventListener("visibilitychange", function () {
    if (!document.hidden) {
      resetTimer();
    }
  });

  // Initialize the timer
  resetTimer();
}

// Toast notification system
function showToast(message, type = "info", duration = 5000) {
  const toastContainer = document.getElementById("toast-container");
  if (!toastContainer) return;

  const toastId = "toast-" + Date.now();
  const toast = document.createElement("div");

  // Base styles
  toast.id = toastId;
  toast.className = `p-4 rounded-lg shadow-lg transform transition-all duration-300 ease-in-out opacity-0 translate-x-full ${getToastStyles(
    type
  )}`;

  // Toast content
  toast.innerHTML = `
      <div class="flex items-start justify-between">
          <div class="flex items-start space-x-3">
              <span class="text-lg">${getToastIcon(type)}</span>
              <div class="flex-1">
                  <p class="text-sm font-medium">${message}</p>
              </div>
          </div>
          <button onclick="removeToast('${toastId}')" class="flex-shrink-0 ml-4 text-gray-400 hover:text-gray-600 transition">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
          </button>
      </div>
      ${
        duration > 0
          ? `<div class="mt-2 h-1 bg-black bg-opacity-10 rounded-full overflow-hidden">
          <div class="h-full bg-current transition-all duration-${duration} ease-linear toast-progress"></div>
      </div>`
          : ""
      }
  `;

  // Add to container
  toastContainer.appendChild(toast);

  // Animate in
  setTimeout(() => {
    toast.classList.remove("opacity-0", "translate-x-full");
    toast.classList.add("opacity-100", "translate-x-0");
  }, 10);

  // Start progress bar if duration is set
  if (duration > 0) {
    const progressBar = toast.querySelector(".toast-progress");
    if (progressBar) {
      setTimeout(() => {
        progressBar.style.width = "0%";
      }, 50);
    }

    // Auto remove after duration
    setTimeout(() => {
      removeToast(toastId);
    }, duration);
  }

  return toastId;
}

function removeToast(toastId) {
  const toast = document.getElementById(toastId);
  if (!toast) return;

  toast.classList.remove("opacity-100", "translate-x-0");
  toast.classList.add("opacity-0", "translate-x-full");

  setTimeout(() => {
    if (toast.parentNode) {
      toast.parentNode.removeChild(toast);
    }
  }, 300);
}

function getToastStyles(type) {
  const styles = {
    success:
      "bg-green-50 border border-green-200 text-green-800 dark:bg-green-900 dark:border-green-700 dark:text-green-200",
    error:
      "bg-red-50 border border-red-200 text-red-800 dark:bg-red-900 dark:border-red-700 dark:text-red-200",
    warning:
      "bg-yellow-50 border border-yellow-200 text-yellow-800 dark:bg-yellow-900 dark:border-yellow-700 dark:text-yellow-200",
    info: "bg-blue-50 border border-blue-200 text-blue-800 dark:bg-blue-900 dark:border-blue-700 dark:text-blue-200",
  };
  return styles[type] || styles.info;
}

function getToastIcon(type) {
  const icons = {
    success: "✅",
    error: "❌",
    warning: "⚠️",
    info: "ℹ️",
  };
  return icons[type] || icons.info;
}

// Quick access functions
const Toast = {
  success: (message, duration = 5000) =>
    showToast(message, "success", duration),
  error: (message, duration = 5000) => showToast(message, "error", duration),
  warning: (message, duration = 5000) =>
    showToast(message, "warning", duration),
  info: (message, duration = 5000) => showToast(message, "info", duration),
  remove: removeToast,
};

// Make Toast globally available
window.Toast = Toast;
window.removeToast = removeToast;

// Convert Django messages to toasts
function convertDjangoMessagesToToasts() {
  const messageContainer = document.getElementById("django-messages");
  if (!messageContainer) return;

  const messages = messageContainer.querySelectorAll(".message");

  messages.forEach((message) => {
    const type = message.getAttribute("data-type") || "info";
    const content = message.getAttribute("data-content");

    // Map Django message tags to toast types
    let toastType = "info";
    if (type === "success") toastType = "success";
    else if (type === "error" || type === "danger") toastType = "error";
    else if (type === "warning") toastType = "warning";
    else toastType = "info";

    if (content) {
      // Show toast with a small delay for better visual effect
      setTimeout(() => {
        Toast[toastType](content);
      }, 100 * Array.from(messages).indexOf(message));
    }
  });

  // Clear the messages container after processing
  messageContainer.innerHTML = "";
}

// Initialize all functionality when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  console.log("Initializing base.js functionality");
  initializeTheme();
  initializeMobileMenu();
  initializeSmoothScroll();
  convertDjangoMessagesToToasts(); // Convert Django messages to toasts

  // Add a small delay before auth check to ensure everything is loaded
  setTimeout(initializeAuth, 50);
});

// Export functions for potential reuse (if using modules)
if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    initializeTheme,
    initializeMobileMenu,
    initializeSmoothScroll,
    initializeAuth,
    initializeSessionTimeout,
    Toast,
    showToast,
    removeToast,
  };
}
