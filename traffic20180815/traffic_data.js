var streetmap = L.tileLayer("https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}", {
  attribution: "Map data &copy; <a href=\"https://www.openstreetmap.org/\">OpenStreetMap</a> contributors, <a href=\"https://creativecommons.org/licenses/by-sa/2.0/\">CC-BY-SA</a>, Imagery © <a href=\"https://www.mapbox.com/\">Mapbox</a>",
  maxZoom: 22,
  id: "mapbox.streets",
  accessToken: API_KEY
});

var darkmap = L.tileLayer("https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}", {
  attribution: "Map data &copy; <a href=\"https://www.openstreetmap.org/\">OpenStreetMap</a> contributors, <a href=\"https://creativecommons.org/licenses/by-sa/2.0/\">CC-BY-SA</a>, Imagery © <a href=\"https://www.mapbox.com/\">Mapbox</a>",
  maxZoom: 22,
  id: "mapbox.dark",
  accessToken: API_KEY
});

// Create a baseMaps object
var baseMaps = {
    "Street Map": streetmap,
    "Dark Map": darkmap
};


// Store our API endpoint as queryUrl
var metaURL = "https://data.cityofchicago.org/resource/8v9j-bter.json?$limit=2000";
var trafficSegmentURL = "https://data.cityofchicago.org/resource/kkgn-a2j4.json?$where=last_update%20between%20%272018-03-13T09:30:00%27%20and%20%272018-03-13T09:40:00%27&$limit=1500";

// Traffic metadata URL
d3.json(metaURL, function(metaData) {
//   console.log(metaData);

  d3.json(trafficSegmentURL, function(trafficSegmentData) {
    // console.log(trafficSegmentData);

    metaData.forEach(function(data) {
        // data.segmentid = +data.segmentid;
        data._lit_lat = +data._lit_lat;
        data._lif_lat = +data._lif_lat;
        data._lit_lon = +data._lit_lon;
        data.start_lon = +data.start_lon;
        data._length = +data._length;
    });
    
    var metaObj = {};
    for (var i = 0; i < metaData.length; i++) {
      var id = metaData[i].segmentid;
      var startCoordinates = [metaData[i]._lif_lat, metaData[i].start_lon];
      var endCoordinates = [metaData[i]._lit_lat, metaData[i]._lit_lon];
      var coordinates = [startCoordinates, endCoordinates];
      metaObj[id] = {"coordinates": coordinates};
    }
    // console.log("metaObj");
    // console.log(metaObj);

    trafficSegmentData.forEach(function(data) {
    //   data.segment_id = +data.segment_id;
        data.traffic = +data.traffic;
        // console.log(data);
        // console.log(data.segment_id);
        // console.log(metaObj[data.segment_id])
        data.coordinates = metaObj[data.segment_id].coordinates;

    });
    // console.log(trafficSegmentData);

    // console.log(trafficSegmentData[0].coordinates);

    var trafficMarkers = [];

    for(i=0;i<trafficSegmentData.length; i++)
    {
        var line;
        console.log(trafficSegmentData[i].traffic);
        if (trafficSegmentData[i].traffic > 20) {
            line = trafficSegmentData[i].coordinates;
            // console.log(line);
    
            var polylineI = L.polyline(line, {
                color: 'red'
            });   
            trafficMarkers.push(polylineI);

        }
        else if (trafficSegmentData[i].traffic > 10) {

            line = trafficSegmentData[i].coordinates;
            // console.log(line);
    
            var polylineI = L.polyline(line, {
                color: 'yellow'
            });   
            trafficMarkers.push(polylineI);

        }
        else if(trafficSegmentData[i].traffic > -1) {
            line = trafficSegmentData[i].coordinates;
            // console.log(line);
    
            var polylineI = L.polyline(line, {
                color: 'green'
            });  
            trafficMarkers.push(polylineI);
        }   


    }
    console.log(trafficMarkers);

    trafficLayer = L.layerGroup(trafficMarkers);

    // Create an overlay object
    var overlayMaps = {
        "Traffic segments": trafficLayer,
    };

    // Define a map object
    var map = L.map("map", {
        center: [41.894741, -87.650566],
        zoom: 10,
        layers: [streetmap, trafficLayer]
    });

    // Add the layer control to the map
    L.control.layers(baseMaps, overlayMaps, {collapsed: false}).addTo(map);
    
    // var latlngs = trafficSegmentData[i].coordinates;
    // var polylineI = L.polyline(latlngs, {
    //     color: 'red'
    // });

    // // Create an overlay object
    // var overlayMaps = {
    //     "Traffic segments": polylineI,
    // };

    // // Define a map object
    // var map = L.map("map", {
    //     center: [41.894741, -87.650566],
    //     zoom: 10,
    //     layers: [streetmap, polylineI]
    // });

    // // Add the layer control to the map
    // L.control.layers(baseMaps, overlayMaps, {collapsed: false}).addTo(map);


  })
})

// d3.csv("./traffic_segments.csv", function(error, metaData) { // Can also use `then`

//   // Log an error if one exists
//   if (error) return console.warn(error);

//   // Print the data
//   console.log(metaData);

//   // Cast the hours value to a number for each piece of metaData
//   metaData.forEach(function(data) {
//     data.SEGMENTID = +data.SEGMENTID;
//     data.END_LATITUDE = +data.END_LATITUDE;
//     data.START_LATITUDE = +data.START_LATITUDE;
//     data.END_LONGITUDE = +data.END_LONGITUDE;
//     data.START_LONGITUDE = +data.START_LONGITUDE;
//     data.LENGTH = +data.LENGTH;
//   });

//   var metaObj = {};
//   for (var i = 0; i < metaData.length; i++) {
//     var id = metaData[i];
//     var startCoordinates = [metaData[i].START_LATITUDE, metaData[i].START_LONGITUDE];
//     var endCoordinates = [metaData[i].END_LATITUDE, metaData[i].END_LONGITUDE];
//     var coordinates = [startCoordinates, endCoordinates];
//     metaObj[id] = {"coordinates": coordinates};
//     console.log(metaObj[id])
//   }
//   console.log(metaObj)

// });
