$(function() {
    $('#search').keyup(function() {
        $.ajax({
            type: "POST",
            url: "/search/",
            data: {
                'search_text' : $('#search').val(),
                'csrfmiddlewaretoken' : $("input[name=csrfmiddlewaretoken]").val()
            },
            success: searchSuccess,
            dataType: 'html'
        });
    });

    $('#sel_marcas').on('change', function() {
        var url = $(this).val(); // get selected value
        if (url) { // require a URL
            window.location = url; // redirect
        }
        return false;
    });
});

function searchSuccess(data, textStatus, jqXHR)
{
    $('#search-results').html(data)
}