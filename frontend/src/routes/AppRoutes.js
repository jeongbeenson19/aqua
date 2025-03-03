import React from "react";
import { Routes, Route } from "react-router-dom";
// import ProtectedRoute from "../pages/protectedRoute";
import Home from "../pages/Home";
import Quiz from "../pages/quiz";
import ExamReview from "../pages/examReview";
import KakaoLogin from "../pages/kakaoLogin";
import Redirection from "../pages/redirection";

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/login" element={<KakaoLogin />} />
      <Route path="/redirection" element={<Redirection />} />

      {/* <Route element={<ProtectedRoute />}>
        <Route path="/" element={<Home />} />
        <Route path="/quiz/:subjectId" element={<Quiz />} />
        <Route path="/examreview/:attempedId" element={<ExamReview />} />
      </Route> */}

      <Route path="/" element={<Home />} />
      <Route path="/quiz/:subjectId" element={<Quiz />} />
      <Route path="/examreview/:attempedId" element={<ExamReview />} />

    </Routes>
  );
};

export default AppRoutes;
