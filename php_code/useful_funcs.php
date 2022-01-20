<?php

/* config ini file parsed as multidimensional array by section
* example config['database']['user']
https://stackoverflow.com/questions/12394104/php-connection-variables-ini-file
 */
$config = parse_ini_file('/home/hdip_proj/config.ini', true);


/* returns three columns as nested arrays for json encoding */
function categoryQuery($result) {
  $rows = array();
  if($result->num_rows > 0){
    $rs = $result->fetch_all();
    foreach($rs as $val){
      $rows[$val[0]][$val[1]][] = $val[2];
    }
  }
  return $rows;
}

/* function to make a histogram from our query */
function makeHistogram($result) {
  /* now that we have the db data we need to zero out any days that
     have no results */

  /* the first result will be the first date and last last date */
  $first = reset($result)[0];
  $last = end($result)[0];

  /* http://thisinterestsme.com/calculating-difference-dates-php/ */
  $date1 = new DateTime($first);
  $date2 = new DateTime($last);

  /* make 2d array of time period with [date, value] */
  /* https://stackoverflow.com/questions/3207749/i-have-2-dates-in-php-how-can-i-run-a-foreach-loop-to-go-through-all-of-those-d */
  for($i = $date1; $i <= $date2; $i->modify('+1 day')){
      $fmt_date = $i->format('Y-m-d');
      $histogram[] = array($fmt_date, 0);
  }

  /* now add results to histogram data
   by going through result and finding the correct date
   and adding the correct value */
  foreach($result as $rs){
      for($i = 0; $i < count($histogram); $i++){
          if($histogram[$i][0] === $rs[0]){
              $histogram[$i][1] = $rs[1];
              break;
          }
      }
  }
  return $histogram;
}

/* constructs graph query and then returns a histogram of this query */
function graphQuery($conn, $district, $neighb,
                    $intersection, $categ, $subcateg, $descrip) {
  $qtables = array("date","incident");
  $qcriteria = array("incident.date_id = date.id");

  if($district !== "Any"){
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

  /* Due to table design that is built up from description
   * this means if we select category we already join on subcategory
   * and description by id. So selecting these drop down menus will just
   * create a name = criteria compared to only selecting a category */

  if($categ !== "Any"){
    $qtables[] = "description";
    $qtables[] = "subcategory";
    $qtables[] = "category";
    $qcriteria[] = "incident.description_id = description.id";
    $qcriteria[] = "description.subcategory_id = subcategory.id";
    $qcriteria[] = "subcategory.category_id = category.id";
    $qcriteria[] = "category.name = '" . $categ . "'";
  }

  if($subcateg !== "Any"){
    $qcriteria[] = "subcategory.name = '" . $subcateg . "'";
  }

  if($descrip !== "Any"){
    $qcriteria[] = "description.description = '" . $descrip . "'";
  }

  /* construct the actual query */
  /* http://www.techfounder.net/2012/04/18/generating-graphs-from-mysql-table-data/ */
  $qs = "SELECT DATE(date.date_time) as date, COUNT(incident.api_row_id)";

  $tbl_str = join(", ", $qtables);
  $crit_str = join(" AND ", $qcriteria);

  $query = $qs . " FROM " . $tbl_str . " WHERE " . $crit_str;
  $query .= " GROUP BY date ORDER by date";

  $result = $conn->query($query);

 //if no results then die
  if($result->num_rows == 0){
    die("No results found!");
  }else{
    $result = $result->fetch_all();
  }

  return makeHistogram($result);
}

?>
