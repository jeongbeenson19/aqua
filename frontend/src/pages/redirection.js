import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { setItemWithExpiry } from '../pages/auth';

const Redirection = () => {
  const navigate = useNavigate();
  const jwtToken = new URLSearchParams(window.location.search).get('jwt_token');
  const userId = new URLSearchParams(window.location.search).get('user_id');

  const needInfo = new URLSearchParams(window.location.search).get('need_info');
  const kakaoId = new URLSearchParams(window.location.search).get('kakao_id');

  const expiryTime = 60;

  useEffect(() => {
    console.log("useEffect 실행");

    if (needInfo && kakaoId) {
      navigate(`/signup`, { state: { kakaoId } });

    } else if (jwtToken && userId) {
      setItemWithExpiry('jwt_token', jwtToken, expiryTime * 60 * 1000);
      setItemWithExpiry('user_id', userId, expiryTime * 60 * 1000);

      navigate('/');
    } else {
      console.error('토큰 또는 사용자 ID가 없습니다!');
    }
  }, []);

  return <div>로그인 중입니다....</div>;
};

export default Redirection;