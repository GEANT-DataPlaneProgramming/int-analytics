
function update_graphs() {
    document.getElementById('graphs').value = 0;
    $.ajax({
        url: "/delay",
        type: "GET",
        data: {
            'selected': document.getElementById('source_id').value,
            'duration': document.getElementById('duration').value,
            'startdate': document.getElementById('startdate').value
        },
        timeout: 5000,
        success: function (data) {
            var graphs = JSON.parse(data);
            var layout = {
                  title: 'Timestamps difference',
                  xaxis: {
                    title: 'time',
                    showgrid: true,
                    zeroline: false
                  },
                  yaxis: {
                    title: 'diff (ms)',
                    showline: false,
                  }
            };
            Plotly.react('delay', graphs, layout);
            document.getElementById('graphs').value++;
        }
    });
    
    $.ajax({
        url: "/delay_hist",
        type: "GET",
        data: {
            'selected': document.getElementById('source_id').value
        },
        timeout: 5000,
        success: function (data) {
            var graphs = JSON.parse(data);
            var layout = {
                  title: 'Timestamps difference histogram',
                  xaxis: {
                    title: 'diff (ms)',
                    showgrid: true,
                    zeroline: false
                  },
                  yaxis: {
                    title: 'count',
                    showline: false,
                  }
            };
            Plotly.react('delay_hist', graphs, layout);
            document.getElementById('graphs').value++;
        }
    });
    
    $.ajax({
        url: "/jitter",
        type: "GET",
        data: {
            'selected': document.getElementById('source_id').value
        },
        timeout: 5000,
        success: function (data) {
            var graphs = JSON.parse(data);
            var layout = {
                  title: 'Packet Inter-Arrival Time',
                  xaxis: {
                    title: 'time',
                    showgrid: true,
                    zeroline: false
                  },
                  yaxis: {
                    title: 'IAT (ms)',
                    showline: false,
                  }
            };
            Plotly.react('jitter', graphs, layout);
            document.getElementById('graphs').value++;
        }
    });
    
    $.ajax({
        url: "/jitter_hist",
        type: "GET",
        data: {
            'selected': document.getElementById('source_id').value
        },
        timeout: 5000,
        success: function (data) {
            var graphs = JSON.parse(data);
            var layout = {
                  title: 'Packet Inter-Arrival Time histogram',
                  xaxis: {
                    title: 'IAT (ms)',
                    showgrid: true,
                    zeroline: false
                  },
                  yaxis: {
                    title: 'count',
                    showline: false,
                  }
            };
            Plotly.react('jitter_hist', graphs, layout);
            document.getElementById('graphs').value++;
        }
    });
    
    $.ajax({
        url: "/reordering",
        type: "GET",
        data: {
            'selected': document.getElementById('source_id').value
        },
        timeout: 5000,
        success: function (data) {
            var graphs = JSON.parse(data);
            var layout = {
                  title: 'Packet reordering',
                  xaxis: {
                    title: 'time',
                    showgrid: true,
                    zeroline: false
                  },
                  yaxis: {
                    title: 'reordering factor',
                    showline: false,
                  }
            };
            Plotly.react('reordering', graphs, layout);
            document.getElementById('graphs').value++;
        }
    });
}

$('#source_id').on('change',function(){
    update_graphs()
})

$('#graphsUpdate').on('click', function(){
    update_graphs()
});

 $(document).ready(function (){
    $.getJSON('/list', {}, function(data){
        var options = '';
        for (var x = 0; x < data.length; x++) {
            options += '<option value="' + data[x]['id'] + '">' + data[x]['text'] + '</option>';
        }
        $('#source_id').html(options);
    });
});
