import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote

from student_factory import StudentFactory
from student_repository import StudentRepository
from student_service import DuplicateStudentID, StudentNotFound, StudentService
from student_facade import StudentManagementFacade
from validation import ValidationError

ROOT = Path(__file__).resolve().parent
HOST, PORT = "127.0.0.1", 8000


def create_facade(filename=ROOT / "student.txt"):
    factory = StudentFactory()
    repository = StudentRepository(filename, factory)
    service = StudentService(repository, factory)
    return StudentManagementFacade(service)


class StudentHandler(BaseHTTPRequestHandler):
    """HTTP handling only: all student work goes through the Facade."""
    facade = None  # Set once when the local server starts.

    def _send(self, status, content, content_type="application/json; charset=utf-8"):
        body = (json.dumps(content, ensure_ascii=False).encode("utf-8")
                if content_type.startswith("application/json") else content)
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        # Allow the VS Code Live Server preview (usually port 5500) to use this API.
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _json_body(self):
        try:
            size = int(self.headers.get("Content-Length", 0))
            if size <= 0 or size > 16000:
                raise ValidationError("Request data is empty or too large.")
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict):
                raise ValueError("JSON must be an object")
            return data
        except (ValueError, UnicodeDecodeError) as exc:
            raise ValidationError("Invalid student data (JSON object required).") from exc

    def _run_action(self, action):
        try:
            action()
        except DuplicateStudentID as exc:
            self._send(409, {"error": str(exc)})
        except ValidationError as exc:
            self._send(400, {"error": str(exc)})
        except StudentNotFound as exc:
            self._send(404, {"error": str(exc)})
        except OSError as exc:
            self._send(500, {"error": str(exc)})

    def do_OPTIONS(self):
        self._send(204, b"", "text/plain")

    def do_GET(self):
        def action():
            url = urlparse(self.path)
            static_files = {
                "/": ("index.html", "text/html; charset=utf-8"),
                "/index.html": ("index.html", "text/html; charset=utf-8"),
                "/style.css": ("style.css", "text/css; charset=utf-8"),
                "/script.js": ("script.js", "text/javascript; charset=utf-8"),
            }
            if url.path in static_files:
                filename, content_type = static_files[url.path]
                self._send(200, (ROOT / filename).read_bytes(), content_type)
            elif url.path == "/api/students":
                params = parse_qs(url.query)
                keyword = params.get("query", [""])[0]
                if keyword.strip():
                    records = self.facade.search_students(params.get("by", ["id"])[0], keyword)
                else:
                    records = self.facade.list_students()
                self._send(200, records)
            else:
                self._send(404, {"error": "Page not found."})
        self._run_action(action)

    def do_POST(self):
        def action():
            if urlparse(self.path).path != "/api/students":
                self._send(404, {"error": "Page not found."})
                return
            student = self.facade.add_student(self._json_body())
            self._send(201, student)
        self._run_action(action)

    def do_PUT(self):
        def action():
            path = urlparse(self.path).path
            if not path.startswith("/api/students/"):
                self._send(404, {"error": "Page not found."})
                return
            student_id = unquote(path.removeprefix("/api/students/"))
            student = self.facade.update_student(student_id, self._json_body())
            self._send(200, student)
        self._run_action(action)

    def do_DELETE(self):
        def action():
            path = urlparse(self.path).path
            if not path.startswith("/api/students/"):
                self._send(404, {"error": "Page not found."})
                return
            student_id = unquote(path.removeprefix("/api/students/"))
            self.facade.delete_student(student_id)
            self._send(200, {"message": "Student deleted successfully."})
        self._run_action(action)


def main():
    try:
        StudentHandler.facade = create_facade()
    except (OSError, ValueError) as exc:
        print(f"Cannot open student records: {exc}")
        return
    try:
        with ThreadingHTTPServer((HOST, PORT), StudentHandler) as server:
            print(f"Student Management System: http://{HOST}:{PORT}")
            print("Open the link in Chrome, or open index.html with VS Code Live Server.")
            print("Press Stop in VS Code to stop the server.")
            server.serve_forever()
    except OSError as exc:
        print(f"Cannot start website: {exc}")
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    main()
