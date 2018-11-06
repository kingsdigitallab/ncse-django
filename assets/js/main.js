// Global variables
var word_highlight_colour = 'rgba(225,225,0,0.2)'
// Word highlight colour
var article_bounding_box_colour = 'rgba(104,152,204,1)'


// This enables canvas functionality
function enableCanvas()
{
    // From https://stackoverflow.com/questions/10834796/validate-that-a-string-is-a-positive-integer
    function isNormalInteger(str) {
       return /^\+?(0|[1-9]\d*)$/.test(str);
    }

    // Validate our entry
    function validate(val, min, max)
    {
        ival = parseInt(val);
        imin = parseInt(min);
        imax = parseInt(max);

        return (isNormalInteger(val) && ival >= imin && ival <= imax)
    }

    // This enables the page switcher
    window.page_switcher_open = false;

    $('body').on('click', '#page_switcher', function(event)
    {
        if(!window.page_switcher_open)
        {
            event.preventDefault();
            event.stopPropagation();
            window.page_switcher_open = true;

            $(this).html('<input type="number" id="page_switcher_input" value="' + $(this).attr('data-initial') + '" min="1" max="' + $(this).attr('data-count') + '" data-issue-url="' + $(this).attr('data-issue-url') + '">');
            $('#page_switcher_input').focus();
        }
    });

    $('body').on('keyup', '#page_switcher_input', function(event)
    {
        if(event.keyCode == 27) // ESC
        {
            $('#page_switcher').html($('#page_switcher').attr('data-initial'));
            window.page_switcher_open = false;
        } else if(event.keyCode == 13) // RETURN
        {
            // Validation
            if(validate($(this).val(), $(this).attr('min'), $(this).attr('max')))
            {
                window.location.href = $(this).attr('data-issue-url') + 'page/' + $(this).val();
            }
        }

        // Validation
        if(!validate($(this).val(), $(this).attr('min'), $(this).attr('max')))
        {
            $(this).addClass('error');
        } else
        {
            $(this).removeClass('error');
        }
    });


    // This enables the canvas expansion option
    $('body').on('click', '#canvas_expand', function(event)
    {
        event.preventDefault();
        event.stopPropagation();

        if($(this).children('i').hasClass('fa-expand'))
        {
            $("#viewer-right").hide();
            $("#viewer-left").addClass('maximize');
            $(this).parent().attr('title', $(this).parent().attr('data-title-collapse'));
            $(this).parent().data().zfPlugin.template.text($(this).parent().attr('title'));
            $('.tooltip').hide();
            $(this).children('i').removeClass('fa-expand').addClass('fa-compress');
        } else
        {
            $("#viewer-right").show();
            $("#viewer-left").removeClass('maximize');
            $(this).parent().attr('title', $(this).parent().attr('data-title-expand'));
            $(this).parent().data().zfPlugin.template.text($(this).parent().attr('title'));
            $('.tooltip').hide();
            $(this).children('i').addClass('fa-expand').removeClass('fa-compress');
        }
    });

    $('body').on('click', '#canvas_save', function(event)
    {
        $(this).attr('href', document.getElementById("pageCanvas").toDataURL());
        $(this).attr('download', $('h1.underline').text().trim() + ".png");
    });

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
            }).done(function()
            {   
                $("img").ready(function(event)
                {
                    $(document).foundation();
                });
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

function enableVis()
{
    $('.vis').each(function()
    {

        var slug = $(this).attr('data-slug');
        var url = "/periodicals/ajax/chart_data/" + slug + "/";
        var vis = $(this);

        if ($(this).attr('data-width'))
        {
            var width = parseInt($(this).attr('data-width'));
        } else
        {
            var width = 860;
        }

        if ($(this).attr('data-height'))
        {
            var height = parseInt($(this).attr('data-height'));
        } else
        {
            var height = 290;
        }

        if ($(this).attr('data-start'))
        {
            var start = parseInt($(this).attr('data-start'));
        } else
        {
            var start = false;
        }

        if ($(this).attr('data-end'))
        {
            var end = parseInt($(this).attr('data-end'));
        } else
        {
            var end = false;
        }

        $.ajax({ 
            type: 'GET', 
            url: url, 
            data: {  },
            success: function (data) { 

                var statuses_to_use = ["Article", "Ad", "Picture"];
                var status = [];

                $(statuses_to_use).each(function(key, val)
                {
                    if(~data.indexOf(val))
                    {
                        status.push(val);
                    }
                });


                data = JSON.parse(data);

                function drawBarGraph(data) {

                  var colors = [ ["Successful", "#001038"],
                                ["Unsuccessful", "#02247a"] ];

                  var margin = {top: 30, right: 30, bottom: 40, left: 60};

                  width  = width - margin.left - margin.right;
                  height = height - margin.top - margin.bottom;

                  var z = d3.scale.ordinal()
                  .range(["#0584ba", "#ddd", "#000", "#0584ba", "#a5f7ec"]);

                  if(!start)
                  {
                    start = data[0]["date"];
                  }

                  if(!end)
                  {
                    end = data[data.length - 1]["date"];
                  }

                  
                  var x = d3.scale.linear()
                  .domain([start, end])
                  .rangeRound([0, width], .1);

                  var y = d3.scale.linear()
                  .rangeRound([height, 0]);

                  var xAxis = d3.svg.axis()
                  .scale(x)
                  .orient("bottom")
                  .tickFormat(d3.format("d"))
                  .ticks(5);

                  var yAxis = d3.svg.axis()
                  .scale(y)
                  .orient("left")
                  .ticks(5)
                  .tickFormat(d3.format("d"));

                  var svg = d3.select($(vis)[0]).select("#chart-bar")
                  .append("svg")
                  .attr("viewBox", "0 0 " + (width + margin.left + margin.right) + " " + (height + margin.top + margin.bottom))
                  .attr("preserveAspectRatio", "xMinYMin meet")
                  .append("g")
                  .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

                  var layers = d3.layout.stack()
                  (status.map(function (c) {
                    return data.map(function (d) {
                      return {x: d.date, y: d[c]};

                    });
                  }));

                  y.domain([
                    0, d3.max(layers, function (d) {
                      return d3.max(d, function(e)
                      {
                        return e.y0 + e.y;
                      });
                    })
                  ]);


                  // gridlines in y axis function
                  function make_y_gridlines() {
                    return d3.svg.axis().scale(y)
                      .orient("left").ticks(5);
                  }

                  // add the Y gridlines
                  svg.append("g")
                    .attr("class", "gridline")
                    .call(make_y_gridlines()
                          .tickSize(-width)
                          .tickFormat("")
                         );

                  svg.append("g")
                    .attr("class", "axis axis--x")
                    .attr("transform", "translate(6," + height + ")")
                    .call(xAxis)
                    .append("text")
                    .attr("transform", "translate(364,0)")
                    .attr("y", "3em")
                    .style("text-anchor", "middle");

                  svg.append("g")
                    .attr("class", "axis axis--y")
                    .call(yAxis)

                  function type(d) {
                    // d.date = parseDate(d.date);
                    d.date;
                    status.forEach(function (c) {
                        d[c] = +d[c];
                    });
                    return d;
                  }  
                  
                   var tooltip = d3.select($(vis)[0]).select("#chart-bar").append("div")
                  .attr("class", "tooltip")
                  .style("opacity", 0);

                  var layer = svg.selectAll(".layer")
                  .data(layers)
                  .enter().append("g")
                  .attr("class", "layer")
                  .style("fill", function (d, i) {
                    return z(i);
                  });

                  layer.selectAll("rect")
                    .data(function (d) {
                    return d;
                  })
                    .enter().append("rect")
                    .on("mouseover", function (d) {
                    tooltip.transition()
                      .duration(200)
                      .style("opacity", 1);
                      console.log(d3.event);
                    tooltip.html("<span>" + d.y  + "</span>")
                      .style("left", (d3.event.pageX - 25) + "px")
                      .style("top", (d3.event.pageY - 28) + "px");
                  })
                    .on("mouseout", function (d) {
                    tooltip.transition()
                      .duration(500)
                      .style("opacity", 0);
                  })
                      .attr("x", function (d) {
                    return x(d.x);
                  })
                    .attr("y",  function(d) {
                    return height;
                  })
                    .attr("width", 4)
                    .attr("height", 0)
                    .transition().duration(1500)
                    .attr("y", function (d) {
                    return y(d.y + d.y0);
                  })
                    .attr("height", function (d) {
                    return y(d.y0) - y(d.y + d.y0);
                  });

                }

                drawBarGraph(data);
            }
        });
    });
    
    $(".vis .wrapper").delay(10).fadeIn(500);
    $('.vis .count').each(function () {
      $(this).prop('Counter',0).animate({
        Counter: $(this).text()
      }, {
        duration: 1500,
        easing: 'swing',
        step: function (now) {
          $(this).text(Math.ceil(now));
        }
      });
    });
}


$('document').ready(function() {
    if ($('canvas').length) {
        enableCanvas()
    }

    enablePublicationDetailAjax();

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

    enableVis();

    // Initialize Foundation
    $(document).foundation();
})
