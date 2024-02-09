$(function () {
  $("#autocomplete").autocomplete({
    source: function (request, response) {
      $.ajax({
        url: "/autocomplete",
        dataType: "json",
        data: {
          term: request.term,
        },
        success: function (data) {
          response(data);
        },
      });
    },
    minLength: 1, // Minimum length before autocomplete starts
  });
});
