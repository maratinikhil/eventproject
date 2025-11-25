// static/admin/js/amusement_booking.js
(function ($) {
  "use strict";

  // Function to check if selected park is Wonderla
  function isWonderlaPark() {
    var parkSelect = $("#id_amusement_park");
    if (parkSelect.length === 0) return false;

    var selectedOption = parkSelect.find("option:selected");
    var parkName = selectedOption.text().toLowerCase();
    return parkName.includes("wonderla");
  }

  // Function to update URL parameter without reloading
  function updateUrlParameter(url, param, value) {
    var hash = {};
    var parser = document.createElement("a");
    parser.href = url;
    var parameters = parser.search.split(/\?|&/);

    for (var i = 0; i < parameters.length; i++) {
      if (!parameters[i]) continue;
      var ary = parameters[i].split("=");
      hash[ary[0]] = ary[1];
    }

    hash[param] = value;
    var list = [];
    Object.keys(hash).forEach(function (key) {
      list.push(key + "=" + hash[key]);
    });

    parser.search = "?" + list.join("&");
    return parser.href;
  }

  // Function to load tickets for selected park via AJAX
  function loadTicketsForPark(parkId) {
    if (!parkId) {
      // Clear all ticket dropdowns
      $('select[id$="-ticket_type"]').each(function () {
        $(this).html('<option value="">---------</option>');
      });
      return;
    }

    console.log("Loading tickets for park:", parkId);

    $.ajax({
      url: "/admin/get-park-tickets/" + parkId + "/",
      type: "GET",
      success: function (data) {
        console.log("Tickets data received:", data);
        if (data.success && data.tickets) {
          // Update ALL ticket type dropdowns
          $('select[id$="-ticket_type"]').each(function () {
            var dropdown = $(this);
            var currentValue = dropdown.val();

            dropdown.empty();
            dropdown.append('<option value="">---------</option>');

            if (!isWonderlaPark()) {
              dropdown.append(
                '<option value="general">General Admission</option>'
              );
            }

            data.tickets.forEach(function (ticket) {
              dropdown.append(
                $("<option></option>")
                  .attr("value", ticket.id)
                  .text(ticket.name)
              );
            });

            // For non-Wonderla parks, auto-select "General Admission"
            if (!isWonderlaPark() && !currentValue) {
              dropdown.val("general");
            } else if (currentValue) {
              dropdown.val(currentValue);
            }
          });
        } else {
          console.error("No tickets found for park");
          $('select[id$="-ticket_type"]').each(function () {
            var dropdown = $(this);
            dropdown.html('<option value="">---------</option>');
            if (!isWonderlaPark()) {
              dropdown.append(
                '<option value="general">General Admission</option>'
              );
              dropdown.val("general");
            }
          });
        }
      },
      error: function (xhr, status, error) {
        console.error("Error loading tickets:", error);
        $('select[id$="-ticket_type"]').each(function () {
          var dropdown = $(this);
          dropdown.html('<option value="">---------</option>');
          if (!isWonderlaPark()) {
            dropdown.append(
              '<option value="general">General Admission</option>'
            );
            dropdown.val("general");
          }
        });
      },
    });
  }

  // Function to toggle ticket type visibility
   function toggleTicketTypeVisibility() {
     var isWonderla = isWonderlaPark();
     console.log("Is Wonderla:", isWonderla);

     $(".dynamic-amusementbookingitem").each(function () {
       var $row = $(this);
       var $ticketTypeField = $row.find(".field-ticket_type");

       // Always show the ticket_type field, but handle it differently
       $ticketTypeField.show();

       if (!isWonderla) {
         // For non-Wonderla parks, we still show the field but auto-select "General Admission"
         console.log("Non-Wonderla park - auto-selecting General Admission");
       }
     });
   }


  // Function to update ticket prices when ticket type is selected
  function updateTicketPrices(selectElement) {
    var $select = $(selectElement);
    var ticketValue = $select.val();
    var $row = $select.closest(".dynamic-amusementbookingitem");

    if (ticketValue === "general") {
      // For general admission in non-Wonderla parks
      if (!isWonderlaPark()) {
        updatePricesForNonWonderla($row);
      }
    } else if (ticketValue && isWonderlaPark()) {
      // For Wonderla parks with specific ticket types
      console.log("Fetching details for Wonderla ticket:", ticketValue);
      $row.find('input[id$="-base_price"]').addClass("loading-price");

      $.ajax({
        url: "/admin/get-ticket-details/" + ticketValue + "/",
        type: "GET",
        success: function (data) {
          $row.find('input[id$="-base_price"]').removeClass("loading-price");

          if (data.success) {
            console.log("Ticket details:", data);
            $row.find('input[id$="-base_price"]').val(data.base_price);
            $row
              .find('input[id$="-discount_percent"]')
              .val(data.discount_percent);
            $row.find('input[id$="-gst_percent"]').val(data.gst_percent);

            // Trigger quantity change to recalculate totals
            var quantityInput = $row.find('input[id$="-quantity"]');
            if (!quantityInput.val() || quantityInput.val() === "0") {
              quantityInput.val("1");
            }
            quantityInput.trigger("change");
          } else {
            console.error("Error fetching ticket details:", data.error);
            $select.val("");
            clearPriceFields($row);
          }
        },
        error: function (xhr, status, error) {
          $row.find('input[id$="-base_price"]').removeClass("loading-price");
          console.error("AJAX Error:", error);
          $select.val("");
          clearPriceFields($row);
        },
      });
    } else {
      clearPriceFields($row);
    }
  }


  // Function to update prices for non-Wonderla parks
  function updatePricesForNonWonderla($row) {
    var parkSelect = $("#id_amusement_park");
    var parkId = parkSelect.val();

    if (parkId) {
      console.log("Fetching park price for non-Wonderla:", parkId);
      $.ajax({
        url: "/admin/get-park-price/" + parkId + "/",
        type: "GET",
        success: function (data) {
          if (data.success) {
            $row.find('input[id$="-base_price"]').val(data.ticket_price);
            $row.find('input[id$="-discount_percent"]').val("0");
            $row.find('input[id$="-gst_percent"]').val("18.00");

            // Trigger quantity change to recalculate totals
            var quantityInput = $row.find('input[id$="-quantity"]');
            if (!quantityInput.val() || quantityInput.val() === "0") {
              quantityInput.val("1");
            }
            quantityInput.trigger("change");
          }
        },
        error: function () {
          // Fallback price
          $row.find('input[id$="-base_price"]').val("1000.00");
          $row.find('input[id$="-discount_percent"]').val("0");
          $row.find('input[id$="-gst_percent"]').val("18.00");

          var quantityInput = $row.find('input[id$="-quantity"]');
          if (!quantityInput.val() || quantityInput.val() === "0") {
            quantityInput.val("1");
          }
          quantityInput.trigger("change");
        },
      });
    }
  }

  // Function to clear price fields
  function clearPriceFields($row) {
    $row.find('input[id$="-base_price"]').val("0.00");
    $row.find('input[id$="-discount_percent"]').val("0.00");
    $row.find('input[id$="-gst_percent"]').val("0.00");
    $row.find('input[id$="-subtotal"]').val("0.00");
    $row.find('input[id$="-gst_amount"]').val("0.00");
    $row.find('input[id$="-total_with_gst"]').val("0.00");
  }

  // Function to recalculate item totals
  function recalculateItemTotals(inputElement) {
    var $input = $(inputElement);
    var $row = $input.closest(".dynamic-amusementbookingitem");

    var basePrice =
      parseFloat($row.find('input[id$="-base_price"]').val()) || 0;
    var discountPercent =
      parseFloat($row.find('input[id$="-discount_percent"]').val()) || 0;
    var gstPercent =
      parseFloat($row.find('input[id$="-gst_percent"]').val()) || 0;
    var quantity = parseInt($input.val()) || 0;

    if (basePrice > 0 && quantity > 0) {
      var discountedPrice = basePrice - (basePrice * discountPercent) / 100;
      var subtotal = discountedPrice * quantity;
      var gstAmount = discountedPrice * (gstPercent / 100) * quantity;
      var totalWithGst = subtotal + gstAmount;

      $row.find('input[id$="-subtotal"]').val(subtotal.toFixed(2));
      $row.find('input[id$="-gst_amount"]').val(gstAmount.toFixed(2));
      $row.find('input[id$="-total_with_gst"]').val(totalWithGst.toFixed(2));
    } else {
      $row.find('input[id$="-subtotal"]').val("0.00");
      $row.find('input[id$="-gst_amount"]').val("0.00");
      $row.find('input[id$="-total_with_gst"]').val("0.00");
    }
  }

  // Function to initialize the form
  function initializeForm() {
    console.log("Initializing amusement booking form");

    // Get initial park ID
    var initialParkId = $("#id_amusement_park").val();
    var urlParams = new URLSearchParams(window.location.search);
    var urlParkId = urlParams.get("amusement_park");

    // Use URL parameter if available (for new bookings)
    if (urlParkId && !initialParkId) {
      $("#id_amusement_park").val(urlParkId);
      initialParkId = urlParkId;
    }

    console.log("Initial park ID:", initialParkId);

    if (initialParkId) {
      // Load tickets for the initial park
      loadTicketsForPark(initialParkId);

      // Wait a bit for tickets to load, then toggle visibility
      setTimeout(function () {
        toggleTicketTypeVisibility();

        if (isWonderlaPark()) {
          // For Wonderla, initialize existing ticket selections
          $('select[id$="-ticket_type"]').each(function () {
            if ($(this).val()) {
              updateTicketPrices(this);
            }
          });
        } else {
          updatePricesForNonWonderla();
        }
      }, 500);
    } else {
      toggleTicketTypeVisibility();
    }
  }

  // Main event handlers
  $(document).ready(function () {
    console.log("Amusement booking JS loaded");

    // Make sure all ticket_type fields are visible
    $(".field-ticket_type").show();

    // Initialize the form
    initializeForm();

    // Park change handler
    $(document).on("change", "#id_amusement_park", function () {
      var parkId = $(this).val();
      console.log("Park changed to:", parkId);

      // Load tickets for the selected park
      loadTicketsForPark(parkId);

      // Toggle visibility and update prices
      setTimeout(function () {
        toggleTicketTypeVisibility();

        if (isWonderlaPark()) {
          // For Wonderla, clear all prices initially
          $(".dynamic-amusementbookingitem").each(function () {
            clearPriceFields($(this));
          });
        } else {
          // For non-Wonderla, auto-populate prices for all rows
          $(".dynamic-amusementbookingitem").each(function () {
            var $row = $(this);
            // Make sure General Admission is selected
            var ticketSelect = $row.find('select[id$="-ticket_type"]');
            if (!ticketSelect.val()) {
              ticketSelect.val("general");
            }
            updatePricesForNonWonderla($row);
          });
        }
      }, 300);
    });

    // Ticket type change handler
    $(document).on("change", 'select[id$="-ticket_type"]', function () {
      console.log("Ticket type changed:", $(this).val());
      updateTicketPrices(this);
    });

    // Quantity change handler
    $(document).on("change", 'input[id$="-quantity"]', function () {
      recalculateItemTotals(this);
    });

    // Base price change handler (manual entry for Wonderla)
    $(document).on("change", 'input[id$="-base_price"]', function () {
      var $row = $(this).closest(".dynamic-amusementbookingitem");
      var quantityInput = $row.find('input[id$="-quantity"]');
      quantityInput.trigger("change");
    });

    // Handle new inline items being added
    $(document).on("click", ".add-row a", function () {
      setTimeout(function () {
        var parkId = $("#id_amusement_park").val();
        if (parkId) {
          loadTicketsForPark(parkId);
          setTimeout(function () {
            toggleTicketTypeVisibility();
          }, 200);
        }
      }, 100);
    });
  });
})(django.jQuery);
