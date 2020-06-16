// TODO:
    // välja rotation och startkordinat på bilarna
    // fixa random val av väg
    // placera en bil där den är in real time, om vi säger åt den att åka till kordinat (whatever de fuc) placera en bil där
    // skapa ett environment open ai gym för att hitta ut

let map_dimensions = [4, 4];
let car_coord = [0, 3];
let tile_rotation = 0;
let clientID = "clientID_" + parseInt(Math.random() * 100); // Generate a random client ID

window.onload = function() {
    var y_container = document.getElementById("map_container");
    for(y = map_dimensions[1]-1; y >= 0; y--){
        var new_y = '<div class="y_axis" id="' + y + '"></div>';
        y_container.innerHTML += new_y;
        for(x = 0; x < map_dimensions[0]; x++){
            var x_container = document.getElementById(this.y);  
            var coord = this.x + "," + this.y;
            var new_x = '<div class="box" " id="' + coord + '"><img style="" class="road_types" id="img' + coord + '" src="Images/PNG/missing.png"></div>';
            x_container.innerHTML += new_x;
        }
    }
}

function startConnect() {
    host = "maqiatto.com";                                  // Fetch the hostname/IP address and port number from the form
    port = 8883;
    username = "simon.ogaardjozic@abbindustrigymnasium.se";
    password = "scavenger";

    document.getElementById("messages").innerHTML += '<span>Connecting to: ' + host + ' on port: ' + port + '</span><br/>'; // Print output for the user in the messages div
    document.getElementById("messages").innerHTML += '<span>Using the following client value: ' + clientID + '</span><br/>';

    client = new Paho.MQTT.Client(host, Number(port), clientID);// Initialize new Paho client connection
    
    client.onConnectionLost = onConnectionLost; // Set callback handlers
    client.onMessageArrived = onMessageArrived;

    client.connect({
        userName : username, 
        password : password,
        onSuccess: onConnect,
        onFailure: onFail,
    });

    document.getElementById("Button").innerHTML = '<button onclick="startDisconnect()">Disconnect</button>'
}

function startDisconnect() {
    client.disconnect();
    document.getElementById("messages").innerHTML += '<span>Disconnected</span><br/>';
    document.getElementById("Button").innerHTML = '<button onclick="startConnect()">Connect</button>'
}

function onFail() {
    document.getElementById("messages").innerHTML += '<span>ERROR: Connection to: ' + host + ' on port: ' + port + ' failed.</span><br/>'
}

function onConnect() {
    topic = "simon.ogaardjozic@abbindustrigymnasium.se/Scavenger";  // Fetch the MQTT topic from the form

    document.getElementById("messages").innerHTML += '<span>Subscribing to: ' + topic + '</span><br/>'; // Print output for the user in the messages div

    client.subscribe(topic);    // Subscribe to the requested topic
    
    init_order();
}

function onConnectionLost(responseObject) { // Called when the client loses its connection
    document.getElementById("messages").innerHTML += '<span>ERROR: Connection lost</span><br/>';
    if (responseObject.errorCode !== 0) {
        document.getElementById("messages").innerHTML += '<span>ERROR: ' + + responseObject.errorMessage + '</span><br/>';
    }
    document.getElementById("Button").innerHTML = '<button onclick="startConnect()">Connect</button>'
}

function init_order(){
    let order;
    order = new Paho.MQTT.Message('["A", 0]');
    order.destinationName = "simon.ogaardjozic@abbindustrigymnasium.se/Scavenger";
    client.send(order);
}

function onMessageArrived(message) {    // Called when a message arrives
    console.log("onMessageArrived: " + message.payloadString);
    document.getElementById("messages").innerHTML += '<span>Topic: ' + message.destinationName + '  | ' + message.payloadString + '</span><br/>';
    if(message.payloadString.slice(-2) == ']]'){

        let car_road_array;
        let car;
        let road_array;
        let road_image;
        let theway_order;
        let theway;
        let order;
        var javascriptbighomo = [car_coord[0],car_coord[1]];

        car_road_array = get_json_data(message.payloadString);
        car = car_road_array[0];
        road_array = car_road_array[1];
        console.log("1",theway, order, car_coord);
        road_image = pick_image(road_array);
        theway_order = pick_way(road_array, javascriptbighomo, tile_rotation);
        theway = theway_order[0];
        order = theway_order[1];
        console.log("2",theway, order, car_coord);
        update_map(road_image, tile_rotation, car_coord)
        console.log("3",theway, order, car_coord);
        car_coord = calculate_car_coords(tile_rotation, theway, car_coord);
        tile_rotation = calculate_rotation(tile_rotation, theway);        

        client.send(order);

        console.log("order:", order, "car_coord:", car_coord, "tile_rotation:", tile_rotation, "theway:", theway, "road_image:", road_image, "road_array:", road_array, "car:", car);
    }
}

