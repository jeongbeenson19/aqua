import React from "react";
import { Routes, Route } from "react-router-dom";
import KakaoLogin from "../pages/kakaoLogin";
import Redirection from "../pages/redirection";
import Signup from "../pages/signup";
import Home from "../pages/Home";
import Quiz from "../pages/quiz";
import ExamReview from "../pages/examReview";


const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/login" element={<KakaoLogin />} />
      <Route path="/redirection" element={<Redirection />} />
      <Route path="/signup" element={<Signup />} />

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
