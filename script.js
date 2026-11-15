"use strict";
// If using VS Code Live Server (usually port 5500), the API still runs on port 8000.
const API_BASE = location.port === "8000" ? "" : "http://127.0.0.1:8000";
const $ = (id) => document.getElementById(id);
let students = [];
let editingId = null;

async function api(path, options = {}) {
  let response;
  try {
    response = await fetch(API_BASE + path, {
      ...options,
      headers: { "Content-Type": "application/json", ...options.headers }
    });
  } catch (error) {
    throw new Error("Cannot connect to Python. Run app.py in VS Code before using the website.");
  }
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Something went wrong.");
  return data;
}

function showMessage(message, isError = false) {
  const node = $("message");
  node.textContent = message;
  node.classList.toggle("error", isError);
  node.hidden = false;
}

function makeCell(value, className = "") {
  const td = document.createElement("td");
  td.textContent = value; // Use textContent to avoid injecting HTML from student names.
  if (className) td.className = className;
  return td;
}

function renderRows(records) {
  const tbody = $("studentRows");
  tbody.replaceChildren();
  $("recordCount").textContent = `${records.length} record${records.length === 1 ? "" : "s"}`;
  $("emptyState").hidden = records.length !== 0;
  records.forEach((student) => {
    const row = document.createElement("tr");
    row.append(makeCell(student.student_id), makeCell(student.name, "name"));

    const programmeCell = document.createElement("td");
    const pill = document.createElement("span");
    pill.className = "programme-pill " + (student.programme === "Business" ? "programme-business" : "programme-computing");
    pill.textContent = student.programme;
    programmeCell.appendChild(pill);
    row.appendChild(programmeCell);
    row.append(makeCell(student.dob), makeCell(Number(student.cgpa).toFixed(2)));

    const actions = document.createElement("td");
    const buttons = document.createElement("div");
    buttons.className = "row-actions";
    const edit = document.createElement("button");
    edit.type = "button"; edit.className = "link-button"; edit.textContent = "Edit";
    edit.addEventListener("click", () => openForm(student));
    const del = document.createElement("button");
    del.type = "button"; del.className = "link-button delete"; del.textContent = "Delete";
    del.addEventListener("click", () => deleteStudent(student));
    buttons.append(edit, del); actions.appendChild(buttons); row.appendChild(actions);
    tbody.appendChild(row);
  });
}

function updateStatistics() {
  $("totalStudents").textContent = students.length;
  $("businessStudents").textContent = students.filter(s => s.programme === "Business").length;
  $("computingStudents").textContent = students.filter(s => s.programme === "Computing").length;
  $("averageCGPA").textContent = students.length
    ? (students.reduce((sum, s) => sum + Number(s.cgpa), 0) / students.length).toFixed(2)
    : "0.00";
}

async function loadStudents() {
  students = await api("/api/students");
  updateStatistics();
  const term = $("searchInput").value.trim();
  if (term) {
    const result = await api(`/api/students?by=${encodeURIComponent($("searchBy").value)}&query=${encodeURIComponent(term)}`);
    renderRows(result);
  } else {
    renderRows(students);
  }
}

function openForm(student = null) {
  editingId = student ? student.student_id : null;
  $("studentForm").reset();
  $("formError").hidden = true;
  $("modalHeading").textContent = student ? "Edit Student" : "Add Student";
  $("saveStudent").textContent = student ? "Update Student" : "Save Student";
  $("studentId").disabled = Boolean(student);
  if (student) {
    $("studentId").value = student.student_id;
    $("studentName").value = student.name;
    $("studentProgramme").value = student.programme;
    $("studentDob").value = student.dob;
    $("studentCgpa").value = Number(student.cgpa).toFixed(2);
  }
  $("studentModal").hidden = false;
  $(student ? "studentName" : "studentId").focus();
}

function closeForm() { $("studentModal").hidden = true; editingId = null; }

async function deleteStudent(student) {
  if (!confirm(`Delete ${student.name} (${student.student_id})? This cannot be undone.`)) return;
  try {
    await api(`/api/students/${encodeURIComponent(student.student_id)}`, { method: "DELETE" });
    await loadStudents();
    showMessage(`${student.name} was deleted successfully.`);
  } catch (error) { showMessage(error.message, true); }
}

$("addStudentBtn").addEventListener("click", () => openForm());
$("closeModal").addEventListener("click", closeForm);
$("cancelModal").addEventListener("click", closeForm);
$("studentModal").addEventListener("click", (event) => {
  if (event.target === $("studentModal")) closeForm();
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !$("studentModal").hidden) closeForm();
});

$("studentForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = {
    student_id: $("studentId").value.trim(), name: $("studentName").value.trim(),
    programme: $("studentProgramme").value, dob: $("studentDob").value,
    cgpa: $("studentCgpa").value
  };
  try {
    const originalId = editingId;
    if (originalId) {
      await api(`/api/students/${encodeURIComponent(originalId)}`, { method: "PUT", body: JSON.stringify(data) });
    } else {
      await api("/api/students", { method: "POST", body: JSON.stringify(data) });
    }
    closeForm();
    await loadStudents();
    showMessage(originalId ? "Student updated successfully." : "Student added successfully.");
  } catch (error) {
    $("formError").textContent = error.message;
    $("formError").hidden = false;
  }
});

$("searchBy").addEventListener("change", () => {
  const placeholders = { id: "Search by Student ID", name: "Search by name", programme: "Search by programme" };
  $("searchInput").placeholder = placeholders[$("searchBy").value];
  $("searchInput").value = "";
  renderRows(students);
});

$("searchForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const term = $("searchInput").value.trim();
    if (!term) { renderRows(students); return; }
    const result = await api(`/api/students?by=${encodeURIComponent($("searchBy").value)}&query=${encodeURIComponent(term)}`);
    renderRows(result);
    $("message").hidden = true;
  } catch (error) { showMessage(error.message, true); }
});

$("resetSearch").addEventListener("click", () => {
  $("searchInput").value = "";
  renderRows(students);
  $("message").hidden = true;
});

loadStudents().catch(error => showMessage(error.message, true));
