// Semesters
const semesters = [
  "Freshman Fall",
  "Freshman Spring",
  "Sophomore Fall",
  "Sophomore Spring",
  "Junior Fall",
  "Junior Spring",
  "Senior Fall",
  "Senior Spring",
];

// --- Fetch data from backend ---
async function loadPlan() {
  try {
    // Check for token
    const token = localStorage.getItem("token");
    if (!token) {
      console.warn("No token found, user may not be logged in");
      return {};
    }

    const response = await fetch("/api/plans/load", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        console.warn("Unauthorized - token may be expired");
        localStorage.removeItem("token");
        // Optionally redirect to login
        // window.location.href = "/";
        return {};
      }
      throw new Error(`Failed to load plan: ${response.status}`);
    }

    const data = await response.json();
    // Format: { "Freshman Fall": ["CSCI-UA.0101 Intro to CS (4 credits)", ...], ... }
    return data;
  } catch (err) {
    console.error("Error loading plan:", err);
    return {};
  }
}

// --- Populate full plan view ---
async function populateFullPlan() {
  // Show loading state
  semesters.forEach((semester) => {
    const semesterId = semester.toLowerCase().replace(" ", "-");
    const semesterDiv = document.getElementById(semesterId);
    if (semesterDiv) {
      const courseList = semesterDiv.querySelector(".course-list");
      if (courseList) {
        courseList.innerHTML = "<li style='color: #666;'>Loading...</li>";
      }
    }
  });

  const plan = await loadPlan();

  semesters.forEach((semester, idx) => {
    const semesterId = semester.toLowerCase().replace(" ", "-"); // "Freshman Fall" -> "freshman-fall"
    const semesterDiv = document.getElementById(semesterId);
    if (!semesterDiv) {
      console.warn(`Semester div not found: ${semesterId}`);
      return;
    }

    const courseList = semesterDiv.querySelector(".course-list");
    if (!courseList) {
      console.warn(`Course list not found for: ${semesterId}`);
      return;
    }

    courseList.innerHTML = "";

    if (plan[semester] && plan[semester].length > 0) {
      plan[semester].forEach((course) => {
        const li = document.createElement("li");
        li.textContent = course; // already includes code + name + credits
        courseList.appendChild(li);
      });
    } else {
      const li = document.createElement("li");
      li.textContent = "(No courses added yet)";
      li.style.color = "#666";
      courseList.appendChild(li);
    }
  });
}

// --- Initialize ---
document.addEventListener("DOMContentLoaded", populateFullPlan);
