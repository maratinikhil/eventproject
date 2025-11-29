// events_booking.js - Event Booking Page JavaScript

document.addEventListener("DOMContentLoaded", function () {
  // Initialize booking functionality
  initBookingPage();
});

function initBookingPage() {
  const ticketPrice = parseFloat(document.getElementById("ticket-price").value);
  const ticketSelect = document.getElementById("number_of_tickets");
  const quantityDisplay = document.getElementById("quantity-display");
  const totalAmountDisplay = document.getElementById("total-amount");
  const ticketPriceDisplay = document.getElementById("ticket-price-display");
  const bookingForm = document.getElementById("booking-form");
  const submitBtn = document.getElementById("submit-btn");
  const termsCheckbox = document.getElementById("terms_agree");

  // Initialize display values
  ticketPriceDisplay.textContent = ticketPrice.toFixed(2);

  // Ticket quantity change handler
  if (ticketSelect) {
    ticketSelect.addEventListener("change", function () {
      updatePriceCalculation();
      validateForm();
    });
  }

  // Terms agreement change handler
  if (termsCheckbox) {
    termsCheckbox.addEventListener("change", function () {
      validateForm();
    });
  }

  // Form submission handler
  if (bookingForm) {
    bookingForm.addEventListener("submit", function (e) {
      if (!validateFormSubmission()) {
        e.preventDefault();
        showNotification("Please fill all required fields correctly.", "error");
      } else {
        // Disable submit button to prevent double submission
        submitBtn.disabled = true;
        submitBtn.textContent = "Processing...";

        // Show loading state
        showNotification("Processing your booking...", "info");
      }
    });
  }

  // Input validation for customer information
  const customerName = document.getElementById("customer_name");
  const customerEmail = document.getElementById("customer_email");
  const customerPhone = document.getElementById("customer_phone");

  if (customerName) {
    customerName.addEventListener("blur", validateName);
  }

  if (customerEmail) {
    customerEmail.addEventListener("blur", validateEmail);
  }

  if (customerPhone) {
    customerPhone.addEventListener("blur", validatePhone);
  }

  // Initialize price calculation on page load
  updatePriceCalculation();
  validateForm();
}

function updatePriceCalculation() {
  const ticketPrice = parseFloat(document.getElementById("ticket-price").value);
  const ticketSelect = document.getElementById("number_of_tickets");
  const quantityDisplay = document.getElementById("quantity-display");
  const totalAmountDisplay = document.getElementById("total-amount");

  if (ticketSelect && quantityDisplay && totalAmountDisplay) {
    const quantity = parseInt(ticketSelect.value);
    const totalAmount = ticketPrice * quantity;

    quantityDisplay.textContent = quantity;
    totalAmountDisplay.textContent = `₹${totalAmount.toFixed(2)}`;
  }
}

function validateForm() {
  const termsCheckbox = document.getElementById("terms_agree");
  const submitBtn = document.getElementById("submit-btn");

  if (termsCheckbox && submitBtn) {
    submitBtn.disabled = !termsCheckbox.checked;
  }
}

function validateFormSubmission() {
  const customerName = document.getElementById("customer_name");
  const customerEmail = document.getElementById("customer_email");
  const termsCheckbox = document.getElementById("terms_agree");

  let isValid = true;

  // Validate name
  if (!validateName()) {
    isValid = false;
  }

  // Validate email
  if (!validateEmail()) {
    isValid = false;
  }

  // Validate terms agreement
  if (!termsCheckbox.checked) {
    isValid = false;
    highlightField(termsCheckbox, false);
  } else {
    highlightField(termsCheckbox, true);
  }

  return isValid;
}

function validateName() {
  const nameField = document.getElementById("customer_name");
  const name = nameField.value.trim();

  if (name === "") {
    highlightField(nameField, false);
    showFieldError(nameField, "Please enter your full name");
    return false;
  }

  if (name.length < 2) {
    highlightField(nameField, false);
    showFieldError(nameField, "Name must be at least 2 characters long");
    return false;
  }

  highlightField(nameField, true);
  clearFieldError(nameField);
  return true;
}

function validateEmail() {
  const emailField = document.getElementById("customer_email");
  const email = emailField.value.trim();
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (email === "") {
    highlightField(emailField, false);
    showFieldError(emailField, "Please enter your email address");
    return false;
  }

  if (!emailRegex.test(email)) {
    highlightField(emailField, false);
    showFieldError(emailField, "Please enter a valid email address");
    return false;
  }

  highlightField(emailField, true);
  clearFieldError(emailField);
  return true;
}

function validatePhone() {
  const phoneField = document.getElementById("customer_phone");
  const phone = phoneField.value.trim();

  // Phone is optional, but if provided, validate format
  if (phone !== "") {
    const phoneRegex = /^[\+]?[0-9\s\-\(\)]{10,}$/;

    if (!phoneRegex.test(phone)) {
      highlightField(phoneField, false);
      showFieldError(phoneField, "Please enter a valid phone number");
      return false;
    }
  }

  highlightField(phoneField, true);
  clearFieldError(phoneField);
  return true;
}

function highlightField(field, isValid) {
  if (isValid) {
    field.classList.remove("border-red-500", "dark:border-red-400");
    field.classList.add("border-green-500", "dark:border-green-400");
  } else {
    field.classList.remove("border-green-500", "dark:border-green-400");
    field.classList.add("border-red-500", "dark:border-red-400");
  }
}

function showFieldError(field, message) {
  // Remove existing error message
  clearFieldError(field);

  // Create error message element
  const errorElement = document.createElement("p");
  errorElement.className = "text-red-500 text-xs mt-1";
  errorElement.textContent = message;
  errorElement.id = `${field.id}-error`;

  // Insert after the field
  field.parentNode.appendChild(errorElement);
}

function clearFieldError(field) {
  const existingError = document.getElementById(`${field.id}-error`);
  if (existingError) {
    existingError.remove();
  }
}

function showNotification(message, type = "info") {
  // Remove existing notifications
  const existingNotifications = document.querySelectorAll(
    ".custom-notification"
  );
  existingNotifications.forEach((notification) => notification.remove());

  // Create notification element
  const notification = document.createElement("div");
  notification.className = `custom-notification fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg transform transition-transform duration-300 ${
    type === "error"
      ? "bg-red-100 text-red-700 border border-red-300"
      : type === "success"
      ? "bg-green-100 text-green-700 border border-green-300"
      : "bg-blue-100 text-blue-700 border border-blue-300"
  }`;

  notification.innerHTML = `
        <div class="flex items-center">
            <span class="mr-2">${getNotificationIcon(type)}</span>
            <span>${message}</span>
        </div>
    `;

  // Add to page
  document.body.appendChild(notification);

  // Animate in
  setTimeout(() => {
    notification.classList.add("translate-x-0", "opacity-100");
  }, 10);

  // Remove after 5 seconds
  setTimeout(() => {
    notification.classList.remove("translate-x-0", "opacity-100");
    notification.classList.add("translate-x-full", "opacity-0");
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 300);
  }, 5000);
}

function getNotificationIcon(type) {
  switch (type) {
    case "error":
      return "❌";
    case "success":
      return "✅";
    case "info":
      return "ℹ️";
    default:
      return "💡";
  }
}

// Utility function to format currency
function formatCurrency(amount) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    minimumFractionDigits: 2,
  }).format(amount);
}

// Export functions for potential use in other modules
if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    initBookingPage,
    updatePriceCalculation,
    validateFormSubmission,
    formatCurrency,
  };
}
