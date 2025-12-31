-- ===============================
-- DATABASE
-- ===============================
CREATE DATABASE skill_recommender;
USE skill_recommender;

-- ===============================
-- USERS
-- ===============================
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    experience_years INT NOT NULL
);

-- ===============================
-- SKILLS
-- ===============================
CREATE TABLE skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    skill_name VARCHAR(100) UNIQUE NOT NULL
);

-- ===============================
-- JOBS
-- ===============================
CREATE TABLE jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    min_experience INT NOT NULL
);

-- ===============================
-- USER ↔ SKILLS (MANY-TO-MANY)
-- ===============================
CREATE TABLE user_skills (
    user_id INT NOT NULL,
    skill_id INT NOT NULL,
    PRIMARY KEY (user_id, skill_id),
    CONSTRAINT fk_user_skills_user
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_user_skills_skill
        FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
);

-- ===============================
-- JOB ↔ SKILLS (MANY-TO-MANY)
-- ===============================
CREATE TABLE job_skills (
    job_id INT NOT NULL,
    skill_id INT NOT NULL,
    PRIMARY KEY (job_id, skill_id),
    CONSTRAINT fk_job_skills_job
        FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    CONSTRAINT fk_job_skills_skill
        FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
);

-- ===============================
-- INDEXES (PERFORMANCE)
-- ===============================
CREATE INDEX idx_user_skills_skill ON user_skills(skill_id);
CREATE INDEX idx_job_skills_skill ON job_skills(skill_id);
CREATE INDEX idx_jobs_experience ON jobs(min_experience);
