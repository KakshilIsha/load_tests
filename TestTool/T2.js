import http from 'k6/http';
import { check, sleep} from 'k6';

export default function () {
    var url = 'http://3.108.3.226:9000/test1?value=10';
    let res = http.get(url);
    check(res, {
        "success": (r) => r.status == 200
    });
}
export let options = {
    vus: 100,
    duration: "30s"
};


