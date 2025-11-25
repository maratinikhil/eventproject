document.addEventListener("DOMContentLoaded", function () {
  const screenOptions = document.querySelectorAll('input[name="screen"]');
  const seats = document.querySelectorAll(".seat");
  const selectedSeatsSummary = document.getElementById(
    "selected-seats-summary"
  );
  const priceBreakdown = document.getElementById("price-breakdown");
  const submitBtn = document.getElementById("submit-btn");
  const clearSeatsBtn = document.getElementById("clear-seats");
  const bookingForm = document.getElementById("booking-form");

  let selectedSeats = [];

  // Handle screen selection change
  screenOptions.forEach((option) => {
    option.addEventListener("change", function () {
      // Clear selected seats when changing screens
      clearSelectedSeats();

      const screenId = this.value;
      const url = new URL(window.location.href);
      url.searchParams.set("screen", screenId);
      window.location.href = url.toString();
    });
  });

  // Handle seat selection
  seats.forEach((seat) => {
    seat.addEventListener("click", function () {
      // Don't allow selection if seat is disabled (booked)
      if (this.disabled || this.classList.contains("bg-red-500")) {
        return;
      }

      const seatId = this.dataset.seatId; // Use database seat ID
      const seatType = this.dataset.seatType;
      const row = this.dataset.row;
      const number = this.dataset.number;
      const price = parseFloat(this.dataset.price);

      const isSelected = this.classList.contains("bg-yellow-400");

      if (isSelected) {
        // Deselect seat
        this.classList.remove("bg-yellow-400", "border-yellow-500");
        this.classList.add(
          "bg-green-500",
          "border-green-600",
          "hover:bg-green-400"
        );
        selectedSeats = selectedSeats.filter((s) => s.id !== seatId);
      } else {
        // Select seat
        this.classList.remove(
          "bg-green-500",
          "border-green-600",
          "hover:bg-green-400"
        );
        this.classList.add("bg-yellow-400", "border-yellow-500");
        selectedSeats.push({
          id: seatId, // Use database ID
          row: row,
          number: number,
          type: seatType,
          price: price,
        });
      }

      updateBookingSummary();
    });
  });

  // Update booking summary
  function updateBookingSummary() {
    if (selectedSeats.length === 0) {
      selectedSeatsSummary.innerHTML = `
        <div class="text-center py-8 text-gray-500 dark:text-gray-400">
          <svg class="w-12 h-12 mx-auto mb-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
          </svg>
          <p>Select seats to continue</p>
        </div>
      `;
      if (priceBreakdown) {
        priceBreakdown.classList.add("hidden");
      }
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.classList.add("opacity-50", "cursor-not-allowed");
        submitBtn.classList.remove("hover:bg-red-600");
      }
      return;
    }

    // Update selected seats list
    let seatsHTML = "";
    let totalBasePrice = 0;

    selectedSeats.forEach((seat) => {
      totalBasePrice += seat.price;
      seatsHTML += `
        <div class="flex justify-between items-center bg-white dark:bg-gray-600 p-3 rounded-lg mb-2 last:mb-0">
          <div>
            <span class="font-semibold text-gray-900 dark:text-white">${
              seat.row
            }${seat.number}</span>
            <span class="text-sm text-gray-500 dark:text-gray-300 ml-2 capitalize">${
              seat.type
            }</span>
          </div>
          <div class="font-medium text-gray-900 dark:text-white">₹${seat.price.toFixed(
            2
          )}</div>
        </div>
      `;
    });

    selectedSeatsSummary.innerHTML = seatsHTML;

    // Update price breakdown
    if (priceBreakdown) {
      const platformFee = 2.0;
      const gstRate = 18;
      const gstAmount = ((totalBasePrice * gstRate) / 100).toFixed(2);
      const totalPrice = (
        parseFloat(totalBasePrice) +
        parseFloat(platformFee) +
        parseFloat(gstAmount)
      ).toFixed(2);

      document.getElementById("ticket-count").textContent =
        selectedSeats.length;
      document.getElementById("base-price").textContent =
        totalBasePrice.toFixed(2);
      document.getElementById("platform-fee").textContent =
        platformFee.toFixed(2);
      document.getElementById("gst-rate").textContent = gstRate;
      document.getElementById("gst-amount").textContent = gstAmount;
      document.getElementById("total-price").textContent = totalPrice;

      priceBreakdown.classList.remove("hidden");
    }

    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.classList.remove("opacity-50", "cursor-not-allowed");
      submitBtn.classList.add("hover:bg-red-600");
    }
  }

  // Clear all selected seats
  function clearSelectedSeats() {
    selectedSeats = [];

    // Reset all seat elements to available state
    seats.forEach((seat) => {
      if (!seat.disabled && !seat.classList.contains("bg-red-500")) {
        seat.classList.remove("bg-yellow-400", "border-yellow-500");
        seat.classList.add(
          "bg-green-500",
          "border-green-600",
          "hover:bg-green-400"
        );
      }
    });

    updateBookingSummary();
  }

  // Attach clear seats event listener if button exists
  if (clearSeatsBtn) {
    clearSeatsBtn.addEventListener("click", clearSelectedSeats);
  }

  // Handle form submission
  if (bookingForm) {
    bookingForm.addEventListener("submit", function (e) {
      // Check if a screen is selected
      const selectedScreen = document.querySelector(
        'input[name="screen"]:checked'
      );
      if (!selectedScreen) {
        e.preventDefault();
        alert("Please select a screen.");
        return;
      }

      if (selectedSeats.length === 0) {
        e.preventDefault();
        alert("Please select at least one seat.");
        return;
      }

      // Remove any previously added seat inputs to avoid duplicates
      const existingSeatInputs = this.querySelectorAll('input[name="seats"]');
      existingSeatInputs.forEach((input) => input.remove());

      // Add selected seats to form data
      selectedSeats.forEach((seat) => {
        const input = document.createElement("input");
        input.type = "hidden";
        input.name = "seats";
        input.value = seat.id; // Use database seat ID
        this.appendChild(input);
      });
    });
  }

  // Initialize booking summary on page load
  updateBookingSummary();

  // Add keyboard navigation for accessibility
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      clearSelectedSeats();
    }
  });
});
