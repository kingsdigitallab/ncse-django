
// Enables drawing to a canvas
function enableCanvas()
{
    // Only run if we have a page canvas!
    if ($('.pageCanvas').length)
    {
        $('.pageCanvas').each(function() {
            var canvas = $(this)[0];
            var ctx = canvas.getContext("2d");
            var img = new Image;
            img.onload = function() {
                ctx.drawImage(this, 0, 0);
            };
            img.src = $('#' + $(this).attr('data-image-id')).attr('src');
        });
    }
}

$(function() {
    // Your JS Here
    enableCanvas();
});
