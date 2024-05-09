"use strict";
exports.__esModule = true;
var http_1 = require("http");
var req = http_1.request({
    host: 'localhost',
    port: '51234',
    path: '/posts',
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    }
}, function (response) {
    console.log(response.statusCode); // 200
});
req.end();
var message = "Hello World";
console.log(message);
var num = 12;
console.log(num);
