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
require_once $abs_us_root.$us_url_root.'users/includes/header3.php';
require_once $abs_us_root.$us_url_root.'users/includes/navigation.php';
?>

<?php if (!securePage($_SERVER['PHP_SELF'])){die();} ?>
<?php
//PHP Goes Here!
?>
<div id="page-wrapper">
	<div class="container-fluid">
		<div class="row">
			<div class="col-sm-12">
					<h1></h1>
					<!-- Content Goes Here. Class width can be adjusted -->
				<!--djcontent_start-->
				

  
<br><br/>

 

<table id="table"
data-toggle="table"
data-toolbar="#toolbar"
           data-toolbar="#toolbar"
           data-show-export="true"
           data-search="true"
           data-show-refresh="true"
           data-show-toggle="true"
           data-show-columns="true"           
           data-detail-view="true"
           data-detail-formatter="detailFormatter"
           data-minimum-count-columns="2"
           data-show-pagination-switch="true"
           data-pagination="true"
           data-id-field="id"
           data-page-list="[5,10, 25, 50, 100, ALL]"
           data-show-footer="false"
           data-url="access_info.php"
           data-sort-name="bccdc_id"
           data-sort-order="desc"
>
    <thead>
        <tr>
            <th data-field="bccdc_id" data-sortable="true">Run ID</th>
            <th data-field="source" data-sortable="true">Source</th>
            <th data-field="folder" data-sortable="true">Folder</th>
             <th data-formatter="reportFormatter_date" data-field="run_date" data-sortable="true">Date</th>
            <th data-field="start_time" data-sortable="true">Archiving start time</th>
             <th data-field="end_time" data-sortable="true">Analysis finish time</th>
             <th data-formatter="reportFormatter_status" data-sortable="true">Status</th>
             <th data-formatter="reportFormatter">Report</th>
           
        </tr>
    </thead>
</table>




</div>
				
				
				<!--djcontent_end-->

					<!-- End of main content section -->
			</div> <!-- /.col -->
		</div> <!-- /.row -->
	</div> <!-- /.container -->
</div> <!-- /.wrapper -->


	<!-- footers -->
<?php require_once $abs_us_root.$us_url_root.'users/includes/page_footer.php'; // the final html footer copyright row + the external js calls ?>

<!-- Place any per-page javascript here -->
   

    <script src="./test/assets/bootstrap-table/src/bootstrap-table.js"></script>
    <script src="./test/assets/bootstrap-table/src/extensions/export/bootstrap-table-export.js"></script>  
 
    <script src="/test/assets/jquery.min.js"></script> 
    <script src="/test/assets/bootstrap/js/bootstrap.min.js"></script>
    <script src="//rawgit.com/hhurz/tableExport.jquery.plugin/master/tableExport.js"></script>
 
    <script src="/test/ga.js"></script>


