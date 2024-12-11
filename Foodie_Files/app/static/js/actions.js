$(document).ready(function () {
    // Like Recipe
    $(".like-button").on("click", function () {
        const recipeId = $(this).data("recipe-id");
        const likeButton = $(this);

        $.ajax({
            url: '/like_recipe',
            type: 'POST',
            contentType: "application/json",
            data: JSON.stringify({ recipe_id: recipeId }),
            success: function (response) {
                // Update the button text and likes count
                if (response.status === 'liked') {
                    likeButton.text("Unlike");
                } else if (response.status === 'unliked') {
                    likeButton.text("Like");
                }
                likeButton.siblings(".like-count").text(`Likes: ${response.like_count}`);
            },
            error: function (error) {
                console.error("Error:", error);
            }
        });
    });
});



// Save Recipe
$(".save-button").on("click", function () {
    const recipeId = $(this).data("recipe-id");
    const saveButton = $(this);

    $.ajax({
        url: '/save_recipe',
        type: 'POST',
        contentType: "application/json",
        data: JSON.stringify({ recipe_id: recipeId }),
        success: function (response) {
            if (response.status === 'saved') {
                saveButton.text("Saved");
            } else if (response.status === 'unsaved') {
                saveButton.text("Save");
            }
        },
        error: function (error) {
            console.error("Error:", error);
        }
    });
});

