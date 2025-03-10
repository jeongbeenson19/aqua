import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { setItemWithExpiry } from '../pages/auth';

const Redirection = () => {
  const navigate = useNavigate();
  const jwtToken = new URLSearchParams(window.location.search).get('jwt_token');
  const userId = new URLSearchParams(window.location.search).get('user_id');

  const needsInfo = new URLSearchParams(window.location.search).get('needs_info') === "true";
  const kakaoId = new URLSearchParams(window.location.search).get('kakao_id');

  const expiryTime = 60;

  useEffect(() => {

    if (needsInfo && kakaoId) {
      setItemWithExpiry('kakao_id', kakaoId, expiryTime * 60 * 1000);

      navigate(`/signup`);

    } else if (jwtToken && userId) {
      setItemWithExpiry('jwt_token', jwtToken, expiryTime * 60 * 1000);
      setItemWithExpiry('user_id', userId, expiryTime * 60 * 1000);

      navigate('/');
    } else {
      console.error('토큰 또는 사용자 ID가 없습니다!');
    }
  }, []);

  return <div>로그인 처리 중입니다.....</div>;
};

export default Redirection;