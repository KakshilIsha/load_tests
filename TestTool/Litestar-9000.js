import http from 'k6/http';
import { sleep } from 'k6';

export default function() {
  http.get('http://3.110.145.75:9000/test1');
}
