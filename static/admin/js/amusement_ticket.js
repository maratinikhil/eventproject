// static/admin/js/amusement_ticket.js
(function ($) {
  "use strict";

  function isWonderlaPark(parkName) {
    if (!parkName) return false;
    return parkName.toLowerCase().includes("wonderla");
  }

  function updateFormForPark(parkId) {
    var basePriceField = $("#id_base_price");
    var categoryField = $(".field-category");
    var subCategoryField = $(".field-sub_category");
    var basePriceHelp = $(".field-base_price .dynamic-help");

    // Remove existing help text
    if (basePriceHelp.length) {
      basePriceHelp.remove();
    }

    // Remove any existing help text from category/sub_category fields
    categoryField.find(".help-text").remove();
    subCategoryField.find(".help-text").remove();

    if (parkId) {
      $.ajax({
        url: "/admin/get-park-price/" + parkId + "/",
        type: "GET",
        success: function (data) {
          if (data.success) {
            var isWonderla = isWonderlaPark(data.park_name);

            if (!isWonderla) {
              // For non-Wonderla parks
              // Auto-populate base_price and make read-only
              basePriceField.val(data.ticket_price);
              basePriceField.prop("readonly", true);
              basePriceField.css("background-color", "#f8f9fa");

              // Hide category and sub_category fields
              categoryField.hide();
              subCategoryField.hide();

              // Add help text for base price
              $(".field-base_price").append(
                '<p class="help dynamic-help" style="color: #28a745; font-weight: bold;">' +
                  "Base price auto-populated from park ticket price</p>"
              );

              // Add help text for hidden fields
              var hiddenFieldsHelp = $(".field-category")
                .closest(".form-row")
                .find(".hidden-fields-help");
              if (!hiddenFieldsHelp.length) {
                $(".field-category")
                  .closest(".form-row")
                  .before(
                    '<div class="form-row" style="background: #e9f7ef; padding: 10px; border-radius: 4px; margin-bottom: 10px;">' +
                      '<p style="margin: 0; color: #28a745; font-weight: bold;">' +
                      "✓ Category and Sub-category are automatically set for non-Wonderla parks</p>" +
                      "</div>"
                  );
              }
            } else {
              // For Wonderla parks
              // Allow editing of base_price
              basePriceField.prop("readonly", false);
              basePriceField.css("background-color", "");

              // Show category and sub_category fields
              categoryField.show();
              subCategoryField.show();

              // Remove any hidden fields help
              $(".form-row")
                .has(".field-category")
                .prev(".form-row")
                .filter(function () {
                  return (
                    $(this).css("background-color") === "rgb(233, 247, 239)"
                  );
                })
                .remove();

              // Add help text for Wonderla
              $(".field-base_price").append(
                '<p class="help dynamic-help" style="color: #007bff;">' +
                  "For Wonderla parks, you can set custom base price and select ticket categories</p>"
              );
            }
          }
        },
        error: function () {
          // If AJAX fails, default to editable mode
          handleAJAXError();
        },
      });
    } else {
      // No park selected
      handleNoParkSelected();
    }
  }

  function handleAJAXError() {
    var basePriceField = $("#id_base_price");
    var categoryField = $(".field-category");
    var subCategoryField = $(".field-sub_category");

    basePriceField.prop("readonly", false);
    basePriceField.css("background-color", "");
    categoryField.show();
    subCategoryField.show();

    $(".field-base_price").append(
      '<p class="help dynamic-help" style="color: #dc3545;">Unable to fetch park details. Please set prices manually.</p>'
    );
  }

  function handleNoParkSelected() {
    var basePriceField = $("#id_base_price");
    var categoryField = $(".field-category");
    var subCategoryField = $(".field-sub_category");

    basePriceField.prop("readonly", false);
    basePriceField.css("background-color", "");
    categoryField.show();
    subCategoryField.show();

    $(".field-base_price").append(
      '<p class="help dynamic-help">Please select an amusement park first</p>'
    );
  }

  function initializeForm() {
    // Update form when amusement park changes
    $(document).on("change", "#id_amusement_park", function () {
      var parkId = $(this).val();
      updateFormForPark(parkId);
    });

    // Initialize on page load
    var initialParkId = $("#id_amusement_park").val();
    if (initialParkId) {
      updateFormForPark(initialParkId);
    } else {
      handleNoParkSelected();
    }

    // Handle inline forms in AmusementPark admin
    $(document).on("formset:added", function (event, $row, formsetName) {
      if (formsetName === "amusementticket_set") {
        // Reinitialize for new inline forms
        setTimeout(function () {
          var parkId = $("#id_amusement_park").val();
          if (parkId) {
            updateFormForPark(parkId);
          }
        }, 100);
      }
    });
  }

  // Initialize when document is ready
  $(document).ready(function () {
    initializeForm();
  });
})(django.jQuery);
