// Semester array
const semesters = [
  "Freshman Fall", "Freshman Spring",
  "Sophomore Fall", "Sophomore Spring",
  "Junior Fall", "Junior Spring",
  "Senior Fall", "Senior Spring"
];

// Get semester index from query string
const urlParams = new URLSearchParams(window.location.search);
let currentSemesterIndex = parseInt(urlParams.get("semester")) || 0;

// Temporary dummy data - course array with codes
const dummyCourses = [
  { code: "CSCI-UA 101", name: "Introduction to Computer Science", credits: 4 },
  { code: "MATH-UA 121", name: "Calculus I", credits: 4 },
  { code: "EXPOS-UA 1", name: "Writing the Essay", credits: 4 },
  { code: "PSYCH-UA 1", name: "Foundations of Psychology", credits: 4 }
];

// --- DOM references ---
const semesterTitle = document.getElementById("semesterTitle");
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

// --- Initialize semester title ---
function setSemesterTitle() {
  semesterTitle.textContent = `${semesters[currentSemesterIndex]}`;
}
setSemesterTitle();

// --- Generate course ideas (dummy data for now) ---
function generateCourseIdeas() {
  courseList.innerHTML = ""; // clear old list
  dummyCourses.forEach((course, idx) => {
    const li = document.createElement("li");

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.id = `course${idx}`;
    checkbox.value = `${course.code} ${course.name} (${course.credits} credits)`;

    const label = document.createElement("label");
    label.htmlFor = checkbox.id;
    label.textContent = `${course.code} ${course.name} (${course.credits} credits)`;

    const replaceBtn = document.createElement("button");
    replaceBtn.type = "button";
    replaceBtn.textContent = "Replace";
    replaceBtn.classList.add("replace-btn");
    replaceBtn.addEventListener("click", () => {
      // Replace with a new dummy course (for demo)
      const newCourse = { code: `ALT-UA ${100 + idx}`, name: `Alternate Course ${idx + 1}`, credits: 3 };
      label.textContent = `${newCourse.code} ${newCourse.name} (${newCourse.credits} credits)`;
      checkbox.value = `${newCourse.code} ${newCourse.name} (${newCourse.credits} credits)`;
    });

    li.appendChild(checkbox);
    li.appendChild(label);
    li.appendChild(replaceBtn);
    courseList.appendChild(li);
  });
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