import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import { getItemWithExpiry } from '../pages/auth';
import styles from '../styles/signup.module.css';

const backendURL = process.env.REACT_APP_BACKEND_URL;

useEffect(() => {
  console.log("kakaoId", kakaoId);
}, [kakaoId]);

const SingUp = () => {
  const navigate = useNavigate();
  const location = useLocation();

  // const kakaoId = location.state?.kakaoId || '';
  const [kakaoId, setUserId] = useState(getItemWithExpiry('kakao_id'));
  const [nickname, setNickname] = useState('');
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const signupHandler = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const url = `${backendURL}/auth/kakao/complete/${kakaoId}/${email}/${nickname}`;

    try {
      const response = await axios.post(url);

      if (response.status === 200) {
        console.log('회원가입 성공', response.data);
        navigate('/');
      }
    } catch (error) {
      console.error('회원가입 실패:', error.response?.data || error.message);
      setError(error.response?.data?.message || '회원가입에 실패했습니다. 다시 시도해주세요.');
    }
    finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.signup}>
      <h1 className={styles.title}>회원가입</h1>

      {error && <p className={styles.error}>{error}</p>} {/* 에러 메시지 출력 */}

      <form className={styles.form} onSubmit={signupHandler}>
        <div className={styles.field}>
          <label className={styles.label} htmlFor="nickname">이름</label>
          <input
            className={styles.input}
            id="nickname"
            type="text"
            value={nickname}
            onChange={(e) => setNickname(e.target.value)}
            disabled={loading}
          />
        </div>
        <div className={styles.field}>
          <label className={styles.label} htmlFor="email">이메일</label>
          <input
            className={styles.input}
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={loading}
          />
        </div>

        <button className={styles.button} type="submit" disabled={loading}>
          {loading ? '가입 중...' : '회원가입 하기'}
        </button>
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