function get_json_data(JSON_DATA){
    let road_probability = 0.7
    let JSON_array = JSON.parse(JSON_DATA);
    let JSON_road_type = JSON_array[1];
    let road_array = [];
    
    for(i = 0; i < JSON_road_type.length; i++) {
        let probability = JSON_road_type[i]/JSON_road_type[2];
        if (probability >= road_probability){
            road_array.push(1);           
        }else{
            road_array.push(0);
        }
        // road_array.push(parseInt(probability + 0.5));
    }

    return [JSON_array[0], road_array];
}

function pick_image(road_array){
    let images = [
        "Images/PNG/straight.png", 
        "Images/PNG/curve-left.png", 
        "Images/PNG/curve-right.png", 
        "Images/PNG/three-way-left.png", 
        "Images/PNG/three-way-right.png", 
        "Images/PNG/three-way.png", 
        "Images/PNG/four-way.png"
    ];

    let type_ = [
        [1, 0, 1, 0], 
        [0, 0, 1, 1],
        [0, 1, 1, 0], 
        [1, 0, 1, 1], 
        [1, 1, 1, 0], 
        [0, 1, 1, 1], 
        [1, 1, 1, 1]
    ];

    let img;
    for(j = 0; j <type_.length; j++){
        if(JSON.stringify(type_[j]) == JSON.stringify(road_array)) {
            img = images[j];
        }
    }

    return img;
}

function pick_way(road_array, car_coord_, tile_rotation){

    var road_array;
    var car_coord_;
    var tile_rotation;
    var order;
    var theway;
    
    road_array[2] = 0;

    if (road_array.reduce((a, b) => a + b, 0) == 1){
        theway = road_array.findIndex(element => element == 1);
        var javascriptbighomo2 = [car_coord_[0],car_coord_[1]];
        var car_coord_test = calculate_car_coords(tile_rotation, theway, javascriptbighomo2);
        if (car_coord_test[0] >= 0 && car_coord_test[0] < map_dimensions[0] && car_coord_test[1] >= 0 && car_coord_test[1] < map_dimensions[1]){
            console.log("You lied!");
        }
        update_map("Images/PNG/car.png", 0, car_coord_test);
        order = new Paho.MQTT.Message('["A", 0]');
        order.destinationName = "simon.ogaardjozic@abbindustrigymnasium.se/Scavenger";
        return [theway, order];
    } else {
        var indexes = [], i;
        for (i=0; i<road_array.length; i++){
            if (road_array[i] == 1){
                var javascriptbighomo3 = [car_coord_[0],car_coord_[1]];
                var car_coord_test = calculate_car_coords(tile_rotation, i, javascriptbighomo3);
                if (car_coord_test[0] >= 0 && car_coord_test[0] < map_dimensions[0] && car_coord_test[1] >= 0 && car_coord_test[1] < map_dimensions[1]){

                    // account for two coords that are not connected
                    indexes.push(i);
                    
                    if (document.getElementById("img" + car_coord_test[0] + "," + car_coord_test[1]).src.slice(-22) == "Images/PNG/missing.png"){
                        update_map("Images/PNG/car.png", 0, car_coord_test);
                        order = choose_order(i);
                        return [i, order];
                    }
                }
            }
        }
        if (!indexes.length){
            console.log("You lied!");
        }
        var javascriptbighomo3 = [car_coord_[0],car_coord_[1]];
        var x = indexes[Math.floor(Math.random()*indexes.length)];
        var car_coord_test = calculate_car_coords(tile_rotation, x, javascriptbighomo3);
        console.log(indexes, car_coord_test, tile_rotation, x, javascriptbighomo3, car_coord_, Math.floor(Math.random()*indexes.length));
        update_map("Images/PNG/car.png", 0, car_coord_test);
        order = choose_order(x);
        return [x, order];
    }
}

function choose_order(i){
    if (i == 0){
        order = new Paho.MQTT.Message('["A", 0]');
    } else if (i == 1){
        order = new Paho.MQTT.Message('["A", 1]');
    } else {
        order = new Paho.MQTT.Message('["A", 2]');
    }
    order.destinationName = "simon.ogaardjozic@abbindustrigymnasium.se/Scavenger";
    return order;
}

function update_map(img_name, tile_rotation, car_coord){
    let img_container = document.getElementById("img" + car_coord[0] + "," + car_coord[1]);
    img_container.src = img_name;
    img_container.style.transform = "rotate(" + tile_rotation + "deg)";
}

function calculate_rotation(tile_rotation, theway){
    if (theway == 3){
        tile_rotation-=90;
    } else if (theway == 1){
        tile_rotation+=90;
    }

    if (tile_rotation < 0){
        tile_rotation = 270;
    } else if (tile_rotation > 360){
        tile_rotation = 90;
    }

    return tile_rotation;
}

function calculate_car_coords(tile_rotation, theway, car_coord_){
    var car_coord_;
    var theway;
    var tile_rotation;

    for (x=0; x<tile_rotation/90; x++){
        theway+=1
        if (theway>3){
            theway=0;
        }
    }

    if (theway==0){
        car_coord_[1]++;
    } else if (theway==1){
        car_coord_[0]++;
    } else if (theway==2){
        car_coord_[1]--;
    } else{
        car_coord_[0]--;
    }

    return car_coord_;
}
