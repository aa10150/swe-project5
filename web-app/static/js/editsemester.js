// Semester array
const semesters = [
  "Freshman Fall", "Freshman Spring",
  "Sophomore Fall", "Sophomore Spring",
  "Junior Fall", "Junior Spring",
  "Senior Fall", "Senior Spring"
];

// Get semester index from query string
const urlParams = new URLSearchParams(window.location.search);
let currentSemesterIndex = parseInt(urlParams.get("semester"), 10);
if (isNaN(currentSemesterIndex) || currentSemesterIndex < 0 || currentSemesterIndex >= semesters.length) {
  currentSemesterIndex = 0;
}
// Initialize semester title
document.addEventListener("DOMContentLoaded", () => {
  const semesterTitle = document.getElementById("semesterTitle");
  if (semesterTitle) {
    semesterTitle.textContent = semesters[currentSemesterIndex];
  }
});

// --- DOM references ---
const careerPath = document.getElementById("careerPath");
const sideInterest1 = document.getElementById("sideInterest1");
const sideInterest2 = document.getElementById("sideInterest2");
const generateBtn = document.getElementById("generateCourses");
const courseList = document.getElementById("courseList");
const addManualBtn = document.getElementById("addManualCourse");
const manualCourseCode = document.getElementById("manualCourseCode");
const manualCourseName = document.getElementById("manualCourseName");
const manualCourseCredits = document.getElementById("manualCourseCredits");
const saveBtn = document.getElementById("saveSemester");


// Generate course ideas
async function generateCourseIdeas() {
  courseList.innerHTML = "";

  const body = {
    semester: semesters[currentSemesterIndex],
    career_path: careerPath.value,
    side_interests: [sideInterest1.value, sideInterest2.value].filter(Boolean)
  };

  try {
    const response = await fetch("/api/recommendations/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${localStorage.getItem("token")}` // assuming you store JWT
      },
      body: JSON.stringify(body)
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Failed to generate");

    data.courses.forEach((course, idx) => {
      const li = document.createElement("li");

      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.id = `course${idx}`;
      checkbox.value = `${course.course_code} ${course.title} (${course.credits} credits)`;

      const label = document.createElement("label");
      label.htmlFor = checkbox.id;
      label.textContent = `${course.course_code} ${course.title} (${course.credits} credits)`;

      li.appendChild(checkbox);
      li.appendChild(label);
      courseList.appendChild(li);
    });
  } catch (err) {
    console.error(err);
    alert("Error generating courses. Please try again.");
  }
}

// --- Add manual course ---
function addManualCourse() {
  const code = manualCourseCode.value.trim();
  const name = manualCourseName.value.trim();
  const credits = manualCourseCredits.value.trim();

  if (!name || !credits) {
    alert("Please enter both course name and credits.");
    return;
  }

  const li = document.createElement("li");

  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.checked = true; // manual courses default to selected
  checkbox.value = `${code} ${name} (${credits} credits)`;

  const label = document.createElement("label");
  label.textContent = `${code} ${name} (${credits} credits)`;

  li.appendChild(checkbox);
  li.appendChild(label);
  courseList.appendChild(li);

  // Clear inputs
  manualCourseName.value = "";
  manualCourseCredits.value = "";
}

// --- Save semester plan ---
async function saveSemesterPlan() {
  const selectedCourses = [];
  courseList.querySelectorAll("input[type='checkbox']").forEach(cb => {
    if (cb.checked) {
      selectedCourses.push(cb.value);
    }
  });

  try {
    // API endpoint -- fix later
    const response = await fetch("/api/???", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        semester: semesters[currentSemesterIndex],
        courses: selectedCourses
      })
    });

    if (!response.ok) throw new Error("Failed to save semester plan");

    alert(`Semester plan saved\n${selectedCourses.join("\n")}`);
  } catch (err) {
    console.error(err);
    alert("Error saving semester plan. Please try again.");
  }
}

// --- Event listeners ---
generateBtn.addEventListener("click", generateCourseIdeas);
addManualBtn.addEventListener("click", addManualCourse);
saveBtn.addEventListener("click", saveSemesterPlan);