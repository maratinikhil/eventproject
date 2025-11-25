// Read variables from data attributes
const bookingData = document.getElementById("booking-data");
const isWonderla = bookingData
  ? bookingData.dataset.isWonderla === "true"
  : false;
const parkTicketPrice = bookingData
  ? parseFloat(bookingData.dataset.ticketPrice)
  : 0;

console.log(
  "Booking Data - isWonderla:",
  isWonderla,
  "parkTicketPrice:",
  parkTicketPrice
);

// Ticket information details
const ticketDetails = {
  regular_adult: "Unlimited access to land and water rides",
  regular_child: "Unlimited access to land and water rides",
  regular_senior:
    "Unlimited access to land and water rides. 25% discount for senior citizens with valid Govt ID proof (Aadhar card, driving license, or PAN card)",
  offer_student:
    "Limited-time offer. 25% off for students with valid school or college ID (age up to 21 years)",
  offer_defence: "Limited-time offer for defence families with valid ID proof",
  fasttrack_adult_buffet:
    "Skip the queue | 75% faster. Height above 140 cms. Includes buffet",
  fasttrack_child_buffet:
    "Skip the queue | 75% faster. Height between 85 cms to 140 cms. Includes buffet. Free for kids less than 85 cms",
  fasttrack_adult: "Skip the queue | 75% faster. Height above 140 cms",
  fasttrack_child:
    "Skip the queue | 75% faster. Height between 85 cms to 140 cms. Free for kids less than 85 cms",
};

// Track selected tickets
let selectedTickets = {};

// Toggle category expansion
function toggleCategory(header) {
  const category = header.parentElement;
  const content = category.querySelector(".category-content");
  const icon = header.querySelector("svg");

  content.classList.toggle("hidden");
  icon.classList.toggle("rotate-180");
}

// Helper function to get display name for ticket type
function getDisplayName(type) {
  const names = {
    regular_adult: "Regular Adult",
    regular_child: "Regular Child",
    regular_senior: "Regular Senior Citizen",
    offer_student: "Student Offer",
    offer_defence: "Defence Family",
    fasttrack_adult_buffet: "Fasttrack Adult + Buffet",
    fasttrack_child_buffet: "Fasttrack Child + Buffet",
    fasttrack_adult: "Fasttrack Adult",
    fasttrack_child: "Fasttrack Child",
  };
  return names[type] || type;
}

// Update ticket summary when quantity changes
function updateTicketSummary() {
  const summaryContent = document.getElementById("ticketSummaryContent");
  const totalAmountElement = document.getElementById("totalAmount");

  // Reset selected tickets
  selectedTickets = {};

  // Get all quantity inputs with values > 0
  const quantityInputs = document.querySelectorAll(".ticket-quantity");
  let totalAmount = 0;
  let hasTickets = false;

  quantityInputs.forEach((input) => {
    const quantity = parseInt(input.value) || 0;
    if (quantity > 0) {
      const price = parseInt(input.getAttribute("data-price")) || 0;
      const type = input.getAttribute("data-type");
      const ticketTotal = quantity * price;

      selectedTickets[type] = {
        quantity: quantity,
        price: price,
        total: ticketTotal,
      };

      totalAmount += ticketTotal;
      hasTickets = true;
    }
  });

  // Update summary display
  if (hasTickets) {
    let summaryHTML = "";
    for (const [type, details] of Object.entries(selectedTickets)) {
      const displayName = getDisplayName(type);
      summaryHTML += `
                <div class="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700">
                    <div>
                        <span class="font-medium">${displayName}</span>
                        <span class="text-sm text-gray-500 ml-2">x${details.quantity}</span>
                    </div>
                    <span class="font-semibold">₹${details.total}</span>
                </div>
            `;
    }
    summaryContent.innerHTML = summaryHTML;
  } else {
    summaryContent.innerHTML =
      '<p class="text-center py-4">No tickets selected yet</p>';
  }

  // Update total amount
  totalAmountElement.textContent = `₹${totalAmount}`;

  // Update the main calculation
  calculateTotal();
}

