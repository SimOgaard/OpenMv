var mqtt= require('mqtt');
var client= mqtt.connect("mqtt:/192.168.0.113",{clientId:"Lyssnarlasse",clean:false});

client.on("connect",function () {    
    client.subscribe({"mess":0,"json":0,"offline":2});
});

client.on("message",function(topic,message) {
    var context= message.toString() ;
    
    if (topic=="json") {
        var json= JSON.parse(context);
        console.log(json.name+" åker "+json.direction);
    }

    if (topic=="offline") {
        console.log(context+" har gått vidare");
    } else{
        console.log(context); 
    }
});