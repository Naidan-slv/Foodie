$(document).ready(function() {
    var csrf_token = $('meta[name="csrf-token"]').attr('content');

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            }
        }
    });

    // LIKE BUTTON HANDLER
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
                // Update button text
                if (response.status === 'liked') {
                    clicked_obj.text('Unlike');
                } else {
                    clicked_obj.text('Like');
                }

                // Update the like count in the modal if it's open
                // If the modal is showing the same recipe, update like-count
                $("#like-count-" + recipeId).text(response.like_count);
            },
            error: function(error) {
                console.log(error);
            }
        });
    });

    // SAVE BUTTON HANDLER
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
                // Update button text
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

    // VIEW DETAILS BUTTON HANDLER
    $("body").on("click", ".view-details-button", function() {
        var recipeId = $(this).data('recipe-id');

        $.ajax({
            url: '/get_recipe_details',
            type: 'GET',
            data: { recipe_id: recipeId },
            dataType: 'json',
            success: function(response) {
                // Populate the modal with recipe data
                $("#recipeTitle").text(response.title);
                $("#recipeAuthor").text(response.author);
                $("#recipeDescription").text(response.description);
                $("#recipeIngredients").text(response.ingredients);
                $("#recipeSteps").text(response.steps);

                if(response.image_url) {
                    $("#recipeImageContainer").html('<img src="'+response.image_url+'" alt="'+response.title+'" style="max-width:100%;">');
                } else {
                    $("#recipeImageContainer").html('');
                }

                updateCommentList(response.comments);

                // Store recipeId in submit comment button
                $("#submitCommentBtn").data('recipe-id', recipeId);

                // Show the modal
                var myModal = new bootstrap.Modal(document.getElementById('recipeModal'));
                myModal.show();
            },
            error: function(error) {
                console.log(error);
            }
        });
    });

    // SUBMIT COMMENT HANDLER
    $("body").on("click", "#submitCommentBtn", function() {
        var recipeId = $(this).data('recipe-id');
        var content = $("#newCommentContent").val().trim();
        if(!content) {
            alert("Comment cannot be empty");
            return;
        }

        $.ajax({
            url: '/add_comment',
            type: 'POST',
            data: JSON.stringify({ recipe_id: recipeId, content: content }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(response) {
                if(response.status === 'success') {
                    $("#newCommentContent").val(''); // clear textarea
                    updateCommentList(response.comments);
                } else {
                    console.log("Error adding comment");
                }
            },
            error: function(error) {
                console.log(error);
            }
        });
    });

    function updateCommentList(comments) {
        var commentList = $("#commentList");
        commentList.empty();
        if(comments.length === 0) {
            commentList.append("<p>No comments yet.</p>");
        } else {
            for(var i=0; i<comments.length; i++) {
                var c = comments[i];
                var commentHTML = "<div class='mb-2'><strong>"+c.author+"</strong> <small>("+c.created_at+")</small><br>"+c.content+"</div>";
                commentList.append(commentHTML);
            }
        }
    }
});
