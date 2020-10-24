/* ********************************************************************************************
   | Handle Submitting Posts - called by $('#post-button').click(submitPost)
   ********************************************************************************************
   */
function submitPost(event) {
    let content = $("#post-text").text();
    function handleResponse(status){
      if(status=='success'){
        window.location.reload(true);
      }

    }
    event.preventDefault();
    data = {'postContent': content}
    $.post(post_submit_url,
           data,
           handleResponse)
    }


/* ********************************************************************************************
   | Handle Liking Posts - called by $('.like-button').click(submitLike)
   ********************************************************************************************
   */
function submitLike(event) {
    // TODO Objective 10: send post-n id via AJAX POST to like_view (reload page upon success)

    event.preventDefault();
    var elem = $(this)
    var ID = elem.attr("id");
    data = {'postID': ID}
    function handleResponse(status){
      if(status == "success"){
        window.location.reload(true);
      }
    }
    $.post(like_post_url,
           data,
           handleResponse);
    

}

/* ********************************************************************************************
   | Handle Requesting More Posts - called by $('#more-button').click(submitMore)
   ********************************************************************************************
   */
function moreResponse(data,status) {
    if (status == 'success') {
        // reload page to display new Post
        location.reload();
    }
    else {
        alert('failed to request more posts' + status);
    }
}

function submitMore(event) {
    // submit empty data
    let json_data = { };
    // globally defined in messages.djhtml using i{% url 'social:more_post_view' %}
    let url_path = more_post_url;

    // AJAX post
    $.post(url_path,
           json_data,
           moreResponse);
}

/* ********************************************************************************************
   | Document Ready (Only Execute After Document Has Been Loaded)
   ********************************************************************************************
   */
$(document).ready(function() {
    // handle post submission
    $('#post-button').click(submitPost);
    // handle likes
    $('.like-button').click(submitLike);
    // handle more posts
    $('#more-button').click(submitMore);
});
