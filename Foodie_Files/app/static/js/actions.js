$(document).ready(function() {
    // Set the CSRF token so we are not rejected by server
    var csrf_token = $('meta[name="csrf-token"]').attr('content');

    // Configure ajaxSetup so that the CSRF token is added to the header of every request
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            }
        }
    });

    // Event handler for like button clicks
    $("body").on("click", ".like-button", function() {
        var recipeId = $(this).data('recipe-id');
        var clicked_obj = $(this);

        $.ajax({
            url: '/like_recipe',
            type: 'POST',
            data: JSON.stringify({ recipe_id: recipeId }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(response) {
                // Update like count text
                $("#like-count-" + recipeId).text(response.like_count);

                // Update button text based on liked or unliked
                if (response.status === 'liked') {
                    clicked_obj.text('Unlike');
                } else {
                    clicked_obj.text('Like');
                }
            },
            error: function(error) {
                console.log(error);
            }
        });
    });

    // Event handler for save button clicks
    $("body").on("click", ".save-button", function() {
        var recipeId = $(this).data('recipe-id');
        var clicked_obj = $(this);

        $.ajax({
            url: '/save_recipe',
            type: 'POST',
            data: JSON.stringify({ recipe_id: recipeId }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(response) {
                // Update button text based on saved or unsaved
                if (response.status === 'saved') {
                    clicked_obj.text('Unsave');
                } else {
                    clicked_obj.text('Save');
                }
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
});
