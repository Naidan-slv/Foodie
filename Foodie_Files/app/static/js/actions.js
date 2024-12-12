$(document).ready(function() {
    var csrf_token = $('meta[name="csrf-token"]').attr('content');

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            }
        }
    });

    // Load recipes on initial page load
    loadRecipes();

    // Event handler for dropdown change
    $("#sortOption").on("change", function() {
        loadRecipes();
    });

    // Event handler for search button
    $("#searchBtn").on("click", function() {
        loadRecipes();
    });

    // Handle "Enter" key in search bar
    $("#searchQuery").on("keypress", function(e) {
        if(e.which === 13) {
            loadRecipes();
        }
    });

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
    
        if(recipes.length === 0) {
            recipeList.append("<li>No recipes found.</li>");
            return;
        }
    
        var isAuthenticated = $('meta[name="user-authenticated"]').attr('content') === 'true';
    
        recipes.forEach(function(r) {
            var li = $("<li></li>");
            // Display likes similarly to saved_recipes:
            // For example: "<strong>Title</strong> by Author (Likes: X)"
            li.append("<strong>" + r.title + "</strong> by <em>" + r.author + "</em> " +
                      "(Likes: <span id='like-count-" + r.id + "'>" + r.like_count + "</span>) ");
            
            li.append('<button class="view-details-button" data-recipe-id="'+r.id+'">View Details</button> ');
    
            if(isAuthenticated) {
                var likeText = r.user_liked ? 'Unlike' : 'Like';
                var saveText = r.user_saved ? 'Unsave' : 'Save';
    
                li.append('<button class="like-button" data-recipe-id="'+r.id+'">'+likeText+'</button> ');
                li.append('<button class="save-button" data-recipe-id="'+r.id+'">'+saveText+'</button>');
            }
    
            recipeList.append(li);
        });
    }
    

    // LIKE HANDLER
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

    // SAVE HANDLER
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

    // VIEW DETAILS HANDLER (modal)
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
});
