import React from 'react';
import styles from '../styles/kakaoLogin.module.css';

const backendURL = process.env.REACT_APP_BACKEND_URL;

const KakaoLogin = () => {
  const loginHandler = () => {
    // 백엔드에서 제공하는 카카오 로그인 URL로 리디렉션
    window.location.href = `${backendURL}/auth/kakao/login`;
  };

  return (
    <div className={styles.login}>
      <img
        src='/images/aqua.png'
        alt="aqua"
        className={styles.aquaImage}
      />
      <img
        src='/images/kakao_login.png'
        alt="카카오톡 로그인"
        onClick={loginHandler}
        className={styles.kakaoLoginImage}
      />
    </div>
  );
};

export default KakaoLogin;