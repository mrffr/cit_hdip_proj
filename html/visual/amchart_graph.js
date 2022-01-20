/* https://www.amcharts.com/demos/date-based-data/ */
function create_graph(graph_data){
    am4core.useTheme(am4themes_animated);

    var chart = am4core.create("chartdiv", am4charts.XYChart);

    chart.data = graph_data;

    // Create axes
    var dateAxis = chart.xAxes.push(new am4charts.DateAxis());
    dateAxis.renderer.minGridDistance = 60;
    dateAxis.baseInterval = {"timeUnit": "day", "count":1};
    dateAxis.dateFormats.setKey("day", "dd-MM-YY");

    var valueAxis = chart.yAxes.push(new am4charts.ValueAxis());
    valueAxis.title.text = "Incidents";

    // Create series
    var series = chart.series.push(new am4charts.ColumnSeries());
    series.dataFields.valueY = "value";
    series.dataFields.dateX = "date";
    series.tooltipText = "{value}"

    //tooltip
    series.tooltip.pointerOrientation = "vertical";
    series.tooltip.label.textAlign = "middle";
    series.tooltip.label.textValign = "middle";

    //panning cursor
    chart.cursor = new am4charts.XYCursor();
    chart.cursor.behavior = "panXY";
    chart.cursor.xAxis = dateAxis;
    chart.cursor.snapToSeries = series;

    //scrollbar
    chart.scrollbarX = new am4charts.XYChartScrollbar();
    chart.scrollbarX.series.push(series);
    chart.scrollbarX.parent = chart.bottomAxesContainer;
    chart.events.on("ready", function () {
	dateAxis.zoom({start:0.79, end:1});
    });
}

/* if graph_data has been set by php script then we use it to draw
 * a graph */
if(graph_data !== ""){
    /* data for graph is in histogram format anyway so just put
       it in the array */
    let data = [];
    for(let i = 0; i < graph_data.length; i++){
	data.push({date:graph_data[i][0], value: graph_data[i][1]});
    }
    create_graph(data);
    /* now scroll to the chart */
    var chart = document.getElementById("chartdiv");
    chart.scrollIntoView();
}
