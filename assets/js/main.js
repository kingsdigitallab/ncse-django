// Enables drawing to a canvas
function enableCanvas() {
    // Only run if we have a page canvas!
    if ($(".pageCanvas").length) {
        $(".pageCanvas").each(function() {
            var canvas = $(this)[0];
            var ctx = canvas.getContext("2d");
            var img = new Image();
            img.onload = function() {
                ctx.drawImage(this, 0, 0);
                if (typeof highlight_words !== "undefined") {
                    ctx.lineWidth = "1";
                    ctx.fillStyle = "rgba(225,225,0,0.5)";

                    jQuery.each(highlight_words, function(k1, v1) {
                        jQuery.each(v1, function(k2, v2) {
                            var x0 = parseInt(this["x0"]);
                            var x1 = parseInt(this["x1"]);

                            var y0 = parseInt(this["y0"]);
                            var y1 = parseInt(this["y1"]);
                            ctx.beginPath();
                            ctx.fillRect(x0, y0, x1 - x0, y1 - y0);
                            ctx.stroke();
                        });
                    });
                }
            };
            img.src = $("#" + $(this).attr("data-image-id")).attr("src");
        });
    }
}

$(function() {
    // Your JS Here
    enableCanvas();
});
