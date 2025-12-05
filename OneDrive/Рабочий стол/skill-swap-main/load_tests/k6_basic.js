import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Кастомная метрика для отслеживания ошибок
const errorRate = new Rate('errors');

// Конфигурация теста
export const options = {
  stages: [
    { duration: '30s', target: 10 },   // Разогрев: 10 пользователей за 30 секунд
    { duration: '1m', target: 20 },      // Нормальная нагрузка: 20 пользователей
    { duration: '30s', target: 30 },     // Пиковая нагрузка: 30 пользователей
    { duration: '1m', target: 20 },      // Возврат к нормальной нагрузке
    { duration: '30s', target: 0 },      // Снижение до 0
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],    // 95% запросов должны быть быстрее 500ms
    http_req_failed: ['rate<0.01'],      // Меньше 1% ошибок
    errors: ['rate<0.01'],
  },
};

// Базовый URL API (можно изменить через переменную окружения)
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

// Тестовые данные
const TEST_USERNAME = __ENV.TEST_USERNAME || 'testuser';
const TEST_PASSWORD = __ENV.TEST_PASSWORD || 'testpass123';

let authToken = null;

// Функция для аутентификации
function login() {
  const loginRes = http.post(`${BASE_URL}/api/auth/login/`, JSON.stringify({
    username: TEST_USERNAME,
    password: TEST_PASSWORD,
  }), {
    headers: { 'Content-Type': 'application/json' },
  });

  const success = check(loginRes, {
    'login status is 200': (r) => r.status === 200,
    'login has token': (r) => JSON.parse(r.body).token !== undefined,
  });

  errorRate.add(!success);

  if (success) {
    authToken = JSON.parse(loginRes.body).token;
  }

  return success;
}

// Основная функция теста
export default function () {
  // Аутентификация
  if (!authToken) {
    const loggedIn = login();
    if (!loggedIn) {
      sleep(1);
      return;
    }
  }

  const headers = {
    'Authorization': `Token ${authToken}`,
    'Content-Type': 'application/json',
  };

  // Тест 1: Получение списка пользователей
  const usersRes = http.get(`${BASE_URL}/api/users/`, { headers });
  const usersSuccess = check(usersRes, {
    'users list status is 200': (r) => r.status === 200,
    'users list has results': (r) => JSON.parse(r.body).results !== undefined,
  });
  errorRate.add(!usersSuccess);

  sleep(1);

  // Тест 2: Поиск пользователей
  const searchRes = http.get(`${BASE_URL}/api/users/?search=test`, { headers });
  const searchSuccess = check(searchRes, {
    'search status is 200': (r) => r.status === 200,
  });
  errorRate.add(!searchSuccess);

  sleep(1);

  // Тест 3: Получение списка навыков
  const skillsRes = http.get(`${BASE_URL}/api/skills/`, { headers });
  const skillsSuccess = check(skillsRes, {
    'skills list status is 200': (r) => r.status === 200,
    'skills list has results': (r) => JSON.parse(r.body).results !== undefined,
  });
  errorRate.add(!skillsSuccess);

  sleep(1);

  // Тест 4: Получение списка обменов
  const exchangesRes = http.get(`${BASE_URL}/api/exchanges/`, { headers });
  const exchangesSuccess = check(exchangesRes, {
    'exchanges list status is 200': (r) => r.status === 200,
  });
  errorRate.add(!exchangesSuccess);

  sleep(1);
}

// Функция вызывается после завершения всех итераций
export function teardown(data) {
  console.log('Load test completed');
}

