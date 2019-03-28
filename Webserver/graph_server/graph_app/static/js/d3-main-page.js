
$(document).ready(()=>{
    var svg = d3.select("svg"),
        width = +svg.attr("width"),
        height = +svg.attr("height");

    var simulation = d3.forceSimulation()
        .force("link", d3.forceLink().id(function(d) { return d.id; }))
        .force("charge", d3.forceManyBody())
        .force("center", d3.forceCenter(width / 2, height / 2));

    var color = d3.scaleOrdinal(d3.schemeAccent);

    d3.json('./API/get_main').then(function(data, error){
        if (error) throw error;


        var link = svg.append("g")
              .attr("class", "links")
              .selectAll("line")
              .data(data.links)
              .enter().append("line")

        var node = svg.append("g")
              .attr("class", "nodes")
              .selectAll("g")
              .data(data.nodes)
              .enter().append("g")

        var circles = node.append("circle")
              .attr("r", function(d){
                  if ((d.weight != undefined) & (d.weight != 0)){
                    return Math.log1p(d.weight);
                  }else{
                    return 10;
                  }
              })
              .attr("fill", function (d) {
                 return color(d.weight);
              });
              
        svg.on("mouseover", handleMouseOver)
           .on("mouseout", handleMouseOut)
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

          // Create Event Handlers for mouse
        function handleMouseOver(d, i) {  // Add interactivity

            // Use D3 to select element, change color and size
            d3.select(this).attr({
                fill: "orange",
                r: this.r * 2
            });

            // Specify where to put label of text
            svg.append("text").attr({
                id: "t" + d.x + "-" + d.y + "-" + i,  // Create an id for text so we can select it later for removing on mouseout
                    x: function() { return xScale(d.x) - 30; },
                    y: function() { return yScale(d.y) - 15; }
                })
                .text(function() {
                    return [d.x, d.y];  // Value of the text
            });
        }

        function handleMouseOut(d, i) {
            // Use D3 to select element, change color back to normal
            d3.select(this).attr({
                fill: "black",
                r: this.r
            });

            // Select text by id and then remove
            d3.select("#t" + d.x + "-" + d.y + "-" + i).remove();  // Remove text location
        }
    });
});