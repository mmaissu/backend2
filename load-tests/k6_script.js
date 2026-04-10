import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  stages: [
    { duration: "10s", target: 5 },   // ramp up
    { duration: "20s", target: 20 },  // steady
    { duration: "10s", target: 0 },   // ramp down
  ],
  thresholds: {
    http_req_failed: ["rate<0.01"], // <1% errors
    http_req_duration: ["p(95)<800"], // 95% under 800ms (adjust for your environment)
  },
};

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";

export default function () {
  const url = `${BASE_URL}/api/articles?search=AI&page=1&page_size=6&sort_by=newest&only_with_doi=false`;
  const res = http.get(url, { tags: { name: "GET /api/articles" } });

  check(res, {
    "status is 200": (r) => r.status === 200,
    "has items": (r) => {
      try {
        const body = r.json();
        return Array.isArray(body.items);
      } catch (_) {
        return false;
      }
    },
  });

  sleep(1);
}

