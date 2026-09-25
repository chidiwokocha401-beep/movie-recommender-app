import http from 'k6/http';
import { check } from 'k6';

export const options = {
  scenarios: {
    steady: {
      executor: 'constant-arrival-rate',
      rate: 100,
      timeUnit: '1s',
      duration: '2m',
      preAllocatedVUs: 20,
      maxVUs: 50,
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<200'],
    http_req_failed: ['rate<0.01'],
  },
};

const BASE = __ENV.API_URL ?? 'http://127.0.0.1:8000';

export default function () {
  const user = 1 + Math.floor(Math.random() * 50);
  const res = http.get(`${BASE}/users/${user}/recommendations?k=10`);
  check(res, { 'status 200': (r) => r.status === 200 });
}
