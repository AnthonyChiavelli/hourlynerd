var launchPopup = function() {
    $("#popup").show();
}

var dismissPopup = function() {
    $('#popup').hide();
}

// When document is ready
$(function() {

    // For each of the individual zone checkboxes
    $(":checkbox[name='zone']").each(function() {
        // When the checked state is changed
        $(this).change(function() {
            // Toggle the visibility of the corresponding image
            var correspondingImage = "#" + $(this).val() + "Img";
            if ($(this).is(":checked")) {
                $(correspondingImage).show();
            }
            else {
                $(correspondingImage).hide();
            }
        });
    });


    // When the All Zones button is clicked
    $(":checkbox[value='all_zones']").click(function() {

        // If checked, check all boxes and make all images visible
        if ($(this).is(":checked")) {
            $(".overlay").show();
            $(":checkbox[name='zone']").each (function() {
                this.checked = true;

            });
        }
         // If not checked, uncheck all boxes and make all images invisible
        else {
            $(".overlay").hide();
            $(":checkbox[name='zone']").each (function() {
                this.checked = false;
            });
        }
    });
});
