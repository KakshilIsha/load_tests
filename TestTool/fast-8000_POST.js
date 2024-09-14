import http from 'k6/http';
import { sleep } from 'k6';

function getRandomInt(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function generateRandomParams() {
    const params = {};
    for (let i = 0; i < 30; i++) {
        params[`param${i}`] = getRandomInt(1, 100); // Generate random integers as parameter values
    }
    params['limit'] = getRandomInt(1, 100); // Ensuring 'limit' parameter is included
    params['offset'] = getRandomInt(0, 50); // Ensuring 'offset' parameter is included
    return params;
}

export default function() {
    const url = 'http://localhost:8080/users';
    const payload = JSON.stringify(generateRandomParams());
    const params = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    http.post(url, payload, params);
}
