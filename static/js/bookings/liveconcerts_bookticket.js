// Global variables
let currentTicketType = "NORMAL";
let currentQuantity = 1;
let ticketPrices, fees, gstPercentage, maxSeats;

// Initialize concert data from HTML
function initializeConcertData() {
  const concertData = document.getElementById("concert-data");

  if (!concertData) {
    console.error("Concert data element not found");
    return false;
  }

  ticketPrices = {
    NORMAL: parseFloat(concertData.dataset.normalPrice),
    COUPLES: parseFloat(concertData.dataset.couplesPrice),
    VIP: parseFloat(concertData.dataset.vipPrice),
    VVIP: parseFloat(concertData.dataset.vvipPrice),
  };

  fees = {
    province: parseFloat(concertData.dataset.provinceFee),
    convenience: parseFloat(concertData.dataset.convenienceFee),
    charity: parseFloat(concertData.dataset.charityFee),
  };

  gstPercentage = parseFloat(concertData.dataset.gstPercentage);
  maxSeats = parseInt(concertData.dataset.availableSeats);

  return true;
}

function updateQuantity(value) {
  const quantityInput = document.getElementById("quantity");

  if (value < 1) value = 1;
  if (value > maxSeats) value = maxSeats;

  quantityInput.value = value;
  currentQuantity = value;
  calculateTotal();
}

function incrementQuantity() {
  updateQuantity(currentQuantity + 1);
}

function decrementQuantity() {
  updateQuantity(currentQuantity - 1);
}
function calculateTotal() {
  if (!ticketPrices || !fees) {
    console.error("Concert data not initialized");
    return;
  }

  const basePrice = ticketPrices[currentTicketType] * currentQuantity;
  const gstAmount = (basePrice * gstPercentage) / 100;

  // Individual fees
  const platformFee = fees.province * currentQuantity;
  const convenienceFee = fees.convenience * currentQuantity;
  const charityFee = fees.charity * currentQuantity;
  const totalFees = platformFee + convenienceFee + charityFee;

  const totalAmount = basePrice + gstAmount + totalFees;

  // Update UI
  const basePriceElement = document.getElementById("basePrice");
  const gstAmountElement = document.getElementById("gstAmount");
  const feesAmountElement = document.getElementById("feesAmount");
  const totalAmountElement = document.getElementById("totalAmount");
  const platformFeeElement = document.getElementById("platformFee");
  const convenienceFeeElement = document.getElementById("convenienceFee");
  const charityFeeElement = document.getElementById("charityFee");

  if (basePriceElement)
    basePriceElement.textContent = `₹${basePrice.toFixed(2)}`;
  if (gstAmountElement)
    gstAmountElement.textContent = `₹${gstAmount.toFixed(2)}`;
  if (feesAmountElement)
    feesAmountElement.textContent = `₹${totalFees.toFixed(2)}`;
  if (totalAmountElement)
    totalAmountElement.textContent = `₹${totalAmount.toFixed(2)}`;
  if (platformFeeElement)
    platformFeeElement.textContent = `₹${platformFee.toFixed(2)}`;
  if (convenienceFeeElement)
    convenienceFeeElement.textContent = `₹${convenienceFee.toFixed(2)}`;
  if (charityFeeElement)
    charityFeeElement.textContent = `₹${charityFee.toFixed(2)}`;
}
// Event listeners
document.addEventListener("DOMContentLoaded", function () {
  // Initialize concert data first
  if (!initializeConcertData()) {
    return;
  }

  // Ticket type selection
  document.querySelectorAll('input[name="ticket_type"]').forEach((radio) => {
    radio.addEventListener("change", function () {
      currentTicketType = this.value;
      calculateTotal();
    });
  });

  // Quantity input
  const quantityInput = document.getElementById("quantity");
  if (quantityInput) {
    quantityInput.addEventListener("input", function () {
      updateQuantity(parseInt(this.value) || 1);
    });
  }

  // Increment/Decrement buttons
  const incrementBtn = document.querySelector(
    'button[onclick="incrementQuantity()"]'
  );
  const decrementBtn = document.querySelector(
    'button[onclick="decrementQuantity()"]'
  );

  if (incrementBtn) {
    incrementBtn.addEventListener("click", incrementQuantity);
  }
  if (decrementBtn) {
    decrementBtn.addEventListener("click", decrementQuantity);
  }

  // Remove onclick attributes from HTML and use event listeners instead
  const manualIncrementBtn = document.querySelector(
    'button[onclick*="incrementQuantity"]'
  );
  const manualDecrementBtn = document.querySelector(
    'button[onclick*="decrementQuantity"]'
  );

  if (manualIncrementBtn) {
    manualIncrementBtn.removeAttribute("onclick");
    manualIncrementBtn.addEventListener("click", incrementQuantity);
  }
  if (manualDecrementBtn) {
    manualDecrementBtn.removeAttribute("onclick");
    manualDecrementBtn.addEventListener("click", decrementQuantity);
  }

  // Initial calculation
  calculateTotal();
});
