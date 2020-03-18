var mqtt= require('mqtt');

var client= mqtt.connect("mqtt:/192.168.0.113",{
    clientId: "Lamplennert",
    clean: false,
    will: {
        topic: "offline",
        payload: "Lamplennert",
        qos:2
    }
});

client.on("connect",function () {
    var lampa = setInterval(function () {
        client.publish("lamp/lampa","change",{qos:0, retain:false});
    },3000);
    
    var messtimer= setInterval(function () {
        client.publish("mess","hejhopp!", {qos:0, retain:false});    
    },30000);
});

client.on("error",function(error) {
    console.log("Cant connect "+error);
    process.exit(1);
})

function End(timers) {
    timers.forEach(timer => {
        clearInterval(timer);
    });
    client.end();
}