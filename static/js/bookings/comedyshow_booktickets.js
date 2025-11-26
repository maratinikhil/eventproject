function updateTotalPrice() {
  // Get values from data attributes
  const dataElement = document.getElementById("comedy-show-data");
  const ticketPrice = parseFloat(dataElement.getAttribute("data-ticket-price"));
  const availableSeats = parseInt(
    dataElement.getAttribute("data-available-seats")
  );

  let ticketCount =
    parseInt(document.getElementById("number_of_tickets").value) || 1;

  console.log("Ticket Price:", ticketPrice);
  console.log("Available Seats:", availableSeats);
  console.log("Ticket Count:", ticketCount);

  // Validate ticket count
  if (ticketCount > availableSeats) {
    document.getElementById("number_of_tickets").value = availableSeats;
    ticketCount = availableSeats;
  }

  if (ticketCount < 1) {
    document.getElementById("number_of_tickets").value = 1;
    ticketCount = 1;
  }

  const totalPrice = ticketCount * ticketPrice;

  console.log("Total Price:", totalPrice);

  // Update displays
  document.getElementById("ticket-count").textContent = ticketCount;
  document.getElementById("total-price").textContent = totalPrice.toFixed(2);
  document.getElementById("button-total").textContent = totalPrice.toFixed(2);

  // Update availability text
  const remainingSeats = availableSeats - ticketCount;
  document.getElementById(
    "availability-text"
  ).textContent = `${remainingSeats} seats will remain after this booking`;
}

// Initialize on page load and add event listeners
document.addEventListener("DOMContentLoaded", function () {
  updateTotalPrice();

  // Add event listeners for real-time updates
  const ticketInput = document.getElementById("number_of_tickets");
  if (ticketInput) {
    ticketInput.addEventListener("input", updateTotalPrice);
    ticketInput.addEventListener("change", updateTotalPrice);
  }
});
