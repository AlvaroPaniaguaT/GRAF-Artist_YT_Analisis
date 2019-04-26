
function representGraph(){

    var colorCodes = {
        0: '#e6194b', 
        1: '#3cb44b', 
        2: '#ffe119', 
        3: '#4363d8', 
        4: '#f58231', 
        5: '#911eb4', 
        6: '#46f0f0', 
        7: '#f032e6', 
        8: '#bcf60c', 
        9: '#fabebe', 
        10: '#008080', 
        11: '#e6beff', 
        12: '#9a6324', 
        13: '#fffac8', 
        14: '#800000', 
        15: '#aaffc3', 
        16: '#808000', 
        17: '#ffd8b1', 
        18: '#000075', 
        19: '#808080', 
        20: '#ffffff', 
        21: '#000000'
    }
    var svg = d3.select("svg");

    svg.call(d3.zoom().on("zoom", zoomed)).call(responsivefy);

    var container = svg.append('g');

    var width = +svg.attr("width");
    var height = +svg.attr("height");

    // Creates simulation D3 object
    var simulation = d3.forceSimulation()
                       .force("link", d3.forceLink().id(function(d) { return d.id; }))
                       .force("charge", d3.forceManyBody().strength([-50]).distanceMax([500]))
                       .force("collide", d3.forceCollide().radius(function (d) {
                            return 10;
                       }))
                       .force("center", d3.forceCenter(width / 2, height / 2));

    // Add divs to append text on mouse over
    var div = d3.select("body")
                .append("div")
                .attr("class", "tooltip")
                .style("opacity", 0);
    
    // Define a color scheme
    var color = d3.scaleOrdinal(d3.schemePaired);
    
    d3.json('/API/get_modularity').then(function(data, error){
        if (error) throw error;

        // Make object of all neighboring nodes.
        var linkedByIndex = {};
        data.links.forEach(function(d) {
            linkedByIndex[d.target + ',' + d.target] = 1;
	        linkedByIndex[d.source + ',' + d.target] = 1;
	        linkedByIndex[d.target + ',' + d.source] = 1;
        });

        function neighboring(a, b) {
            return linkedByIndex[a.id + ',' + b.id];
        }

        // Draw lines for the links
        var link = container.append("g")
              .attr("class", "links")
              .selectAll("line")
              .data(data.links)
              .enter().append("line").attr("class", "link")

        var toggle = 0;
        var node = container.append("g")
                      .attr("class", "nodes")
                      .selectAll("g")
                      .data(data.nodes)
                      .enter().append("g")
                      .on('click', function(d, i) {

                      if (toggle == 0) {
                          // Ternary operator restyles links and nodes if they are adjacent.
                          d3.selectAll('.link').style('stroke-opacity', function (l) {
                              return l.target == d || l.source == d ? 1 : 0.1;
                          });
                          d3.selectAll('.node').style('opacity', function (n) {
                              return neighboring(d, n) ? 1 : 0.1;
                          });
                          d3.select(this).style('opacity', 1);
                          toggle = 1;
                      }else {
                          // Restore nodes and links to normal opacity.
                          d3.selectAll('.link').style('stroke-opacity', '0.6');
                          d3.selectAll('.node').style('opacity', '1');
                          toggle = 0;
                      }
                    });

        var circles = node.append("circle").attr("class", "node")
                .attr("r", function(d){
                    return 5;
                })
                .attr("fill", function (d) {
                    // Fill node by genre attr
                    return colorCodes[d['cluster']]
                })
                .on("mouseover", function(d) {
                    div.transition()
                        .duration(200)
                        .style("opacity", .9);
                    div.html(d['cluster'])
                        .style("left", (d3.event.pageX) + "px")
                        .style("top", (d3.event.pageY) + "px")
                        .style('background', colorCodes[d['cluster']]);
                })
                .on("mouseout", function(d) {
                    div.transition()
                        .duration(500)
                        .style("opacity", 0);
            });;

        // Uncomment to show all texts of nodes      
        //var labels = node.append("text")
        //        .text(function(d){
        //            return d.id;
        //        })
        //        .attr('x', 6)
        //        .attr('y', 3);

        simulation
              .nodes(data.nodes)
              .on("tick", ticked);

        simulation.force("link")
              .links(data.links);

        function ticked() {
            link
                .attr("x1", function(d) { return d.source.x; })
                .attr("y1", function(d) { return d.source.y; })
                .attr("x2", function(d) { return d.target.x; })
                .attr("y2", function(d) { return d.target.y; });

            node
                .attr("transform", function(d) {
                  return "translate(" + d.x + "," + d.y + ")";
                })
          }

          var drag_handler = d3.drag()
            .on("start", drag_start)
            .on("drag", drag_drag)
            .on("end", drag_end);

        drag_handler(node);

        function drag_start(d) {
            if (!d3.event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }

        function drag_drag(d) {
            d.fx = d3.event.x;
            d.fy = d3.event.y;
        }

        function drag_end(d) {
            if (!d3.event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }

    });


    function zoomed() {

        container.attr("transform", "translate(" + d3.event.transform.x + ", " + d3.event.transform.y + ") scale(" + d3.event.transform.k + ")");
    }

    
}

function responsivefy(svg) {
    // get container + svg aspect ratio
    var container = d3.select(svg.node().parentNode),
        width = parseInt(svg.style("width")),
        height = parseInt(svg.style("height")),
        aspect = width / height;

    // add viewBox and preserveAspectRatio properties,
    // and call resize so that svg resizes on inital page load
    svg.attr("viewBox", "0 0 " + width + " " + height)
        .attr("perserveAspectRatio", "xMinYMid")
        .call(resize);

    // to register multiple listeners for same event type, 
    // you need to add namespace, i.e., 'click.foo'
    // necessary if you call invoke this function for multiple svgs
    // api docs: https://github.com/mbostock/d3/wiki/Selections#on
    d3.select(window).on("resize." + container.attr("id"), resize);

    // get width of container and resize svg to fit it
    function resize() {
        var targetWidth = parseInt(container.style("width"));
        svg.attr("width", targetWidth);
        svg.attr("height", Math.round(targetWidth / aspect));
    }
}