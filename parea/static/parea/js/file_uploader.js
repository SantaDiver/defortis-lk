$(function() {
  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
  }

  // We can watch for our custom `fileselect` event like this
  $(document).ready( function() {
      // console.log('(_!_)');
      $("#file-uploader1").change(function () {
        $("#upload-form1").submit();
      });

      $("[id*=file_downloader]").click(function(event){
        var file_id = $(this).attr('file_id');
        var csrftoken = getCookie('csrftoken');
        $.ajaxSetup({
          beforeSend: function(xhr, settings) {
            xhr.setRequestHeader('X-CSRFToken', csrftoken);
          }
        });
        data = {
          'file_id' : file_id
        }
        $.get('./download_file/', data)
      });
  });

});