<script>
    var $table = $('#table1'),
        $remove = $('#remove'),
        selections = [];

    function initTable() {
        $table.bootstrapTable({
            height: getHeight(),            
            columns: [
                [
                    {
                        field: 'state',
                        checkbox: true,
                        rowspan: 2,
                        align: 'center',
                        valign: 'middle'
                    }, {
                        title: 'Items ID',
                        field: 'id',
                        rowspan: 2,
                        align: 'center',
                        valign: 'middle',
                        sortable: true,
                        footerFormatter: totalTextFormatter
                    }, {
                        title: 'Item Detail',
                        colspan: 3,
                        align: 'center'
                    }
                ],
                [
                    {
                        field: 'bccdc_id',
                        title: 'Item 1Name',
                        sortable: true,
                        editable: true,
                        formatter: operateFormatter,         
                        footerFormatter: totalNameFormatter,
                        align: 'center'
                    }, {
                        field: 'price',
                        title: 'Item Price',
                        sortable: true,
                        align: 'center',
                        editable: {
                            type: 'text',
                            title: 'Item Price1',
                            validate: function (value) {
                                value = $.trim(value);
                                if (!value) {
                                    return 'This field is required';
                                }
                                if (!/^\$/.test(value)) {
                                    return 'This field needs to start width $.'
                                }
                                var data = $table.bootstrapTable('getData'),
                                    index = $(this).parents('tr').data('index');
                                console.log(data[index]);
                                return '';
                            }
                        },
                        footerFormatter: totalPriceFormatter
                    }, {
                        field: 'operate',
                        title: 'Item Operate',
                        align: 'center',
                        events: operateEvents,
                        formatter: operateFormatter
      
                    }
                ]
            ]
        });
        // sometimes footer render error.
        setTimeout(function () {
            $table.bootstrapTable('resetView');
        }, 200);
        $table.on('check.bs.table uncheck.bs.table ' +
                'check-all.bs.table uncheck-all.bs.table', function () {
            $remove.prop('disabled', !$table.bootstrapTable('getSelections').length);

            // save your data, here just save the current page
            selections = getIdSelections();
            // push or splice the selections if you want to save all data selections
        });
       
        $table.on('all.bs.table', function (e, name, args) {
            console.log(name, args);
        });
        $remove.click(function () {
            var ids = getIdSelections();
            $table.bootstrapTable('remove', {
                field: 'id',
                values: ids
            });
            $remove.prop('disabled', true);
        });
        $(window).resize(function () {
            $table.bootstrapTable('resetView', {
                height: getHeight()
            });
        });
    }

    function getIdSelections() {
        return $.map($table.bootstrapTable('getSelections'), function (row) {
            return row.id
        });
    }

    function responseHandler(res) {
        $.each(res.rows, function (i, row) {
            row.state = $.inArray(row.id, selections) !== -1;
        });
        return res;
    }

      function gettaxon(jsfile_taxon,num,program){
                        var xmlhttp = new XMLHttpRequest();
                        xmlhttp.onreadystatechange = function() {
                        if (this.readyState == 4 && this.status == 200) {
                             var myArr = JSON.parse(this.responseText); 
                             var note="";
                           for (m = 0; m < myArr.length; m++) {
                             note=note+myArr[m].clade_name+": "+myArr[m].percent_reads_in_clade+"%"+"<br>";
                             //alert(note)
                            }
                           document.getElementById("clan"+"_"+program+num).innerHTML=note;
                         //    document.getElementById("demo").innerHTML = myArr.length+myArr[0].email + ", " + myArr[0].name+"<br>"+myArr.length+myArr[1].email + ", " + myArr[1].name;
                           }
                         };
                         xmlhttp.open("GET", jsfile_taxon, true);
                         xmlhttp.send();
                     };       
   function detailFormatter(index, row) {
        var html = [];
        var qc='/miseq/img/'+row.folder+'/'+row.folder+'_qcreport.html';
        var sample=row.sample;
        var sample_array = sample.split(',');
        var arrayLength = sample_array.length;
        //var regex = /\(([0-9]+)\)/;
        var regex=/(\S+)\((\d+)\)/
        var regex2 = /\(\)/;
        if(row.status>5) {
            html.push('<table class="table">  <thead><tr><th></th><th>Sample ID</th><th>Sample name</th><th>Project</th><th colspan="2">Kraken (Genus level: >5%)</th><th colspan="2">Kaiju (Genus level: >5%)</th><th>FastQC</th></tr><tbody>');
				    for (var i = 1; i <= arrayLength; i++) {
                var project = sample_array[i-1].match(regex);
					      if (null != project) {
					    	   var sample_name=project[1];
                   var projectid = project[2];
                   html.push('<tr>' +'<td>'+'&nbsp&nbsp&nbsp&nbsp&nbsp'+'</td>');
                   html.push('<td>'+'S'+i+'</td>');
                   html.push('<td>'+sample_name+'</td>');
                   html.push('<td>'+'<a target="_blank" href="http://sabin.bcgsc.ca:8080/irida-latest/projects/'+projectid+'">'+projectid+'</a>'+'</td>');                   	
                  } 
                 else {
                 	  sample_name=sample_array[i-1].replace(regex2,"");
                   	html.push('<tr>' +'<td>'+'&nbsp&nbsp&nbsp&nbsp&nbsp'+'</td>');
                   	html.push('<td>'+'S'+i+'</td>');
                   	html.push('<td>'+sample_name+'</td>');
                   	html.push('<td>'+'</td>');
                 	
                 	}
                   
                   var jsfile_kraken_taxon="/miseq/img/"+row.folder+'/'+sample_name+"\_kraken.js";
                   var jsfile_kaiju_taxon="/miseq/img/"+row.folder+'/'+sample_name+"\_kaiju.js";

                   gettaxon(jsfile_kraken_taxon,i,"kraken");
                   html.push('<td>'+'<p id="clan_kraken'+i+'"></p>'+'</td>');
                   html.push('<td>'+'<a title="Kraken Report"target="_blank" href="/miseq/img/'+row.folder+'/'+sample_name+"\_krona.out.html"+'"><i class="fa fa-file-image-o" style="font-size:24px;color:#8000ff""></i></span></a>');
                   gettaxon(jsfile_kaiju_taxon,i,"kaiju");
                   html.push('<td>'+'<p id="clan_kaiju'+i+'"></p>'+'</td>');
                   html.push('<td>'+'<a title="Kaiju Report"target="_blank" href="/miseq/img/'+row.folder+'/'+sample_name+"\_kaiju_krona.out.html"+'"><i class="glyphicon glyphicon-list-alt" style="font-size:24px;color:#ff4000""></i></span></a>');
                   html.push('<td>'+'<a target="_blank" href="/miseq/img/'+row.folder+'/'+sample_name+"\_F.html"+'">Forward</a>&nbsp&nbsp&nbsp'+'<a target="_blank" href="/miseq/img/'+row.folder+'/'+sample_name+"\_R.html"+'">Reverse</a>'+'</td>');
                   html.push('</tr> ');
               
					   }
				
           html.push('</thead></table>');
//        $.each(row, function (key, value) {
//            html.push('<p><b>' + key + ':</b> ' + value +qc+ '</p>');
//        });
        html.push('<p><b>' + ' ' + '</b> ');
      }


        return html.join('');
      }
 
 
 
 


    function reportFormatter(value, row, index) {
        var icon = row.status >1 ? 'glyphicon-star' : 'glyphicon-star-empty'
        if(row.status==4) {
        	      var qc='/miseq/img/'+row.folder+'/'+row.folder+'_qcreport.html';
        	     return [
                '<a target="_blank" title="MiSeq Reporter" class="like" href="show.php?name=',
                row.folder,
                '&id=',
                row.bccdc_id,                
                '">',
                 '<i class="fa fa-bar-chart" style="font-size:24px;color:#E91E63""></i>',
                 '</a>'
              ].join('');
        	}
        	if(row.status>4) {
        	      var qc='/miseq/img/'+row.folder+'/'+row.folder+'_qcreport.html';
        	     return [
                '<a target="_blank" title="MiSeq Reporter" class="like" href="show.php?name=',
                row.folder,
                '&id=',
                row.bccdc_id,                
                '">',
                 '<i class="fa fa-bar-chart" style="font-size:24px;color:#E91E63""></i>',
                 '</a>&nbsp&nbsp&nbsp',                 
                   '<a target="_blank" title="MultQC Report" class="like" href="/miseq/img/',
                row.folder,
                '/',
                row.folder,
                '_qcreport.html',                
                '">',
                 '<i class="glyphicon glyphicon-picture" style="font-size:24px;color:#3498DB""></i>',
                 '</a>  '
              ].join('');
        	}
       
        	
//        else {
//        	   return '<i class="glyphicon ' + icon + '"></i> ' ;
//        	}
      
    }
      function reportFormatter_date(value, row, index) {
        function IsNum(s){
           if(s!=null){
           var r,re;
           re = /\d{6}/i; 
           r = s.match(re);
           return (r==s)?true:false;
         }
           return false;
         }

        var folder_name = row.folder
        var date=folder_name.split("\_")
        if (IsNum(date[0])) {
            var year = parseInt(date[0].substr(0,2), 10);
            var month = parseInt(date[0].substr(2, 2), 10);
            var day = parseInt(date[0].substr(4, 2), 10);
            var date_formated='20'+year + '\-' + month + '\-' + day;
            return date_formated;
       
        	}
        else {
           return ""
        }
      
    }
    function reportFormatter_status(value, row, index) {
        if(row.status==1) {
        	        return ["Archiving process is running"].join('');
        	}
        if(row.status==2) {
        	        return ["Data has been transferred. Waiting for md5 check"].join('');
        	}
        if(row.status==3) {
        	        return ["Data has been transferred successfully. Waiting for QC report"].join('');
        	}
        if(row.status==4) {
        	        return ["Data has been transferred successfully. Waiting for FastQC result"].join('');
        	      }
        if(row.status==5) {
        	        return ["Data has been transferred successfully. Waiting for MultiQC result"].join('');
        	      }
        if(row.status==6) {
        	        return ["Data has been transferred successfully. Waiting for Kraken result"].join('');
        	      }
        if(row.status==7) {
        	        return ["Data has been transferred successfully. Waiting for Uploading to IRIDA"].join('');
        	      }
        if(row.status>=8) {
        	        return ["Archiving and analysis have been done"].join('');
        	      }      
                
    }
    window.operateEvents = {
        'click .like': function (e, value, row, index) {
            alert('You click like action, row: ' + JSON.stringify(row));
        },
        'click .remove': function (e, value, row, index) {
        	   alert('You click like action, row: ' + row.price);
            $table.bootstrapTable('remove', {
                field: 'id',
                values: [row.id]
            });
        }
    };

    function totalTextFormatter(data) {
        return 'Total';
    }