// Main calculation function
function calculateTotal() {
  let subtotal = 0;

  console.log("calculateTotal called - isWonderla:", isWonderla);
  console.log("selectedTickets:", selectedTickets);

  if (isWonderla) {
    // Calculate for Wonderla tickets
    for (const [type, details] of Object.entries(selectedTickets)) {
      subtotal += details.total;
    }
  } else {
    // Calculate for simple booking
    const quantity =
      parseInt(document.getElementById("simpleQuantity").value) || 0;
    const price = parseFloat(parkTicketPrice) || 0;
    subtotal = quantity * price;
    console.log(
      "Simple booking - quantity:",
      quantity,
      "price:",
      price,
      "subtotal:",
      subtotal
    );
  }

  const gst = subtotal * 0.18;
  const total = subtotal + gst;

  console.log(
    "Final calculation - subtotal:",
    subtotal,
    "gst:",
    gst,
    "total:",
    total
  );

  // Update all display elements
  document.getElementById("subtotalAmount").textContent =
    "₹" + subtotal.toFixed(2);
  document.getElementById("gstAmount").textContent = "₹" + gst.toFixed(2);
  document.getElementById("finalAmount").textContent = "₹" + total.toFixed(2);
  document.getElementById("paymentTotalAmount").textContent =
    "₹" + total.toFixed(2);

  updateTicketBreakdown();
}

// Update ticket breakdown in order summary
function updateTicketBreakdown() {
  const breakdown = document.getElementById("ticketBreakdown");
  breakdown.innerHTML = "";

  console.log("updateTicketBreakdown called - isWonderla:", isWonderla);

  if (isWonderla) {
    for (const [type, details] of Object.entries(selectedTickets)) {
      const displayName = getDisplayName(type);
      const itemDiv = document.createElement("div");
      itemDiv.className = "flex justify-between text-sm";
      itemDiv.innerHTML = `
                <div>
                    <div class="font-medium text-gray-800 dark:text-white">${displayName}</div>
                    <div class="text-gray-500 dark:text-gray-400">${
                      details.quantity
                    } × ₹${details.price}</div>
                </div>
                <div class="font-semibold text-gray-800 dark:text-white">₹${details.total.toFixed(
                  2
                )}</div>
            `;
      breakdown.appendChild(itemDiv);
    }

    // Show message if no tickets selected
    if (Object.keys(selectedTickets).length === 0) {
      const emptyDiv = document.createElement("div");
      emptyDiv.className = "text-center text-gray-500 dark:text-gray-400 py-4";
      emptyDiv.textContent = "No tickets selected yet";
      breakdown.appendChild(emptyDiv);
    }
  } else {
    const quantity =
      parseInt(document.getElementById("simpleQuantity").value) || 0;
    const price = parseFloat(parkTicketPrice) || 0;
    const total = quantity * price;

    const itemDiv = document.createElement("div");
    itemDiv.className = "flex justify-between text-sm";
    itemDiv.innerHTML = `
            <div>
                <div class="font-medium text-gray-800 dark:text-white">General Admission</div>
                <div class="text-gray-500 dark:text-gray-400">${quantity} × ₹${price}</div>
            </div>
            <div class="font-semibold text-gray-800 dark:text-white">₹${total.toFixed(
              2
            )}</div>
        `;
    breakdown.appendChild(itemDiv);
  }
}

// Initialize event listeners
document.addEventListener("DOMContentLoaded", function () {
  console.log("DOM loaded - initializing event listeners");
  console.log(
    "Global variables - isWonderla:",
    isWonderla,
    "parkTicketPrice:",
    parkTicketPrice
  );

  // Check if variables are defined
  if (typeof isWonderla === "undefined") {
    console.error("isWonderla is not defined!");
    return;
  }

  if (typeof parkTicketPrice === "undefined") {
    console.error("parkTicketPrice is not defined!");
    return;
  }

  // Wonderla event listeners
  if (isWonderla) {
    console.log("Setting up Wonderla event listeners");
    const quantityInputs = document.querySelectorAll(".ticket-quantity");
    console.log("Found quantity inputs:", quantityInputs.length);

    quantityInputs.forEach((input) => {
      input.addEventListener("input", updateTicketSummary);
      input.addEventListener("change", updateTicketSummary);
    });

    // Expand first category by default
    const firstCategory = document.querySelector(".ticket-category");
    if (firstCategory) {
      firstCategory
        .querySelector(".category-content")
        .classList.remove("hidden");
      firstCategory.querySelector("svg").classList.add("rotate-180");
    }
  } else {
    // Simple booking event listeners
    console.log("Setting up simple booking event listeners");
    const simpleQuantity = document.getElementById("simpleQuantity");
    if (simpleQuantity) {
      simpleQuantity.addEventListener("input", calculateTotal);
      simpleQuantity.addEventListener("change", calculateTotal);
    }
  }

  // Initial calculation
  calculateTotal();

  // Form submission handler
  document
    .getElementById("bookingForm")
    .addEventListener("submit", function (e) {
      const total =
        parseFloat(
          document.getElementById("finalAmount").textContent.replace("₹", "")
        ) || 0;
      if (total === 0) {
        e.preventDefault();
        alert(
          "Please select at least one ticket before proceeding to payment."
        );
      }
    });
});
