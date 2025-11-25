// static/js/signup.js

document.addEventListener("DOMContentLoaded", function () {
  console.log("Signup JS loaded successfully!"); // Debug line

  // Get DOM elements
  const mobileInput = document.getElementById("mobile");
  const passwordInput = document.getElementById("password");
  const confirmPasswordInput = document.getElementById("confirmPassword");
  const togglePasswordBtn = document.getElementById("togglePassword");
  const toggleConfirmPasswordBtn = document.getElementById(
    "toggleConfirmPassword"
  );
  const eyeIcon = document.getElementById("eyeIcon");
  const eyeConfirmIcon = document.getElementById("eyeConfirmIcon");
  const submitBtn = document.getElementById("submitBtn");
  const signupForm = document.getElementById("signupForm");

  // Password requirement check elements
  const lengthCheck = document.getElementById("lengthCheck");
  const numberCheck = document.getElementById("numberCheck");
  const specialCheck = document.getElementById("specialCheck");
  const matchCheck = document.getElementById("matchCheck");

  // Check if all elements exist
  if (!mobileInput || !passwordInput || !confirmPasswordInput) {
    console.error("Required form elements not found!");
    return;
  }

  // Mobile number formatting
  mobileInput.addEventListener("input", function (e) {
    let value = e.target.value.replace(/\D/g, ""); // Remove non-digits

    // Ensure it starts with +91
    if (!value.startsWith("91")) {
      value = "91" + value;
    }

    // Format as +91 XXXXX XXXXX
    if (value.length > 2) {
      const number = value.substring(2); // Remove 91
      if (number.length <= 5) {
        e.target.value = "+91 " + number;
      } else if (number.length <= 10) {
        e.target.value =
          "+91 " + number.substring(0, 5) + " " + number.substring(5);
      } else {
        e.target.value =
          "+91 " + number.substring(0, 5) + " " + number.substring(5, 10);
      }
    } else {
      e.target.value = "+91 ";
    }

    validateMobile();
  });

  // Mobile validation
  function validateMobile() {
    const value = mobileInput.value;
    const isValid = /^\+91\s[6-9]\d{4}\s\d{5}$/.test(value);

    if (value && !isValid) {
      mobileInput.classList.add("border-red-500");
      mobileInput.classList.remove("border-gray-300", "dark:border-gray-600");
    } else {
      mobileInput.classList.remove("border-red-500");
      mobileInput.classList.add("border-gray-300", "dark:border-gray-600");
    }

    updateSubmitButton();
    return isValid;
  }

  // Toggle password visibility
  togglePasswordBtn.addEventListener("click", function () {
    const type =
      passwordInput.getAttribute("type") === "password" ? "text" : "password";
    passwordInput.setAttribute("type", type);

    // Toggle eye icon
    if (type === "text") {
      eyeIcon.innerHTML =
        '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L6.59 6.59m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>';
    } else {
      eyeIcon.innerHTML =
        '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>';
    }
  });

  // Toggle confirm password visibility
  toggleConfirmPasswordBtn.addEventListener("click", function () {
    const type =
      confirmPasswordInput.getAttribute("type") === "password"
        ? "text"
        : "password";
    confirmPasswordInput.setAttribute("type", type);

    // Toggle eye icon
    if (type === "text") {
      eyeConfirmIcon.innerHTML =
        '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L6.59 6.59m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>';
    } else {
      eyeConfirmIcon.innerHTML =
        '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>';
    }
  });

  // Password validation
  passwordInput.addEventListener("input", function () {
    validatePassword();
    validatePasswordMatch();
  });

  confirmPasswordInput.addEventListener("input", validatePasswordMatch);

  function validatePassword() {
    const password = passwordInput.value;

    // Check minimum 8 characters
    const hasMinLength = password.length >= 8;
    updateCheckmark(lengthCheck, hasMinLength);

    // Check at least 1 number
    const hasNumber = /\d/.test(password);
    updateCheckmark(numberCheck, hasNumber);

    // Check at least 1 special character
    const hasSpecial = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password);
    updateCheckmark(specialCheck, hasSpecial);

    updateSubmitButton();

    return hasMinLength && hasNumber && hasSpecial;
  }

  function validatePasswordMatch() {
    const password = passwordInput.value;
    const confirmPassword = confirmPasswordInput.value;
    const passwordsMatch = password === confirmPassword && password.length > 0;

    updateCheckmark(matchCheck, passwordsMatch);

    if (confirmPassword) {
      if (passwordsMatch) {
        confirmPasswordInput.classList.remove("border-red-500");
        confirmPasswordInput.classList.add(
          "border-gray-300",
          "dark:border-gray-600"
        );
      } else {
        confirmPasswordInput.classList.add("border-red-500");
        confirmPasswordInput.classList.remove(
          "border-gray-300",
          "dark:border-gray-600"
        );
      }
    } else {
      confirmPasswordInput.classList.remove("border-red-500");
      confirmPasswordInput.classList.add(
        "border-gray-300",
        "dark:border-gray-600"
      );
    }

    updateSubmitButton();

    return passwordsMatch;
  }

  function updateCheckmark(element, isValid) {
    if (isValid) {
      element.innerHTML = "✓";
      element.classList.remove("bg-gray-200", "dark:bg-gray-700");
      element.classList.add("bg-green-500", "text-white");
    } else {
      element.innerHTML = "✓";
      element.classList.remove("bg-green-500", "text-white");
      element.classList.add("bg-gray-200", "dark:bg-gray-700");
    }
  }

  function updateSubmitButton() {
    const isMobileValid = validateMobile();
    const isPasswordValid = validatePassword();
    const isPasswordMatch = validatePasswordMatch();
    const isTermsChecked = document.getElementById("terms").checked;

    if (isMobileValid && isPasswordValid && isPasswordMatch && isTermsChecked) {
      submitBtn.disabled = false;
    } else {
      submitBtn.disabled = true;
    }
  }

  // Terms checkbox validation
  document
    .getElementById("terms")
    .addEventListener("change", updateSubmitButton);

  // Form submission validation
  signupForm.addEventListener("submit", function (e) {
    if (!validateMobile() || !validatePassword() || !validatePasswordMatch()) {
      e.preventDefault();
      alert("Please fix the validation errors before submitting.");
    }
  });

  // Initialize validation on page load
  updateSubmitButton();
});
