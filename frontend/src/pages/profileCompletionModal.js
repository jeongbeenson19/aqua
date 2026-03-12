import React from "react";
import { Link } from "react-router-dom";
import styles from "../styles/profileCompletionModal.module.css";

const fieldLabels = {
  nickname: "이름",
  email: "이메일",
};

function ProfileCompletionModal({
  isOpen,
  profileForm,
  missingFields,
  errorMessage,
  isSubmitting,
  hasAcknowledgedPrivacyNotice,
  onChange,
  onPrivacyNoticeToggle,
  onSubmit,
}) {
  if (!isOpen) {
    return null;
  }

  const missingFieldNames = missingFields
    .map((field) => fieldLabels[field])
    .filter(Boolean)
    .join(", ");

  return (
    <div className={styles.modalOverlay}>
      <div className={styles.modalPanel} onClick={(event) => event.stopPropagation()}>
        <div className={styles.modalHeader}>
          <p className={styles.eyebrow}>PROFILE REQUIRED</p>
          <h2>이름과 이메일을 입력해주세요</h2>
          <p className={styles.description}>
            {missingFieldNames
              ? `${missingFieldNames} 정보가 비어 있어 로그인 마무리를 위해 입력이 필요합니다.`
              : "로그인을 완료하려면 이름과 이메일을 입력해주세요."}
          </p>
        </div>

        <form className={styles.formBody} onSubmit={onSubmit}>
          <section className={styles.noticeCard}>
            <h3>개인정보 수집 및 이용 안내</h3>
            <ul className={styles.noticeList}>
              <li>수집 항목: 이름, 이메일</li>
              <li>수집 목적: 회원 식별, 로그인 완료, 서비스 이용 안내 및 문의 대응</li>
              <li>보유 기간: 회원 탈퇴 시까지 또는 관련 법령상 보존 기간 종료 시까지</li>
              <li>거부 시 불이익: 로그인 완료 및 서비스 이용이 제한될 수 있습니다</li>
            </ul>
            <Link
              to="/privacy-policy"
              target="_blank"
              rel="noreferrer"
              className={styles.policyLink}
            >
              개인정보 처리방침 보기
            </Link>
          </section>

          <label className={styles.fieldGroup}>
            <span>이름</span>
            <input
              type="text"
              name="nickname"
              autoComplete="nickname"
              placeholder="이름을 입력하세요"
              value={profileForm.nickname}
              onChange={onChange}
              disabled={isSubmitting}
            />
          </label>

          <label className={styles.fieldGroup}>
            <span>이메일</span>
            <input
              type="email"
              name="email"
              autoComplete="email"
              placeholder="example@email.com"
              value={profileForm.email}
              onChange={onChange}
              disabled={isSubmitting}
            />
          </label>

          <label className={styles.checkRow}>
            <input
              type="checkbox"
              checked={hasAcknowledgedPrivacyNotice}
              onChange={onPrivacyNoticeToggle}
              disabled={isSubmitting}
            />
            <span>위 개인정보 수집 및 이용 안내를 확인했습니다.</span>
          </label>

          {errorMessage ? <p className={styles.errorText}>{errorMessage}</p> : null}

          <button type="submit" className={styles.submitButton} disabled={isSubmitting}>
            {isSubmitting ? "저장 중..." : "저장하고 계속하기"}
          </button>
        </form>
      </div>
    </div>
  );
}

export default ProfileCompletionModal;