function LinkFormatter(value, row, index) {
  return "<a href='"+row.url+"'>"+value+"</a>";
}
    function totalNameFormatter(data) {
        return data.length;
    }

    function totalPriceFormatter(data) {
        var total = 0;
        $.each(data, function (i, row) {
            total += +(row.price.substring(1));
        });
        return '$' + total;
    }

    function getHeight() {
        return $(window).height() - $('h1').outerHeight(true);
    }

    $(function () {
        var scripts = [
                location.search.substring(1) || 'test/assets/bootstrap-table/src/bootstrap-table.js',
                'test/assets/bootstrap-table/src/extensions/export/bootstrap-table-export.js',
                'http://rawgit.com/hhurz/tableExport.jquery.plugin/master/tableExport.js',
                'test/assets/bootstrap-table/src/extensions/editable/bootstrap-table-editable.js',
                'http://rawgit.com/vitalets/x-editable/master/dist/bootstrap3-editable/js/bootstrap-editable.js'
            ],
            eachSeries = function (arr, iterator, callback) {
                callback = callback || function () {};
                if (!arr.length) {
                    return callback();
                }
                var completed = 0;
                var iterate = function () {
                    iterator(arr[completed], function (err) {
                        if (err) {
                            callback(err);
                            callback = function () {};
                        }
                        else {
                            completed += 1;
                            if (completed >= arr.length) {
                                callback(null);
                            }
                            else {
                                iterate();
                            }
                        }
                    });
                };
                iterate();
            };

        eachSeries(scripts, getScript, initTable);
    });

    function getScript(url, callback) {
        var head = document.getElementsByTagName('head')[0];
        var script = document.createElement('script');
        script.src = url;

        var done = false;
        // Attach handlers for all browsers
        script.onload = script.onreadystatechange = function() {
            if (!done && (!this.readyState ||
                    this.readyState == 'loaded' || this.readyState == 'complete')) {
                done = true;
                if (callback)
                    callback();

                // Handle memory leak in IE
                script.onload = script.onreadystatechange = null;
            }
        };

        head.appendChild(script);

        // We handle everything using the script element injection
        return undefined;
    }
</script>
<?php require_once $abs_us_root.$us_url_root.'users/includes/html_footer.php'; // currently just the closing /body an