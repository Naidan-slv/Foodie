$(document).ready(function() {
    var csrf_token = $('meta[name="csrf-token"]').attr('content');

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            }
        }
    });

    // Check if this page has the filter/sort/search elements
    // If yes, we assume this is a page like view_recipes.html and handle filtering.
    if ($("#sortOption").length > 0 && $("#searchQuery").length > 0 && $("#recipeList").length > 0) {
        // Set up event handlers related to sorting and searching
        $("#sortOption").on("change", function() {
            loadRecipes();
        });

        $("#searchBtn").on("click", function() {
            loadRecipes();
        });

        $("#searchQuery").on("keypress", function(e) {
            if(e.which === 13) {
                loadRecipes();
            }
        });

        // Load recipes on initial page load if this is a page that uses loadRecipes()
        loadRecipes();
    }

    // Event handlers for like/unlike, save/unsave, and view details (works on any page)
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
                if (response.status === 'liked') {
                    clicked_obj.text('Unlike');
                } else {
                    clicked_obj.text('Like');
                }
                $("#like-count-" + recipeId).text(response.like_count);
            },
            error: function(error) {
                console.log(error);
            }
        });
    });

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

    $("body").on("click", ".view-details-button", function() {
        var recipeId = $(this).data('recipe-id');

        $.ajax({
            url: '/get_recipe_details',
            type: 'GET',
            data: { recipe_id: recipeId },
            dataType: 'json',
            success: function(response) {
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

                $("#submitCommentBtn").data('recipe-id', recipeId);

                var myModal = new bootstrap.Modal(document.getElementById('recipeModal'));
                myModal.show();
            },
            error: function(error) {
                console.log(error);
            }
        });
    });

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
                    $("#newCommentContent").val('');
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

    // These functions only run if the necessary elements are present
    function loadRecipes() {
        var sort = $("#sortOption").val();
        var query = $("#searchQuery").val().trim();

        $.ajax({
            url: '/filter_recipes',
            type: 'GET',
            data: { sort: sort, q: query },
            dataType: 'json',
            success: function(response) {
                renderRecipeList(response);
            },
            error: function(error) {
                console.log(error);
            }
        });
    }

    function renderRecipeList(recipes) {
        var recipeList = $("#recipeList");
        recipeList.empty();
    
        if (recipes.length === 0) {
            recipeList.append("<li>No recipes found.</li>");
            return;
        }
    
        var isAuthenticated = $('meta[name="user-authenticated"]').attr('content') === 'true';
    
        recipes.forEach(function(r) {
            var li = $("<li class='recipe-item'></li>");

            var infoDiv = $("<div class='recipe-info'></div>");
            infoDiv.append("<strong>" + r.title + "</strong> by <em>" + r.author + "</em> (Likes: <span id='like-count-" + r.id + "'>" + r.like_count + "</span>)");

            var actionsDiv = $("<div class='recipe-actions'></div>");
            actionsDiv.append('<button class="btn action-button view-details-button" data-recipe-id="' + r.id + '">View Details</button>');
    
            if (isAuthenticated) {
                var likeText = r.user_liked ? 'Unlike' : 'Like';
                var saveText = r.user_saved ? 'Unsave' : 'Save';
                actionsDiv.append('<button class="btn action-button like-button" data-recipe-id="' + r.id + '">' + likeText + '</button>');
                actionsDiv.append('<button class="btn action-button save-button" data-recipe-id="' + r.id + '">' + saveText + '</button>');
            }

            li.append(infoDiv);
            li.append(actionsDiv);

            recipeList.append(li);
        });
    }
});
