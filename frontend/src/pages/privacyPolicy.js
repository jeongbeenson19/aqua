import React from "react";
import styles from "../styles/privacyPolicy.module.css";

function PrivacyPolicy() {
  return (
    <div className={styles.page}>
      <main className={styles.sheet}>
        <p className={styles.eyebrow}>AQUA PRIVACY</p>
        <h1>개인정보 처리방침</h1>
        <p className={styles.updatedAt}>최종 업데이트: 2026년 3월 12일</p>

        <section className={styles.section}>
          <h2>1. 수집하는 개인정보 항목</h2>
          <p>
            AQUA는 로그인 및 서비스 제공을 위해 이름, 이메일, 카카오 로그인 식별정보와 서비스 이용 중
            생성되는 학습 기록을 수집할 수 있습니다.
          </p>
        </section>

        <section className={styles.section}>
          <h2>2. 개인정보 이용 목적</h2>
          <p>수집한 개인정보는 다음 목적 범위에서 이용합니다.</p>
          <ul>
            <li>회원 식별 및 로그인 완료 처리</li>
            <li>퀴즈, 오답노트, 학습 기록 등 서비스 제공</li>
            <li>이용자 문의 응대 및 서비스 운영 공지</li>
            <li>서비스 품질 개선 및 오류 대응</li>
          </ul>
        </section>

        <section className={styles.section}>
          <h2>3. 보유 및 이용 기간</h2>
          <p>
            원칙적으로 회원 탈퇴 시 지체 없이 파기합니다. 다만 관계 법령에 따라 일정 기간 보존이 필요한
            경우 해당 기간 동안 별도로 보관할 수 있습니다.
          </p>
        </section>

        <section className={styles.section}>
          <h2>4. 제3자 제공 및 처리 위탁</h2>
          <p>
            법령상 근거가 있거나 이용자의 별도 동의가 있는 경우를 제외하고, 개인정보를 제3자에게 제공하지
            않습니다. 서비스 운영상 필요한 범위에서 처리 위탁이 발생하는 경우 관련 사실을 별도로 안내합니다.
          </p>
        </section>

        <section className={styles.section}>
          <h2>5. 이용자의 권리</h2>
          <p>
            이용자는 언제든지 자신의 개인정보에 대해 조회, 수정, 삭제를 요청할 수 있으며 관련 문의는 서비스
            운영 채널을 통해 접수할 수 있습니다.
          </p>
        </section>

        <section className={styles.section}>
          <h2>6. 안전성 확보 조치</h2>
          <p>
            AQUA는 개인정보의 분실, 도난, 유출, 위변조를 방지하기 위해 접근 통제, 인증 관리 등 합리적인
            보호조치를 적용하기 위해 노력합니다.
          </p>
        </section>

        <section className={styles.section}>
          <h2>7. 고지 의무</h2>
          <p>
            본 처리방침의 내용 추가, 삭제, 수정이 있는 경우 시행일자 기준으로 서비스 내에서 안내합니다.
          </p>
        </section>
      </main>
    </div>
  );
}

export default PrivacyPolicy;
