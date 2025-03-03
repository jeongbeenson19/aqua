import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { setItemWithExpiry } from '../pages/auth';

const Redirection = () => {
  const navigate = useNavigate();
  const jwtToken = new URLSearchParams(window.location.search).get('jwt_token');
  const userId = new URLSearchParams(window.location.search).get('user_id');
  const expiryTimeInMinutes = 60;

  useEffect(() => {
    if (jwtToken && userId) {

      setItemWithExpiry('jwt_token', jwtToken, expiryTimeInMinutes * 60 * 1000);
      setItemWithExpiry('user_id', userId, expiryTimeInMinutes * 60 * 1000);

      navigate('/');
    } else {
      console.error('토큰 또는 사용자 ID가 없습니다.');
    }
  }, [jwtToken, userId, navigate]);

  return <div>로그인 중입니다...</div>;
};

export default Redirection;