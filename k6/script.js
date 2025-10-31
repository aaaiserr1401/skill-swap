import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 10,
  duration: '45s',
};

export default function () {
  const base = __ENV.BASE_URL || 'http://localhost:8000';
  const username = __ENV.USERNAME;
  const password = __ENV.PASSWORD;

  let headers = { 'Content-Type': 'application/json' };

  if (username && password) {
    // Try login
    const loginRes = http.post(`${base}/api/auth/login/`, JSON.stringify({ username, password }), { headers });
    if (loginRes.status === 200) {
      const token = JSON.parse(loginRes.body).token;
      headers = { ...headers, Authorization: `Token ${token}` };
      const users = http.get(`${base}/api/users/?search=test`, { headers });
      check(users, { 'users 200': (r) => r.status === 200 });
    }
  } else {
    // Anonymous check
    const res = http.get(`${base}/api/users/`);
    check(res, {
      'status is 401/403': (r) => r.status === 401 || r.status === 403,
    });
  }
  sleep(1);
}

