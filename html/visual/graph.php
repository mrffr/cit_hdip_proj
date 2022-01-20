<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width">
    <title>Graph</title>
    <link href="https://fonts.googleapis.com/css?family=Open+Sans" rel="stylesheet">
    <link rel="stylesheet" href="../css/style.css" type="text/css" media="all">
    <link rel="stylesheet" href="../css/forms.css" type="text/css" media="all">
<!-- Amchart stuff -->
<script src="https://www.amcharts.com/lib/4/core.js"></script>
<script src="https://www.amcharts.com/lib/4/charts.js"></script>
<script src="https://www.amcharts.com/lib/4/themes/animated.js"></script>
  </head>

  <body>
	<div class="header">
	  <img src="../images/golden_gate.jpg" id="banner_image">
	    <div class="navbar">
		<a class="navbar_link" href="../index.html">Start-Up</a>
		<div class="dropdown">
		    <a class="navbar_link tab_curr" href="../visualize.html">Visualize</a>
		    <div class="dropdown-content">
			<a href="map.html">Map</a>
			<a class="navbar_curr" href="graph.php">Graph</a>
		    </div>
		</div>
		<a class="navbar_link" href="../contact.html">Contact Us</a>
		<a class="navbar_link" href="../sources.html">Sources</a>
		<a class="navbar_link" href="../about.html">About</a>
	    </div>
	    <h1>Graph</h1>
	</div>

      <div class="content">
	<p>Make your selections below to view a histogram of the results.</p>


<!-- Dropdown menus -->
<!-- Onchange functions are added later -->
	<div id="controldiv">
	    <form action="" method="GET">
		<ul class="form_list">
		    <div id="categ_drops">
		    <li>
			<label class="main_label">Category:</label>
			<select name="category" id="cat_sel" onchange="">
			    <option value="">Nothing</option>
			</select>
		    </li>
		    <li>
			<label>Subcategory:</label>
			<select name="subcategory" id="subcat_sel" onchange="">
			    <option value="">Nothing</option>
			</select>
		    </li>
		    <li>
			<label>Description:</label>
			<select name="description" id="desc_sel" onchange="">
			    <option value="">Nothing</option>
			</select>
		    </li>
		    </div>

		    <!-- Area -->
		    <div id="area_drops">
		    <li>
			<label class="main_label">District:</label>
			<select name="district" id="district_sel" onchange="">
			    <option value="">Nothing</option>
			</select>
		    </li>
		    <li>
			<label>Neighbourhood:</label>
			<select name="neighbourhood" id="neighb_sel" onchange="">
			    <option value="">Nothing</option>
			</select>
		    </li>
		    <li>
			<label>Intersection:</label>
			<select name="intersection" id="intersect_sel" onchange="">
			    <option value="">Nothing</option>
			</select>
		    </li>
		    </div>

		    <div id="submitdiv">
		    <li>
			<input type="submit" name="gen_graph" id="submit_btn" value="Submit" />
		    </li>
		    </div>

		</ul>
	    </form>
	</div>

	<!-- Chart position -->
	<div id="chartdiv"></div>
      </div>
  </body>

  <footer>© 2019 SFCrimeStats</footer>


<?php

/* initial db requests */
include '/home/hdip_proj/server_php_code/useful_funcs.php';

//config is read in useful_funcs file
$cfgdb = $config['database'];
$conn = new mysqli($cfgdb['host'], $cfgdb['user'], $cfgdb['password'], $cfgdb['db']);

if($conn->connect_error){
  die("Connection failed: ". $conn->connect_error);
}

$cat = $conn->query("
SELECT DISTINCT category.name, subcategory.name, description.description
FROM category, subcategory, description
WHERE category.id = subcategory.category_id
  AND subcategory.id = description.subcategory_id ORDER BY category.name");

  //area
$area = $conn->query("
SELECT DISTINCT police_district.name, neighbourhood.name, intersection.name
FROM police_district, neighbourhood, location, intersection
WHERE location.police_district_id = police_district.id
  AND location.neighbourhood_id = neighbourhood.id
  AND location.intersection_id = intersection.id
ORDER BY police_district.name");

/* globals used in JS drop down menus
  * These are overwritten by ajax_graph_query.php AJAX requests */
$cat_res = categoryQuery($cat);
$locat_res = categoryQuery($area);


$graph_dates = "";
if(isset($_GET["gen_graph"])){

    /*
Sanitize inputs otherwise someone could mess with db
     */
    $distr = mysqli_real_escape_string($conn, $_GET["district"]);
    $neighb = mysqli_real_escape_string($conn, $_GET["neighbourhood"]);
    $inters = mysqli_real_escape_string($conn, $_GET["intersection"]);
    $categ = mysqli_real_escape_string($conn, $_GET["category"]);
    $subcateg = mysqli_real_escape_string($conn, $_GET["subcategory"]);
    $descrip = mysqli_real_escape_string($conn, $_GET["description"]);

  /* get incidents matching criteria */
  $graph_dates = graphQuery($conn,
                            $distr,
                            $neighb,
                            $inters,
                            $categ,
                            $subcateg,
                            $descrip);

}

$conn->close();
?>

<script src="dropdowns.js"></script>
<script>
var area = new Area();
var categ = new Category();

area.php_loc_info = <?php echo json_encode($locat_res, JSON_HEX_TAG); ?>;
categ.php_cat_info = <?php echo json_encode($cat_res, JSON_HEX_TAG); ?>;

/* initializing dropdown settings as though nothing is selected
   this will fill top level drop downs with values and everything else
   will be 'any' */
categ.set_cat();
area.set_district();

/* Now handle GET params
   set dropdown selections equal to the GET params if they were set.
   Need to call the set function only after category above has run.
   Otherwise we can't set the values correctly as options are not populated yet. */
var urlParams = new URLSearchParams(window.location.search);

if(urlParams.has("category")){
    document.getElementById("cat_sel").value = urlParams.get("category");
    categ.set_cat();
}

if(urlParams.has("subcategory")){
    document.getElementById("subcat_sel").value = urlParams.get("subcategory");
    categ.set_subcat();
}

if(urlParams.has("description")){
    document.getElementById("desc_sel").value = urlParams.get("description");
    categ.set_desc();
}

if(urlParams.has("district")){
    document.getElementById("district_sel").value = urlParams.get("district");
    area.set_district();
}

if(urlParams.has("neighbourhood")){
    document.getElementById("neighb_sel").value = urlParams.get("neighbourhood");
    area.set_neighbour();
}

if(urlParams.has("intersection")){
    document.getElementById("intersect_sel").value = urlParams.get("intersection");
    area.set_intersection();
}

/* Finally add onchange elements to the select menus
   This is added here to avoid sending too many requests when the page is being created.
   Otherwise we'd trigger a lot of calls.
*/
document.getElementById('cat_sel').onchange = function() { categ.change_cat(); };
document.getElementById('subcat_sel').onchange = function() { categ.change_subcat(); };
document.getElementById('desc_sel').onchange = function() { categ.change_desc(); };

document.getElementById('district_sel').onchange = function() { area.change_district(); };
document.getElementById('neighb_sel').onchange = function() { area.change_neighb(); };
document.getElementById('intersect_sel').onchange = function() { area.change_intersect(); };

</script>
<script>
/* For the amchart graph */
var graph_data = <?php echo json_encode($graph_dates, JSON_HEX_TAG); ?>;
</script>
<!-- The am chart must be generated after the container div is already created. So the script is run at the end -->
  <script src="amchart_graph.js"></script>
</html>
