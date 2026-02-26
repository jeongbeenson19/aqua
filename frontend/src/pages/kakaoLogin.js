import React from "react";
import styles from "../styles/kakaoLogin.module.css";

const backendURL = process.env.REACT_APP_BACKEND_URL;

const KakaoLogin = () => {
  const loginHandler = () => {
    window.location.href = `${backendURL}/auth/kakao/login`;
  };

  return (
    <div className={styles.loginPage}>
      <div className={styles.loginCard}>
        <img src="/images/aqua.png" alt="aqua" className={styles.brandLogo} />
        <p className={styles.caption}>AQUA START</p>
        <h1>카카오 로그인으로 학습 시작</h1>
        <p className={styles.description}>
          매일 과목별 퀴즈를 풀고 오답노트로 반복 학습을 이어가세요.
        </p>

        <button type="button" onClick={loginHandler} className={styles.loginButton}>
          <img src="/images/kakao_login.png" alt="카카오톡 로그인" className={styles.kakaoLoginImage} />
        </button>
      </div>
    </div>
  );
};

export default KakaoLogin;
