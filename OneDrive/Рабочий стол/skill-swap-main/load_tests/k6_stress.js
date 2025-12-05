import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');

// Стресс-тест: постепенное увеличение нагрузки до предела
export const options = {
  stages: [
    { duration: '1m', target: 50 },   // Быстро до 50 пользователей
    { duration: '2m', target: 100 },   // До 100 пользователей
    { duration: '2m', target: 150 },   // До 150 пользователей
    { duration: '2m', target: 200 },  // До 200 пользователей (максимум)
    { duration: '1m', target: 0 },    // Снижение до 0
  ],
  thresholds: {
    http_req_duration: ['p(95)<1000'],  // 95% запросов быстрее 1 секунды
    http_req_failed: ['rate<0.05'],     // Меньше 5% ошибок
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const TEST_USERNAME = __ENV.TEST_USERNAME || 'testuser';
const TEST_PASSWORD = __ENV.TEST_PASSWORD || 'testpass123';

let authToken = null;

function login() {
  const loginRes = http.post(`${BASE_URL}/api/auth/login/`, JSON.stringify({
    username: TEST_USERNAME,
    password: TEST_PASSWORD,
  }), {
    headers: { 'Content-Type': 'application/json' },
  });

  const success = check(loginRes, {
    'login successful': (r) => r.status === 200,
  });

  if (success) {
    authToken = JSON.parse(loginRes.body).token;
  }

  return success;
}

export default function () {
  if (!authToken) {
    if (!login()) {
      sleep(1);
      return;
    }
  }

  const headers = {
    'Authorization': `Token ${authToken}`,
    'Content-Type': 'application/json',
  };

  // Параллельные запросы для создания нагрузки
  const responses = http.batch([
    ['GET', `${BASE_URL}/api/users/`, null, { headers }],
    ['GET', `${BASE_URL}/api/skills/`, null, { headers }],
    ['GET', `${BASE_URL}/api/exchanges/`, null, { headers }],
  ]);

  const allSuccess = responses.every(r => r.status === 200);
  errorRate.add(!allSuccess);

  sleep(0.5);
}

