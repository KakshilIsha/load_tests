import http from 'k6/http';
import { check, sleep } from 'k6';

export default function () {
    var url = 'http://3.108.226.242:9000/test3';
    var payload = JSON.stringify({
        username: "isha",
        password: "password",
    });

    var params = {
        headers: {
            'Content-Type': 'application/json',
        },
    };

    let res = http.post(url, payload, params);
    check(res, {
    "success": (r) => r.status === 200 || r.status === 201,
});

}

export let options = {
    vus: 100,
    duration: "30s"
};
