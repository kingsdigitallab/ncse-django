// Global variables
var word_highlight_colour = 'rgba(225,225,0,0.2)'
// Word highlight colour
var article_bounding_box_colour = 'rgba(104,152,204,1)'


// This enables canvas functionality
function enableCanvas()
{
    // Reworked code from https://jsfiddle.net/ndYdk/7/

    function draw(scale, translatePos){
        var canvas = document.getElementById("pageCanvas");
        var context = canvas.getContext("2d");
     
        // clear canvas
        context.clearRect(0, 0, canvas.width, canvas.height);
     
        context.save();
        context.translate(translatePos.x, translatePos.y);
        context.scale(scale, scale);
        
        // Magic starts here
        var img=document.getElementById("canvasImage");
        context.drawImage(img, 0, 0);

        if (typeof highlight_words !== "undefined") {
            context.lineWidth = "1";
            context.fillStyle = word_highlight_colour;
            context.strokeStyle = "rgba(0,0,0,0)";

            jQuery.each(highlight_words, function(k1, v1) {
                jQuery.each(v1, function(k2, v2) {
                    var x0 = parseInt(this["x0"]);
                    var x1 = parseInt(this["x1"]);

                    var y0 = parseInt(this["y0"]);
                    var y1 = parseInt(this["y1"]);
                    context.beginPath();
                    context.fillRect(x0, y0, x1 - x0, y1 - y0);
                    context.stroke();
                });
            });
        }

        if (typeof article_bounding_box !== "undefined") {
            context.lineWidth = "4";
            context.fillStyle = "rgba(0,0,0,0)";
            context.strokeStyle = article_bounding_box_colour;

            context.beginPath();
            context.moveTo(
                parseInt(article_bounding_box[0]["x"]),
                parseInt(article_bounding_box[0]["y"])
            );

            count = article_bounding_box.length;

            for (var i = 1; i <= count; i++) {
                context.lineTo(
                    parseInt(article_bounding_box[i % count]["x"]),
                    parseInt(article_bounding_box[i % count]["y"])
                );
            }

            context.stroke();
        }

        // End magic

        context.restore();
    }
 
    var initialize = (function(){
        var canvas = document.getElementById("pageCanvas");
     
        var translatePos = {
            x: 0,
            y: 0
        };
     
        var scale = 1.0;
        var scaleMultiplier = 0.8;
        var startDragOffset = {};
        var mouseDown = false;
     
        // add button event listeners
        document.getElementById("plus").addEventListener("click", function(evt){
            evt.preventDefault();
            scale /= scaleMultiplier;
            draw(scale, translatePos);
        }, false);
     
        document.getElementById("minus").addEventListener("click", function(evt){
            evt.preventDefault();
            scale *= scaleMultiplier;
            draw(scale, translatePos);
        }, false);
     
        // add event listeners to handle screen drag
        canvas.addEventListener("mousedown", function(evt){
            mouseDown = true;
            startDragOffset.x = evt.clientX - translatePos.x;
            startDragOffset.y = evt.clientY - translatePos.y;
        });
     
        canvas.addEventListener("mouseup", function(evt){
            mouseDown = false;
        });
     
        canvas.addEventListener("mouseover", function(evt){
            mouseDown = false;
        });
     
        canvas.addEventListener("mouseout", function(evt){
            mouseDown = false;
        });
     
        canvas.addEventListener("mousemove", function(evt){
            if (mouseDown) {
                translatePos.x = evt.clientX - startDragOffset.x;
                translatePos.y = evt.clientY - startDragOffset.y;
                draw(scale, translatePos);
            }
        });
     
        draw(scale, translatePos);
    }());
}

// Enables ajax functionality in the publication detail view
function enablePublicationDetailAjax()
{
    $('body').on('click', '.ajax-trigger-year-switcher', function(event)
    {

        // Do some sanity checking to make sure we aren't re-loading what's
        // already there:

        if(!$(this).hasClass('ajax-active'))
        {

            $('.ajax-trigger-year-switcher.ajax-active').removeClass('ajax-active');
            $(this).addClass('ajax-active');
            
            var url = $(this).attr('href');
            $.get(url, function(data)
            {
                $('#ajax-target-gallery').html(data);
            });
        }
    });
}

function enableReadMore() {
    $('body').on('click', '.read-more', function(event) {
        event.preventDefault()
        event.stopPropagation()

        $(this)
            .parent()
            .slideUp()
        $($(this).attr('data-target')).slideDown()
    })
}


function resizeViewer()
{
     $("body").on("click", "#viewer-right a", function()
    {
        if(!$('[aria-expanded="true"]').length)
        {
            $('#viewer-left').addClass('medium-9').removeClass('medium-6');
            $('#viewer-right').addClass('medium-3').removeClass('medium-6');
        } else
        {
            $('#viewer-left').removeClass('medium-9').addClass('medium-6');
            $('#viewer-right').removeClass('medium-3').addClass('medium-6');
        }
    });
}

$(function() {
    if ($('canvas').length) {
        enableCanvas()
    }

    enablePublicationDetailAjax();

    resizeViewer();

    if ($('#jump-to-results-section').size > 0) {
        // Jump to results if search has been run
        $(document).scrollTop($('#jump-to-results-section').offset().top)
    }

    enableReadMore()

    // Cookie policy banner
    if (!Cookies.get('ncse-cookie')) {
        $('#cookie-disclaimer').removeClass('hide')
    }

    // Set cookie
    $('#cookie-disclaimer .closeme').on('click', function() {
        Cookies.set('ncse-cookie', 'ncse-cookie-set', {
            expires: 30
        })
    })

    $('.closeme').bind('click', function() {
        $('#cookie-disclaimer').addClass('hide')
        return false
    })

    // ReInit Equalizer on issue-detail page
    $('#tab2').on('click', function() {
        Foundation.reInit($('#equal-again'))
    })

    // Initialize Foundation
    $(document).foundation()
})
