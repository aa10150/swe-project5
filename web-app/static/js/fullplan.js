// Semesters
const semesters = [
  "Freshman Fall", "Freshman Spring",
  "Sophomore Fall", "Sophomore Spring",
  "Junior Fall", "Junior Spring",
  "Senior Fall", "Senior Spring"
];

// --- Fetch data from backend ---
async function loadPlan() {
  try {
    // API endpoint -- fix later
    const response = await fetch("/api/???");
    if (!response.ok) throw new Error("Failed to load plan");
    return await response.json();
    // Format: { "Freshman Fall": ["CSCI-UA 101 Intro to CS (4 credits)", ...], ... }
  } catch (err) {
    console.error(err);
    return {};
  }
}

// --- Populate full plan view ---
async function populateFullPlan() {
  const plan = await loadPlan();

  semesters.forEach((semester, idx) => {
    const semesterId = semester.toLowerCase().replace(" ", "-"); // "Freshman Fall" -> "freshman-fall"
    const semesterDiv = document.getElementById(semesterId);
    const courseList = semesterDiv.querySelector(".course-list");
    courseList.innerHTML = "";

    if (plan[semester] && plan[semester].length > 0) {
      plan[semester].forEach(course => {
        const li = document.createElement("li");
        li.textContent = course; // already includes code + name + credits
        courseList.appendChild(li);
      });
    } else {
      const li = document.createElement("li");
      li.textContent = "(No courses added yet)";
      courseList.appendChild(li);
    }
  });
}

// --- Initialize ---
document.addEventListener("DOMContentLoaded", populateFullPlan);