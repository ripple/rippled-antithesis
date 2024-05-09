import * as http from 'http';
import { request } from 'http';


const req = request(
  {
    host: 'localhost',
    port: '51234',
    path: '/posts',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  },
  response => {
    console.log(response.statusCode); // 200
  }
);

req.end();


var message:string = "Hello World"
console.log(message)

var num:number = 12
console.log(num)
