// Semester array
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

// Get semester index from query string
const urlParams = new URLSearchParams(window.location.search);
let currentSemesterIndex = parseInt(urlParams.get("semester"), 10);
if (
  isNaN(currentSemesterIndex) ||
  currentSemesterIndex < 0 ||
  currentSemesterIndex >= semesters.length
) {
  currentSemesterIndex = 0;
}

// --- DOM references (will be set in DOMContentLoaded) ---
let careerPath, sideInterest1, sideInterest2, generateBtn, courseList;
let addManualBtn,
  courseSearch,
  courseSuggestions,
  manualCourseCode,
  manualCourseName,
  manualCourseCredits,
  saveBtn;
let searchTimeout = null;
let selectedCourse = null;

// Initialize when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  // Set semester title
  const semesterTitle = document.getElementById("semesterTitle");
  if (semesterTitle) {
    semesterTitle.textContent = semesters[currentSemesterIndex];
  }

  // Get DOM references
  careerPath = document.getElementById("careerPath");
  sideInterest1 = document.getElementById("sideInterest1");
  sideInterest2 = document.getElementById("sideInterest2");
  generateBtn = document.getElementById("generateCourses");
  courseList = document.getElementById("courseList");
  courseSearch = document.getElementById("courseSearch");
  courseSuggestions = document.getElementById("courseSuggestions");
  addManualBtn = document.getElementById("addManualCourse");
  manualCourseCode = document.getElementById("manualCourseCode");
  manualCourseName = document.getElementById("manualCourseName");
  manualCourseCredits = document.getElementById("manualCourseCredits");
  saveBtn = document.getElementById("saveSemester");

  // Attach event listeners
  if (generateBtn) {
    generateBtn.addEventListener("click", generateCourseIdeas);
  }
  if (addManualBtn) {
    addManualBtn.addEventListener("click", addManualCourse);
  }
  if (saveBtn) {
    saveBtn.addEventListener("click", saveSemesterPlan);
  }

  // Load existing courses for this semester
  loadExistingCourses();

  // Setup autocomplete for course search
  if (courseSearch) {
    courseSearch.addEventListener("input", handleCourseSearch);
    courseSearch.addEventListener("blur", () => {
      // Hide suggestions after a short delay to allow click events
      setTimeout(() => {
        if (courseSuggestions) courseSuggestions.style.display = "none";
      }, 200);
    });
    courseSearch.addEventListener("focus", () => {
      // Show suggestions again if there's text
      if (courseSearch.value.trim().length > 0) {
        handleCourseSearch({ target: courseSearch });
      }
    });
  }

  // Close suggestions when clicking outside
  document.addEventListener("click", (e) => {
    if (
      courseSearch &&
      courseSuggestions &&
      !courseSearch.contains(e.target) &&
      !courseSuggestions.contains(e.target)
    ) {
      courseSuggestions.style.display = "none";
    }
  });
});

// Generate course ideas
async function generateCourseIdeas() {
  // Validate DOM elements
  if (!courseList) {
    console.error("Course list element not found");
    alert("Error: Page elements not loaded. Please refresh the page.");
    return;
  }

  // Check for token
  const token = localStorage.getItem("token");
  if (!token) {
    alert("Please login first");
    window.location.href = "/";
    return;
  }

  // Validate career path
  if (!careerPath || !careerPath.value.trim()) {
    alert("Please enter your intended career path");
    if (careerPath) careerPath.focus();
    return;
  }

  // Clear and show loading
  courseList.innerHTML =
    "<li style='color: #666;'>Loading recommendations...</li>";
  if (generateBtn) generateBtn.disabled = true;

  const body = {
    semester: semesters[currentSemesterIndex],
    career_path: careerPath.value.trim(),
    side_interests: [
      sideInterest1?.value?.trim(),
      sideInterest2?.value?.trim(),
    ].filter(Boolean),
  };

  try {
    const response = await fetch("/api/recommendations/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();

    if (!response.ok) {
      // Handle specific error types
      if (response.status === 401) {
        alert("Session expired. Please login again.");
        localStorage.removeItem("token");
        window.location.href = "/";
        return;
      }
      throw new Error(data.error || "Failed to generate recommendations");
    }

    // Validate response structure
    if (!data.courses || !Array.isArray(data.courses)) {
      throw new Error("Invalid response format from server");
    }

    // Clear loading message
    courseList.innerHTML = "";

    if (data.courses.length === 0) {
      courseList.innerHTML =
        "<li style='color: #666;'>No courses available for this semester.</li>";
      return;
    }

    // Populate courses
    data.courses.forEach((course, idx) => {
      const li = document.createElement("li");

      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.id = `course${idx}`;
      checkbox.value = `${course.course_code} ${course.title} (${course.credits} credits)`;
      checkbox.checked = true; // Default to selected

      const label = document.createElement("label");
      label.htmlFor = checkbox.id;
      label.textContent = `${course.course_code} ${course.title} (${course.credits} credits)`;

      li.appendChild(checkbox);
      li.appendChild(label);
      courseList.appendChild(li);
    });
  } catch (err) {
    console.error(err);
    courseList.innerHTML = `<li style="color: red;">Error: ${err.message}</li>`;
    alert(`Error generating courses: ${err.message}`);
  } finally {
    if (generateBtn) generateBtn.disabled = false;
  }
}

// --- Course search autocomplete ---
async function handleCourseSearch(e) {
  const query = e.target.value.trim();

  if (!courseSuggestions) return;

  // Clear previous timeout
  if (searchTimeout) {
    clearTimeout(searchTimeout);
  }

  // Hide suggestions if query is too short
  if (query.length < 2) {
    courseSuggestions.style.display = "none";
    courseSuggestions.innerHTML = "";
    selectedCourse = null;
    clearCourseFields();
    return;
  }

  // Debounce search requests
  searchTimeout = setTimeout(async () => {
    try {
      const response = await fetch(
        `/api/courses/search?q=${encodeURIComponent(query)}&limit=10`
      );
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to search courses");
      }

      displayCourseSuggestions(data.courses || []);
    } catch (err) {
      console.error("Error searching courses:", err);
      courseSuggestions.style.display = "none";
    }
  }, 300);
}

