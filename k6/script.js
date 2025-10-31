import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 5,
  duration: '30s',
};

export default function () {
  const res = http.get('http://localhost:8000/api/users/');
  check(res, {
    'status is 401/403': (r) => r.status === 401 || r.status === 403,
  });
  sleep(1);
}

