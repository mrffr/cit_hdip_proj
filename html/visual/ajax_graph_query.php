<?php

include '/home/hdip_proj/server_php_code/useful_funcs.php';

$cfgdb = $config['database'];

$conn = new mysqli($cfgdb['host'], $cfgdb['user'], $cfgdb['password'], $cfgdb['db']);

if($conn->connect_error){
    die("Connection failed: ". $conn->connect_error);
}

function format_query($qtables, $qcriteria){
}

/* Data for the drop down menus
   to avoid having conflicted choices that result in empty graphs
   the data must be rechecked when the user makes a selection and the
   other drop down menus will then be updated. */

/* Update category by passing in new district */
if(isset($_GET["sel_district"])){
    $categ = NULL;

    /* In this query the criteria will change depending on the drop down values */
    $qtables = array("category", "subcategory", "description");
    $qcriteria = array(
        "category.id = subcategory.category_id",
        "subcategory.id = description.subcategory_id"
    );

    $district = mysqli_real_escape_string($conn, $_GET["sel_district"]);
    $neighb = mysqli_real_escape_string($conn, $_GET["sel_neighbourhood"]);
    $intersection = mysqli_real_escape_string($conn, $_GET["sel_intersection"]);


    if($district !== "Any"){
        $qtables[] = "incident";
        $qtables[] = "location";
        $qcriteria[] = "incident.location_id = location.id";
        $qtables[] = "police_district";
        $qcriteria[] = "location.police_district_id = police_district.id";
        $qcriteria[] = "police_district.name = '" . $district . "'";
    }

    if($neighb !== "Any"){
        $qtables[] = "neighbourhood";
        $qcriteria[] = "location.neighbourhood_id = neighbourhood.id";
        $qcriteria[] = "neighbourhood.name = '" . $neighb . "'";
    }

    if($intersection !== "Any"){
        $qtables[] = "intersection";
        $qcriteria[] = "location.intersection_id = intersection.id";
        $qcriteria[] = "intersection.name = '" . $intersection . "'";
    }

    /* formulate query */
    $qs = "
SELECT DISTINCT category.name, subcategory.name, description.description";

    $tbl_str = join(", ", $qtables);
    $crit_str = join(" AND ", $qcriteria);

    $query = $qs . " FROM " . $tbl_str . " WHERE " . $crit_str;
    $query .= " ORDER BY category.name";

    $res = $conn->query($query);

    $categ = categoryQuery($res);
    /* echo out results as json to be used by javascript */
    echo json_encode($categ, JSON_HEX_TAG);
}

/* Update location by passing in category selections */
if(isset($_GET["sel_category"])){
    $area = NULL;

    $qtables = array("police_district", "neighbourhood",
                     "location", "intersection");
    $qcriteria = array(
        "location.police_district_id = police_district.id",
        "location.neighbourhood_id = neighbourhood.id",
        "location.intersection_id = intersection.id"
    );

    $categ = mysqli_real_escape_string($conn, $_GET["sel_category"]);
    $subcateg = mysqli_real_escape_string($conn, $_GET["sel_subcategory"]);
    $descrip = mysqli_real_escape_string($conn, $_GET["sel_description"]);

    if($categ !== "Any"){
        $qtables[] = "incident";
        $qcriteria[] = "incident.location_id = location.id";
        $qcriteria[] = "incident.description_id = description.id";

        $qtables[] = "description";
        $qcriteria[] = "description.subcategory_id = subcategory.id";

        $qtables[] = "subcategory";
        $qcriteria[] = "subcategory.category_id = category.id";

        $qtables[] = "category";
        $qcriteria[] = "category.name = '" . $categ . "'";
    }

    if($subcateg !== "Any"){
        $qcriteria[] = "subcategory.name = '" . $subcateg . "'";
    }

    if($descrip !== "Any"){
        $qcriteria[] = "description.description = '" . $descrip . "'";
    }

    /* formulate query */
    $qs = "
SELECT DISTINCT police_district.name, neighbourhood.name, intersection.name";

    $tbl_str = join(", ", $qtables);
    $crit_str = join(" AND ", $qcriteria);

    $query = $qs . " FROM " . $tbl_str . " WHERE " . $crit_str;
    $query .= " ORDER BY police_district.name";

    $res = $conn->query($query);

    $area = categoryQuery($res);

    /* echo out results as json to be used by javascript */
    echo json_encode($area, JSON_HEX_TAG);
}


$conn->close();
?>