function displayCourseSuggestions(courses) {
  if (!courseSuggestions) return;

  if (courses.length === 0) {
    courseSuggestions.innerHTML =
      "<div class='suggestion-item'>No courses found</div>";
    courseSuggestions.style.display = "block";
    return;
  }

  courseSuggestions.innerHTML = "";
  courses.forEach((course) => {
    const item = document.createElement("div");
    item.className = "suggestion-item";
    item.innerHTML = `
      <strong>${course.course_code}</strong> - ${course.title} (${course.credits} credits)
    `;
    item.addEventListener("click", () => {
      selectCourse(course);
    });
    courseSuggestions.appendChild(item);
  });

  courseSuggestions.style.display = "block";
}

function selectCourse(course) {
  selectedCourse = course;

  // Fill in the fields
  if (manualCourseCode) {
    manualCourseCode.value = course.course_code;
  }
  if (manualCourseName) {
    manualCourseName.value = course.title;
  }
  if (manualCourseCredits) {
    manualCourseCredits.value = course.credits;
  }

  // Update search input to show selected course
  if (courseSearch) {
    courseSearch.value = `${course.course_code} - ${course.title}`;
  }

  // Hide suggestions
  if (courseSuggestions) {
    courseSuggestions.style.display = "none";
  }
}

function clearCourseFields() {
  if (manualCourseCode) manualCourseCode.value = "";
  if (manualCourseName) manualCourseName.value = "";
  if (manualCourseCredits) manualCourseCredits.value = "";
  selectedCourse = null;
}

// --- Add manual course ---
function addManualCourse() {
  if (!manualCourseName || !manualCourseCredits || !courseList) {
    alert("Error: Page elements not loaded. Please refresh the page.");
    return;
  }

  const code = manualCourseCode?.value?.trim() || "";
  const name = manualCourseName.value.trim();
  const credits = manualCourseCredits.value.trim();

  if (!code || !name || !credits) {
    alert("Please search and select a course first.");
    if (courseSearch) courseSearch.focus();
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
  if (courseSearch) courseSearch.value = "";
  clearCourseFields();
}

// --- Load existing courses for current semester ---
async function loadExistingCourses() {
  const token = localStorage.getItem("token");
  if (!token) {
    return; // Not logged in, skip loading
  }

  try {
    const response = await fetch("/api/plans/load", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        return; // Not authorized, skip
      }
      return; // Error loading, continue without existing courses
    }

    const data = await response.json();
    const currentSemester = semesters[currentSemesterIndex];
    const existingCourses = data[currentSemester] || [];

    if (existingCourses.length > 0 && courseList) {
      // Clear any loading message
      courseList.innerHTML = "";

      // Add existing courses to the list
      existingCourses.forEach((courseString, idx) => {
        const li = document.createElement("li");

        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.id = `existingCourse${idx}`;
        checkbox.value = courseString;
        checkbox.checked = true; // Existing courses are selected by default

        const label = document.createElement("label");
        label.htmlFor = checkbox.id;
        label.textContent = courseString;

        li.appendChild(checkbox);
        li.appendChild(label);
        courseList.appendChild(li);
      });
    }
  } catch (err) {
    console.error("Error loading existing courses:", err);
    // Continue without existing courses
  }
}

// --- Save semester plan ---
async function saveSemesterPlan() {
  if (!courseList) {
    alert("Error: Page elements not loaded. Please refresh the page.");
    return;
  }

  // Check for token
  const token = localStorage.getItem("token");
  if (!token) {
    alert("Please login first");
    window.location.href = "/";
    return;
  }

  const selectedCourses = [];
  courseList.querySelectorAll("input[type='checkbox']").forEach((cb) => {
    if (cb.checked) {
      selectedCourses.push(cb.value);
    }
  });

  if (selectedCourses.length === 0) {
    alert("Please select at least one course to save.");
    return;
  }

  // Show loading
  if (saveBtn) saveBtn.disabled = true;
  const originalText = saveBtn?.textContent;
  if (saveBtn) saveBtn.textContent = "Saving...";

  try {
    const response = await fetch("/api/plans/save", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        semester: semesters[currentSemesterIndex],
        courses: selectedCourses,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      if (response.status === 401) {
        alert("Session expired. Please login again.");
        localStorage.removeItem("token");
        window.location.href = "/";
        return;
      }
      throw new Error(data.error || "Failed to save semester plan");
    }

    alert(
      `Semester plan saved successfully!\n${selectedCourses.length} course(s) saved.`
    );
    // Optionally redirect to full plan view
    // window.location.href = "/fullplan";
  } catch (err) {
    console.error(err);
    alert(`Error saving semester plan: ${err.message}`);
  } finally {
    if (saveBtn) {
      saveBtn.disabled = false;
      if (originalText) saveBtn.textContent = originalText;
    }
  }
}
