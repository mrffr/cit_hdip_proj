
/* File used to populate dropdown menus through calls to ajax_graph_query.php */


/* AJAX to populate drop down menus on change */
//https://www.w3resource.com/ajax/working-with-PHP-and-MySQL.php
function dropdown_ajax_cat() {
    let xhr;
    if(window.XMLHttpRequest) {
	xhr = new XMLHttpRequest();
    }else if (window.ActiveXObject) {
	xhr = new ActiveXObject("Microsoft.XMLHTTP");
    }

    /* here we pass in the location info
     * to get the new category data */
    let district = document.getElementById("district_sel").value;
    let neighbourhood = document.getElementById("neighb_sel").value;
    let intersection = document.getElementById("intersect_sel").value;
    let query_str = "ajax_graph_query.php?sel_district=" + district +
	"&sel_neighbourhood=" + neighbourhood +
	"&sel_intersection=" + intersection;
    xhr.open("GET", query_str, true); //true use async

    xhr.send();

    xhr.onreadystatechange = display_data; //presume this is a callback
    function display_data() {
	if(xhr.readyState === 4) { //request done
	    if(xhr.status === 200) { //status 200
		categ.php_cat_info = JSON.parse(xhr.responseText);
		categ.set_cat();
	    }else{
		alert("Problem with the request");
	    }
	}
    }
}

/* update location drop downs
 * by passing in the new category */
function dropdown_ajax_loc() {
    let xhr;
    if(window.XMLHttpRequest) {
	xhr = new XMLHttpRequest();
    }else if (window.ActiveXObject) {
	xhr = new ActiveXObject("Microsoft.XMLHTTP");
    }

    let categ = document.getElementById("cat_sel").value;
    let subcat = document.getElementById("subcat_sel").value;
    let desc = document.getElementById("desc_sel").value;
    let query_str = "ajax_graph_query.php?sel_category=" + categ +
	"&sel_subcategory=" + subcat +
	"&sel_description=" + desc;
    xhr.open("GET", query_str, true); //true use async

    xhr.send();

    xhr.onreadystatechange = display_data; //presume this is a callback
    function display_data() {
	if(xhr.readyState === 4) { //request done
	    if(xhr.status === 200) { //status 200
		area.php_loc_info = JSON.parse(xhr.responseText);
		area.set_district();
	    }else{
		alert("Problem with the request");
	    }
	}
    }
}

/* Fill drop down menus with options */
function fill_dropdown(select_menu, keys, cur_val) {
    /* cur_val is used to setup drop downs on page load */
    if(cur_val === undefined) {
	cur_val = select_menu.value;
    }

    /* first empty drop down */
    select_menu.innerHTML = "";

    /* now go through keys and create drop down option for each */
    keys = ["Any"].concat(keys); //Add 'any' selection to menus
    keys.forEach(el => {
	let opt = document.createElement("option");
	opt.value = el;
	opt.innerHTML = el;
	select_menu.add(opt);
    });

    /* if we already had selected a valid value
       then set this as selected value */
    if(keys.indexOf(cur_val) >= 0){
	select_menu.selectedIndex = keys.indexOf(cur_val);
    }
}

/*****************************************/
/* category drop down menus */
function Category() {
    this.php_cat_info;

    /* functions to fill out drop down tables */
    this.set_cat = function() {
	let sel = document.getElementById("cat_sel");
	let k = Object.keys(this.php_cat_info);
	fill_dropdown(sel, k);
	this.set_subcat(); //subsequent drop down menus fill out
    };

    this.set_subcat = function() {
	let sel = document.getElementById("subcat_sel");
	let cat_key = document.getElementById("cat_sel").value;

	/* Check we selected a key in the parent
	 * if we didn't then fade out the dropdown */
	if(cat_key === "Any"){
	    var k = [];
	    sel.classList.add("faded_dropdown");
	}else{
	    var k = Object.keys(this.php_cat_info[cat_key]);
	    sel.classList.remove("faded_dropdown");
	}
	fill_dropdown(sel, k);
	this.set_desc();
    };

    this.set_desc = function() {
	let sel = document.getElementById("desc_sel");
	let cat_key = document.getElementById("cat_sel").value;
	let subcat_key = document.getElementById("subcat_sel").value;

	if(cat_key === "Any" || subcat_key === "Any"){
	    var k = [];
	    sel.classList.add("faded_dropdown");
	}else{
	    var k = Object.values(this.php_cat_info[cat_key][subcat_key]);
	    sel.classList.remove("faded_dropdown");
	}
	fill_dropdown(sel, k);
    };

    /* handle updating the drop down menus selection and
       updating location drop down menus */
    this.change_cat = function() {
	dropdown_ajax_loc();
	this.set_subcat();
    };

    this.change_subcat = function() {
	dropdown_ajax_loc();
	this.set_desc();
    };

    this.change_desc = function() {
	dropdown_ajax_loc();
    };

}

/*****************************************/
/* area drop down menus */
function Area() {
    this.php_loc_info;

    /* handle populating the area drop downs */
    this.set_district = function() {
	let sel = document.getElementById("district_sel");
	let k = Object.keys(this.php_loc_info);
	fill_dropdown(sel, k);
	this.set_neighbour();
    };

    this.set_neighbour = function() {
	let sel = document.getElementById("neighb_sel");
	let district_key = document.getElementById("district_sel").value;

	if(district_key === "Any"){
	    var k = []; //use var so it's in scope below
	    sel.classList.add("faded_dropdown");
	}else{
	    var k = Object.keys(this.php_loc_info[district_key]);
	    sel.classList.remove("faded_dropdown");
	}
	fill_dropdown(sel, k);
	this.set_intersection();
    };

    this.set_intersection = function() {
	let sel = document.getElementById("intersect_sel");
	let district_key = document.getElementById("district_sel").value;
	let neighb_key = document.getElementById("neighb_sel").value;

	/* Can't make selection if choosing any district */
	if(district_key === "Any" || neighb_key === "Any"){
	    var k = [];
	    sel.classList.add("faded_dropdown");
	}else{
	    var k = Object.values(this.php_loc_info[district_key][neighb_key]);
	    sel.classList.remove("faded_dropdown");
	}
	fill_dropdown(sel, k);
    };

    /* handle updating after district selection */

    this.change_district = function() {
	dropdown_ajax_cat(); //update the category drop down list
	this.set_neighbour();
    };

    this.change_neighb = function() {
	dropdown_ajax_cat();
	this.set_intersection();
    };

    this.change_intersect = function() {
	dropdown_ajax_cat();
    };
}
