// Global variables
var word_highlight_colour = "rgba(225,225,0,0.2)";
// Word highlight colour
var article_bounding_box_colour = "rgba(104,152,204,1)";

// Article bounding box colour
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
                    ctx.fillStyle = word_highlight_colour;
                    ctx.strokeStyle = "rgba(0,0,0,0)";

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

                if (typeof article_bounding_box !== "undefined") {
                    ctx.lineWidth = "4";
                    ctx.fillStyle = "rgba(0,0,0,0)";
                    ctx.strokeStyle = article_bounding_box_colour;

                    ctx.beginPath();
                    ctx.moveTo(
                        parseInt(article_bounding_box[0]["x"]),
                        parseInt(article_bounding_box[0]["y"]),
                    );

                    count = article_bounding_box.length;

                    for (var i = 1; i <= count; i++) {
                        ctx.lineTo(
                            parseInt(article_bounding_box[i % count]["x"]),
                            parseInt(article_bounding_box[i % count]["y"]),
                        );
                    }

                    ctx.stroke();
                }
            };
            img.src = $("#" + $(this).attr("data-image-id")).attr("src");
        });
    }
}

$(function() {
    // Your JS Here
    if ($("canvas")) {
        enableCanvas();
    }

    if ($(".tabs")) {
        $(".tabs ul li").on("click", function() {
            var option = $(this).data("option");
            $(".tabs ul li").removeClass("is-active");
            $(this).addClass("is-active");
            $(".tabs-container section").removeClass("is-active");
            $('section[data-item="' + option + '"]').addClass("is-active");
        });
    }
});
