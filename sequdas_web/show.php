<style>
	
.divTable{
	display: table;
	width: 100%;
}
.divTableRow {
	display: table-row;
}
.divTableHeading {
	background-color: #EEE;
	display: table-header-group;
}
.divTableCell, .divTableHead {
	border: 1px solid #999999;
	display: table-cell;
	padding: 3px 10px;
}
.divTableHeading {
	background-color: #EEE;
	display: table-header-group;
	font-weight: bold;
}
.divTableFoot {
	background-color: #EEE;
	display: table-footer-group;
	font-weight: bold;
}
.divTableBody {
	display: table-row-group;
}
div.tab {
    overflow: hidden;
    border: 1px solid #ccc;
    background-color: #f1f1f1;
}

/* Style the buttons inside the tab */
div.tab button {
    background-color: inherit;
    float: left;
    border: none;
    outline: none;
    cursor: pointer;
    padding: 14px 16px;
    transition: 0.3s;
}

/* Change background color of buttons on hover */
div.tab button:hover {
    background-color: #f22121;
    color: #fff;
}

/* Create an active/current tablink class */
div.tab button.active {
    background-color: #ccc;
}

/* Style the tab content */
.tabcontent.1 {
    display: active

}
.tabcontent {
    display: none;
    padding: 6px 12px;
    border: 1px solid #ccc;
    border-top: none;
}
img {
height: 600px;
width: 600px;

}
span {
position: absolute;
text-align: center;
top: 50px;
left: 50px;
}
</style>
<?php
/*
UserSpice 4
An Open Source PHP User Management System
by the UserSpice Team at http://UserSpice.com

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/
?>
<?php
require_once 'users/init.php';
require_once $abs_us_root.$us_url_root.'users/includes/header.php';
//echo $self_path;
//echo $us_url_root;
require_once $abs_us_root.$us_url_root.'users/includes/navigation.php';
?>



<?php if (!securePage($_SERVER['PHP_SELF'])){die();} ?>
<script>
window.onload = function(){
  QCREPORT(event, 'QC1')
};
</script>
<?php
//PHP Goes Here!
?>
<div id="page-wrapper">
	<div class="container-fluid">
		<div class="row">
			<div class="col-sm-12">
				<!--	<h1>The quality report of : <?php echo "<h1>" . $_GET["id"] . "</h1>";?></h1> -->
		
			
		<script>		
				function QCREPORT(evt, qcName) {
    // Declare all variables
    var i, tabcontent, tablinks;

    // Get all elements with class="tabcontent" and hide them
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    // Get all elements with class="tablinks" and remove the class "active"
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    // Show the current tab, and add an "active" class to the link that opened the tab
    document.getElementById(qcName).style.display = "block";
    evt.currentTarget.className += " active";
}
</script>
<div class="tab">
	<button class="tablinks" onclick="QCREPORT(event, 'QC1')">Summary</button>
  <button class="tablinks" onclick="QCREPORT(event, 'QC2')">Index Summany</button>
  <button class="tablinks" onclick="QCREPORT(event, 'QC3')">Intensity by Cycle</button>
  <button class="tablinks" onclick="QCREPORT(event, 'QC4')">Plot by Lane</button>
  <button class="tablinks" onclick="QCREPORT(event, 'QC5')">Flowcell Intensity</button>
  <button class="tablinks" onclick="QCREPORT(event, 'QC6')">Qscore Histogram</button>
  <button class="tablinks" onclick="QCREPORT(event, 'QC7')">Qscore Heatmap</button>
  <button class="tablinks" onclick="QCREPORT(event, 'QC8')">Sample QC</button>
  <button class="tablinks" onclick="QCREPORT(event, 'QC9')">Details</button>
  <button class="tablinks" onclick="QCREPORT(event, 'QC10')">Samplesheet</button>
</div>				

<div id="QC1" class="tabcontent">
	
	<?php echo "<h3>" . $_GET["id"] . "</h3>";?>
  <p>QC Summary</p>
  <!--xxxxxxxxxxxxxxxxxxx -->
  
 <table align="center">
<tbody>
<tr>
<td> <a href="#" onclick="QCREPORT(event, 'QC3')"> <img src="./img/<?php echo $_GET["name"]?>/<?php echo $_GET["name"]?>_Intensity-by-cycle_Intensity.png"><a/></td>
<td> <a href="#" onclick="QCREPORT(event, 'QC6')"> <img src="./img/<?php echo $_GET["name"]?>/<?php echo $_GET["name"]?>_q-histogram.png"><a/></td>
</tr>
<tr>
<td><a href="#" onclick="QCREPORT(event, 'QC7')"> <img src="./img/<?php echo $_GET["name"]?>/<?php echo $_GET["name"]?>_q-heat-map.png"><a/></td>
<td><a href="#" onclick="QCREPORT(event, 'QC8')">  <img src="./img/<?php echo $_GET["name"]?>/<?php echo $_GET["name"]?>_sample-qc.png"><a/></td>
</tr>
</tbody>
</table>
	<!--xxxxxxxxxxxxxxxxxxx -->
</div>


<div id="QC2" class="tabcontent">
	<?php echo "<h3>" . $_GET["id"] . "</h3>";?>
  <p>Index Summary</p>
   <pre>
  		<?php
  				
  				$file1="./img/".$_GET["name"]."/".$_GET["name"]."_index-summary.txt";
  				//echo $file1;
					$myfile = fopen($file1, "r") or die("Unable to open $file2!");
					echo fread($myfile,filesize($file1));
					fclose($myfile);
			?>
	</pre>
</div>
				
<div id="QC3" class="tabcontent">
	<?php echo "<h3>" . $_GET["id"] . "</h3>";?>
  <p>Intensity by Cycle</p>
  <div align="center"><a href="#" onclick="QCREPORT(event, 'QC1')">  <img src="./img/<?php echo $_GET["name"]?>/<?php echo $_GET["name"]?>_Intensity-by-cycle_Intensity.png"></a></div> 
  <h3><font color="blue">Note:</font> The plot displays an average over all tiles for each lane.<h3/>
  <h3><font color="red">Tips:</font> Fluorophore intensities should be fairly uniform along each read. It is normal for one channel (C) to have higher intensity than others. A sudden drop in intensity may indicate over-clustering.<h3/>
</div>

<div id="QC4" class="tabcontent">
	<?php echo "<h3>" . $_GET["id"] . "</h3>";?>
  <p>Plot by Lane</p>
   <div align="center"> <img src="./img/<?php echo $_GET["name"]?>/<?php echo $_GET["name"]?>_ClusterCount-by-lane.png"></div>
   <h3><font color="blue">Note:</font> The plot at the bottom center position displays an average over all tiles for each lane. <h3/>
   <h3><font color="red">Tips:</font> Ideal cluster density is ~800-1000 (K/mm^2). Overloading the MiSeq with high concentration libraries will result in poor data quality or run failure.</h3>
</div>

<div id="QC5" class="tabcontent">
  	<?php echo "<h3>" . $_GET["id"] . "</h3>";?>
  <p>Flowcell Intensity</p>
   <div align="center"> <img src="./img/<?php echo $_GET["name"]?>/<?php echo $_GET["name"]?>_flowcell-Intensity.png">  </div>
    <h3><font color="blue">Note:</font> The plot shows the intensity of channel for each tile on a MiSeq flowcell <h3/>
   

</div>
				
<div id="QC6" class="tabcontent">
  	<?php echo "<h3>" . $_GET["id"] . "</h3>";?>
  <p> QScore Distribution</p>
   <div align="center"><a href="#" onclick="QCREPORT(event, 'QC1')"> <img src="./img/<?php echo $_GET["name"]?>/<?php echo $_GET["name"]?>_q-histogram.png"></a></div>
   <h3><font color="blue">Note:</font> The plot displays a histogram of the Q-scores over all cycles. The quality score is cumulative for current cycle and previous cycles, and only reads that pass the quality filter are included. <h3/>
   <h3><font color="red"><font color="red">Tips:</font></font> Bulk of data should be on the right side of the histogram. In a good run, more than 80% of bases have a Q score over 30. A base with Q score 30 has a 0.1% probability of being incorrectly called.<h3/>
   	<h3>Qscore:  Error Rate<h3/>
<h4>Q10: 10%</h4>
<h4>Q20: 1%</h4>
<h4>Q30: 0.1%</h4>
<h4>Q40: 0.01 %</h4>
</div>
<div id="QC7" class="tabcontent">
  	<?php echo "<h3>" . $_GET["id"] . "</h3>";?>
  <p>Qscore Heatmap</p>
   <div align="center"> <a href="#" onclick="QCREPORT(event, 'QC1')"><img src="./img/<?php echo $_GET["name"]?>/<?php echo $_GET["name"]?>_q-heat-map.png"></a></div>
    <h3><font color="blue">Note:</font> The plot displays Q-score heatmap, which compares Q-score on the Y-axis to the cycle on the X-axis. <h3/>
   <h3><font color="red">Tips:</font> Green bands near the top (Q Score ~40) indicate good quality reads. Left half of this graph corresponds to Read 1, Right half corresponds to Read 2. Q scores typically decrease somewhat towards the ends of reads.<h3/>
</div>
<div id="QC8" class="tabcontent">
  	<?php echo "<h3>" . $_GET["id"] . "</h3>";?>
  <p>Sample QC</p>
   <div align="center"> <a href="#" onclick="QCREPORT(event, 'QC1')"><img src="./img/<?php echo $_GET["name"]?>/<?php echo $_GET["name"]?>_sample-qc.png"></a></div>

 <h3><font color="red">Tips:</font> Percentage of reads assigned to each index should closely match the expected result based on library pooling.<h3/>

</div>	
		<div id="QC9" class="tabcontent">
	<?php echo "<h3>" . $_GET["id"] . "</h3>";?>
  <p></p>
		<pre>
  	  	<?php
  				
  				$file1="./img/".$_GET["name"]."/".$_GET["name"]."_summary.txt";
  				//echo $file1;
					$myfile = fopen($file1, "r") or die("Unable to open $file2!");
					echo fread($myfile,filesize($file1));
					fclose($myfile);
			?>
		</pre>
</div>	

		<div id="QC10" class="tabcontent">
	<?php echo "<h3>" . $_GET["id"] . "</h3>";?>
  <p></p>
		<pre>
  	  	<?php
  				
  				$file1="./img/".$_GET["name"]."/"."SampleSheet.csv";
  				//echo $file1;
					$myfile = fopen($file1, "r") or die("Unable to open $file2!");
					echo fread($myfile,filesize($file1));
					fclose($myfile);
			?>
		</pre>
</div>	
					<!-- End of main content section -->
				
			</div> <!-- /.col -->
		</div> <!-- /.row -->
	</div> <!-- /.container -->
</div> <!-- /.wrapper -->


	<!-- footers -->
<?php require_once $abs_us_root.$us_url_root.'users/includes/page_footer.php'; // the final html footer copyright row + the external js calls ?>

<!-- Place any per-page javascript here -->

<?php require_once $abs_us_root.$us_url_root.'users/includes/html_footer.php'; // currently just the closing /body and /html ?>
