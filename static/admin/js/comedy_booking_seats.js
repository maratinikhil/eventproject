(function ($) {
  $(document).ready(function () {
    // Dynamic seat filtering based on comedy show selection
    function updateSeatsOptions() {
      var comedyShowId = $("#id_comedy_show").val();
      var seatsSelect = $("#id_seats");

      if (comedyShowId) {
        // Show loading
        seatsSelect.html(
          '<option value="">Loading available seats...</option>'
        );

        // Fetch available seats
        $.ajax({
          url: "/admin/eventapp/bookingcomedyshow/get-available-seats/",
          data: {
            comedy_show_id: comedyShowId,
          },
          dataType: "json",
          success: function (data) {
            seatsSelect.empty();
            if (data.results && data.results.length > 0) {
              $.each(data.results, function (index, seat) {
                seatsSelect.append(
                  $("<option></option>").val(seat.id).text(seat.text)
                );
              });
              // Enable select2 if available
              if ($.fn.select2) {
                seatsSelect.select2();
              }
            } else {
              seatsSelect.append(
                $('<option value="">No available seats for this show</option>')
              );
            }
          },
        });
      } else {
        seatsSelect.html(
          '<option value="">Select a comedy show first</option>'
        );
      }
    }

    // Update seats when comedy_show changes
    $("#id_comedy_show").change(function () {
      updateSeatsOptions();
    });

    // Initial update
    updateSeatsOptions();

    // Add seat visualization
    function renderSeatGrid() {
      var container = $('<div class="seat-grid-container"></div>');
      $(".field-seats").after(container);
      // You can extend this to show a visual seat map
    }
  });
})(django.jQuery);
