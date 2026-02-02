import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
  withCredentials: true, // refresh token 쿠키용
});

// ✅ 요청 인터셉터 (그대로 유지)
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ✅ 응답 인터셉터 (추가!)
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // 🔴 access token 만료 감지
    if (
      error.response?.status === 401 &&
      error.response?.data?.detail === "Token expired" &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true;

      try {
        // 🔁 refresh token으로 재발급 요청
        const res = await axios.post(
          "http://localhost:8000/auth/refresh",
          {},
          { withCredentials: true }
        );

        const newAccessToken = res.data.access_token;

        // 🔐 새 토큰 저장
        localStorage.setItem("access_token", newAccessToken);

        // 🔁 원래 요청 헤더 갱신
        originalRequest.headers.Authorization =
          `Bearer ${newAccessToken}`;

        // 🔁 원래 요청 다시 실행
        return api(originalRequest);
      } catch (refreshError) {
        // ❌ refresh 실패 → 완전 로그아웃
        localStorage.removeItem("access_token");
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
