import React from 'react';
import styles from '../styles/signup.module.css';

const backendURL = process.env.REACT_APP_URL

const SingUp = () => {
  const loginHandler = () => {

  };

  return (
    <div className={styles.signup}>
      <h1 className={styles.title}>회원가입</h1>

      <form className={styles.form}>
        <div className={styles.field}>
          <label className={styles.label} htmlFor="name">이름</label>
          <input className={styles.input} id="name" type="text" />
        </div>
        <div className={styles.field}>
          <label className={styles.label} htmlFor="email">이메일</label>
          <input className={styles.input} id="email" type="email" />
        </div>

        <button className={styles.button}>회원가입 하기</button>
      </form>
      <img
        src='/images/aqua.png'
        alt="aqua"
        className={styles.aquaImage}
      />
    </div>
  );
};

export default SingUp;