import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { getItemWithExpiry, setItemWithExpiry } from "./auth";
import ProfileCompletionModal from "./profileCompletionModal";
import styles from "../styles/redirection.module.css";

const backendURL = process.env.REACT_APP_BACKEND_URL;
const expiryTime = 120;

const getErrorMessage = (error) => {
  const detail = error?.response?.data?.detail;

  if (Array.isArray(detail) && detail.length > 0) {
    return detail.map((item) => item.msg).join(" ");
  }

  if (typeof detail === "string") {
    return detail;
  }

  return "추가 정보를 저장하지 못했습니다. 잠시 후 다시 시도해주세요.";
};

const Redirection = () => {
  const navigate = useNavigate();
  const query = new URLSearchParams(window.location.search);
  const jwtToken = query.get("jwt_token");
  const userId = query.get("user_id");
  const profileRequired = query.get("profile_required") === "true";
  const storedJwtToken = getItemWithExpiry("jwt_token");
  const storedUserId = getItemWithExpiry("user_id");

  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [missingFields, setMissingFields] = useState([]);
  const [profileForm, setProfileForm] = useState({
    nickname: "",
    email: "",
  });
  const [hasAcknowledgedPrivacyNotice, setHasAcknowledgedPrivacyNotice] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    let isMounted = true;

    const bootstrapLogin = async () => {
      if (!jwtToken || !userId) {
        if (storedJwtToken && storedUserId) {
          navigate("/", { replace: true });
          return;
        }

        navigate("/login", { replace: true });
        return;
      }

      setItemWithExpiry("jwt_token", jwtToken, expiryTime * 60 * 1000);
      setItemWithExpiry("user_id", userId, expiryTime * 60 * 1000);

      if (!profileRequired) {
        navigate("/", { replace: true });
        return;
      }

      try {
        const response = await axios.get(`${backendURL}/users/me/profile`, {
          headers: {
            Authorization: `Bearer ${jwtToken}`,
          },
        });

        if (!isMounted) {
          return;
        }

        const { nickname, email, missing_fields: missingFieldsFromApi, profile_required: needsProfile } = response.data;

        setProfileForm({
          nickname: nickname || "",
          email: email || "",
        });
        setHasAcknowledgedPrivacyNotice(false);
        setMissingFields(missingFieldsFromApi || []);

        if (!needsProfile) {
          navigate("/", { replace: true });
          return;
        }

        setIsModalOpen(true);
      } catch (error) {
        if (!isMounted) {
          return;
        }

        console.error("프로필 조회 오류:", error);
        setMissingFields(["nickname", "email"]);
        setErrorMessage("추가 정보를 불러오지 못했습니다. 직접 입력 후 다시 저장해주세요.");
        setIsModalOpen(true);
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    bootstrapLogin();

    return () => {
      isMounted = false;
    };
  }, [jwtToken, navigate, profileRequired, storedJwtToken, storedUserId, userId]);

  const handleChange = (event) => {
    const { name, value } = event.target;

    setProfileForm((previous) => ({
      ...previous,
      [name]: value,
    }));
    setErrorMessage("");
  };

  const handlePrivacyNoticeToggle = (event) => {
    setHasAcknowledgedPrivacyNotice(event.target.checked);
    setErrorMessage("");
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    const trimmedNickname = profileForm.nickname.trim();
    const trimmedEmail = profileForm.email.trim();
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!trimmedNickname || !trimmedEmail) {
      setErrorMessage("이름과 이메일을 모두 입력해주세요.");
      return;
    }

    if (!emailPattern.test(trimmedEmail)) {
      setErrorMessage("올바른 이메일 형식을 입력해주세요.");
      return;
    }

    if (!hasAcknowledgedPrivacyNotice) {
      setErrorMessage("개인정보 수집 및 이용 안내를 확인해주세요.");
      return;
    }

    setIsSubmitting(true);
    setErrorMessage("");

    try {
      const response = await axios.put(
        `${backendURL}/users/me/profile`,
        {
          nickname: trimmedNickname,
          email: trimmedEmail,
        },
        {
          headers: {
            Authorization: `Bearer ${jwtToken}`,
            "Content-Type": "application/json",
          },
        }
      );

      if (response.status === 200 && !response.data.profile_required) {
        setItemWithExpiry("jwt_token", jwtToken, expiryTime * 60 * 1000);
        setItemWithExpiry("user_id", userId, expiryTime * 60 * 1000);
        setIsModalOpen(false);
        navigate("/", { replace: true });
        return;
      }

      setMissingFields(response.data.missing_fields || []);
      setErrorMessage("이름과 이메일을 다시 확인해주세요.");
    } catch (error) {
      console.error("프로필 저장 오류:", error);
      setErrorMessage(getErrorMessage(error));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={styles.redirectPage}>
      <div className={styles.redirectCard}>
        <div className={styles.loaderRing} aria-hidden="true" />
        <p className={styles.eyebrow}>AQUA AUTH</p>
        <h1>{profileRequired ? "회원 정보를 확인하고 있습니다" : "로그인 처리 중입니다"}</h1>
        <p className={styles.description}>
          {profileRequired
            ? "이름과 이메일이 비어 있으면 입력 팝업이 바로 열립니다."
            : "잠시만 기다리면 학습 홈으로 이동합니다."}
        </p>
      </div>

      <ProfileCompletionModal
        isOpen={isModalOpen}
        profileForm={profileForm}
        missingFields={missingFields}
        errorMessage={errorMessage}
        isSubmitting={isSubmitting}
        hasAcknowledgedPrivacyNotice={hasAcknowledgedPrivacyNotice}
        onChange={handleChange}
        onPrivacyNoticeToggle={handlePrivacyNoticeToggle}
        onSubmit={handleSubmit}
      />

      {isLoading && <span className={styles.loadingAssist}>사용자 정보를 확인하는 중입니다.</span>}
    </div>
  );
};

export default Redirection;
